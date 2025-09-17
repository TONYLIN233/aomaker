import pytest
from aomaker.storage import cache
from mockapitest.apis.mock2.auth.apis import LoginForAccessTokenApiLoginTokenPostAPI
from attrs import define, field
from aomaker.core.router import router
from aomaker.core.api_object import BaseAPIObject

@pytest.mark.auth
def test_get_auth_right(self):
    """测试获取access_token"""
    request_body = LoginForAccessTokenApiLoginTokenPostAPI.RequestBodyModel(username=None,password=None)

    res = LoginForAccessTokenApiLoginTokenPostAPI(request_body = request_body).send()

    assert res.response_model.ret_code == 0
    assert res.response_model.data.access_token is not None
    assert res.response_model.message == "登录成功"

@pytest.mark.auth
def test_get_auth_without_username():
    """测试不输入uersname获取access_token"""
    request_body = LoginForAccessTokenApiLoginTokenPostAPI.RequestBodyModel(username=None,password=None)

    res = LoginForAccessTokenApiLoginTokenPostAPI(request_body = request_body).send()

    assert res.response_model.ret_code == 0
    assert res.response_model.data.access_token is not None