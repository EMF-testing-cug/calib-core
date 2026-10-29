"""Keysight N5171B 信号发生器驱动实现 (9kHz~1GHz)"""

from calib_core.drivers.base import BaseInstrument


class SignalGeneratorN5171B(BaseInstrument):
    def __init__(
        self, resource_name: str, timeout_ms: int = 3000, mock_mode: bool = False
    ):
        super().__init__(resource_name, timeout_ms, mock_mode)
        self.current_freq_hz: float = 1e6
        self.current_amp_dbm: float = -10.0
        self.output_enabled: bool = False
        self._visa_session = None

    def connect(self) -> bool:
        if self.mock_mode:
            self.logger.info(f"[MOCK] 信号发生器仿真连接成功: {self.resource_name}")
            self.is_connected = True
            return True
        try:
            import pyvisa

            rm = pyvisa.ResourceManager()
            self._visa_session = rm.open_resource(self.resource_name)
            self._visa_session.timeout = self.timeout_ms
            # 查询身份验证
            idn = self._visa_session.query("*IDN?")
            self.logger.info(f"成功连接设备: {idn.strip()}")
            self.is_connected = True
            return True
        except Exception as e:# noqa: BLE001
            self.logger.error(f"连接信号发生器失败: {e}")
            self.is_connected = False
            return False

    def set_frequency(self, freq_hz: float) -> None:
        """设置输出频率 (Hz)，指标范围 9kHz ~ 1GHz[cite: 1, 5]"""
        if not (9e3 <= freq_hz <= 1e9):
            raise ValueError(f"频率超出支持范围 (9kHz~1GHz): {freq_hz} Hz[cite: 1]")
        self.current_freq_hz = freq_hz
        if self.mock_mode:
            self.logger.debug(f"[MOCK] 设置频率: {freq_hz} Hz")
            return
        self._visa_session.write(f":FREQ {freq_hz} Hz")

    def set_amplitude(self, power_dbm: float) -> None:
        """设置输出幅值功率 (dBm)，范围 -100dBm ~ +13dBm[cite: 1, 5]"""
        if not (-100.0 <= power_dbm <= 13.0):
            raise ValueError(
                f"幅值超出指标范围 (-100~+13 dBm): {power_dbm} dBm[cite: 1]"
            )
        self.current_amp_dbm = power_dbm
        if self.mock_mode:
            self.logger.debug(f"[MOCK] 设置幅值: {power_dbm} dBm")
            return
        self._visa_session.write(f":POW {power_dbm} dBm")

    def set_output(self, enable: bool) -> None:
        """开启或切断射频输出"""
        self.output_enabled = enable
        if self.mock_mode:
            self.logger.info(f"[MOCK] 射频输出状态切换为: {'ON' if enable else 'OFF'}")
            return
        cmd = ":OUTP ON" if enable else ":OUTP OFF"
        self._visa_session.write(cmd)

    def safe_stop(self) -> None:
        """安全保护：切断信号输出"""
        try:
            self.set_output(False)
        except Exception as e:# noqa: BLE001
            self.logger.critical(f"执行安全停机切断输出失败: {e}")

    def health_check(self) -> bool:
        if self.mock_mode:
            return True
        try:
            err = self._visa_session.query(":SYST:ERR?")
            return "No error" in err
        except Exception:# noqa: BLE001
            return False

    def close(self) -> None:
        self.safe_stop()
        if self._visa_session and not self.mock_mode:
            self._visa_session.close()
        self.is_connected = False
