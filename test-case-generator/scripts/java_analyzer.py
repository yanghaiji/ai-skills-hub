#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Java代码分析器
分析Java项目结构，提取类、方法、依赖信息
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field


@dataclass
class JavaMethod:
    """Java方法信息"""
    name: str
    return_type: str
    parameters: List[Dict[str, str]]  # [{"type": "String", "name": "param1"}]
    exceptions: List[str]
    annotations: List[str]
    is_public: bool = True
    is_static: bool = False
    body_lines: List[str] = field(default_factory=list)


@dataclass
class JavaClass:
    """Java类信息"""
    package: str
    name: str
    imports: List[str]
    annotations: List[str]
    parent_class: Optional[str]
    interfaces: List[str]
    fields: List[Dict[str, str]]  # [{"type": "String", "name": "field1", "annotations": [...]}]
    methods: List[JavaMethod]
    inner_classes: List['JavaClass'] = field(default_factory=list)
    file_path: str = ""


class JavaAnalyzer:
    """Java代码分析器"""
    
    def __init__(self, repo_dir: str):
        self.repo_dir = Path(repo_dir)
        self.java_files: List[Path] = []
        self.classes: List[JavaClass] = []
        self.service_classes: List[JavaClass] = []
        self.controller_classes: List[JavaClass] = []
        self.repository_classes: List[JavaClass] = []
    
    def analyze(self) -> Dict[str, Any]:
        """执行完整的Java代码分析"""
        print("  正在扫描Java文件...")
        self._find_java_files()
        
        print(f"  找到 {len(self.java_files)} 个Java文件")
        
        print("  正在解析Java类...")
        self._parse_java_files()
        
        print("  正在分类Java类...")
        self._classify_classes()
        
        return self._get_analysis_result()
    
    def _find_java_files(self):
        """查找所有Java文件"""
        self.java_files = []
        for root, dirs, files in os.walk(self.repo_dir):
            # 排除目录
            dirs[:] = [d for d in dirs if d not in ['target', 'build', '.git', 'node_modules']]
            
            for file in files:
                if file.endswith('.java'):
                    self.java_files.append(Path(root) / file)
    
    def _parse_java_files(self):
        """解析所有Java文件"""
        self.classes = []
        for java_file in java_files[:100]:  # 限制数量
            try:
                java_class = self._parse_java_file(java_file)
                if java_class:
                    self.classes.append(java_class)
            except Exception as e:
                print(f"  解析失败 {java_file.name}: {e}")
    
    def _parse_java_file(self, file_path: Path) -> Optional[JavaClass]:
        """解析单个Java文件"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 提取package
        package_match = re.search(r'package\s+([\w.]+);', content)
        package = package_match.group(1) if package_match else ""
        
        # 提取imports
        imports = re.findall(r'import\s+([\w.*]+);', content)
        
        # 提取类注解
        class_annotations = re.findall(r'@(\w+)(?:\([^)]*\))?\s*(?:public|private|protected)?\s*class', content)
        
        # 提取类名和继承关系
        class_match = re.search(
            r'(?:@\w+(?:\([^)]*\))?\s*)*(?:public\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w,\s]+))?',
            content
        )
        
        if not class_match:
            return None
        
        class_name = class_match.group(1)
        parent_class = class_match.group(2)
        interfaces = [i.strip() for i in class_match.group(3).split(',')] if class_match.group(3) else []
        
        # 提取字段
        fields = self._extract_fields(content)
        
        # 提取方法
        methods = self._extract_methods(content)
        
        return JavaClass(
            package=package,
            name=class_name,
            imports=imports,
            annotations=class_annotations,
            parent_class=parent_class,
            interfaces=interfaces,
            fields=fields,
            methods=methods,
            file_path=str(file_path)
        )
    
    def _extract_fields(self, content: str) -> List[Dict[str, str]]:
        """提取类字段"""
        fields = []
        
        # 匹配字段声明
        field_pattern = r'(?:(@\w+(?:\([^)]*\))?\s*)*)\s*(?:private|protected|public)\s+(\w+(?:<[^>]+>)?)\s+(\w+)\s*[;=]'
        
        for match in re.finditer(field_pattern, content):
            annotations = re.findall(r'@(\w+)', match.group(1) or "")
            field_type = match.group(2)
            field_name = match.group(3)
            
            fields.append({
                "type": field_type,
                "name": field_name,
                "annotations": annotations
            })
        
        return fields
    
    def _extract_methods(self, content: str) -> List[JavaMethod]:
        """提取类方法"""
        methods = []
        
        # 简化的方法提取模式
        method_pattern = r'(?:(@\w+(?:\([^)]*\))?\s*)*)\s*(?:public|protected|private)\s+(?:static\s+)?(\w+(?:<[^>]+>)?)\s+(\w+)\s*\(([^)]*)\)'
        
        for match in re.finditer(method_pattern, content):
            annotations = re.findall(r'@(\w+)', match.group(1) or "")
            return_type = match.group(2)
            method_name = match.group(3)
            params_str = match.group(4)
            
            # 解析参数
            parameters = []
            if params_str.strip():
                for param in params_str.split(','):
                    param = param.strip()
                    if param:
                        parts = param.rsplit(None, 1)
                        if len(parts) == 2:
                            parameters.append({"type": parts[0], "name": parts[1]})
            
            # 检查是否是public/static
            is_public = 'public' in (match.group(0)[:match.start(2)])
            is_static = 'static' in (match.group(0)[:match.start(2)])
            
            methods.append(JavaMethod(
                name=method_name,
                return_type=return_type,
                parameters=parameters,
                exceptions=[],
                annotations=annotations,
                is_public=is_public,
                is_static=is_static
            ))
        
        return methods
    
    def _classify_classes(self):
        """分类Java类"""
        for java_class in self.classes:
            class_name_lower = java_class.name.lower()
            annotations_lower = [a.lower() for a in java_class.annotations]
            
            # 识别Service类
            if ('service' in class_name_lower or 
                'service' in annotations_lower or
                '@service' in annotations_lower):
                self.service_classes.append(java_class)
            
            # 识别Controller类
            elif ('controller' in class_name_lower or
                  'restcontroller' in annotations_lower or
                  '@controller' in annotations_lower or
                  '@restcontroller' in annotations_lower):
                self.controller_classes.append(java_class)
            
            # 识别Repository类
            elif ('repository' in class_name_lower or
                  'dao' in class_name_lower or
                  '@repository' in annotations_lower):
                self.repository_classes.append(java_class)
    
    def _get_analysis_result(self) -> Dict[str, Any]:
        """获取分析结果"""
        return {
            "total_java_files": len(self.java_files),
            "total_classes": len(self.classes),
            "service_classes": self._class_to_dict_list(self.service_classes),
            "controller_classes": self._class_to_dict_list(self.controller_classes),
            "repository_classes": self._class_to_dict_list(self.repository_classes),
            "all_classes": self._class_to_dict_list(self.classes[:50])  # 限制数量
        }
    
    def _class_to_dict_list(self, classes: List[JavaClass]) -> List[Dict[str, Any]]:
        """将类列表转换为字典列表"""
        result = []
        for java_class in classes:
            result.append({
                "package": java_class.package,
                "name": java_class.name,
                "annotations": java_class.annotations,
                "parent_class": java_class.parent_class,
                "interfaces": java_class.interfaces,
                "fields": java_class.fields,
                "methods": [
                    {
                        "name": m.name,
                        "return_type": m.return_type,
                        "parameters": m.parameters,
                        "annotations": m.annotations,
                        "is_public": m.is_public,
                        "is_static": m.is_static
                    }
                    for m in java_class.methods
                ],
                "file_path": java_class.file_path
            })
        return result
    
    def get_service_method_test_info(self, service_class: JavaClass) -> List[Dict[str, Any]]:
        """获取Service类方法的测试信息"""
        test_info = []
        
        for method in service_class.methods:
            if not method.is_public:
                continue
            
            # 跳过getter/setter
            if method.name.startswith('get') or method.name.startswith('set'):
                continue
            
            # 生成方法参数
            params = []
            for param in method.parameters:
                params.append({
                    "type": param["type"],
                    "name": param["name"],
                    "mock_type": self._get_mock_type(param["type"])
                })
            
            test_info.append({
                "method_name": method.name,
                "return_type": method.return_type,
                "parameters": params,
                "class_name": service_class.name,
                "package": service_class.package,
                "annotations": method.annotations
            })
        
        return test_info
    
    def _get_mock_type(self, java_type: str) -> str:
        """获取Java类型对应的Mock类型"""
        type_map = {
            "String": "String",
            "int": "Integer",
            "long": "Long",
            "boolean": "Boolean",
            "List": "List",
            "Map": "Map",
            "Set": "Set",
        }
        
        # 处理泛型
        if '<' in java_type:
            base_type = java_type.split('<')[0]
            return base_type
        
        return type_map.get(java_type, java_type)
