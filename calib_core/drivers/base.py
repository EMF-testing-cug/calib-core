"""仪器驱动通用基类，规范统一的通信生命周期与仿真行为"""

import logging
from abc import ABC, abstractmethod


class BaseInstrument(ABC):
    def __init__(
        self, resource_name: str, timeout_ms: int = 3000, mock_mode: bool = False
    ):
        """
        :param resource_name: VISA 资源名称或串口号 (如 'TCPIP0::192.168.1.100::inst0::INSTR' 或 'COM3')
        :param timeout_ms: 通信超时时间 (毫秒)
        :param mock_mode: 是否启用离线纯软件仿真模式
        """
        self.resource_name = resource_name
        self.timeout_ms = timeout_ms
        self.mock_mode = mock_mode
        self.is_connected = False
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def connect(self) -> bool:
        """建立连接并执行状态自检"""
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """查询设备在线状态与自检错误码"""
        raise NotImplementedError

    @abstractmethod
    def safe_stop(self) -> None:
        """异常发生时的紧急安全收尾动作（如关闭射频输出、停止电机）"""
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """安全释放底层通信资源"""
        raise NotImplementedError
