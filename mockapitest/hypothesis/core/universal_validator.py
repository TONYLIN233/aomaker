"""
通用Hypothesis验证工具类 - 支持任何API接口的入参验证
"""
import hypothesis
from hypothesis import strategies as st, given, assume, settings, HealthCheck
from hypothesis.strategies import composite, lists, dictionaries, text, integers, booleans
from typing import Any, Dict, List, Optional, Type, get_type_hints, Union, Callable
import inspect
from datetime import datetime, date
import re
from functools import wraps


class UniversalHypothesisValidator:
    """通用Hypothesis API入参验证工具类"""

    # 类型映射字典
    TYPE_MAPPING = {
        int: integers,
        str: text,
        bool: booleans,
        float: st.floats,
        datetime: st.datetimes,
        date: st.dates,
        List: lists,
        Dict: dictionaries,
    }

    @staticmethod
    def generate_strategy_for_type(field_type: Type, **constraints) -> st.SearchStrategy:
        """根据字段类型生成Hypothesis策略"""
        # 处理Optional类型
        if hasattr(field_type, '__origin__') and field_type.__origin__ is Union:
            if type(None) in field_type.__args__:
                actual_type = next(t for t in field_type.__args__ if t is not type(None))
                return st.one_of(st.none(),
                                 UniversalHypothesisValidator.generate_strategy_for_type(actual_type, **constraints))

        # 处理泛型类型
        origin_type = getattr(field_type, '__origin__', field_type)

        if origin_type in UniversalHypothesisValidator.TYPE_MAPPING:
            strategy_func = UniversalHypothesisValidator.TYPE_MAPPING[origin_type]

            # 处理List[SomeType]
            if origin_type == List and hasattr(field_type, '__args__'):
                item_type = field_type.__args__[0]
                return lists(UniversalHypothesisValidator.generate_strategy_for_type(item_type), **constraints)

            # 处理Dict[KeyType, ValueType]
            elif origin_type == Dict and hasattr(field_type, '__args__') and len(field_type.__args__) >= 2:
                key_type, value_type = field_type.__args__[:2]
                return dictionaries(
                    UniversalHypothesisValidator.generate_strategy_for_type(key_type),
                    UniversalHypothesisValidator.generate_strategy_for_type(value_type),
                    **constraints
                )

            return strategy_func(**constraints)

        # 默认文本策略
        return text(**constraints)

    @staticmethod
    @composite
    def generate_from_model(draw, model_class: Type, **overrides):
        """从模型类生成测试数据"""
        type_hints = get_type_hints(model_class)
        result = {}

        for field_name, field_type in type_hints.items():
            if field_name == 'self':
                continue

            if field_name in overrides:
                result[field_name] = overrides[field_name]
            else:
                # 获取字段的metadata（约束条件）
                field_info = getattr(model_class, '__attrs_attrs__', [])
                constraints = {}

                for attr in field_info:
                    if attr.name == field_name and hasattr(attr, 'metadata'):
                        metadata = attr.metadata or {}
                        constraints.update(metadata)

                strategy = UniversalHypothesisValidator.generate_strategy_for_type(field_type, **constraints)
                result[field_name] = draw(strategy)

        return result

    @staticmethod
    def api_test(max_examples: int = 50, deadline: int = 5000):
        """API测试装饰器"""

        def decorator(test_func):
            @settings(max_examples=max_examples, deadline=deadline,
                      suppress_health_check=[HealthCheck.too_slow])
            @given(st.data())
            @wraps(test_func)
            def wrapper(*args, **kwargs):
                return test_func(*args, **kwargs)

            return wrapper

        return decorator


# 导出单例实例
validator = UniversalHypothesisValidator()