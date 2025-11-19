import subprocess
import os
import xml.etree.ElementTree as ET
from typing import Dict, Any
from app.models import PerformanceTest
from app.schemas import PerformanceTestResult
from config import settings


def run_performance_test(test: PerformanceTest) -> PerformanceTestResult:
    """
    执行性能测试
    
    使用subprocess调用JMeter命令行执行JMX文件
    然后解析JTL结果文件，提取关键性能指标
    """
    if not test.jmx_file_path or not os.path.exists(test.jmx_file_path):
        return PerformanceTestResult(
            success=False,
            duration=0,
            error="JMX file not found"
        )
    
    # 确保结果目录存在
    os.makedirs(settings.JMETER_RESULTS_DIR, exist_ok=True)
    
    # 生成结果文件路径
    jtl_file = os.path.join(settings.JMETER_RESULTS_DIR, f"result_{test.id}.jtl")
    html_report_dir = os.path.join(settings.JMETER_RESULTS_DIR, f"report_{test.id}")
    
    try:
        # 执行JMeter命令
        # jmeter -n -t [file.jmx] -l [result.jtl] -e -o [html_report_dir]
        jmeter_cmd = [
            "jmeter",
            "-n",  # 非GUI模式
            "-t", test.jmx_file_path,  # 测试计划文件
            "-l", jtl_file,  # 结果文件
            "-e",  # 生成HTML报告
            "-o", html_report_dir  # HTML报告输出目录
        ]
        
        # 检查JMeter是否可用
        jmeter_path = os.getenv("JMETER_HOME")
        if jmeter_path:
            jmeter_cmd[0] = os.path.join(jmeter_path, "bin", "jmeter")
        
        result = subprocess.run(
            jmeter_cmd,
            capture_output=True,
            text=True,
            timeout=3600  # 1小时超时
        )
        
        if result.returncode != 0:
            return PerformanceTestResult(
                success=False,
                duration=0,
                error=f"JMeter execution failed: {result.stderr}"
            )
        
        # 解析JTL文件提取指标
        metrics = _parse_jtl_file(jtl_file)
        
        # 获取HTML报告路径
        html_report_path = html_report_dir if os.path.exists(html_report_dir) else None
        
        return PerformanceTestResult(
            success=True,
            duration=metrics.get("duration", 0),
            metrics=metrics,
            html_report_path=html_report_path,
            error=None
        )
        
    except subprocess.TimeoutExpired:
        return PerformanceTestResult(
            success=False,
            duration=0,
            error="Performance test execution timeout (exceeded 1 hour)"
        )
    except Exception as e:
        return PerformanceTestResult(
            success=False,
            duration=0,
            error=f"Error executing performance test: {str(e)}"
        )


def _parse_jtl_file(jtl_file: str) -> Dict[str, Any]:
    """
    解析JMeter的JTL结果文件
    
    JTL文件格式通常是CSV或XML
    这里提供XML格式的解析（JMeter默认XML格式）
    """
    metrics = {
        "total_samples": 0,
        "successful_samples": 0,
        "failed_samples": 0,
        "error_rate": 0.0,
        "average_response_time": 0.0,
        "min_response_time": 0.0,
        "max_response_time": 0.0,
        "p95_response_time": 0.0,
        "p99_response_time": 0.0,
        "throughput": 0.0,  # 请求/秒
        "duration": 0.0
    }
    
    if not os.path.exists(jtl_file):
        return metrics
    
    try:
        # 尝试解析为XML格式
        tree = ET.parse(jtl_file)
        root = tree.getroot()
        
        response_times = []
        start_time = None
        end_time = None
        
        # 解析每个HTTP采样结果
        for sample in root.findall(".//httpSample"):
            # 响应时间（毫秒）
            elapsed = float(sample.get("t", 0))
            response_times.append(elapsed)
            
            # 时间戳
            ts = float(sample.get("ts", 0))
            if start_time is None or ts < start_time:
                start_time = ts
            if end_time is None or ts > end_time:
                end_time = ts
            
            # 成功/失败
            success = sample.get("s", "true").lower() == "true"
            if success:
                metrics["successful_samples"] += 1
            else:
                metrics["failed_samples"] += 1
        
        metrics["total_samples"] = len(response_times)
        
        if response_times:
            # 计算统计指标
            response_times_sorted = sorted(response_times)
            metrics["average_response_time"] = sum(response_times) / len(response_times)
            metrics["min_response_time"] = min(response_times)
            metrics["max_response_time"] = max(response_times)
            
            # 计算百分位数
            if len(response_times_sorted) > 0:
                p95_index = int(len(response_times_sorted) * 0.95)
                p99_index = int(len(response_times_sorted) * 0.99)
                metrics["p95_response_time"] = response_times_sorted[min(p95_index, len(response_times_sorted) - 1)]
                metrics["p99_response_time"] = response_times_sorted[min(p99_index, len(response_times_sorted) - 1)]
            
            # 计算错误率
            if metrics["total_samples"] > 0:
                metrics["error_rate"] = (metrics["failed_samples"] / metrics["total_samples"]) * 100
            
            # 计算吞吐量（请求/秒）
            if start_time and end_time:
                duration_seconds = (end_time - start_time) / 1000.0
                metrics["duration"] = duration_seconds
                if duration_seconds > 0:
                    metrics["throughput"] = metrics["total_samples"] / duration_seconds
        
    except ET.ParseError:
        # 如果不是XML格式，尝试CSV格式
        try:
            import csv
            with open(jtl_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                response_times = []
                
                for row in reader:
                    elapsed = float(row.get("elapsed", 0))
                    response_times.append(elapsed)
                    
                    success = row.get("success", "true").lower() == "true"
                    if success:
                        metrics["successful_samples"] += 1
                    else:
                        metrics["failed_samples"] += 1
                
                metrics["total_samples"] = len(response_times)
                
                if response_times:
                    response_times_sorted = sorted(response_times)
                    metrics["average_response_time"] = sum(response_times) / len(response_times)
                    metrics["min_response_time"] = min(response_times)
                    metrics["max_response_time"] = max(response_times)
                    
                    p95_index = int(len(response_times_sorted) * 0.95)
                    p99_index = int(len(response_times_sorted) * 0.99)
                    metrics["p95_response_time"] = response_times_sorted[min(p95_index, len(response_times_sorted) - 1)]
                    metrics["p99_response_time"] = response_times_sorted[min(p99_index, len(response_times_sorted) - 1)]
                    
                    if metrics["total_samples"] > 0:
                        metrics["error_rate"] = (metrics["failed_samples"] / metrics["total_samples"]) * 100
        except Exception as e:
            print(f"Error parsing JTL file: {e}")
    
    return metrics

