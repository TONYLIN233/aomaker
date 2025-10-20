from hypothesis import given, strategies as st, settings, assume
import pytest
from mockapitest.apis.mock2.users import apis

@pytest.mark.smoke
@pytest.mark.userbyidsmoke
def test_query_existent_user():
    """获取存在的单个用户信息"""
    path_params = apis.GetUserApiUsersUserIdGetAPI.PathParams(user_id = 1)
    response = apis.GetUserApiUsersUserIdGetAPI(path_params=path_params).send()

    assert response.response_model.ret_code == 0
    assert response.response_model.message == "success"
    # print(response.response_model.data)
    assert response.response_model.data.username and "张" in response.response_model.data.username

@pytest.mark.smoke
@pytest.mark.userbyidsmoke
def test_exact_nonexistent_user():
    """获取不存在的单个用户信息"""
    path_params = apis.GetUserApiUsersUserIdGetAPI.PathParams(user_id=10)
    response = apis.GetUserApiUsersUserIdGetAPI(path_params=path_params).send()

    assert response.cached_response.raw_response.status_code == 404
    assert response.response_model.detail == "用户不存在"

