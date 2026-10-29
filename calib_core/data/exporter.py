"""统一 CSV 数据报表生成器"""

from __future__ import annotations

import csv

from calib_core.data.models import CalibrationRecord

CSV_HEADERS = [
    "task_id",
    "system_type",
    "point_id",
    "timestamp",
    "freq_hz",
    "source_amp_dbm",
    "current_a",
    "angle_deg",
    "power_val_dbm",
    "dmm_volt_v",
    "ref_field_val",
    "ocr_raw_text",
    "eut_field_val",
    "eut_unit",
    "ocr_confidence",
    "frame_consistent",
    "std_field_val",
    "calib_factor",
    "expanded_uncert_k2",
    "status",
]


class DataExporter:
    @staticmethod
    def append_records_to_csv(file_path: str, records: list[CalibrationRecord]) -> None:
        """将测量记录追加写入 CSV 文件 (UTF-8 编码，带防乱码 BOM)"""
        import os

        file_exists = os.path.exists(file_path)

        with open(file_path, mode="a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            if not file_exists:
                writer.writeheader()  # 首行写入标准表头

            for r in records:
                row_dict = {
                    "task_id": r.task_id,
                    "system_type": r.system_type,
                    "point_id": r.point_id,
                    "timestamp": r.timestamp,
                    "freq_hz": r.freq_hz,
                    "source_amp_dbm": r.source_amp_dbm,
                    "current_a": r.current_a if r.current_a is not None else "",
                    "angle_deg": r.angle_deg if r.angle_deg is not None else "",
                    "power_val_dbm": r.power_val_dbm
                    if r.power_val_dbm is not None
                    else "",
                    "dmm_volt_v": r.dmm_volt_v if r.dmm_volt_v is not None else "",
                    "ref_field_val": r.ref_field_val
                    if r.ref_field_val is not None
                    else "",
                    "ocr_raw_text": r.ocr_raw_text,
                    "eut_field_val": r.eut_field_val,
                    "eut_unit": r.eut_unit,
                    "ocr_confidence": r.ocr_confidence,
                    "frame_consistent": r.frame_consistent,
                    "std_field_val": r.std_field_val,
                    "calib_factor": r.calib_factor,
                    "expanded_uncert_k2": r.expanded_uncert_k2,
                    "status": r.status,
                }
                writer.writerow(row_dict)
