"""
基础策略生成器 - 提供通用的Hypothesis数据生成策略
"""
from hypothesis import strategies as st
from hypothesis.strategies import composite
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
import re
import string


class BaseStrategies:
    """基础数据生成策略"""

    # ==================== 基础类型策略 ====================

    @staticmethod
    def integers(min_value: int = -1000, max_value: int = 10000,
                 allow_null: bool = False) -> st.SearchStrategy:
        """生成整数策略"""
        strategies = [st.integers(min_value=min_value, max_value=max_value)]
        if allow_null:
            strategies.append(st.none())
        return st.one_of(*strategies)

    @staticmethod
    def strings(min_length: int = 0, max_length: int = 100,
                allow_null: bool = False, allow_empty: bool = True) -> st.SearchStrategy:
        """生成字符串策略"""
        strategies = []

        if allow_empty:
            strategies.append(st.text(min_size=min_length, max_size=max_length))
        else:
            strategies.append(st.text(min_size=max(1, min_length), max_size=max_length))

        if allow_null:
            strategies.append(st.none())

        return st.one_of(*strategies)

    @staticmethod
    def booleans(allow_null: bool = False) -> st.SearchStrategy:
        """生成布尔值策略"""
        strategies = [st.booleans()]
        if allow_null:
            strategies.append(st.none())
        return st.one_of(*strategies)

    @staticmethod
    def floats(min_value: float = -1000.0, max_value: float = 10000.0,
               allow_nan: bool = False, allow_infinity: bool = False,
               allow_null: bool = False) -> st.SearchStrategy:
        """生成浮点数策略"""
        strategies = [st.floats(
            min_value=min_value,
            max_value=max_value,
            allow_nan=allow_nan,
            allow_infinity=allow_infinity
        )]
        if allow_null:
            strategies.append(st.none())
        return st.one_of(*strategies)

    @staticmethod
    def decimals(allow_null: bool = False) -> st.SearchStrategy:
        """生成十进制数策略"""
        strategies = [st.decimals()]
        if allow_null:
            strategies.append(st.none())
        return st.one_of(*strategies)

    @staticmethod
    def dates(min_date: Optional[date] = None, max_date: Optional[date] = None,
              allow_null: bool = False) -> st.SearchStrategy:
        """生成日期策略"""
        strategies = [st.dates(
            min_value=min_date or date(2000, 1, 1),
            max_value=max_date or date(2030, 12, 31)
        )]
        if allow_null:
            strategies.append(st.none())
        return st.one_of(*strategies)

    @staticmethod
    def datetimes(min_date: Optional[datetime] = None, max_date: Optional[datetime] = None,
                  allow_null: bool = False) -> st.SearchStrategy:
        """生成日期时间策略"""
        strategies = [st.datetimes(
            min_value=min_date or datetime(2000, 1, 1),
            max_value=max_date or datetime(2030, 12, 31, 23, 59, 59)
        )]
        if allow_null:
            strategies.append(st.none())
        return st.one_of(*strategies)

    # ==================== 特定格式策略 ====================

    @staticmethod
    def emails() -> st.SearchStrategy:
        """生成邮箱地址策略"""
        return st.emails()

    @staticmethod
    def urls() -> st.SearchStrategy:
        """生成URL策略"""
        return st.urls()

    @staticmethod
    def uuids() -> st.SearchStrategy:
        """生成UUID策略"""
        return st.uuids()

    @staticmethod
    def ip_addresses() -> st.SearchStrategy:
        """生成IP地址策略"""
        return st.ip_addresses()

    @staticmethod
    def regex_patterns(pattern: str = r".+") -> st.SearchStrategy:
        """生成符合正则表达式的字符串策略"""
        return st.from_regex(pattern, fullmatch=True)

    # ==================== 复杂结构策略 ====================

    @staticmethod
    def lists(element_strategy: st.SearchStrategy,
              min_size: int = 0, max_size: int = 10,
              allow_null: bool = False) -> st.SearchStrategy:
        """生成列表策略"""
        strategies = [st.lists(
            element_strategy,
            min_size=min_size,
            max_size=max_size
        )]
        if allow_null:
            strategies.append(st.none())
        return st.one_of(*strategies)

    @staticmethod
    def dictionaries(key_strategy: st.SearchStrategy,
                     value_strategy: st.SearchStrategy,
                     min_size: int = 0, max_size: int = 10,
                     allow_null: bool = False) -> st.SearchStrategy:
        """生成字典策略"""
        strategies = [st.dictionaries(
            key_strategy,
            value_strategy,
            min_size=min_size,
            max_size=max_size
        )]
        if allow_null:
            strategies.append(st.none())
        return st.one_of(*strategies)

    @staticmethod
    def fixed_dictionaries(fields: Dict[str, st.SearchStrategy],
                           allow_extra: bool = False) -> st.SearchStrategy:
        """生成固定字段字典策略"""
        return st.fixed_dictionaries(fields, allow_extra=allow_extra)


    # ==================== 采样策略 ====================

    @staticmethod
    def one_of(*strategies: st.SearchStrategy) -> st.SearchStrategy:
        """组合多个策略，生成其中任意一个策略的值

        Args:
            *strategies: 要组合的策略列表

        Returns:
            组合后的策略

        Example:
            >>> int_strategy = base_strategies.integers(min_value=1, max_value=10)
            >>> str_strategy = base_strategies.strings(min_length=1, max_length=5)
            >>> combined = base_strategies.one_of(int_strategy, str_strategy)
            >>> combined.example()  # 可能返回整数或字符串
        """
        if not strategies:
            raise ValueError("至少需要提供一个策略")

        return st.one_of(*strategies)


    @staticmethod
    def sampled_from(elements: List[Any],
                     allow_null: bool = False) -> st.SearchStrategy:
        """从给定元素列表中采样的策略

        Args:
            elements: 用于采样的元素列表
            allow_null: 是否允许生成None值

        Returns:
            采样策略实例

        Example:
            >>> strategy = base_strategies.sampled_from([1, 2, 3])
            >>> strategy.example()  # 可能返回 1, 2 或 3
        """
        if not elements:
            raise ValueError("元素列表不能为空")

        strategies = [st.sampled_from(elements)]

        if allow_null:
            strategies.append(st.none())

        return st.one_of(*strategies)


    @staticmethod
    def choices_from(elements: List[Any],
                     min_choices: int = 1,
                     max_choices: int = 5,
                     allow_duplicates: bool = False) -> st.SearchStrategy:
        """从给定元素列表中选择多个元素的策略

        Args:
            elements: 可供选择的元素列表
            min_choices: 最小选择数量
            max_choices: 最大选择数量
            allow_duplicates: 是否允许重复选择

        Returns:
            选择策略实例
        """
        if not elements:
            raise ValueError("元素列表不能为空")

        if allow_duplicates:
            return st.lists(
                st.sampled_from(elements),
                min_size=min_choices,
                max_size=max_choices
            )
        else:
            # 不允许重复时，确保选择数量不超过元素个数
            max_choices = min(max_choices, len(elements))
            return st.lists(
                st.sampled_from(elements),
                min_size=min_choices,
                max_size=max_choices,
                unique=True
            )


    @staticmethod
    def weighted_sampled_from(elements: List[Any],
                              weights: List[float],
                              allow_null: bool = False) -> st.SearchStrategy:
        """带权重的采样策略

        Args:
            elements: 用于采样的元素列表
            weights: 对应的权重列表
            allow_null: 是否允许生成None值

        Returns:
            加权采样策略实例
        """
        if not elements:
            raise ValueError("元素列表不能为空")

        if len(elements) != len(weights):
            raise ValueError("元素列表和权重列表长度必须一致")

        strategies = [st.sampled_from(elements)]

        if allow_null:
            strategies.append(st.none())

        return st.one_of(*strategies)


# 创建基础策略实例
base_strategies = BaseStrategies()