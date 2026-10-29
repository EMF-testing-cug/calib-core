"""统一数据模型与测量记录定义"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CalibrationRecord:
    """单点测量记录数据模型，严格对应方案统一数据字段规范"""

    # 任务与点位标识
    task_id: str
    system_type: str  # 如: TEM, GTEM, CHAMBER, MAGNETIC
    point_id: str
    step_name: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # 设定参数
    freq_hz: float = 0.0  # 激励频率 (Hz)
    source_amp_dbm: float = 0.0  # 信号源幅值 (dBm)
    current_a: float | None = None  # 恒流源设定值 (A)
    angle_deg: float | None = None  # 转台当前角度 (度)

    # 仪器实测数据
    power_val_dbm: float | None = None  # 功率计实测功率 (dBm)
    dmm_volt_v: float | None = None  # 六位半电压表交流电压 (V)
    ref_field_val: float | None = None  # 参考场强计读数

    # OCR 采集数据
    ocr_raw_text: str = ""  # OCR 原始识别文本
    eut_field_val: float = 0.0  # 解析出的被检场强仪示值
    eut_unit: str = "V/m"  # 示值单位: V/m, A/m, uT 等
    ocr_confidence: float = 0.0  # 识别置信度
    frame_consistent: bool = True  # 是否通过三帧一致性校验

    # 计量计算结果
    std_field_val: float = 0.0  # 依据模型反算的标准场强/磁场
    calib_factor: float = 0.0  # 校准因子/示值误差
    expanded_uncert_k2: float = 0.0  # 扩展不确定度 (k=2)
    status: str = "SUCCESS"  # SUCCESS, FAILED, TIMEOUT 等
