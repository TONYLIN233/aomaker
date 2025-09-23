from hypothesis import given, strategies as st
import pytest

# 将常用的无效数据策略定义为常量，方便复用和管理
#无效的数据类型
_INVALID_TYPES = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(),
    st.lists(st.text())
)

#无效的字符串长度
_INVALID_LENGTHS = st.one_of(
    st.text(min_size=1000, max_size=2000),  # 超长字符串
    st.just(""),  # 空字符串
    st.text(alphabet=' ', min_size=1, max_size=5)  # 纯空格字符串
)

#异常注入
_SECURITY_INJECTION_PAYLOADS = st.sampled_from([
    "' OR '1'='1' --",
    "<script>alert('xss')</script>",
    "../../etc/passwd"
])

