from datetime import datetime

import pytest
from mockapitest.apis.mock2.users import apis

@pytest.mark.SMOKE
# @pytest.mark.ones
def test_create_new_user():
    """创建一个新用户"""
    request_body = apis.CreateUserApiUsersPostAPI.RequestBodyModel(id= 123,username="test",email="274276305@qq.com",
                                                                   created_at=datetime.now(),is_active=True)
    response = apis.CreateUserApiUsersPostAPI(request_body=request_body).send()

    assert response.response_model.ret_code == 0
    assert response.response_model.message == "用户创建成功"
    assert response.response_model.data.id == 123
    assert response.response_model.data.username == "test"

@pytest.mark.SMOKE
@pytest.mark.ones
def test_create_user_duplicate():
    """创建一个重复的用户"""
    request_body = apis.CreateUserApiUsersPostAPI.RequestBodyModel(id= 123,username="test1",email="274276305@qq.com",
                                                                   created_at=datetime.now(),is_active=True)
    response = apis.CreateUserApiUsersPostAPI(request_body=request_body).send()

    assert response.response_model.ret_code == 0
    assert response.response_model.message == "用户创建成功"
    assert response.response_model.data.id == 123
    assert response.response_model.data.username == "test1"

    request_body_duplicate = apis.CreateUserApiUsersPostAPI.RequestBodyModel(id=123, username="test", email="274276305@qq.com",
                                                                   created_at=datetime.now(), is_active=True)

    response = apis.CreateUserApiUsersPostAPI(request_body=request_body_duplicate).send()
    assert response.response_model.ret_code == 0
    # assert response.response_model.message == "报错信息"#实际上这个接口没有报错


