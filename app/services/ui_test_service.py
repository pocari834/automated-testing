import subprocess
import tempfile
import os
import time
from pathlib import Path
from app.models import UITestCase
from app.schemas import UITestResult
from config import settings


def run_ui_case(case: UITestCase) -> UITestResult:
    """
    执行UI测试用例
    
    通过subprocess运行用例script字段中的Playwright Python代码
    需要在Docker容器中运行，这里提供基础实现
    """
    start_time = time.time()
    screenshot_path = None
    error_log = None
    
    # 创建临时文件存储测试脚本
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        script_path = f.name
        
        # 写入测试脚本
        # 包装用户脚本，添加必要的导入和截图功能
        wrapped_script = f"""
import sys
import os
from playwright.sync_api import sync_playwright
import pytest

# 用户脚本
{case.script}

# 如果用户脚本没有定义test函数，创建一个默认的
if 'def test_' not in '''{case.script}''':
    def test_default():
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://example.com")
            browser.close()
"""
        f.write(wrapped_script)
    
    try:
        # 创建截图目录
        screenshot_dir = os.path.join(settings.UPLOAD_DIR, "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshot_dir, f"ui_test_{case.id}_{int(time.time())}.png")
        
        # 使用pytest执行测试脚本
        # 注意：在实际生产环境中，这应该在Docker容器中运行
        # 这里提供一个基础实现，可以通过环境变量配置Docker执行
        use_docker = os.getenv("USE_DOCKER_FOR_UI_TESTS", "false").lower() == "true"
        
        if use_docker:
            # Docker执行方式（需要配置Docker容器）
            result = _run_in_docker(script_path, screenshot_path)
        else:
            # 本地执行方式
            result = _run_locally(script_path, screenshot_path)
        
        duration = time.time() - start_time
        
        if result["success"]:
            return UITestResult(
                success=True,
                duration=duration,
                screenshot_path=screenshot_path if os.path.exists(screenshot_path) else None,
                error_log=None
            )
        else:
            return UITestResult(
                success=False,
                duration=duration,
                screenshot_path=screenshot_path if os.path.exists(screenshot_path) else None,
                error_log=result.get("error", "Unknown error")
            )
            
    except Exception as e:
        duration = time.time() - start_time
        error_log = f"Error executing UI test: {str(e)}"
        
        return UITestResult(
            success=False,
            duration=duration,
            screenshot_path=screenshot_path if screenshot_path and os.path.exists(screenshot_path) else None,
            error_log=error_log
        )
    finally:
        # 清理临时文件
        if os.path.exists(script_path):
            os.remove(script_path)


def _run_locally(script_path: str, screenshot_path: str) -> dict:
    """在本地执行测试脚本"""
    try:
        # 使用pytest执行
        result = subprocess.run(
            ["pytest", script_path, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        return {
            "success": result.returncode == 0,
            "error": result.stderr if result.returncode != 0 else None
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Test execution timeout (exceeded 5 minutes)"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def _run_in_docker(script_path: str, screenshot_path: str) -> dict:
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
        screenshot_dir = os.path.dirname(os.path.abspath(screenshot_path))
        
        # 构建Docker命令
        docker_cmd = [
            "docker", "run", "--rm",
            "-v", f"{script_abs_path}:/app/test_script.py",
            "-v", f"{screenshot_dir}:/app/screenshots",
            docker_image,
            "pytest", "/app/test_script.py", "-v"
        ]
        
        result = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10分钟超时
        )
        
        return {
            "success": result.returncode == 0,
            "error": result.stderr if result.returncode != 0 else None
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Docker test execution timeout"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Docker execution error: {str(e)}"
        }

