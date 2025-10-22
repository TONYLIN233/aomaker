from hypothesis import strategies as st
from hypothesis.strategies import composite
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
import re
import string


class BoundaryStrategies:
    """边界测试策略"""

    @staticmethod
    def string_length_boundaries(min_len: int = 0, max_len: int = 100):
        """生成字符串长度边界值，包含完整的边界情况"""
        strategies = []

        # 处理下边界及其附近
        if min_len > 0:
            strategies.append(st.just("a" * (min_len - 1)))  # 略小于下边界
        strategies.append(st.just("a" * min_len))  # 下边界本身
        strategies.append(st.just("a" * (min_len + 1)))  # 略大于下边界

        # 处理上边界及其附近
        strategies.append(st.just("a" * (max_len - 1)))  # 略小于上边界
        strategies.append(st.just("a" * max_len))  # 上边界本身
        if max_len > 0:  # 避免 max_len 为 0 时生成负长度
            strategies.append(st.just("a" * (max_len + 1)))  # 略大于上边界

        # 保留超长字符串的测试用例
        strategies.append(st.just("a" * 1000))

        # 可选：添加一些随机生成的字符串，以丰富测试场景[1,3](@ref)
        # 这有助于覆盖非单一字符组成的边界长度字符串情况
        strategies.append(st.text(min_size=min_len, max_size=max_len))

        return st.one_of(strategies)

    @staticmethod
    def integer_length_boundaries(min_len: int = 0, max_len: int = 100):
        """生成系统性的整数长度边界值，用于测试"""
        strategies = []

        # 1. 下边界及其附近（重点关注比最小长度稍小的情况）
        if min_len > 1:  # 确保不会生成负长度
            strategies.append(st.just("1" * (min_len - 1)))  # 略小于下边界
        if min_len > 0:
            strategies.append(st.just("1" * min_len))  # 下边界本身
        strategies.append(st.just("1" * (min_len + 1)))  # 略大于下边界

        # 2. 上边界及其附近（重点关注比最大长度稍大的情况）
        strategies.append(st.just("1" * (max_len - 1)))  # 略小于上边界
        strategies.append(st.just("1" * max_len))  # 上边界本身
        strategies.append(st.just("1" * (max_len + 1)))  # 略大于上边界

        # 3. 超长整数测试（压力测试）
        strategies.append(st.just("1" * 1000))

        # 4. 增强测试多样性：生成非全'1'的边界长度字符串
        # 这有助于发现可能依赖于特定字符内容的边界处理错误
        strategies.append(st.text(min_size=min_len, max_size=max_len,
                                  alphabet=st.characters(min_codepoint=48, max_codepoint=57)))  # 生成由数字组成的随机字符串

        return st.one_of(strategies)

    @staticmethod
    def integer_boundaries(min_val: int = -1000, max_val: int = 1000):
        """生成整数边界值"""
        return st.one_of(
            st.just(min_val),  # 最小值
            st.just(min_val - 1),  # 低于最小值
            st.just(max_val),  # 最大值
            st.just(max_val + 1),  # 超过最大值
            st.just(0),  # 零值
            st.just(-1),  # 负一
            st.just(1),  # 正一
        )

    @staticmethod
    def special_characters():
        """生成特殊字符测试数据"""
        return st.sampled_from([
            "!@#$%^&*()",  # 特殊符号
            "中文测试",  # 中文字符
            "🚀🎉🌟",  # emoji表情
            "null", "NULL", "None", "undefined",  # 编程语言空值表示
            "true", "false", "True", "False",  # 布尔值字符串
        ])


    @staticmethod
    def edge_case_integers() -> st.SearchStrategy:
        """生成边界情况整数"""
        return st.sampled_from([
            0, -1, 1,
            2147483647, -2147483648,  # 32位整数边界
            9223372036854775807, -9223372036854775808,  # 64位整数边界
            1000000, -1000000
        ])

    @staticmethod
    def edge_case_strings() -> st.SearchStrategy:
        """生成边界情况字符串"""
        return st.one_of(
            st.just(""),  # 空字符串
            st.just(" "),  # 单个空格
            st.just(" " * 100),  # 长空格字符串
            st.text(min_size=1000, max_size=2000),  # 超长字符串
            st.text(alphabet=st.characters(blacklist_categories=('L', 'N'))),  # 特殊字符
            st.sampled_from(["null", "undefined", "None", "NULL", "true", "false"])
        )

    @staticmethod
    def edge_case_dates() -> st.SearchStrategy:
        """生成边界情况日期"""
        return st.sampled_from([
            date(1970, 1, 1),  # Unix纪元
            date(2000, 1, 1),  # 千禧年
            date(2030, 12, 31),  # 未来边界
            date(1900, 1, 1),  # 早期日期
        ])

    @staticmethod
    def edge_case_booleans() -> st.SearchStrategy:
        """生成边界情况布尔值"""
        return st.one_of(
            st.just(True),
            st.just(False),
            st.none()  # 空值
        )

boundary_strategies = BoundaryStrategies()