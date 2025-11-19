import requests
import time
from typing import Dict, Any, List
from app.models import APITestCase
from app.schemas import APITestResult


def run_api_case(case: APITestCase) -> APITestResult:
    """
    执行单个API测试用例
    
    使用requests库发送请求，并根据assertions进行验证
    """
    start_time = time.time()
    assertion_errors = []
    response_data = None
    status_code = None
    
    try:
        # 准备请求参数
        headers = case.headers or {}
        params = case.params or {}
        json_data = case.body if case.method.upper() in ["POST", "PUT", "PATCH"] else None
        
        # 发送HTTP请求
        response = requests.request(
            method=case.method.upper(),
            url=case.url,
            headers=headers,
            params=params,
            json=json_data,
            timeout=30
        )
        
        status_code = response.status_code
        
        # 尝试解析响应为JSON
        try:
            response_data = response.json()
        except:
            response_data = {"text": response.text}
        
        # 执行断言
        if case.assertions:
            assertion_errors = _execute_assertions(case.assertions, response, response_data)
        
        duration = time.time() - start_time
        success = len(assertion_errors) == 0
        
        return APITestResult(
            success=success,
            duration=duration,
            response_data=response_data,
            status_code=status_code,
            assertion_errors=assertion_errors
        )
        
    except Exception as e:
        duration = time.time() - start_time
        assertion_errors.append(f"Request failed: {str(e)}")
        
        return APITestResult(
            success=False,
            duration=duration,
            response_data=response_data,
            status_code=status_code,
            assertion_errors=assertion_errors
        )


def _execute_assertions(
    assertions: Dict[str, Any],
    response: requests.Response,
    response_data: Any
) -> List[str]:
    """
    执行断言规则
    
    assertions格式示例:
    {
        "status_code": 200,
        "response_contains": "success",
        "response_json": {
            "code": 0,
            "data.id": 123
        }
    }
    """
    errors = []
    
    # 检查状态码
    if "status_code" in assertions:
        expected_status = assertions["status_code"]
        if response.status_code != expected_status:
            errors.append(
                f"Status code assertion failed: expected {expected_status}, got {response.status_code}"
            )
    
    # 检查响应体是否包含特定文本
    if "response_contains" in assertions:
        expected_text = assertions["response_contains"]
        response_text = response.text
        if expected_text not in response_text:
            errors.append(
                f"Response contains assertion failed: expected '{expected_text}' not found in response"
            )
    
    # 检查JSON响应字段
    if "response_json" in assertions and isinstance(response_data, dict):
        json_assertions = assertions["response_json"]
        for key, expected_value in json_assertions.items():
            # 支持嵌套字段，如 "data.id"
            actual_value = _get_nested_value(response_data, key)
            if actual_value != expected_value:
                errors.append(
                    f"JSON assertion failed for '{key}': expected {expected_value}, got {actual_value}"
                )
    
    return errors


def _get_nested_value(data: Dict[str, Any], key: str) -> Any:
    """获取嵌套字典的值，支持点号分隔的键"""
    keys = key.split(".")
    value = data
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return None
    return value

