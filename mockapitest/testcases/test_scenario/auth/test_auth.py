import pytest
from fastapi.dependencies.utils import request_body_to_args

from aomaker.storage import cache
from mockapitest.apis.mock2.auth.apis import LoginForAccessTokenApiLoginTokenPostAPI
from attrs import define, field
from aomaker.core.router import router
from aomaker.core.api_object import BaseAPIObject

@pytest.mark.auth
def test_get_auth_right():
    """测试获取access_token"""
    request_body = LoginForAccessTokenApiLoginTokenPostAPI.RequestBodyModel(username="aomaker",password='123456')

    res = LoginForAccessTokenApiLoginTokenPostAPI(request_body = request_body).send()

    assert res.response_model.ret_code == 0
    assert res.response_model.data.access_token is not None
    assert res.response_model.message == "登录成功"

@pytest.mark.auth
def test_get_auth_without_username():
    """测试不输入uersname获取access_token"""
    request_body = LoginForAccessTokenApiLoginTokenPostAPI.RequestBodyModel(username='',password='123456')

    res = LoginForAccessTokenApiLoginTokenPostAPI(request_body = request_body).send()

    assert res.response_model.detail == "用户名或密码错误"

@pytest.mark.auth
def test_get_auth_without_password():
    """测试不输入password获取access_token"""
    request_body = LoginForAccessTokenApiLoginTokenPostAPI.RequestBodyModel(username="aomaker",password='')
    res = LoginForAccessTokenApiLoginTokenPostAPI(request_body = request_body).send()
    assert res.response_model.detail == "用户名或密码错误"

@pytest.mark.auth
def test_get_auth_with_errusername():
    """测试输入错误uersname获取access_token"""
    request_body = LoginForAccessTokenApiLoginTokenPostAPI.RequestBodyModel(username="aomaker2",password='123456')
    res = LoginForAccessTokenApiLoginTokenPostAPI(request_body = request_body).send()
    assert res.response_model.detail == "用户名或密码错误"

@pytest.mark.auth
def test_get_auth_with_errpassword():
    """测试输入错误的password获取access_token"""
    request_body = LoginForAccessTokenApiLoginTokenPostAPI.RequestBodyModel(username="aomaker",password='234567')
    res = LoginForAccessTokenApiLoginTokenPostAPI(request_body = request_body).send()
    assert res.response_model.detail == "用户名或密码错误"

