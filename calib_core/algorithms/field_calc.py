"""电磁场物理量计算与单位转换算法库"""

import math


class FieldCalculator:
    @staticmethod
    def calculate_tem_field(
        power_watts: float, z0: float = 50.0, plate_height_m: float = 0.5
    ) -> float:
        """
        TEM 室标准场强推算: E = sqrt(P * Z0) / d[cite: 5, 6]
        :param power_watts: 注入 TEM 室的净功率 (W)
        :param z0: 特性阻抗，通常为 50 欧姆
        :param plate_height_m: 芯板距底板高度 d (m)
        :return: 空间中心标准场强 (V/m)
        """
        if plate_height_m <= 0 or power_watts < 0:
            raise ValueError("功率不能为负且芯板间距必须大于 0")
        voltage = math.sqrt(power_watts * z0)
        return round(voltage / plate_height_m, 3)

    @staticmethod
    def calculate_chamber_field(
        net_power_w: float, antenna_gain_num: float, distance_m: float = 1.0
    ) -> float:
        """
        暗室天线辐射标准场强推算: E = sqrt(30 * P * G) / d
        :param net_power_w: 天线端口净输入功率 (W)
        :param antenna_gain_num: 喇叭天线增益（线性放大倍数，非dB）
        :param distance_m: 探头中心距天线口面距离（规范定为 1.0 m）
        """
        if distance_m <= 0 or net_power_w < 0:
            raise ValueError("间距必须大于0且功率不可为负")
        return round(math.sqrt(30.0 * net_power_w * antenna_gain_num) / distance_m, 3)

    @staticmethod
    def magnetic_am_to_ut(h_field_am: float) -> float:
        """
        工频磁场强度 A/m 换算为磁感应强度 uT: B = u0 * H
        u0 约为 4 * pi * 10^-7 H/m = 1.2566 uT/(A/m)
        """
        if h_field_am < 0:
            raise ValueError("磁场强度输入不能为负数")
        return round(h_field_am * 1.256637, 4)
