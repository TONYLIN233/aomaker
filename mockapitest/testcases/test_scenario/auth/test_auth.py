import pytest
from fastapi.dependencies.utils import request_body_to_args

from aomaker.storage import cache
from mockapitest.apis.mock2.auth.apis import LoginForAccessTokenApiLoginTokenPostAPI
from attrs import define, field
from aomaker.core.router import router
from aomaker.core.api_object import BaseAPIObject
from hypothesis import given, strategies as st, assume
"""回去好好改一下看下能不能用"""

@given(
    st.fixed_dictionaries({
        # 生成各种可能无效的用户名
        "username": st.one_of(
            st.none(),
            st.booleans(),
            st.integers(),
            st.lists(st.text()),
            st.text(min_size=1000, max_size=2000),  # 超长用户名
            st.just(""),  # 空用户名
            st.text(alphabet=' ', min_size=1, max_size=5),  # 纯空格用户名
            st.sampled_from([
                "' OR '1'='1' --",
                "<script>alert('xss')</script>",
                "../../etc/passwd"
            ])  # 注入攻击字符串
        ),
        # 生成各种可能无效的密码
        "password": st.one_of(
            st.none(),
            st.booleans(),
            st.integers(),
            st.lists(st.text()),
            st.text(min_size=1000, max_size=2000),  # 超长密码
            st.just(""),  # 空密码
            st.text(alphabet=' ', min_size=1, max_size=5),  # 纯空格密码
            st.sampled_from([
                "' OR '1'='1' --",
                "<script>alert('xss')</script>",
                "../../etc/passwd"
            ])  # 注入攻击字符串
        )
    })
)
def test_login_with_invalid_inputs(self, invalid_credentials):
    """测试使用无效数据类型、超长字符串、空值、攻击字符串等异常输入进行登录，预期接口能妥善处理（如返回4xx状态码）而非抛出服务器错误（5xx）。"""
    # 实例化请求体模型，传入 hypothesis 生成的数据
    request_body = LoginForAccessTokenApiLoginTokenPostAPI.RequestBodyModel(
        username=invalid_credentials['username'],
        password=invalid_credentials['password']
    )

    # 发送请求
    api_instance = LoginForAccessTokenApiLoginTokenPostAPI(request_body=request_body)
    response = api_instance.send()

    # 断言：对于这类明显的无效输入，接口通常应返回 4xx 状态码，而不应是 5xx 或 2xx
    assert 400 <= response.status_code < 500, f"Unexpected status code for invalid input {invalid_credentials}. Status: {response.status_code}"

@given(
    st.fixed_dictionaries({
        # 生成有效的用户名格式，例如邮箱
        "username": st.emails(),
        # 生成有效的密码格式（假设密码需要至少1位，并不含控制字符）
        "password": st.text(
            alphabet=st.characters(blacklist_categories=('Cc', 'Cs')),  # 排除控制字符
            min_size=1,
            max_size=20
        )
    })
)
def test_login_with_valid_format_but_wrong_credential(self, valid_format_credentials):
    """测试格式有效但凭证错误的登录请求，预期返回明确的错误信息（如401 Unauthorized）或特定的错误码。"""
    # 这里我们假设这些生成的随机有效格式账号并未在系统中注册
    request_body = LoginForAccessTokenApiLoginTokenPostAPI.RequestBodyModel(
        username=valid_format_credentials['username'],
        password=valid_format_credentials['password']
    )

    api_instance = LoginForAccessTokenApiLoginTokenPostAPI(request_body=request_body)
    response = api_instance.send()

    # 断言：应为未授权状态
    assert response.status_code == 401, f"Expected 401 for wrong credential, got {response.status_code} for {valid_format_credentials}"
    # 可以进一步断言响应体中包含错误信息
    # assert response.response_model.error_message == "Invalid credentials"  # 根据实际响应结构调整

# 如果需要测试登录成功的情况，通常需要一个已知有效的测试账号
# 注意：hypothesis 不太适合直接用于测试成功的流程，因为需要特定的已知值
# 但可以结合 hypothesis 生成密码的一部分，或者测试成功登录后的其他属性
@given(
    st.text(min_size=1, max_size=5).map(lambda s: f"test_password_{s}")  # 生成密码后缀，与已知有效用户名组合
)
def test_login_success_with_hypothesis_variation(self, password_suffix):
    """示例：结合已知有效用户名和hypothesis生成的密码变体进行测试。"""
    # 假设已知一个有效用户名 "test_user"
    valid_username = "test_user"
    # 但注意：这里生成的密码极大概率不是该用户的有效密码，所以预期是失败
    # 此示例主要用于演示如何组合已知值和生成值
    assume(password_suffix != "actual_valid_suffix")  # 假设排除真正的有效密码后缀

    request_body = LoginForAccessTokenApiLoginTokenPostAPI.RequestBodyModel(
        username=valid_username,
        password=password_suffix
    )

    api_instance = LoginForAccessTokenApiLoginTokenPostAPI(request_body=request_body)
    response = api_instance.send()
    # 预期失败
    assert response.status_code != 200, "Should not login successfully with random password variation"


# 一个更实际的、测试成功登录流程的用例（通常不使用hypothesis生成核心凭证）
def test_login_success_with_valid_credential():
    """使用固定的有效测试账号测试成功登录流程。"""
    # 从配置或环境变量中获取有效的测试账号
    valid_username = "valid_test_user"  # 建议从 aomaker 的 config 或 cache 中获取
    valid_password = "valid_test_password"  # 建议从 aomaker 的 config 或 cache 中获取

    request_body = LoginForAccessTokenApiLoginTokenPostAPI.RequestBodyModel(
        username=valid_username,
        password=valid_password
    )

    api_instance = LoginForAccessTokenApiLoginTokenPostAPI(request_body=request_body)
    response = api_instance.send()

    # 断言成功状态
    assert response.status_code == 200, f"Login failed with valid credential. Status: {response.status_code}"

    # 使用 aomaker 响应模型的优势：可以直接访问结构化数据
    assert response.response_model is not None
    assert hasattr(response.response_model, 'access_token')  # 检查返回的响应模型是否有 access_token 字段
    assert isinstance(response.response_model.access_token, str)  # 检查 access_token 是否是字符串类型
    assert len(response.response_model.access_token) > 0  # 检查 access_token 非空
    # 可以根据实际的 TokenResponseData 结构添加更多断言