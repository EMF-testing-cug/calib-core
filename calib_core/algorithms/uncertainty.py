"""符合 GUM 规范的测量不确定度评定引擎 (k=2)"""
from __future__ import annotations

import math


class UncertaintyEvaluator:
    @staticmethod
    def calc_type_a(repeated_readings: list[float]) -> float:
        """计算 A 类相对标准不确定度（基于贝塞尔公式）"""
        n = len(repeated_readings)
        if n < 2:
            return 0.0
        mean = sum(repeated_readings) / n
        if mean == 0:
            return 0.0
        variance = sum((x - mean) ** 2 for x in repeated_readings) / (n - 1)
        std_dev = math.sqrt(variance)
        return (std_dev / math.sqrt(n)) / mean

    @staticmethod
    def calc_combined_expanded_uncertainty(
        type_a_rel: float,
        b_components_rel: list[float],
        coverage_factor: float = 2.0,
    ) -> float:
        """
        合成各独立分量并计算扩展不确定度 U (k=2)
        :param type_a_rel: A 类相对标准分量
        :param b_components_rel: B 类相对标准分量列表 (如功率计证书、定向耦合器失配、场均匀性等)
        :param coverage_factor: 包含因子 k，默认 2 (对应约 95% 置信度)
        :return: 相对扩展不确定度 U (如 0.045 代表 4.5%)
        """
        sum_sq = type_a_rel**2
        for u_b in b_components_rel:
            sum_sq += u_b**2
        u_c_rel = math.sqrt(sum_sq)
        return round(coverage_factor * u_c_rel, 4)