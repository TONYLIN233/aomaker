"""
API特定策略生成器 - 为mockapitest项目中的各个API域定制策略
"""
from hypothesis import strategies as st
from hypothesis.strategies import composite
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from .base_strategies import base_strategies


class APIStrategies:
    """API特定策略生成器"""

    # ==================== 用户API策略 ====================

    @staticmethod
    @composite
    def users_query_params(draw) -> Dict[str, Any]:
        """生成用户查询参数策略"""
        return {
            'offset': draw(st.integers(min_value=0, max_value=1000)),
            'limit': draw(st.integers(min_value=1, max_value=100)),
            'username': draw(st.one_of(st.none(), st.text(max_length=50))),
            'email': draw(st.one_of(st.none(), st.emails())),
            'is_active': draw(st.one_of(st.none(), st.booleans()))
        }

    @staticmethod
    @composite
    def create_user_body(draw) -> Dict[str, Any]:
        """生成创建用户请求体策略"""
        return {
            'id': draw(st.integers(min_value=1)),
            'username': draw(st.text(min_size=1, max_size=20)),
            'email': draw(st.emails()),
            'created_at': draw(st.datetimes()),
            'is_active': draw(st.booleans())
        }

    @staticmethod
    @composite
    def update_user_body(draw) -> Dict[str, Any]:
        """生成更新用户请求体策略"""
        return {
            'username': draw(st.one_of(st.none(), st.text(min_size=1, max_size=20))),
            'email': draw(st.one_of(st.none(), st.emails())),
            'is_active': draw(st.one_of(st.none(), st.booleans()))
        }

    # ==================== 认证API策略 ====================

    @staticmethod
    @composite
    def login_credentials(draw) -> Dict[str, Any]:
        """生成登录凭据策略"""
        return {
            'username': draw(st.text(min_size=1, max_size=20)),
            'password': draw(st.text(min_size=6, max_size=20)),
            'remember_me': draw(st.booleans())
        }

    @staticmethod
    @composite
    def registration_data(draw) -> Dict[str, Any]:
        """生成注册数据策略"""
        return {
            'username': draw(st.text(min_size=3, max_size=20)),
            'email': draw(st.emails()),
            'password': draw(st.text(min_size=8, max_size=20)),
            'confirm_password': draw(st.text(min_size=8, max_size=20)),
            'first_name': draw(st.text(min_size=1, max_size=30)),
            'last_name': draw(st.text(min_size=1, max_size=30))
        }

    @staticmethod
    @composite
    def password_reset_data(draw) -> Dict[str, Any]:
        """生成密码重置数据策略"""
        return {
            'email': draw(st.emails()),
            'new_password': draw(st.text(min_size=8, max_size=20)),
            'confirm_password': draw(st.text(min_size=8, max_size=20)),
            'token': draw(st.text(min_size=10, max_size=100))
        }

    # ==================== 评论API策略 ====================

    @staticmethod
    @composite
    def comment_query_params(draw) -> Dict[str, Any]:
        """生成评论查询参数策略"""
        return {
            'post_id': draw(st.integers(min_value=1)),
            'user_id': draw(st.one_of(st.none(), st.integers(min_value=1))),
            'limit': draw(st.integers(min_value=1, max_value=100)),
            'offset': draw(st.integers(min_value=0, max_value=1000))
        }

    @staticmethod
    @composite
    def create_comment_body(draw) -> Dict[str, Any]:
        """生成创建评论请求体策略"""
        return {
            'post_id': draw(st.integers(min_value=1)),
            'user_id': draw(st.integers(min_value=1)),
            'content': draw(st.text(min_size=1, max_size=1000)),
            'parent_id': draw(st.one_of(st.none(), st.integers(min_value=1)))
        }

    @staticmethod
    @composite
    def update_comment_body(draw) -> Dict[str, Any]:
        """生成更新评论请求体策略"""
        return {
            'content': draw(st.text(min_size=1, max_size=1000))
        }

    # ==================== 订单API策略 ====================

    @staticmethod
    @composite
    def order_query_params(draw) -> Dict[str, Any]:
        """生成订单查询参数策略"""
        return {
            'user_id': draw(st.one_of(st.none(), st.integers(min_value=1))),
            'status': draw(st.one_of(st.none(), st.sampled_from(['pending', 'processing', 'completed', 'cancelled']))),
            'start_date': draw(st.one_of(st.none(), st.dates())),
            'end_date': draw(st.one_of(st.none(), st.dates())),
            'limit': draw(st.integers(min_value=1, max_value=100)),
            'offset': draw(st.integers(min_value=0, max_value=1000))
        }

    @staticmethod
    @composite
    def create_order_body(draw) -> Dict[str, Any]:
        """生成创建订单请求体策略"""
        return {
            'user_id': draw(st.integers(min_value=1)),
            'items': draw(st.lists(
                st.fixed_dictionaries({
                    'product_id': st.integers(min_value=1),
                    'quantity': st.integers(min_value=1, max_value=10),
                    'price': st.floats(min_value=0.01, max_value=1000.0)
                }),
                min_size=1, max_size=10
            )),
            'shipping_address': draw(st.fixed_dictionaries({
                'street': st.text(min_size=1, max_size=100),
                'city': st.text(min_size=1, max_size=50),
                'state': st.text(min_size=1, max_size=50),
                'zip_code': st.text(min_size=3, max_size=10),
                'country': st.text(min_size=1, max_size=50)
            })),
            'payment_method': draw(st.sampled_from(['credit_card', 'paypal', 'bank_transfer']))
        }

    @staticmethod
    @composite
    def update_order_status_body(draw) -> Dict[str, Any]:
        """生成更新订单状态请求体策略"""
        return {
            'status': draw(st.sampled_from(['processing', 'completed', 'cancelled']))
        }

    # ==================== 产品API策略 ====================

    @staticmethod
    @composite
    def product_query_params(draw) -> Dict[str, Any]:
        """生成产品查询参数策略"""
        return {
            'category_id': draw(st.one_of(st.none(), st.integers(min_value=1))),
            'min_price': draw(st.one_of(st.none(), st.floats(min_value=0.0))),
            'max_price': draw(st.one_of(st.none(), st.floats(min_value=0.0))),
            'in_stock': draw(st.one_of(st.none(), st.booleans())),
            'limit': draw(st.integers(min_value=1, max_value=100)),
            'offset': draw(st.integers(min_value=0, max_value=1000))
        }

    @staticmethod
    @composite
    def create_product_body(draw) -> Dict[str, Any]:
        """生成创建产品请求体策略"""
        return {
            'name': draw(st.text(min_size=1, max_size=100)),
            'description': draw(st.text(min_size=0, max_size=1000)),
            'price': draw(st.floats(min_value=0.01, max_value=10000.0)),
            'category_id': draw(st.integers(min_value=1)),
            'stock_quantity': draw(st.integers(min_value=0)),
            'image_url': draw(st.one_of(st.none(), st.urls())),
            'tags': draw(st.lists(st.text(min_size=1, max_size=20), max_size=10))
        }

    @staticmethod
    @composite
    def update_product_body(draw) -> Dict[str, Any]:
        """生成更新产品请求体策略"""
        return {
            'name': draw(st.one_of(st.none(), st.text(min_size=1, max_size=100))),
            'description': draw(st.one_of(st.none(), st.text(min_size=0, max_size=1000))),
            'price': draw(st.one_of(st.none(), st.floats(min_value=0.01, max_value=10000.0))),
            'stock_quantity': draw(st.one_of(st.none(), st.integers(min_value=0)))
        }

    # ==================== 系统API策略 ====================

    @staticmethod
    @composite
    def system_settings_body(draw) -> Dict[str, Any]:
        """生成系统设置请求体策略"""
        return {
            'site_name': draw(st.text(min_size=1, max_size=50)),
            'site_description': draw(st.text(min_size=0, max_size=200)),
            'admin_email': draw(st.emails()),
            'max_file_size': draw(st.integers(min_value=1, max_value=100)),
            'allowed_file_types': draw(st.lists(st.text(min_size=1, max_size=10), max_size=10)),
            'maintenance_mode': draw(st.booleans())
        }

    @staticmethod
    @composite
    def email_template_body(draw) -> Dict[str, Any]:
        """生成邮件模板请求体策略"""
        return {
            'template_name': draw(st.text(min_size=1, max_size=50)),
            'subject': draw(st.text(min_size=1, max_size=100)),
            'body': draw(st.text(min_size=1, max_size=5000)),
            'is_active': draw(st.booleans())
        }

    # ==================== 边界情况策略 ====================

    @staticmethod
    @composite
    def edge_case_users_query(draw) -> Dict[str, Any]:
        """生成边界情况的用户查询参数"""
        return {
            'offset': draw(base_strategies.edge_case_integers()),
            'limit': draw(base_strategies.edge_case_integers()),
            'username': draw(base_strategies.edge_case_strings()),
            'email': draw(base_strategies.edge_case_strings())
        }

    @staticmethod
    @composite
    def edge_case_login_credentials(draw) -> Dict[str, Any]:
        """生成边界情况的登录凭据"""
        return {
            'username': draw(base_strategies.edge_case_strings()),
            'password': draw(base_strategies.edge_case_strings()),
            'remember_me': draw(st.one_of(st.just(True), st.just(False), st.none()))
        }


# 创建API策略实例
api_strategies = APIStrategies()