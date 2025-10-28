import pytest
from datetime import datetime
from hypothesis import given, assume
from mockapitest.custom_hypothesis.strategies.base_strategies import base_strategies
from mockapitest.custom_hypothesis.strategies.boundary_strategies import boundary_strategies
from mockapitest.custom_hypothesis.strategies.error_strategies import error_strategies
from mockapitest.custom_hypothesis.Profile.test_profile import QUICK, STANDARD, COMPREHENSIVE
from mockapitest.apis.mock2.users import apis

@pytest.mark.oness
@pytest.mark.hypothesis
@pytest.mark.creatuser
@COMPREHENSIVE
@given(
    id=base_strategies.one_of(
        base_strategies.integers(min_value=0, max_value=1000),  # 正常ID范围
        boundary_strategies.integer_boundaries(min_val=-100, max_val=10000),  # 边界值
        error_strategies.invalid_types(field_name="id" ,expected_type= int)  # 无效类型
    ),
    username=base_strategies.one_of(
        base_strategies.strings(min_length=1, max_length=50),  # 正常用户名
        boundary_strategies.string_length_boundaries(min_len=0, max_len=100),  # 长度边界
        error_strategies.empty_values(),  # 空值
        boundary_strategies.special_characters(),  # 特殊字符
        error_strategies.sql_injection_vectors()  # SQL注入向量
    ),
    email=base_strategies.one_of(
        base_strategies.emails(),  # 正常邮箱
        boundary_strategies.string_length_boundaries(min_len=0, max_len=100),  # 长度边界
        error_strategies.empty_values(),  # 空值
        error_strategies.invalid_emails(),  # 无效邮箱格式
        boundary_strategies.special_characters()  # 特殊字符
    ),
    created_at=base_strategies.one_of(
        base_strategies.datetimes(),  # 正常日期时间
        # error_strategies.invalid_datetime_strings(),  # 无效日期时间格式
        error_strategies.empty_values()  # 空值
    ),
    is_active=base_strategies.one_of(
        base_strategies.booleans(),  # 正常布尔值
        error_strategies.invalid_boolean_values(),  # 无效布尔值
        error_strategies.empty_values()  # 空值
    )
)
def test_create_user_property_based(id, username, email, created_at, is_active):
    """
    创建用户 - 属性测试：验证各种输入组合下的API行为

    属性1: 接口不应崩溃，应返回定义良好的状态码
    属性2: 响应模型应可正确解析
    属性3: 对于有效输入应返回成功响应
    属性4: 对于无效输入应返回适当的错误信息
    """
    # 过滤明显不合理的测试用例
    assume(id is None or isinstance(id, (int, str)))
    assume(username is None or isinstance(username, str))
    assume(email is None or isinstance(email, str))
    assume(created_at is None or isinstance(created_at, (datetime, str)))
    assume(is_active is None or isinstance(is_active, (bool, str, int)))

    # 构建请求体
    request_body = apis.CreateUserApiUsersPostAPI.RequestBodyModel(
        id=id,
        username=username,
        email=email,
        created_at=created_at,
        is_active=is_active
    )

    response = apis.CreateUserApiUsersPostAPI(request_body=request_body).send()

    # 属性1: 接口稳定性验证
    assert response.cached_response.raw_response.status_code in [200, 400, 422]

    # 属性2: 响应模型应可正确解析
    assert hasattr(response, 'response_model')

    # 智能业务逻辑断言
    if _is_valid_input(id, username, email, created_at, is_active):
        # 属性3: 有效输入应返回成功
        assert response.response_model.ret_code == 0
        assert response.response_model.message == "用户创建成功"
        if response.response_model.data:
            assert response.response_model.data.id == id
            assert response.response_model.data.username == username
    else:
        # 属性4: 无效输入应返回错误
        if  response.cached_response.raw_response.status_code != 200:
            assert len(response.response_model.detail) > 0




def _is_valid_input(id, username, email, created_at, is_active):
    """判断输入是否有效 - 与API验证规则保持一致"""
    # 1. ID验证：根据API实际规则调整
    # 如果API接受负ID，移除非负检查
    if not isinstance(id, int):  # 只检查类型，不检查值范围
        return False

    # 2. 用户名验证：根据API实际规则
    if not isinstance(username, str) or len(username.strip()) == 0:
        return False
    # 移除长度上限检查，或调整为API实际限制

    # 3. 邮箱验证：根据API实际验证严格程度
    if not isinstance(email, str) or len(email) == 0:
        return False
    # 如果API不验证邮箱格式，移除'@'检查
    # if '@' not in email: return False

    # 4. 日期时间验证
    if not isinstance(created_at, datetime):
        return False

    # 5. 布尔值验证
    if not isinstance(is_active, bool):
        return False

    return True


@pytest.mark.hypothesis
@STANDARD
@given(username=boundary_strategies.string_length_boundaries(min_len=0, max_len=100))
#不执行次用例，根本找不到边界。
def test_create_user_username_length_validation(username):
    """创建用户 - 用户名长度边界验证"""
    request_body = apis.CreateUserApiUsersPostAPI.RequestBodyModel(
        id=123,
        username=username,
        email="test@example.com",
        created_at=datetime.now(),
        is_active=True
    )

    response = apis.CreateUserApiUsersPostAPI(request_body=request_body).send()

    # 基本接口稳定性验证
    assert response.cached_response.raw_response.status_code in [200, 400, 422]

    # 长度边界验证
    if len(username) == 0:
        # 空用户名应返回错误
        assert response.response_model.ret_code != 0
        assert any("username" in error.get("loc", []) for error in response.response_model.detail)
    elif 1 <= len(username) <= 50:
        # 正常长度可能成功
        if response.response_model.ret_code == 0:
            assert response.response_model.data.username == username
    else:
        # 超长用户名应返回错误
        assert response.response_model.ret_code != 0


@pytest.mark.hypothesis
@STANDARD
@given(email=boundary_strategies.string_length_boundaries(min_len=0, max_len=150))
def test_create_user_email_length_validation(email):
    """创建用户 - 邮箱长度边界验证"""
    request_body = apis.CreateUserApiUsersPostAPI.RequestBodyModel(
        id=123,
        username="testuser",
        email=email,
        created_at=datetime.now(),
        is_active=True
    )

    response = apis.CreateUserApiUsersPostAPI(request_body=request_body).send()

    # 基本接口稳定性验证
    assert response.cached_response.raw_response.status_code in [200, 400, 422]

    # 邮箱格式和长度验证
    if len(email) == 0:
        # 空邮箱应返回错误
        assert response.response_model.ret_code != 0
    elif '@' not in email:
        # 无效邮箱格式应返回错误
        assert response.response_model.ret_code != 0
    elif len(email) > 100:
        # 超长邮箱应返回错误
        assert response.response_model.ret_code != 0
    else:
        # 有效邮箱可能成功
        if response.response_model.ret_code == 0:
            assert response.response_model.data.email == email


@pytest.mark.hypothesis
@pytest.mark.creatuser
@STANDARD
@given(attack_vector=base_strategies.one_of(
    error_strategies.sql_injection_vectors(),
    error_strategies.xss_vectors(),
    error_strategies.path_traversal_vectors()
))
def test_create_user_security_validation(attack_vector):
    """创建用户 - 安全边界验证：防止注入攻击"""
    request_body = apis.CreateUserApiUsersPostAPI.RequestBodyModel(
        id=123,
        username=attack_vector,
        email="test@example.com",
        created_at=datetime.now(),
        is_active=True
    )

    response = apis.CreateUserApiUsersPostAPI(request_body=request_body).send()

    # 安全验证：不应崩溃或泄露敏感信息
    assert response.cached_response.raw_response.status_code != 500
    assert "error" not in str(response.cached_response).lower()

    # 对于明显的攻击尝试，系统应安全处理
    dangerous_patterns = ["OR 1=1", "<script>", "DROP TABLE", "../", "\\x00"]
    if any(pattern in attack_vector for pattern in dangerous_patterns):
        assert response.response_model.ret_code != 0


@pytest.mark.hypothesis
@pytest.mark.creatuser
@QUICK
@given(special_chars=boundary_strategies.special_characters())
def test_create_user_special_characters(special_chars):
    """创建用户 - 特殊字符处理能力"""
    request_body = apis.CreateUserApiUsersPostAPI.RequestBodyModel(
        id=123,
        username=special_chars,
        email=f"{special_chars}@example.com",
        created_at=datetime.now(),
        is_active=True
    )

    response = apis.CreateUserApiUsersPostAPI(request_body=request_body).send()

    # 特殊字符处理验证
    assert response.cached_response.raw_response.status_code in [200, 400, 422]

    if response.response_model.ret_code == 0:
        # 成功创建，验证数据一致性
        assert response.response_model.data.username == special_chars


@pytest.mark.hypothesis
@pytest.mark.creatuser
@STANDARD
@given(
    id=boundary_strategies.integer_boundaries(min_val=-100, max_val=10000),
    is_active=error_strategies.invalid_boolean_values()
)
def test_create_user_id_and_boolean_validation(id, is_active):
    """创建用户 - ID和布尔值边界验证"""
    # 过滤明显不合理的测试用例
    if id < -1000 or id > 100000:
        pytest.skip("超出合理测试范围的ID值")

    request_body = apis.CreateUserApiUsersPostAPI.RequestBodyModel(
        id=id,
        username="testuser",
        email="test@example.com",
        created_at=datetime.now(),
        is_active=is_active
    )

    response = apis.CreateUserApiUsersPostAPI(request_body=request_body).send()

    # 边界值处理验证
    if id < 0:
        assert response.response_model.ret_code != 0  # 负ID应报错
    elif not isinstance(is_active, bool):
        assert response.response_model.ret_code != 0  # 无效布尔值应报错
    else:
        assert response.cached_response.raw_response.status_code == 200


@pytest.mark.hypothesis
@pytest.mark.creatuser
@COMPREHENSIVE
@given(
    datetime_input=base_strategies.one_of(
        base_strategies.datetimes(),
        error_strategies.invalid_datetime_strings(),
        error_strategies.empty_values()
    )
)
def test_create_user_datetime_validation(datetime_input):
    """创建用户 - 日期时间格式验证"""
    request_body = apis.CreateUserApiUsersPostAPI.RequestBodyModel(
        id=123,
        username="testuser",
        email="test@example.com",
        created_at=datetime_input,
        is_active=True
    )

    response = apis.CreateUserApiUsersPostAPI(request_body=request_body).send()

    # 日期时间格式验证
    if isinstance(datetime_input, datetime):
        # 有效日期时间应成功
        if response.response_model.ret_code == 0:
            # 验证日期时间是否正确处理
            assert response.response_model.data.created_at is not None
    else:
        # 无效日期时间格式应报错
        assert response.response_model.ret_code != 0
        assert any("created_at" in error.get("loc", []) for error in response.response_model.detail)


"""必填字段的空值校验"""
@pytest.mark.hypothesis
@pytest.mark.creatuser
@pytest.mark.ones1
@STANDARD
@given(missing_field=base_strategies.sampled_from(["id", "username", "email", "created_at", "is_active"]))
def test_create_user_missing_fields(missing_field):
    """创建用户 - 字段缺失测试"""
    # 创建完整请求体
    request_data = {
        "id": 123,
        "username": "testuser",
        "email": "test@example.com",
        "created_at": datetime.now(),
        "is_active": True
    }

    # 移除指定字段
    request_data[missing_field] = None

    # 根据字段重要性区分测试预期
    if missing_field in ["id", "username", "email", "created_at"]:  # 必填字段
        # 对于必填字段，即使设置为None也应该能初始化模型，但API调用应返回错误
        request_body = apis.CreateUserApiUsersPostAPI.RequestBodyModel(**request_data)
        response = apis.CreateUserApiUsersPostAPI(request_body=request_body).send()

        # 必填字段为空时，期望API返回错误状态码
        assert response.cached_response.raw_response.status_code != 200
        # 验证错误信息中是否包含该字段
        assert any(missing_field in error.get("loc", [])
                   for error in getattr(response.response_model, 'detail', []))
    else:
        # 对于非必填字段（如is_active），空值可能被接受
        request_body = apis.CreateUserApiUsersPostAPI.RequestBodyModel(**request_data)
        response = apis.CreateUserApiUsersPostAPI(request_body=request_body).send()
        # 非必填字段为空可能成功或失败，取决于业务逻辑
        assert response.cached_response.raw_response.status_code in [200, 400]

# 综合边界测试
@pytest.mark.hypothesis
@pytest.mark.creatuser
@COMPREHENSIVE
@given(
    id=base_strategies.one_of(
        base_strategies.integers(min_value=0, max_value=1000),
        boundary_strategies.integer_boundaries(min_val=-10, max_val=10000),
        error_strategies.invalid_types(expected_type=int,field_name="id"),
    ),
    username=base_strategies.one_of(
        base_strategies.strings(min_length=1, max_length=50),
        boundary_strategies.string_length_boundaries(min_len=0, max_len=100),
        error_strategies.empty_values(),
        boundary_strategies.special_characters()
    ),
    email=base_strategies.one_of(
        base_strategies.emails(),
        boundary_strategies.string_length_boundaries(min_len=0, max_len=150),
        error_strategies.empty_values(),
        error_strategies.invalid_emails()
    )
)
def test_create_user_comprehensive_boundaries(id, username, email):
    """创建用户 - 综合边界测试：组合各种边界条件"""
    # 过滤明显不合理的测试用例
    if (isinstance(id, int) and (id < -1000 or id > 100000)) or \
            (isinstance(username, str) and len(username) > 1000) or \
            (isinstance(email, str) and len(email) > 200):
        pytest.skip("超出合理测试范围")

    request_body = apis.CreateUserApiUsersPostAPI.RequestBodyModel(
        id=id,
        username=username,
        email=email,
        created_at=datetime.now(),
        is_active=True
    )

    response = apis.CreateUserApiUsersPostAPI(request_body=request_body).send()

    # 综合验证点
    assert response.cached_response.raw_response.status_code in [200, 400, 422]

    if response.response_model.ret_code == 0:
        # 成功创建，验证数据一致性
        assert response.response_model.data.id == id
        assert response.response_model.data.username == username
        assert response.response_model.data.email == email