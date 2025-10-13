from hypothesis import given, strategies as st, settings, assume
import pytest
from mockapitest.apis.mock2.users import apis


@pytest.mark.userscenario
def test_fuzzy_search_user():
    """获取系统中的用户列表模糊检索"""
    request_body = apis.GetUsersApiUsersGetAPI.QueryParams(offset=0, limit=10, username="张")

    response = apis.GetUsersApiUsersGetAPI(query_params=request_body).send()

    assert response.response_model.ret_code == 0
    assert response.response_model.message == "success"
    # print(response.response_model.data)
    for info in response.response_model.data:
        assert info.username is not None and "张" in info.username
        

@pytest.mark.userscenario
def test_exact_search_user():
    """获取系统中的用户列表精确检索"""
    request_body = apis.GetUsersApiUsersGetAPI.QueryParams()