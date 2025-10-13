"""
Hypothesis测试夹具
"""
import pytest
from hypothesis import settings, HealthCheck

# 测试配置预设
@pytest.fixture(scope="session")
def hypothesis_test_config():
    """返回Hypothesis测试配置"""
    return {
        'quick': {'max_examples': 20, 'deadline': 1000},
        'standard': {'max_examples': 50, 'deadline': 5000},
        'comprehensive': {'max_examples': 100, 'deadline': 10000}
    }

@pytest.fixture
def quick_test(request):
    """快速测试配置"""
    marker = request.node.get_closest_marker("hypothesis_settings")
    if marker and 'quick' in marker.kwargs:
        return settings(max_examples=20, deadline=1000,
                       suppress_health_check=[HealthCheck.too_slow])
    return settings(max_examples=20, deadline=1000)

@pytest.fixture
def standard_test(request):
    """标准测试配置"""
    return settings(max_examples=50, deadline=5000)

@pytest.fixture
def comprehensive_test(request):
    """全面测试配置"""
    return settings(max_examples=100, deadline=10000)