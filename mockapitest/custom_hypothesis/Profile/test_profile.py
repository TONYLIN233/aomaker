from hypothesis import settings, given, HealthCheck
import hypothesis.strategies as st

# 定义可重用的配置
QUICK = settings(max_examples=20, deadline=1000)
STANDARD = settings(max_examples=50, deadline=5000)
COMPREHENSIVE = settings(max_examples=100, deadline=10000, suppress_health_check=list(HealthCheck))
