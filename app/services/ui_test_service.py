import subprocess
import tempfile
import os
import time
import json
import re
from pathlib import Path
from app.models import UITestCase
from app.schemas import UITestResult, UITestStepResult
from config import settings


def run_ui_case(case: UITestCase, progress_callback=None) -> UITestResult:
    """
    执行UI测试用例
    
    通过subprocess运行用例script字段中的Playwright Python代码
    支持步骤截图和注释功能
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"[UI Test Service] 开始执行用例: {case.name} (ID: {case.id})")
    
    start_time = time.time()
    screenshot_path = None
    error_log = None
    steps = []
    
    # 更新进度：准备环境
    if progress_callback:
        logger.info("[UI Test Service] 进度: 5% - 准备测试环境")
        progress_callback(5, "准备测试环境", "正在创建截图目录...")
    
    # 创建截图目录（每个用例一个目录）
    screenshot_dir = os.path.join(settings.UPLOAD_DIR, "screenshots", f"case_{case.id}")
    os.makedirs(screenshot_dir, exist_ok=True)
    
    # 更新进度：准备脚本
    if progress_callback:
        logger.info("[UI Test Service] 进度: 10% - 准备测试脚本")
        progress_callback(10, "准备测试脚本", "正在生成测试脚本...")
    
    # 创建临时文件存储测试脚本
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        script_path = f.name
        
        # 修改用户脚本，设置截图目录环境变量
        modified_script = case.script
        
        # 如果脚本中没有设置截图目录，添加设置
        if 'SCREENSHOT_DIR' in modified_script:
            # 替换现有的 SCREENSHOT_DIR 设置
            modified_script = re.sub(
                r'SCREENSHOT_DIR = os\.getenv\("SCREENSHOT_DIR", "[^"]*"\)',
                f'SCREENSHOT_DIR = "{screenshot_dir}"',
                modified_script
            )
        else:
            # 在导入后添加截图目录设置
            if 'import os' in modified_script:
                modified_script = modified_script.replace(
                    'import os',
                    f'import os\nos.environ["SCREENSHOT_DIR"] = "{screenshot_dir}"'
                )
            else:
                modified_script = f'import os\nos.environ["SCREENSHOT_DIR"] = "{screenshot_dir}"\n{modified_script}'
        
        f.write(modified_script)
    
    try:
        # 更新进度：开始执行
        if progress_callback:
            logger.info("[UI Test Service] 进度: 20% - 开始执行测试")
            progress_callback(20, "开始执行测试", "正在启动浏览器...")
        
        # 使用pytest执行测试脚本
        use_docker = os.getenv("USE_DOCKER_FOR_UI_TESTS", "false").lower() == "true"
        
        if use_docker:
            result = _run_in_docker(script_path, screenshot_dir, progress_callback)
        else:
            result = _run_locally(script_path, screenshot_dir, progress_callback)
        
        duration = time.time() - start_time
        
        # 更新进度：解析结果
        if progress_callback:
            logger.info("[UI Test Service] 进度: 80% - 解析测试结果")
            progress_callback(80, "解析测试结果", "正在处理步骤截图...")
        
        # 解析执行结果，提取步骤信息
        output = result.get("output", "")
        steps_data = []
        
        # 尝试从输出中解析 JSON 结果
        try:
            # 查找 JSON 输出（通常在最后）
            lines = output.split('\n')
            json_start = -1
            for i in range(len(lines) - 1, -1, -1):
                line = lines[i].strip()
                if line.startswith('{'):
                    json_start = i
                    break
            
            if json_start >= 0:
                json_str = '\n'.join(lines[json_start:])
                parsed_result = json.loads(json_str)
                
                # 提取步骤信息
                if "steps" in parsed_result:
                    for step_data in parsed_result["steps"]:
                        step_result = UITestStepResult(
                            step_index=step_data.get("step_index", 0),
                            step_name=step_data.get("step_name", ""),
                            step_type=step_data.get("step_type", ""),
                            success=step_data.get("success", True),
                            screenshot_path=step_data.get("screenshot_path"),
                            comment=step_data.get("comment", ""),
                            error=step_data.get("error"),
                            timestamp=step_data.get("timestamp", time.time())
                        )
                        steps_data.append(step_result)
                
                # 获取最终截图
                final_screenshot = parsed_result.get("final_screenshot") or parsed_result.get("error_screenshot")
                if final_screenshot:
                    screenshot_path = final_screenshot
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # 如果无法解析 JSON，使用传统方式
            pass
        
        # 如果没有步骤数据，尝试从截图目录中查找
        if not steps_data and os.path.exists(screenshot_dir):
            screenshot_files = sorted([f for f in os.listdir(screenshot_dir) if f.endswith('.png')])
            for idx, screenshot_file in enumerate(screenshot_files):
                screenshot_path_full = os.path.join(screenshot_dir, screenshot_file)
                step_result = UITestStepResult(
                    step_index=idx,
                    step_name=f"步骤 {idx + 1}",
                    step_type="screenshot",
                    success=True,
                    screenshot_path=screenshot_path_full,
                    comment=f"自动截图: {screenshot_file}",
                    timestamp=time.time()
                )
                steps_data.append(step_result)
            
            if screenshot_files:
                screenshot_path = os.path.join(screenshot_dir, screenshot_files[-1])
        
        # 更新进度：完成
        if progress_callback:
            logger.info("[UI Test Service] 进度: 95% - 生成测试报告")
            progress_callback(95, "生成测试报告", "正在保存测试结果...")
        
        if result["success"]:
            return UITestResult(
                success=True,
                duration=duration,
                screenshot_path=screenshot_path,
                error_log=None,
                steps=steps_data if steps_data else None
            )
        else:
            # 失败时也返回步骤信息
            error_msg = result.get("error", "Unknown error")
            return UITestResult(
                success=False,
                duration=duration,
                screenshot_path=screenshot_path,
                error_log=error_msg,
                steps=steps_data if steps_data else None
            )
            
    except Exception as e:
        duration = time.time() - start_time
        error_log = f"Error executing UI test: {str(e)}"
        
        return UITestResult(
            success=False,
            duration=duration,
            screenshot_path=screenshot_path if screenshot_path and os.path.exists(screenshot_path) else None,
            error_log=error_log,
            steps=steps if steps else None
        )
    finally:
        # 清理临时文件
        if os.path.exists(script_path):
            os.remove(script_path)


def _run_locally(script_path: str, screenshot_dir: str, progress_callback=None) -> dict:
    """在本地执行测试脚本"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # 更新进度：执行中
        if progress_callback:
            logger.info("[UI Test Service] 进度: 30% - 执行测试脚本")
            progress_callback(30, "执行测试脚本", "正在运行 Playwright 脚本...")
        
        # 设置环境变量
        env = os.environ.copy()
        env["SCREENSHOT_DIR"] = screenshot_dir
        
        # 使用python直接执行，实时读取输出以更新进度
        import threading
        import queue
        
        process = subprocess.Popen(
            ["python", script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            cwd=os.path.dirname(script_path) or None,
            bufsize=1
        )
        
        output_lines = []
        error_lines = []
        output_queue = queue.Queue()
        error_queue = queue.Queue()
        
        def read_output():
            """读取标准输出"""
            try:
                for line in iter(process.stdout.readline, ''):
                    if not line:
                        break
                    output_lines.append(line)
                    output_queue.put(('stdout', line))
            except Exception as e:
                print(f"Error reading stdout: {e}")
        
        def read_error():
            """读取标准错误"""
            try:
                for line in iter(process.stderr.readline, ''):
                    if not line:
                        break
                    error_lines.append(line)
                    error_queue.put(('stderr', line))
            except Exception as e:
                print(f"Error reading stderr: {e}")
        
        # 启动读取线程
        output_thread = threading.Thread(target=read_output, daemon=True)
        error_thread = threading.Thread(target=read_error, daemon=True)
        output_thread.start()
        error_thread.start()
        
        # 实时处理输出并更新进度
        start_time = time.time()
        last_progress = 30
        step_count = 0
        max_wait_time = 300  # 5分钟超时
        
        try:
            while process.poll() is None:
                # 检查超时
                elapsed = time.time() - start_time
                if elapsed > max_wait_time:
                    process.kill()
                    return {
                        "success": False,
                        "error": "Test execution timeout (exceeded 5 minutes)",
                        "output": ""
                    }
                # 处理输出队列
                try:
                    while True:
                        stream_type, line = output_queue.get_nowait()
                        # 检测步骤执行（匹配 [STEP X] 格式）
                        if "[STEP" in line or "步骤" in line or "step_" in line.lower() or "take_screenshot" in line.lower():
                            # 尝试从输出中提取步骤编号
                            import re
                            step_match = re.search(r'\[STEP\s+(\d+)\]', line)
                            if step_match:
                                new_step_count = int(step_match.group(1)) + 1
                                if new_step_count > step_count:
                                    step_count = new_step_count
                            else:
                                step_count += 1
                            
                            # 根据步骤数更新进度（30% - 75%）
                            # 假设最多20个步骤，如果超过则按时间计算
                            if step_count <= 20:
                                last_progress = min(30 + int((step_count / 20) * 45), 75)
                            else:
                                # 超过20步，按时间比例计算
                                time_progress = min(30 + int((elapsed / max_wait_time) * 45), 75)
                                last_progress = max(last_progress, time_progress)
                            
                            if progress_callback:
                                logger.info(f"[UI Test Service] 检测到步骤 {step_count}，更新进度: {last_progress}%")
                                progress_callback(
                                    last_progress,
                                    f"执行步骤 {step_count}",
                                    f"已执行 {step_count} 个步骤"
                                )
                except queue.Empty:
                    pass
                
                # 处理错误队列
                try:
                    while True:
                        stream_type, line = error_queue.get_nowait()
                        # 错误信息也计入输出
                        pass
                except queue.Empty:
                    pass
                
                # 根据时间更新进度（防止长时间无输出，每5秒更新一次）
                elapsed = time.time() - start_time
                if elapsed > 5 and int(elapsed) % 5 == 0:  # 每5秒更新一次
                    time_progress = min(30 + int((elapsed / max_wait_time) * 45), 75)
                    if time_progress > last_progress and progress_callback:
                        logger.info(f"[UI Test Service] 时间进度更新: {time_progress}% (已运行 {int(elapsed)} 秒)")
                        progress_callback(
                            time_progress,
                            "执行中...",
                            f"已运行 {int(elapsed)} 秒"
                        )
                        last_progress = time_progress
                
                time.sleep(0.5)  # 每0.5秒检查一次
            
            # 等待线程完成
            output_thread.join(timeout=2)
            error_thread.join(timeout=2)
            
            output = ''.join(output_lines)
            error_output = ''.join(error_lines)
            
            # 更新进度：执行完成
            if progress_callback:
                progress_callback(75, "测试执行完成", "正在处理结果..." if process.returncode == 0 else "测试执行失败")
            
            result = type('obj', (object,), {
                'returncode': process.returncode,
                'stdout': output,
                'stderr': error_output
            })()
            
        except Exception as e:
            # 如果出错，尝试终止进程
            try:
                process.kill()
            except:
                pass
            raise
        
        return {
            "success": result.returncode == 0,
            "error": error_output if result.returncode != 0 else None,
            "output": output + error_output
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Test execution timeout (exceeded 5 minutes)",
            "output": ""
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "output": ""
        }


def _run_in_docker(script_path: str, screenshot_dir: str, progress_callback=None) -> dict:
    """
    在Docker容器中执行测试脚本
    
    需要配置一个包含Playwright和浏览器的Docker容器
    示例Docker命令：
    docker run --rm -v /path/to/script:/app/script -v /path/to/screenshots:/app/screenshots playwright-test pytest /app/script
    """
    docker_image = os.getenv("PLAYWRIGHT_DOCKER_IMAGE", "playwright-test:latest")
    
    try:
        # 获取脚本和截图的绝对路径
        script_abs_path = os.path.abspath(script_path)
        screenshot_abs_dir = os.path.abspath(screenshot_dir)
        
        # 构建Docker命令
        docker_cmd = [
            "docker", "run", "--rm",
            "-v", f"{script_abs_path}:/app/test_script.py",
            "-v", f"{screenshot_abs_dir}:/app/screenshots",
            "-e", f"SCREENSHOT_DIR=/app/screenshots",
            docker_image,
            "python", "/app/test_script.py"
        ]
        
        result = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10分钟超时
        )
        
        output = result.stdout + result.stderr
        
        return {
            "success": result.returncode == 0,
            "error": result.stderr if result.returncode != 0 else None,
            "output": output
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Docker test execution timeout",
            "output": ""
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Docker execution error: {str(e)}",
            "output": ""
        }
