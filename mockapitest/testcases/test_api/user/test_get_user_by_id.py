from hypothesis import given, assume
import pytest
from mockapitest.apis.mock2.users.apis import GetUserApiUsersUserIdGetAPI
from mockapitest.custom_hypothesis.strategies.base_strategies import base_strategies
from mockapitest.custom_hypothesis.strategies.boundary_strategies import boundary_strategies
from mockapitest.custom_hypothesis.strategies.error_strategies import error_strategies
from mockapitest.custom_hypothesis.Profile.test_profile import QUICK,STANDARD,COMPREHENSIVE

"""
1.Get接口的PathParams格式
2.获取系统中的用户列表-特殊整数处理能力测试内容完整，可以作为范例
3.通过ID获取单个用户信息-用户名长度边界验证测试内容完整，可以作为范例
"""
# @pytest.mark.ones
@pytest.mark.hypothesis
@given(
user_id = base_strategies.integers(min_value=1 , max_value=100),
)
@COMPREHENSIVE
def test_get_user_by_id_property_based(user_id):
    """通过ID获取单个用户信息-验证通用属性"""
    path_params = GetUserApiUsersUserIdGetAPI.PathParams(
        user_id= user_id
    )
    response = GetUserApiUsersUserIdGetAPI(path_params=path_params).send()

    # 接口不应崩溃，应返回定义良好的状态

    assert response.cached_response.raw_response.status_code in [200, 400, 404]


    # 4. 智能业务逻辑断言
    if response.response_model.ret_code == 0:  # 业务逻辑成功时
        data = response.response_model.data

        # 属性3: 如果ID不存在，details返回用户不存在
        if not data:
            assert response.response_model.detail is not None
            assert response.response_model.detail == "用户不存在"
        # 属性4: 如果ID存在，返回data，输入user_id等于返回id
        else:
            assert user_id == data.id
    else:
        # 属性6: 当业务逻辑失败时（如参数错误），应返回非0的错误码和错误信息
        assert response.cached_response.raw_response.status_code in [400, 404]


# 2. 长度验证测试
# @pytest.mark.ones
@COMPREHENSIVE
@given(
    user_id = boundary_strategies.integer_length_boundaries(min_len=4000, max_len=5000),
)
def test_get_user_by_id_length_validation(user_id):
    """通过ID获取单个用户信息-用户名长度边界验证"""
    path_params = GetUserApiUsersUserIdGetAPI.PathParams(
        user_id=user_id
    )
    response = GetUserApiUsersUserIdGetAPI(path_params=path_params).send()
    response_data = response.cached_response.raw_response.json()

    # 基本接口稳定性验证
    assert response.cached_response.raw_response.status_code in [200, 422,404]

    if len(user_id) > 4096:  # 超过定义的最大长度
        # 应该返回错误或截断处理
        # assert response.cached_response.raw_response.status_code == 404
        assert response_data['detail'][0]['msg'] == "Unable to parse input string as an integer, exceeded maximum size"
    if response.cached_response.raw_response.status_code == 200:
        assert response.response_model.data is not None
        assert response.response_model.message == "success"
    if user_id == "" :
        data = response.response_model.data
        for user_info in data:
            assert user_info.username is not None
    if user_id == " " :
        assert response_data['detail'][0]['msg'] == "Input should be a valid integer, unable to parse string as an integer"
    else:
        # 正常长度应该成功或合理处理
        assert response.cached_response.raw_response.status_code in [422,404]
        # assert response.response_model.detail == "用户不存在" #不知道真实最大值


# 3. 安全边界测试
@pytest.mark.userscenario
@STANDARD
# @pytest.mark.ones
@given(
    attack_vector=base_strategies.one_of(
        error_strategies.sql_injection_vectors(),
        error_strategies.xss_vectors(),
        error_strategies.path_traversal_vectors()
    )
)
def test_user_search_security_boundaries( attack_vector):
    """通过ID获取单个用户信息-安全边界：防止SQL注入、XSS等攻击"""
    path_params = GetUserApiUsersUserIdGetAPI.PathParams(user_id= attack_vector)

    response = GetUserApiUsersUserIdGetAPI(path_params=path_params).send()

    # 安全验证：不应执行危险操作或泄露敏感信息
    assert response.cached_response.raw_response.status_code != 500  # 不应崩溃
    assert "error" not in str(response.cached_response).lower()  # 不应泄露错误详情

    # 对于明显的攻击尝试，系统应该安全处理
    if any(keyword in attack_vector for keyword in ["OR 1=1", "<script>", "DROP TABLE"]):
        assert response.response_model.ret_code in [0, 400, 403]




# 4. 特殊字符边界测试
@pytest.mark.API
# @pytest.mark.ones
@STANDARD
@given(
    special_integers=boundary_strategies.edge_case_integers()
)
def test_user_search_special_characters(special_integers):
    """获取系统中的用户列表-特殊整数处理能力"""
    path_params = GetUserApiUsersUserIdGetAPI.PathParams(user_id= special_integers)

    response = GetUserApiUsersUserIdGetAPI(path_params=path_params).send()

    # 特殊字符处理验证
    assert response.cached_response.raw_response.status_code in [200,422, 400,404]

    if response.response_model.ret_code == 0:
        if response.response_model.data is not None:
            assert response.response_model.message == "success"
        else:
            assert response.response_model.detail is not None




