#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工具函数模块
提供通用的工具函数
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


def ensure_directory(dir_path: str) -> Path:
    """
    确保目录存在，不存在则创建
    
    Args:
        dir_path: 目录路径
        
    Returns:
        Path对象
    """
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_hash(file_path: str) -> str:
    """
    计算文件的MD5哈希值
    
    Args:
        file_path: 文件路径
        
    Returns:
        MD5哈希值字符串
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    获取文件详细信息
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件信息字典
    """
    path = Path(file_path)
    
    if not path.exists():
        return {"error": "文件不存在"}
    
    stat = path.stat()
    return {
        "name": path.name,
        "extension": path.suffix,
        "size": stat.st_size,
        "size_human": format_size(stat.st_size),
        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "is_file": path.is_file(),
        "is_dir": path.is_dir()
    }


def format_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 字节数
        
    Returns:
        格式化的大小字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def safe_write_json(data: Any, file_path: str, indent: int = 2) -> bool:
    """
    安全地写入JSON文件
    
    Args:
        data: 要写入的数据
        file_path: 文件路径
        indent: 缩进空格数
        
    Returns:
        是否成功
    """
    try:
        # 确保目录存在
        ensure_directory(str(Path(file_path).parent))
        
        # 写入临时文件
        temp_path = f"{file_path}.tmp"
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        
        # 重命名（原子操作）
        os.replace(temp_path, file_path)
        return True
        
    except Exception as e:
        print(f"写入JSON文件失败: {e}")
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False


def safe_read_json(file_path: str) -> Optional[Any]:
    """
    安全地读取JSON文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        解析后的数据，失败返回None
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"文件不存在: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return None
    except Exception as e:
        print(f"读取文件失败: {e}")
        return None


def validate_test_case(test_case: Dict[str, Any]) -> List[str]:
    """
    验证测试用例格式
    
    Args:
        test_case: 测试用例字典
        
    Returns:
        错误信息列表，空列表表示验证通过
    """
    errors = []
    
    required_fields = ["id", "name", "priority", "test_type", "steps", "expected_results"]
    
    for field in required_fields:
        if field not in test_case:
            errors.append(f"缺少必填字段: {field}")
    
    if "priority" in test_case:
        valid_priorities = ["高", "中", "低"]
        if test_case["priority"] not in valid_priorities:
            errors.append(f"无效的优先级: {test_case['priority']}，有效值: {valid_priorities}")
    
    if "test_type" in test_case:
        valid_types = ["功能测试", "边界测试", "异常测试", "性能测试", "安全测试", "兼容性测试"]
        if test_case["test_type"] not in valid_types:
            errors.append(f"无效的测试类型: {test_case['test_type']}，有效值: {valid_types}")
    
    if "steps" in test_case:
        if not isinstance(test_case["steps"], list):
            errors.append("steps字段必须是列表类型")
        elif len(test_case["steps"]) == 0:
            errors.append("steps字段不能为空")
    
    if "expected_results" in test_case:
        if not isinstance(test_case["expected_results"], list):
            errors.append("expected_results字段必须是列表类型")
        elif len(test_case["expected_results"]) == 0:
            errors.append("expected_results字段不能为空")
    
    return errors


def generate_unique_id(prefix: str = "id") -> str:
    """
    生成唯一ID
    
    Args:
        prefix: ID前缀
        
    Returns:
        唯一ID字符串
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_part = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8]
    return f"{prefix}_{timestamp}_{random_part}"


def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """
    格式化时间戳
    
    Args:
        timestamp: 时间戳，默认当前时间
        
    Returns:
        格式化的时间字符串
    """
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def sanitize_filename(filename: str) -> str:
    """
    清理文件名中的特殊字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        清理后的文件名
    """
    # 移除或替换非法字符
    illegal_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in illegal_chars:
        filename = filename.replace(char, '_')
    
    # 限制长度
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    合并两个字典（深度合并）
    
    Args:
        dict1: 字典1
        dict2: 字典2
        
    Returns:
        合并后的字典
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result:
            if isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_dicts(result[key], value)
            elif isinstance(result[key], list) and isinstance(value, list):
                result[key] = result[key] + value
            else:
                result[key] = value
        else:
            result[key] = value
    
    return result


def print_progress_bar(iteration: int, total: int, prefix: str = '', 
                      suffix: str = '', decimals: int = 1, length: int = 50, 
                      fill: str = '█', print_end: str = "\r") -> None:
    """
    打印进度条
    
    Args:
        iteration: 当前迭代次数
        total: 总迭代次数
        prefix: 前缀字符串
        suffix: 后缀字符串
        decimals: 小数位数
        length: 进度条长度
        fill: 填充字符
        print_end: 结束字符
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    
    # 打印新行（如果完成）
    if iteration == total:
        print()
