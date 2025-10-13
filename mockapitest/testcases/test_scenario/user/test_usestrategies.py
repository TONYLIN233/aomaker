import pytest
from hypothesis import given

from mockapitest.apis.mock2.users.apis import GetUsersApiUsersGetAPI
from mockapitest.hypothesis.strategies import api_strategies, base_strategies


class TestUserAPI:
    """用户API测试"""

    @given(api_strategies.users_query_params())
    def test_get_users_with_hypothesis(self, query_params):
        """使用Hypothesis测试用户查询API"""
        # 构建API请求
        api_request = GetUsersApiUsersGetAPI(
            query_params=GetUsersApiUsersGetAPI.QueryParams(**query_params)
        )

        # 发送请求并验证响应
        response = api_request.send()
        assert response.response_model.ret_code == 0

    @given(api_strategies.edge_case_users_query())
    def test_get_users_edge_cases(self, query_params):
        """测试边界情况的用户查询"""
        # 过滤无效参数
        if query_params.get('offset') is not None and query_params['offset'] < 0:
            pytest.skip("Negative offset not supported")

        if query_params.get('limit') is not None and query_params['limit'] <= 0:
            pytest.skip("Non-positive limit not supported")

        # 构建和发送请求
        api_request = GetUsersApiUsersGetAPI(
            query_params=GetUsersApiUsersGetAPI.QueryParams(**query_params)
        )

        response = api_request.send()
        # API应该能够处理边界情况而不崩溃
        assert hasattr(response, 'response_model')