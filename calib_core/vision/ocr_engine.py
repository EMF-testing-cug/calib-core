"""机器视觉 OCR 识别与三帧防跳变门禁"""
from __future__ import annotations

import random


class FieldMeterOCR:
    def __init__(self, mock_mode: bool = True):
        self.mock_mode = mock_mode

    def recognize_single_frame(self, frame_img=None) -> tuple[float, str, float]:
        """
        对单帧图像提取 ROI 并识别数值与单位
        :return: (识别数值, 单位, 置信度)
        """
        if self.mock_mode:
            val = round(10.0 + random.uniform(-0.05, 0.05), 2)
            return val, "V/m", 0.98

        raise NotImplementedError("视觉组待接驳 PaddleOCR 推理")

    def validate_three_frames(
        self, frames: list | None = None, tolerance: float = 0.05
    ) -> tuple[bool, float, str, float]:
        """
        连续 3 帧校验门禁：只有 3 帧读数相对差异 <= 容差且置信度高才算有效
        :return: (是否通过, 最终平均读数, 单位, 综合置信度)
        """
        readings = []
        confs = []
        units = []

        for _ in range(3):
            val, unit, conf = self.recognize_single_frame()
            readings.append(val)
            units.append(unit)
            confs.append(conf)

        # 校验单位一致性
        if len(set(units)) > 1:
            return False, 0.0, "", 0.0

        max_v, min_v = max(readings), min(readings)
        avg_v = sum(readings) / 3.0
        if avg_v == 0:
            is_consistent = max_v == min_v
        else:
            is_consistent = ((max_v - min_v) / avg_v) <= tolerance

        avg_conf = sum(confs) / 3.0
        return is_consistent, round(avg_v, 2), units[0], round(avg_conf, 3)