from calib_core.algorithms.field_calc import FieldCalculator
from calib_core.algorithms.uncertainty import UncertaintyEvaluator


def test_magnetic_am_to_ut():
    # 验证工频磁场 10 A/m 换算约为 12.5664 uT
    assert FieldCalculator.magnetic_am_to_ut(10.0) == 12.5664


def test_tem_field_calculation():
    # 验证输入净功率 2W，阻抗 50欧，间距 0.5m 时的标准场强: sqrt(100)/0.5 = 20.0 V/m
    assert FieldCalculator.calculate_tem_field(power_watts=2.0, z0=50.0, plate_height_m=0.5) == 20.0


def test_uncertainty_calc():
    # 验证合成扩展不确定度 (k=2)
    # 相对分量: A类 0.01, B类 [0.02, 0.015] -> 合成约 0.0269 -> k=2 扩展约为 0.0539
    u_expanded = UncertaintyEvaluator.calc_combined_expanded_uncertainty(
        type_a_rel=0.01, b_components_rel=[0.02, 0.015], coverage_factor=2.0
    )
    assert u_expanded == 0.0539