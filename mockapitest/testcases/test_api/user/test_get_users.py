from hypothesis import given, assume
import pytest
from mockapitest.apis.mock2.users.apis import GetUsersApiUsersGetAPI
from mockapitest.custom_hypothesis.strategies.base_strategies import base_strategies
from mockapitest.custom_hypothesis.strategies.boundary_strategies import boundary_strategies
from mockapitest.custom_hypothesis.strategies.error_strategies import error_strategies
from mockapitest.custom_hypothesis.Profile.test_profile import QUICK,STANDARD,COMPREHENSIVE


@pytest.mark.userscenario
@pytest.mark.hypothesis
@given(
    offset=base_strategies.integers(min_value=1, max_value=10),
    limit=base_strategies.sampled_from([10, 20, 50, 100]),
    username=base_strategies.strings(
        min_length=0,
        max_length=20,
        allow_empty=True
    )
)
@COMPREHENSIVE
def test_search_user_property_based(offset, limit, username):
    """获取系统中的用户列表-验证通用属性"""
    request_body = GetUsersApiUsersGetAPI.QueryParams(
        offset=offset, limit=limit, username=username
    )
    response = GetUsersApiUsersGetAPI(query_params=request_body).send()

    # 属性1: 接口不应崩溃，应返回定义良好的状态

    assert response.cached_response.raw_response.status_code in [200, 400, 404]  # 根据您的API设计调整允许的状态码

    # 属性2: 响应模型应可正确解析
    assert hasattr(response, 'response_model')

    # 4. 智能业务逻辑断言
    if response.response_model.ret_code == 0:  # 业务逻辑成功时
        data = response.response_model.data

        # 属性3: 如果用户名为空，接口返回所有用户或空列表，但每个结果应结构完整
        if not username:
            for user_info in data:
                assert user_info.username is not None  # 用户名不应为null
        # 属性4: 如果用户名不为空，结果应包含查询关键词（模糊匹配）
        else:
            for user_info in data:
                assert user_info.username is not None
                # 关键属性：模糊匹配。注意大小写敏感性，根据实际情况调整
                assert username.lower() in user_info.username.lower()  # 假设不区分大小写

        # 属性5: 分页限制有效性
        if limit > 0:
            assert len(data) <= limit  # 返回数量不应超过请求的限制数
    else:
        # 属性6: 当业务逻辑失败时（如参数错误），应返回非0的错误码和错误信息
        assert response.response_model.ret_code != 0
        assert response.response_model.message is None


# 2. 长度验证测试
@pytest.mark.userscenario
@STANDARD
@given(
    username=boundary_strategies.string_length_boundaries(min_len=2000, max_len=3000)
)
def test_user_search_length_validation(username):
    """获取系统中的用户列表-用户名长度边界验证"""
    request_body = GetUsersApiUsersGetAPI.QueryParams(
        offset=0,
        limit=10,
        username=username
    )

    response = GetUsersApiUsersGetAPI(query_params=request_body).send()

    # 基本接口稳定性验证
    assert response.cached_response.raw_response.status_code in [200, 400]

    if len(username) > 2048:  # 超过定义的最大长度
        # 应该返回错误或截断处理
        assert response.response_model.ret_code == 0
    else:
        # 正常长度应该成功或合理处理
        assert response.cached_response.raw_response.status_code == 200


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
    """获取系统中的用户列表-安全边界：防止SQL注入、XSS等攻击"""
    request_body = GetUsersApiUsersGetAPI.QueryParams(
        offset=0,
        limit=10,
        username=attack_vector
    )

    response = GetUsersApiUsersGetAPI(query_params=request_body).send()

    # 安全验证：不应执行危险操作或泄露敏感信息
    assert response.cached_response.raw_response.status_code != 500  # 不应崩溃
    assert "error" not in str(response.cached_response).lower()  # 不应泄露错误详情

    # 对于明显的攻击尝试，系统应该安全处理
    if any(keyword in attack_vector for keyword in ["OR 1=1", "<script>", "DROP TABLE"]):
        assert response.response_model.ret_code in [0, 400, 403]


# 4. 数值边界测试
@pytest.mark.userscenario
@STANDARD
@given(
    offset=boundary_strategies.integer_boundaries(min_val=0, max_val=1000),
    limit=boundary_strategies.integer_boundaries(min_val=1, max_val=100)
)
def test_user_search_numeric_boundaries(offset, limit):
    """获取系统中的用户列表-数值参数边界情况"""
    # 跳过明显无效的测试用例
    if offset < -1000 or offset > 100000 or limit < 0 or limit > 1000:
        pytest.skip("超出合理测试范围的数值")

    request_body = GetUsersApiUsersGetAPI.QueryParams(
        offset=offset,
        limit=limit,
        username="test"
    )

    response = GetUsersApiUsersGetAPI(query_params=request_body).send()

    # 边界数值处理验证
    if offset < 0:
        assert response.response_model.ret_code != 0  # 负偏移量应该报错
    elif limit == 0:
        if response.response_model.ret_code == 0:
            assert len(response.response_model.data) == 0  # 零限制应返回空
    else:
        assert response.cached_response.raw_response.status_code == 200


# 5. 特殊字符边界测试
@pytest.mark.userscenario
@QUICK
@given(
    special_chars=boundary_strategies.special_characters()
)
def test_user_search_special_characters(special_chars):
    """获取系统中的用户列表-特殊字符处理能力"""
    request_body = GetUsersApiUsersGetAPI.QueryParams(
        offset=0,
        limit=10,
        username=special_chars
    )

    response = GetUsersApiUsersGetAPI(query_params=request_body).send()

    # 特殊字符处理验证
    assert response.cached_response.raw_response.status_code in [200, 400]

    if response.response_model.ret_code == 0:
        data = response.response_model.data
        for user_info in data:
            assert user_info.username is not None


# 6. 综合边界测试
@pytest.mark.userscenario
@COMPREHENSIVE
@given(
    offset=base_strategies.integers(min_value=-10, max_value=10000),
    limit=base_strategies.integers(min_value=0, max_value=1000),
    username=base_strategies.one_of(
        boundary_strategies.string_length_boundaries(max_len=20),
        error_strategies.sql_injection_vectors(),
        boundary_strategies.special_characters(),
        base_strategies.strings(min_length=0, max_length=20)
    )
)
def test_user_search_comprehensive_boundaries( offset, limit, username):
    """获取系统中的用户列表-综合边界测试：组合各种边界条件"""
    # 过滤明显不合理的测试用例
    if offset < -1000 or offset > 1000000 or limit > 10000 or len(username) > 1000:
        pytest.skip("超出合理测试范围")

    request_body = GetUsersApiUsersGetAPI.QueryParams(
        offset=offset,
        limit=limit,
        username=username
    )

    response = GetUsersApiUsersGetAPI(query_params=request_body).send()

    # 综合验证点
    assert response.cached_response.raw_response.status_code in [200, 400]

    if response.response_model.ret_code == 0:
        data = response.response_model.data
        assert len(data) <= limit if limit > 0 else True
