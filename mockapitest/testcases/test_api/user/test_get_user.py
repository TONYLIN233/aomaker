from hypothesis import given, strategies as st, settings, assume
import pytest
from mockapitest.apis.mock2.users.apis import GetUsersApiUsersGetAPI


class TestUserProcessing:

    # 1. 测试基本数据类型和业务边界
    @given(
        username=st.text(min_size=1, max_size=20),
        offset=st.integers(min_value=0, max_value=150),
        limit=st.integers(min_value=0, max_value=150)
    )
    @settings(max_examples=200)  # 增加测试用例数量以更充分探索边界
    @pytest.mark.getuser
    def test_user_processing_basic(self, username, offset, limit):
        """测试用户处理函数的基本数据类型和业务规则边界"""
        # 使用 assume 过滤掉可能因其他原因导致处理失败的数据
        # 例如，假设用户名不能以数字开头
        assume(not username.startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')))

        request_body = GetUsersApiUsersGetAPI.QueryParams(
        offset=offset,
        limit=limit,
        username = username
        )
        # 发送请求
        api_instance = GetUsersApiUsersGetAPI(request_body=request_body)
        result = api_instance.send()
        # 断言：验证函数返回了有效结果（例如非None）
        assert result is not None
        # 可以根据您的函数逻辑添加更多断言，例如结果中必须包含某些字段
        # assert 'user_id' in result
        assert result.response_model.ret_code == 0

