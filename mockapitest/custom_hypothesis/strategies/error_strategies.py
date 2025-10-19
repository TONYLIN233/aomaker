from hypothesis import strategies as st
from hypothesis.strategies import composite
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
import re
import string

import json


class ErrorStrategies:
    """错误类型验证策略"""

    @staticmethod
    def invalid_types(field_name: str, expected_type: type):
        """生成无效类型数据策略"""
        type_mapping = {
            int: st.one_of(
                st.text(),  # 字符串代替整数
                st.floats(),  # 浮点数代替整数
                st.booleans(),  # 布尔值代替整数
                st.none()  # 空值代替整数
            ),
            str: st.one_of(
                st.integers(),  # 整数代替字符串
                st.floats(),  # 浮点数代替字符串
                st.booleans(),  # 布尔值代替字符串
                st.none()  # 空值代替字符串
            ),
            bool: st.one_of(
                st.text(),  # 字符串代替布尔值
                st.integers(),  # 整数代替布尔值
                st.floats(),  # 浮点数代替布尔值
                st.none()  # 空值代替布尔值
            )
        }

        return type_mapping.get(expected_type, st.nothing())

    @staticmethod
    def sql_injection_vectors():
        """生成SQL注入测试向量"""
        return st.sampled_from([
            "' OR '1'='1",
            "' OR 1=1--",
            "'; DROP TABLE users; --",
            "' UNION SELECT username, password FROM users--",
            "' AND 1=1",
            "' OR 'a'='a"
        ])

    @staticmethod
    def xss_vectors():
        """生成XSS攻击测试向量"""
        return st.sampled_from([
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<body onload=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')"
        ])

    @staticmethod
    def path_traversal_vectors():
        """生成路径遍历攻击测试向量"""
        return st.sampled_from([
            "../../etc/passwd",
            "..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "%2e%2e%2fetc%2fpasswd",
            "....//....//etc/passwd"
        ])

    @staticmethod
    def overflow_values():
        """生成数值溢出测试数据"""
        return st.sampled_from([
            2147483647,  # 32位整数最大值
            2147483648,  # 超过32位整数最大值
            9223372036854775807,  # 64位整数最大值
            9223372036854775808,  # 超过64位整数最大值
            -2147483648,  # 32位整数最小值
            -2147483649,  # 低于32位整数最小值
            999999999999999999999  # 极大整数
        ])

error_strategies = ErrorStrategies()