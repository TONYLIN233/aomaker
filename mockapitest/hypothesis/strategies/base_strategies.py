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

    # ==================== 边界值策略 ====================

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

    # ==================== 组合策略 ====================

    @staticmethod
    @composite
    def pagination_params(draw,
                          offset_min: int = 0, offset_max: int = 1000,
                          limit_min: int = 1, limit_max: int = 100) -> Dict[str, int]:
        """生成分页参数策略"""
        return {
            'offset': draw(st.integers(min_value=offset_min, max_value=offset_max)),
            'limit': draw(st.integers(min_value=limit_min, max_value=limit_max))
        }

    @staticmethod
    @composite
    def sorting_params(draw,
                       fields: List[str] = None) -> Dict[str, str]:
        """生成排序参数策略"""
        if fields is None:
            fields = ['id', 'name', 'created_at', 'updated_at']

        return {
            'sort_by': draw(st.sampled_from(fields)),
            'sort_order': draw(st.sampled_from(['asc', 'desc']))
        }

    @staticmethod
    @composite
    def search_params(draw,
                      min_length: int = 0, max_length: int = 50) -> Dict[str, str]:
        """生成搜索参数策略"""
        return {
            'q': draw(st.text(min_size=min_length, max_size=max_length))
        }


# 创建基础策略实例
base_strategies = BaseStrategies()