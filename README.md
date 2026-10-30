# calib-core
公共底座库：仪器驱动、OCR、算法、数据模型

难点：GPIB的驱动（只有一个设备是）

上层的 4 套独立业务软件（TEM 室、µTEM/GTEM 室、暗室、工频磁场）全部强依赖于我们的封装并输出的 API。

公共底座库工作内容划分为 **5 大核心模块、22 项具体子任务与工程交付物**：

<details>
<summary><b>完成进度</b></summary>

[ ] 01. Keysight N5171B-501 高频信号发生器  
协议：LAN / USBTMC / GPIB (SCPI)  
封装类：SignalGeneratorN5171B
核心接口：connect(), set_frequency(), set_amplitude(), output_on(), output_off(), get_rf_status()

[ ] 02. Keysight N5173B-520 微波信号发生器   
协议：LAN / USBTMC / GPIB (SCPI)   
封装类：SignalGeneratorN5173B
核心接口：connect(), set_frequency(), set_amplitude(), output_on(), output_off(), get_rf_status()

[ ] 03. RIGOL DG811 低频信号发生器   
协议：USBTMC / LAN (Raw Socket)   
封装类：SignalGeneratorDG811
核心接口：connect(), set_frequency(), set_voltage_vpp(), output_on(), output_off()

[ ] 04. Keysight N1914A 双通道功率计   
协议：LAN / USBTMC / GPIB (SCPI)   
封装类：PowerMeterN1914A
核心接口：connect(), zero_cal(), set_frequency(), set_range(), read_power(), wait_stable()

[ ] 05. QF2281A 高频毫伏计   
协议：GPIB / RS-232   
封装类：MillivoltmeterQF2281A
核心接口：connect(), set_range(), read_voltage(), get_unit(), wait_stable()

[ ] 06. Keysight 34461A 6位半数字多用表   
协议：LAN / USBTMC / GPIB (SCPI)   
封装类：DMM34461A核心接口：connect(), set_ac_voltage_mode(), set_ac_current_mode(), read_voltage(), read_current()

[ ] 07. 10020 可编程交流恒流电流源 (0~20A)   
协议：RS-232 / RS-485 (Modbus RTU)   
封装类：CurrentSource10020
核心接口：connect(), set_current(), set_frequency(), output_on(), output_off(), read_output_current()

[ ] 08. CL10R2-100W / CL100R1-100W 高频功放   
协议：RS-232 / 远程电平接口   
封装类：RFPowerAmplifierHF
核心接口：connect(), enable_rf(), disable_rf(), get_interlock_status(), read_forward_power()

[ ] 09. CL1GR4-200W / CL4GR18-100W 微波射频功放   
协议：RS-232 / LAN   封装类：RFPowerAmplifierMW
核心接口：connect(), select_band(), enable_rf(), disable_rf(), safe_shutdown()

[ ] 10. CL002R3-100W 低频功放   协议：RS-232 / 模拟电平   
封装类：LFPowerAmplifier
核心接口：connect(), set_gain(), enable_output(), disable_output()

[ ] 11. SP1T-8T 同轴射频微波开关   
协议：RS-232 / USB-VCP   
封装类：CoaxialSwitchSP1T8T
核心接口：connect(), switch_channel(), get_current_channel(), reset()

[ ] 12. FC1-XZ-XZ01 自动旋转装置   
协议：RS-232 / RS-485 (Modbus RTU)   
封装类：RotationStageFC1
核心接口：connect(), home(), move_to_angle(), step_angle(), wait_in_position(), stop()

[ ] 13. FCI-XZZJ-002 自动对准支架 (水平/上下/旋转)   
协议：RS-232 / RS-485 (Modbus RTU)   
封装类：PositionerFCI002
核心接口：connect(), home_all(), move_x(), move_z(), rotate_to(), align_1m_axis(), emergency_stop()

[ ] 14. 监控装置 / 工业相机 (FCI-SZXJ/SZSX 系列)   
协议：USB (UVC) / RTSP 以太网视频流   
封装类：VisionCaptureDevice
核心接口：open_camera(), capture_frame(), set_exposure(), set_roi(), release()

[ ] 15. Narda FieldMan 参考场强仪   
协议：USB-SDK / RS-232   
封装类：FieldManMeter
核心接口：connect(), read_field(), read_axes_components(), get_probe_info()

[ ] 16. FCT-SP0110 / Narda EHP-50F 传递标准与低频场强仪   
协议：USB-SDK / 光纤串口   
封装类：TransferStandardMeter
核心接口：connect(), read_field(), set_frequency(), read_raw_data()

[ ] 17. Mock 虚拟设备仿真驱动套件   
协议：Loopback 
内存总线封装类：MockDeviceSuite
核心接口：仿真对应设备的所有控制方法、时延模拟及异常注入

</details>

---

### 一、统一仪器驱动库开发（硬件适配层）

根据设备清单中的通信接口（GPIB / LAN / USB / RS232 / Modbus），定义统一驱动基类 `BaseDriver`（实现 `initialize`、`connect`、`health_check`、`close`、`reset`、`get_status` 等统一生命周期接口），输出结构化测量对象 `MeasurementResult(device_id, value, unit, timestamp, status, raw_response, error_code)`，并针对全量设备开发独立适配器：

<details>
<summary><b>GPIB</b></summary>

GPIB（General Purpose Interface Bus，通用接口总线）是由惠普公司（HP）在 20 世纪 60 年代末研制（原称 HP-IB），后被正式标准化为 **IEEE-488** 的一种并行数字通信总线，至今仍广泛应用于电子测量仪器、自动化测试系统（ATE）与实验室仪器控制领域。

---

## 一、物理特性与电气规格

GPIB 采用 24 芯双排屏蔽接插件（微型带状 Amphenol/Centronics 接口），支持背靠背（Piggyback）级联堆叠。

| 规格项 | 参数指标 / 规范 | 说明 |
| --- | --- | --- |
| **标准代号** | IEEE-488.1（物理/电气）、IEEE-488.2（协议/数据格式） | 配合 SCPI 命令集使用 |
| **传输模式** | 8 位字节并行、异步半双工 | 低电平有效（TTL 负逻辑） |
| **最大设备容量** | 15 个设备（含 1 个主控制器） | 逻辑主地址范围：0 ～ 30 |
| **标准传输速率** | 典型 250 kB/s ～ 1 MB/s | IEEE-488.1 标准速率 |
| **高速扩展（HS488）** | 最高 8 MB/s | 需所有总线节点均支持 HS488 |
| **单网段线缆限制** | 总长 $\le 20\text{ m}$，且平均每台设备 $\le 2\text{ m}$ | 超过时需使用 GPIB 中继器或光纤扩展器 |
| **网络拓扑** | 菊花链式（线性）或星型 | 可混合连接，接头支持上下串叠 |

---

## 二、总线引脚与信号线定义

24 根引脚中包含 **16 根有效信号线**与 **8 根接地/屏蔽线**。16 根信号线按功能划分为三大类：

### 1. 数据总线（8 根）

* **DIO1 ～ DIO8**（Data Input/Output 1~8）：传输双向数据、仪器控制命令及主/次地址。采用负逻辑（低电平为逻辑 `1`，高电平为逻辑 `0`）。

### 2. 数据传送控制线 / 握手线（3 根）

GPIB 采用严格的**异步三线互锁握手机制**，确保总线上速度最慢的设备完成数据接收后才发送下一字节：

* **DAV**（Data Valid，数据有效）：由讲者（Talker）控制。低电平时表示 DIO 总线上的数据稳定有效。
* **NRFD**（Not Ready For Data，未准备好接收数据）：由听者（Listener）控制。低电平时表示存在听者未准备好接收新数据；全总线听者均变为高阻态（总线上拉为高电平）后，表示全部就绪。
* **NDAC**（Not Data Accepted，未接受数据）：由听者（Listener）控制。低电平时表示尚有听者未完成数据读取；当所有听者均读取完成释放该线（变为高电平），讲者方可撤销 DAV。

### 3. 通用总线管理线（5 根）

* **ATN**（Attention，注意）：由控制器（Controller）驱动。
* `ATN = 0`（低电平/有效）：总线处于**命令模式**，DIO 上传输的是总线命令或寻址地址（如 Talker/Listener 指定）。
* `ATN = 1`（高电平/无效）：总线处于**数据模式**，DIO 上传输的是仪器测量数据或配置字符串。


* **IFC**（Interface Clear，接口清零）：由系统控制器驱动，强制复位总线接口逻辑（使所有设备退出 Talker/Listener 状态）。
* **REN**（Remote Enable，远程使能）：使能仪器面板锁定与远程程控状态。
* **SRQ**（Service Request，服务请求）：由设备发起的总线中断请求，通知控制器发生异常、测量完成或缓冲区溢出。
* **EOI**（End Or Identify，结束或识别）：在数据模式下由讲者置低表示当前字节为多字节消息的“最后一个字节”；在命令模式下与 ATN 配合执行并行轮询（Parallel Poll）。

---

## 三、总线设备角色划分

GPIB 网络中的设备具有三种逻辑角色（单台物理仪器可根据状态动态切换）：

1. **控制器（Controller）**
* 管理总线通信秩序，负责分配哪些设备作为讲者、哪些设备作为听者。
* 系统中允许存在多个控制器，但在同一时刻只能有 1 个**活动控制器（Controller-in-Charge, CIC）**。系统通常由装有 GPIB 板卡（如 PCIe-GPIB、USB-GPIB 适配器）的工控机充当系统控制器（System Controller）。


2. **讲者（Talker）**
* 向数据总线发送数据的设备（如数字万用表返回读数、功率计返回测量功率）。
* 同一时刻总线上**只能有且仅有 1 个**处于活动状态的讲者。


3. **听者（Listener）**
* 从数据总线接收控制指令、参数或数据的设备（如信号发生器设置频点/幅值）。
* 同一时刻总线上**可以同时存在多个**听者。



---

## 四、软件栈与程控实现（VISA + SCPI）

现代工业控制与测量软件极少直接操作底层寄存器，均基于 IVI 基金会定义的 **VISA（Virtual Instrument Software Architecture）** 标准驱动库访问 GPIB。

### 1. 资源描述符规则

GPIB 设备在 VISA 中的标准寻址格式为：


$$\text{GPIB}[board]::primary\_address[::secondary\_address]::\text{INSTR}$$

* `GPIB0::18::INSTR`：表示板卡号为 0、主地址为 18 的通用仪器。
* `GPIB0::1::2::INSTR`：带次地址 2 的设备。

### 2. Python (PyVISA) 核心调用示例

```python
import pyvisa

# 1. 创建 VISA 资源管理器
rm = pyvisa.ResourceManager()

# 2. 扫描总线上的所有有效设备
devices = rm.list_resources("GPIB?*::INSTR")
print(f"Discovered GPIB Devices: {devices}")

# 3. 连接目标仪器（以地址 18 的信号源为例）
inst = rm.open_resource("GPIB0::18::INSTR")

# 配置通信超时（单位 ms）与终止符
inst.timeout = 5000
inst.write_termination = "\n"
inst.read_termination = "\n"

# 4. 发送 IEEE-488.2 / SCPI 标准命令并读取响应
idn_response = inst.query("*IDN?")
print(f"Device Identification: {idn_response}")

# 设置参数与输出控制
inst.write("FREQ 1.0GHz")
inst.write("POW:AMPL -10dBm")
inst.write("OUTP ON")

# 5. 安全释放总线连接
inst.close()
rm.close()

```

---

## 五、工程调试与现场排查要点

* **主地址（Primary Address）冲突**
* 每台连接在同一条 GPIB 链条上的设备，其主地址（0～30）必须唯一。两台设备地址重复会导致三线握手冲突，出现全总线挂死或数据乱码。


* **电缆物理长度约束（2 米法则）**
* 物理总长度不得超过 20 米，且必须满足 $\text{总长} \le 2\text{ m} \times \text{在线设备数}$。若总线上仅接 2 台仪器却使用了 10 米长的长电缆，信号反射与分布电容易导致高频边沿退化，引发超时或丢字节。


* **设备上电比例**
* 总线网络中至少应有 **2/3 以上的设备保持上电状态**。断电设备内部未加电的总线终端网络会造成信号线阻抗严重失配，下拉总线电平。


* **结束符识别（EOI 与 EOS）**
* GPIB 既支持硬件信号线 `EOI` 标识帧结束，也支持软件 ASCII 字符（如 `\n` 即 LF，`0x0A`）作为终止符（EOS）。配置仪器时需保证上位机读写终止符与仪器菜单内的设定一致，否则会频繁触发 `VI_ERROR_TMO`（操作超时）。

</details>

---

<details>
<summary><b>LAN</b></summary>

LAN（以太网/局域网）在现代电子测量与自动化测试系统（ATE）中已成为替代传统 GPIB 的主流总线技术。基于以太网构建的测试系统具备传输速率高、布线成本低、支持远距离分布式测量（如暗室、屏蔽室与远端监控室隔离控制）等优势，并在 **LXI（LAN eXtensions for Instrumentation）** 标准下实现了对传统 GPIB 仪器特性的兼容与扩展。

---

## 一、物理与网络层规格

| 规格项 | 参数指标 / 规范 | 说明 |
| --- | --- | --- |
| **物理接口** | RJ45 屏蔽双绞线接口（8P8C） / M12 工业接头 | 支持超五类（Cat 5e）或六类（Cat 6）屏蔽线缆（STP） |
| **电气标准** | IEEE 802.3（10BASE-T / 100BASE-TX / 1000BASE-T） | 现代仪表标配百兆或千兆自适应网口 |
| **单段最大传输距离** | $\le 100\text{ m}$（点对点双绞线） | 超出可通过以太网交换机级联，或通过光纤收发器延长至数公里 |
| **网络拓扑** | 星型拓扑（经交换机/路由器汇聚） | 支持点对点直连（需 Auto-MDIX 或交叉网线） |
| **IP 分配机制** | 静态 IP（Static IP）/ 动态 DHCP / Link-Local (Auto-IP) | 自动化控制系统中**强烈推荐静态 IP** |
| **仪器行业规范** | **LXI 核心标准（LXI Device Specification）** | 由 LXI 联盟定义，统一 Web 服务、发现机制与时间同步 |

---

## 二、仪器 LAN 通信协议类型（VXI-11 / HiSLIP / Raw Socket）

在底层 TCP/IP 协议栈之上，仪器 LAN 控制通常分为以下三种应用层协议：

### 1. VXI-11 协议

* **机制**：基于 ONC/RPC（开放网络计算远程过程调用）与 Sun RPC 规范开发，由 VXIbus 联盟推出。
* **特点**：在软件行为上**完全仿真 GPIB**，完整复刻了 GPIB 的主听/主讲、串行轮询（Serial Poll）、服务请求（SRQ）以及总线清除（Device Clear）等核心机制。
* **优缺点**：兼容性极佳，传统 VISA 程序几乎零代码修改即可迁移；但由于多次 RPC 往返与端口映射器（Portmapper）查询，网络开销大，延迟相对较高。

### 2. HiSLIP 协议（High-Speed LAN Instrument Protocol）

* **机制**：由 IVI 基金会制定的现代以太网仪器通信标准（IVI-6.1），采用轻量级定制帧封装于原生 TCP/IP 之上。
* **特点**：使用两条 TCP 连接（一条“同步信道”用于传输命令与数据，一条“异步信道”用于传递打断、排队锁与 SRQ 状态）。
* **优缺点**：继承了 VXI-11 的完整仪器控制特性（包含设备锁定、SRQ 中断、硬打断），同时消除了 RPC 带来的传输瓶颈，吞吐量和延迟接近底层 Socket，是 Keysight/R&S 等主流厂商推荐的现代连接方式。

### 3. Raw Socket（原始套接字）

* **机制**：直接与仪器的特定 TCP 监听端口（行业常用标准为 **端口 5025**）建立长连接，直接通过原始 ASCII 字节流收发 SCPI 命令。
* **特点**：协议栈极其轻量，几乎没有额外协议头部开销，单次命令往返速度最快。
* **局限**：缺少仪器级控制状态（不支持 SRQ 硬件打断、无法由底层自动执行 Device Clear），且**必须严格依赖换行符（如 `\n`）作为消息边界**。

---

## 三、LXI 标准与高级扩展功能

现代以太网仪器大多具备 LXI 认证，其核心能力包括：

* **内嵌 Web 诊断与控制（LXI Web Interface）**：通过浏览器直接访问仪器 IP 地址，即可查看仪器序列号、固件版本、配置网络参数，甚至进行虚拟面板交互操作。
* **网络广播发现（mDNS / VXI-11 Discovery）**：支持网络内零配置自动查找仪器（如 VISA `list_resources` 能自动广播发现局域网内的在线设备）。
* **IEEE 1588 PTP 精确时钟同步（LXI Class B / 扩展功能）**：允许局域网内多台仪器通过纳秒级硬件时间戳对齐时钟，实现无需硬触发电缆的多通道纳秒级同步采集。
* **LAN 事件触发（LXI Event Messaging）**：仪器之间可通过网络组播报文（LAN Packet）互相发送触发信号，替代物理 BNC 触发线。

---

## 四、软件栈与 VISA 地址描述符规范

### 1. VISA 资源描述符规则

| 连接方式 | VISA 资源字符串格式 | 示例 |
| --- | --- | --- |
| **VXI-11** | `TCPIP[board]::host_address[::LAN_device_name]::INSTR` | `TCPIP0::192.168.1.100::inst0::INSTR` |
| **HiSLIP** | `TCPIP[board]::host_address::hislip[index]::INSTR` | `TCPIP0::192.168.1.100::hislip0::INSTR` |
| **Raw Socket** | `TCPIP[board]::host_address::port::SOCKET` | `TCPIP0::192.168.1.100::5025::SOCKET` |

### 2. Python (PyVISA) 核心调用示例

```python
import pyvisa

rm = pyvisa.ResourceManager()

# 示例 1: 使用 HiSLIP / VXI-11 方式连接 (推荐，资源类型为 INSTR)
instr = rm.open_resource("TCPIP0::192.168.1.100::hislip0::INSTR")
instr.timeout = 5000  # 毫秒
instr.write_termination = "\n"
instr.read_termination = "\n"

# 查询设备身份
print("Device IDN:", instr.query("*IDN?"))

# 发送控制指令
instr.write("FREQ 1.0GHz")
instr.write("POW:AMPL -10dBm")
instr.write("OUTP ON")
instr.close()

# ----------------------------------------------------------------------

# 示例 2: 使用 Raw Socket 方式连接 (资源类型为 SOCKET，必须显式指定读写终止符)
sock_instr = rm.open_resource("TCPIP0::192.168.1.101::5025::SOCKET")
sock_instr.timeout = 5000
# SOCKET 模式必须严格设置终止符，否则 query/read 会持续阻塞直至超时
sock_instr.write_termination = "\n"
sock_instr.read_termination = "\n"

response = sock_instr.query("*IDN?")
print("Socket Device IDN:", response)
sock_instr.close()

rm.close()

```

---

## 五、工程调试与现场排查要点

* **IP 地址规划与固定**
* 严禁在正式校准测试系统中使用动态 DHCP 自动分配 IP。路由器重新分配租约会导致上位机无法根据固定描述符寻址仪器。调试前应规划统一子网，将所有测试仪器配置为连续的静态私网地址（如 `192.168.1.101 ~ 192.168.1.120`，掩码 `255.255.255.0`）。


* **防火墙与专用端口屏蔽**
* 上位机工控机的 Windows 防火墙经常拦截仪器网络发现与通信端口。需确保在专用网络中放行：
* **Port 111 (TCP/UDP)**：Sun RPC 端口映射器（VXI-11 依赖）；
* **Port 5025 (TCP)**：SCPI Raw Socket 常用通信端口；
* **Port 4880 (TCP)**：HiSLIP 握手与通信端口；
* **Port 5353 (UDP)**：mDNS 局域网设备自发现。




* **TCP 半开连接（Half-Open）死锁**
* 当上位机控制软件意外崩溃、强行终止或网线意外瞬断时，仪器端可能仍认为上一个 TCP 连接未断开，拒绝上位机重新发起的连接请求（提示被占用或连接被重置）。现场排查时若出现频繁连接被拒，需重启仪器网络服务或重启仪器释放套接字。


* **SOCKET 模式下的终止符遗漏**
* 在 VXI-11 / HiSLIP 模式下，底层协议具备帧结束标志位（END 位）；但在 Raw Socket 模式下，底层仅按纯字符流传输，若上位机未配置 `write_termination = '\n'`，仪器收不到换行符将一直等待命令输入；上位机未配置 `read_termination = '\n'`，读取时将一直等待结束符直至抛出 `VI_ERROR_TMO` 超时异常。

</details>

---

<details>
<summary><b>USB</b></summary>

USB（Universal Serial Bus，通用串行总线）因其即插即用、高传输带宽和普及度极高的优势，在台式仪器、便携式仪表及模块化测试设备中得到了全面应用。为了解决 USB 在仪器控制领域替代 GPIB 的标准化问题，USB-IF 与 IVI 基金会联合制定了 **USBTMC（USB Test & Measurement Class）** 规范，使 USB 具备了完全媲美 GPIB 的仪器状态管理与异步中断能力。

---

## 一、物理特性与电气规格

台式仪器的程控接口多采用物理稳固性更强的 **USB Type-B（方口）** 或现代 **USB Type-C** 接口，工控机端通常采用标准的 Type-A / Type-C 接口。

| 规格项 | 参数指标 / 规范 | 说明 |
| --- | --- | --- |
| **标准协议** | USB 2.0（High-Speed） / USB 3.0+（SuperSpeed） | 绝大多数测试仪器标配 USB 2.0（480 Mbps） |
| **拓扑结构** | 树状分层星型拓扑（通过 USB Hub 扩展） | 最多支持 5 层 Hub 级联，单总线理论上限 127 个设备 |
| **电气特性** | 差分半双工（D+ / D-，USB 2.0）；全双工差分对（USB 3.0+） | 典型信号摆幅约 400 mV（高速模式） |
| **供电特性** | 5V VBUS 供电 | 台式仪器多为**自供电（Self-Powered）**；便携式探头多为**总线供电（Bus-Powered）** |
| **线缆长度限制** | 单段无源线缆 $\le 3\text{ m} \sim 5\text{ m}$ | 超过时必须使用工业级带供电的 USB 有源延长线或光纤扩展器 |
| **行业测试标准** | **USBTMC 规范** 与 **USB488 子类规范** | 由 USB-IF 制定，与 IVI-VISA 和 SCPI 规范无缝契合 |

---

## 二、仪器 USB 通信协议分类

在上位机与设备交互时，USB 仪器主要分为以下三类通信架构：

### 1. USBTMC / USB488（标准仪器类）

* **定位**：专为测试测量设备制定的标准协议栈（如 Keysight、Rohde & Schwarz、RIGOL 等主流台式仪器标配）。
* **特点**：在 USB 协议层上完整复刻了 **IEEE-488（GPIB）** 的所有控制机制（包括设备清除、触发、服务请求 SRQ 等）。操作系统无需为不同厂商安装专用驱动，只要安装标准 VISA 运行库即可原生识别与控制。

### 2. USB-VCP / CDC-ACM（虚拟串口模式）

* **定位**：多见于低成本仪表、旋转台/升降台控制器、以及基于单片机（STM32 等）的传感器控制板。
* **特点**：通过 USB 转串口芯片（如 FTDI FT232、Silicon Labs CP210x、CH340）或单片机自带的 USB-CDC 固件，在工控机上虚拟出一个 `COM` 口。上位机使用标准串行协议（RS232 / Modbus RTU）进行读写交互。

### 3. Vendor-Specific / USB-RAW（厂商专属驱动 / 私有 SDK）

* **定位**：多见于高速工业相机、私有总线采集中继盒或专用场强计探头（如部分 Narda 探头）。
* **特点**：不遵循标准 USBTMC 类，采用厂商定制的私有驱动（基于 WinUSB、libusb 或专有内核驱动），上位机需调用厂商提供的动态链接库（DLL / C SDK）进行通信。

---

## 三、USBTMC / USB488 协议深度解析

USBTMC 在 USB 规范的端点（Endpoint）架构之上，规范了严格的数据传输与中断管道：

### 1. 端点配置架构

* **Control Endpoint 0（控制端点 0）**：负责设备枚举、获取描述符以及执行特定的 USBTMC 请求（如 `INITIATE_ABORT_BULK_OUT` 中止传输、`CHECK_STATUS` 等）。
* **Bulk-OUT Endpoint（大容量输出端点）**：上位机向仪器发送 SCPI 指令和配置数据包（数据被封装在 `MsgID = DEV_DEP_MSG_OUT` 的 12 字节头部包中）。
* **Bulk-IN Endpoint（大容量输入端点）**：上位机从仪器接收测量数据和响应字符串（数据封装在 `MsgID = DEV_DEP_MSG_IN` 中）。
* **Interrupt-IN Endpoint（中断输入端点，USB488 必需）**：仪器向控制器主动上报状态字节（STB），**完美模拟 GPIB 的 SRQ（服务请求）中断机制**。上位机无需在 Bulk 通道频繁轮询，仪器完成测量或发生错误时会自动触发中断包。

### 2. USB488 兼容特性

* **Device Clear（设备清除）**：上位机可在 Bulk 传输卡死或异常时，通过控制端点发送中断包，强行清空仪器的输入/输出缓冲区并复位解析器，而无需物理拔插 USB。
* **Trigger（总线触发）**：支持毫秒级低延迟的软件触发包（`TRIGGER` 请求），使仪器同步执行测量。

---

## 四、软件栈与 VISA 地址描述符规范

### 1. VISA 资源描述符规则

USBTMC 设备在 VISA 库中的寻址格式基于仪器的物理硬件属性（VID、PID、序列号）：

$$\text{USB}[board]::\text{VID}::\text{PID}::\text{SerialNumber}[::\text{InterfaceNumber}]::\text{INSTR}$$

| 参数 | 含义 | 示例 |
| --- | --- | --- |
| **board** | USB 控制器索引号 | 默认通常为 `0` |
| **VID** | 供应商 ID（Vendor ID，4 位十六进制，`0x` 开头） | `0x0957`（Agilent/Keysight）、`0x1AB1`（RIGOL） |
| **PID** | 产品 ID（Product ID，4 位十六进制） | `0x0607`（某型号信号源）、`0x0E11`（某型号功率计） |
| **SerialNumber** | 仪器出厂唯一硬件序列号 | `MY53001234` |
| **类型后缀** | 资源类别 | `INSTR`（标准 TMC 接口）或 `RAW`（裸数据接口） |

* 标准 USBTMC 描述符示例：`USB0::0x0957::0x0607::MY53001234::0::INSTR`
* 非 TMC 的直接裸端点通信示例：`USB0::0x1234::0x5678::SN001::RAW`

### 2. Python (PyVISA) 核心调用示例

```python
import pyvisa

rm = pyvisa.ResourceManager()

# 1. 扫描当前连接的所有 USBTMC 设备
usb_devices = rm.list_resources("USB?*::INSTR")
print(f"Discovered USB Instruments: {usb_devices}")

# 2. 连接目标仪器 (以 Keysight N5171B 为例)
# 也可直接使用搜索到的第一个资源: rm.open_resource(usb_devices[0])
inst = rm.open_resource("USB0::0x0957::0x0607::MY53001234::0::INSTR")

# 配置通信超时（单位 ms）与终止符
inst.timeout = 5000
inst.write_termination = "\n"
inst.read_termination = "\n"

# 3. 发送标准 SCPI 指令
print("Device IDN:", inst.query("*IDN?"))

# 设置射频信号源参数
inst.write("FREQ 1.0GHz")
inst.write("POW:AMPL -10dBm")
inst.write("OUTP ON")

# 4. 执行设备清除 (Device Clear，相当于 GPIB 的 Selected Device Clear)
inst.clear()

# 5. 安全释放连接
inst.close()
rm.close()

```

---

## 五、工程调试与现场排查要点

* **现场电磁干扰（EMI）导致 USB 断连（“掉盘”）**
* 在射频暗室、高频功率放大器（如 100W/200W 功放）或高场强校准环境中，空间的强电磁辐射极易耦合进普通 USB 线缆，引发 USB 控制器 CRC 校验错误、总线挂起或端口被系统禁用。
* **应对措施**：必须使用**双屏蔽工业级 USB 线缆（带高导磁率铁氧体磁环）**；若靠近功放或天线，推荐在上位机与设备之间接入**工业级 USB 光纤隔离器（USB Isolator）**，切断地线环路并阻隔射频串扰。


* **Windows 电源管理“选择性挂起”（Selective Suspend）**
* Windows 默认开启了 USB 电源节电策略。在数小时的长时间无人值守自动校准过程中，操作系统若检测到总线短暂停滞，可能会主动切断 USB 根集线器（Root Hub）供电，导致后续测量命令抛出 `VI_ERROR_RSRC_NFOUND` 或超时异常。
* **应对措施**：在工控机的设备管理器中，找到所有“通用串行总线控制器”下的“USB 根集线器”，在属性页的“电源管理”中**取消勾选“允许计算机关闭此设备以节约电源”**。


* **仪器序列号缺失或非唯一导致端口漂移**
* 部分定制设备或低成本仪器的固件在烧录时未配置唯一 SN，枚举时序列号为空或固定为 `000000`。当工控机接入多台同型号设备时，VISA 资源描述符将发生冲突，导致控制指令错乱发到另一台设备上。
* **排查建议**：接入前逐一通过测试工具核对序列号；若 SN 重复，必须配合硬件厂商烧录唯一 SN，或使用专用 USB 端口绑定工具。


* **VISA 驱动冲突与后端替换问题**
* 在安装过 Zadig、libusb-win32、Wireshark 或第三方开发驱动的机器上，USBTMC 设备的底层驱动可能会被篡改为通用 WinUSB，导致 NI-VISA 或 Keysight VISA 无法将其识别为 `::INSTR` 设备。
* **排查建议**：在 Windows 设备管理器中，确认设备所属类别为“Test and Measurement Devices”（测试测量设备），驱动提供商应为 National Instruments 或 Keysight Technologies。若被误刷为通用 USB，需在设备管理器中“更新驱动程序”并重新指向官方 VISA 的 TMC 驱动文件（如 `ausbtmc.sys`）。

</details>

---

<details>
<summary><b>RS232</b></summary>

**RS-232**（正式标准名称为 **EIA/TIA-232**）是由美国电子工业联盟（EIA）于 1960 年代制定的串行二进制数据交换接口标准。在电磁兼容（EMC）与计量测试系统中，RS-232 广泛应用于**旋转台/升降台控制器、可编程恒流源、射频功率放大器监控接口以及各类辅助传感器**的通信控制。

---

## 一、物理特性与电气规格

RS-232 采用**单端非平衡传输**（Unbalanced/Single-Ended Signaling），所有信号均以公共地线（GND）作为电压参考点，采用负逻辑电平传输。

| 规格项 | 参数指标 / 规范 | 说明 |
| --- | --- | --- |
| **标准代号** | EIA-232-E / TIA-232-F / CCITT V.24/V.28 | 行业习惯简称为 RS-232（Recommended Standard 232） |
| **通信模式** | 异步串行、全双工（Full-Duplex） | 依靠起始位/停止位维持字符间时钟同步 |
| **逻辑电平（负逻辑）** | **逻辑 1（Mark/传号）**：$-3\text{ V} \sim -15\text{ V}$（典型 $-5\text{ V} \sim -12\text{ V}$）<br>

<br>**逻辑 0（Space/空号）**：$+3\text{ V} \sim +15\text{ V}$（典型 $+5\text{ V} \sim +12\text{ V}$） | 门限死区：$-3\text{ V} \sim +3\text{ V}$（处于该范围为不确定状态） |
| **常用波特率** | 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200 bps | 仪器控制中最常用 **9600** 与 **115200 bps** |
| **最大有效距离** | 典型 $\le 15\text{ m}$（在 19200 bps 速率下） | 距离由分布电容决定（电容上限通常为 $2500\text{ pF}$）；速率降低时可延至数十米 |
| **拓扑结构** | **严格点对点（Point-to-Point）** | 1 条通信线上仅支持 1 个发送端与 1 个接收端（不支持多机总线挂载） |
| **常见接口物理形态** | **DB9（DE-9）公头/母头**（主流）、DB25、RJ45（终端服务器常用） | 仪表端通常为 DB9 公头（Male）或母头（Female） |

---

## 二、引脚定义与流控机制（DB9 标准）

在 RS-232 网络中，通信两端划分为 **DTE（数据终端设备，如工控机/PC）** 与 **DCE（数据通信设备，如调制解调器/被控仪器）**。

### 1. DB9 标准引脚功能表

| 引脚号 | 信号名称 | 英文全称 | 信号方向（从 DTE 视角） | 功能说明 |
| --- | --- | --- | --- | --- |
| **1** | **DCD** | Data Carrier Detect | 输入（$\leftarrow$） | 数据载波检测（Modem 专用，仪器控制中常悬空） |
| **2** | **RXD** | Receive Data | 输入（$\leftarrow$） | 接收串行数据 |
| **3** | **TXD** | Transmit Data | 输出（$\rightarrow$） | 发送串行数据 |
| **4** | **DTR** | Data Terminal Ready | 输出（$\rightarrow$） | 数据终端就绪（上位机告知设备已准备好通信） |
| **5** | **GND** | Signal Ground | — | **信号公共地**（电平参考基准，必须直连） |
| **6** | **DSR** | Data Set Ready | 输入（$\leftarrow$） | 数据设备就绪（仪器告知上位机已加电并就绪） |
| **7** | **RTS** | Request To Send | 输出（$\rightarrow$） | 请求发送（硬件流控：上位机告知仪器准备接收） |
| **8** | **CTS** | Clear To Send | 输入（$\leftarrow$） | 清除发送（硬件流控：仪器允许上位机发送数据） |
| **9** | **RI** | Ring Indicator | 输入（$\leftarrow$） | 振铃提示（仪器控制中通常悬空） |

### 2. 线缆连接模式

* **直通线（Straight-Through Cable）**：用于连接 DTE（PC）与标准 DCE（设备），引脚 2 对 2、3 对 3、5 对 5 直连。
* **交叉转接线 / 零调制解调线（Null Modem Cable）**：绝大多数台式仪器内部端口实际被设计为 DTE 架构。当两台 DTE（PC 与仪器）对接时，**必须交叉连接 TXD 与 RXD**：
* 3 线制最小系统：`PC_TXD(3) -> Device_RXD(2)`，`PC_RXD(2) <- Device_TXD(3)`，`GND(5) <-> GND(5)`。
* 带硬件流控系统：除交叉数据线外，还需交叉 `RTS(7) <-> CTS(8)`。



### 3. 流控机制（Flow Control）

防止发送端发送速率过快导致接收端缓冲区溢出丢数据：

* **无流控（None）**：完全依靠软件轮询与延时，适用于低波特率、交互指令简短的系统。
* **硬件流控（RTS/CTS）**：通过物理引脚电平变化控制启闭。当接收端缓冲区水位达到阈值时拉低 CTS/RTS，通知对方暂停发送。
* **软件流控（XON/XOFF）**：通过数据流中内嵌的 ASCII 控制字符实现（`XOFF = 0x13` 暂停发送，`XON = 0x11` 恢复发送）。**注意**：在传输二进制数据（如 Modbus RTU、固件升级、波形块）时严禁使用软件流控，否则二进制数据中若出现 `0x13` 会导致总线意外挂起。

---

## 三、异步数据帧格式

RS-232 采用基于字符的异步成帧协议，每个数据字符（Frame）由 4 部分构成：

```text
 空闲状态 (Idle, -12V)
 ──────┐       ┌───┬───┬───┬───┬───┬───┬───┬───┬───────┬───────┐────── 空闲状态
       │ 起始位 │ D0│ D1│ D2│ D3│ D4│ D5│ D6│ D7│ 校验位│ 停止位 │
       └───┴───┴───┴───┴───┴───┴───┴───┴───┴───────┴───────┘
         (+12V)               (LSB -> MSB)

```

1. **起始位（Start Bit）**：固定 1 位低电平（Space，$+3\text{ V} \sim +15\text{ V}$），用于打断空闲态的高电平（Mark），触发接收端本地波特率时钟采样计数器重置。
2. **数据位（Data Bits）**：通常为 **7 位**（纯 ASCII 控制）或 **8 位**（标准字节，低位 LSB 先出）。
3. **校验位（Parity Bit，可选）**：
* `None`（无校验，工业最常见）
* `Even`（偶校验：数据位加校验位中“1”的个数保持偶数）
* `Odd`（奇校验：使“1”的个数为奇数）
* `Mark / Space`（固定填 1 或 0）


4. **停止位（Stop Bit）**：固定恢复为高电平（Mark，$-3\text{ V} \sim -15\text{ V}$），宽度可选 **1 位、1.5 位或 2 位**，为接收端解析字符留出恢复时间。

* **常见配置简记**：`9600, 8, N, 1`（9600 波特率、8 位数据位、无校验、1 位停止位）。通信双方配置必须严格一致，否则会出现乱码或帧错误（Framing Error）。

---

## 四、软件栈与程控实现

在上位机控制系统中，RS-232 既可以通过 VISA 体系进行标准仪表控制，也可以通过原生 Python 串口库（`pyserial`）直接控制工业控制器。

### 1. VISA 资源描述符规则

RS-232 串口在 VISA 库中通过 `ASRL`（Asynchronous Serial）表示：


$$\text{ASRL}[board]::\text{INSTR} \quad \text{或} \quad \text{ASRL}[port\_number]::\text{INSTR}$$

* `ASRL1::INSTR`：对应工控机物理原生的 `COM1`。
* `ASRL6::INSTR`：对应 USB 转串口适配器枚举出来的 `COM6`。

### 2. 程控代码示例

#### 方式 A：通过 PyVISA（推荐用于支持 SCPI 的台式仪表/电流源）

```python
import pyvisa

rm = pyvisa.ResourceManager()

# 打开 COM3 串口设备 (对应 ASRL3::INSTR)
serial_inst = rm.open_resource("ASRL3::INSTR")

# 配置通信波特率与帧格式 (需与仪器面板菜单一致)
serial_inst.baud_rate = 9600
serial_inst.data_bits = 8
serial_inst.parity = pyvisa.constants.Parity.none
serial_inst.stop_bits = pyvisa.constants.StopBits.one
serial_inst.flow_control = pyvisa.constants.VI_ASRL_FLOW_NONE

# 设置超时 (毫秒) 与终止符
serial_inst.timeout = 3000
serial_inst.write_termination = "\n"
serial_inst.read_termination = "\n"

# 查询仪器身份
idn = serial_inst.query("*IDN?")
print("Instrument ID:", idn)

# 控制可编程电流源
serial_inst.write("CURR 5.0A")
serial_inst.write("OUTP ON")

serial_inst.close()
rm.close()

```

#### 方式 B：通过 `pyserial`（推荐用于旋转台控制器、Modbus RTU 机构）

```python
import serial
import time

# 初始化原生串口
ser = serial.Serial(
    port="COM4",
    baudrate=115200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1.0  # 秒
)

# 清空历史缓冲区，避免残留脏数据
ser.reset_input_buffer()
ser.reset_output_buffer()

# 示例：发送旋转台步进移动 ASCII 指令
cmd = "MOVE:ABS 90.0\r\n"
ser.write(cmd.encode("ascii"))

# 等待响应
response = ser.readline().decode("ascii").strip()
print("Positioner Response:", response)

ser.close()

```

---

## 五、工程调试与现场排查要点

* **线序交叉错误（TX/RX 颠倒）**
* 现存设备中 DB9 引脚定义极易混淆（部分厂商将 DTE 接头做成了母头，或内部已预先反接）。
* **现场判定技巧**：在不接通信线、设备上电处于空闲态时，用万用表直流电压档分别测量 PC 端和设备端 DB9 的 2 脚和 3 脚对 5 脚（GND）的电压。**有负电压（$-5\text{ V} \sim -12\text{ V}$）的引脚必定是该设备的发送端（TXD）**。正常连接必须保证**一端的发送端连至另一端的接收端**；若两端都在同一引脚测出负电压，说明必须加装交叉转接头。


* **硬件流控配置不匹配导致软件假死**
* 若仪器默认开启了硬件流控（RTS/CTS），而通信线缆只接了 3 根线（TX/RX/GND），此时上位机发送指令后，CTS 引脚处于悬空未使能状态，操作系统底层串口驱动会无限期挂起等待发送许可，引发软件卡死或 `Timeout` 异常。
* **排查建议**：若仅采用 3 根线通信，上位机必须显式配置 `flow_control = NONE`；或在 DB9 插头内部短接本地的 RTS 与 CTS（引脚 7 与 8）。


* **强电磁环境下的共模干扰与地环路（Ground Loop）**
* 在功放输出（如 100W/200W 射频功放）或工频大电流（20A 恒流源）环境中，RS-232 的单端信号极易受到地电位波动干扰：
* 工控机与被控设备处于不同电源插座时，地电位差（Ground Offset）会直接叠加在信号线上，导致负逻辑电平落入死区（$-3\text{ V} \sim +3\text{ V}$），造成严重误码或硬件收发芯片（如 MAX232）击穿。
* **排查建议**：在暗室或高功率试验台架上，串口必须加装**光电隔离型 RS-232 隔离器**（隔离电压 $\ge 2500\text{ Vrms}$），彻底切断两端的地环路。




* **通信残留字节与终止符粘包**
* RS-232 是字符流传输，没有以太网或 USB 那样的硬件帧封装概念。若上一次通信因超时异常中断，接收缓冲区内残留的部分字符会与下一次查询的返回结果粘连，导致数据解析崩溃。
* **排查建议**：每次执行关键指令前，驱动代码中应主动调用 `flush()` 或 `reset_input_buffer()` 清空输入缓冲区；同时严格约定响应终止符（如 `\r\n`），读取时使用按行读取机制（`readline`）。

</details>

---

<details>
<summary><b>Modbus</b></summary>

**Modbus** 是由 Modicon 公司（现施耐德电气）于 1979 年为可编程逻辑控制器（PLC）通信开发的一种**主从式（Master-Slave / Client-Server）应用层总线协议**。在工业测控与实验室自动化中，Modbus 广泛应用于**旋转台/升降台控制器、温湿度监控仪、可编程交直流恒流源、低频功率放大器保护模块及各类工业传感器**的控制与数据采集。

---

## 一、传输模式与物理层规格对比

Modbus 是一种纯应用层协议规范，可基于不同的物理层和通信信道封装为三种主流变体：**Modbus RTU**、**Modbus ASCII** 与 **Modbus TCP**。

| 规格项 | Modbus RTU | Modbus ASCII | Modbus TCP |
| --- | --- | --- | --- |
| **物理层介质** | RS-485（差分半双工）、RS-232 | RS-485、RS-232 | 以太网（RJ45、光纤） |
| **编码方式** | 8 位二进制（紧凑型，高吞吐） | 7/8 位 ASCII 文本字符（易于监控读数） | 二进制数据封装于 TCP 报文负载 |
| **帧定界方式** | 物理静默时间间隔 $\ge 3.5$ 字符时间 | 起始符 `:`（`0x3A`），终止符 `CR LF`（`0x0D 0x0A`） | MBAP 头部包含 2 字节报文长度字段 |
| **错误校验机制** | 16 位循环冗余校验（CRC-16） | 8 位纵向冗余校验（LRC） | 依靠 TCP/IP 传输层校验和保证可靠性 |
| **传输效率** | **高**（工业现场主流推荐） | 低（数据量扩大一倍） | **极高**（无波特率瓶颈，百兆/千兆） |
| **网络端口/从站容量** | 单总线最多 31/128/247 个从站（受 RS-485 芯片驱动能力约束） | 同 RTU | 默认监听 **TCP 端口 502**，支持多客户端并发 |

---

## 二、核心存储区模型（寄存器类型）

Modbus 将从站（Server）内部的数据存储划分为 **4 种独立的逻辑存储区**。每个存储区具有不同的读写权限与数据位宽：

| 存储区名称 | 常见缩写 | 访问权限 | 位宽 | 典型 PLC 寻址前缀 | 应用场景示例 |
| --- | --- | --- | --- | --- | --- |
| **离散量输入**<br>

<br>(Discrete Inputs) | DI | 只读 | 1 位 (bit) | `1xxxx` (如 10001) | 机械限位开关状态、急停按钮闭合、光电到位信号 |
| **线圈状态**<br>

<br>(Coils) | DO | 读写 | 1 位 (bit) | `0xxxx` (如 00001) | 继电器吸合、功放输出使能、电机启停控制 |
| **输入寄存器**<br>

<br>(Input Registers) | AI | 只读 | 16 位 (word) | `3xxxx` (如 30001) | 模拟量电压/电流采样值、温度传感器实时读数 |
| **保持寄存器**<br>

<br>(Holding Registers) | AO/HR | 读写 | 16 位 (word) | `4xxxx` (如 40001) | 电流源目标值、旋转台目标角度、通信超时配置 |

> **寻址规范注意点**：PLC 传统地址（如 `40001`）为 **1-based** 逻辑地址；而通信报文传输的物理协议地址（PDU Address）为 **0-based**（从 `0x0000` 开始）。即请求 `40001` 时，报文中的地址字段实际填 `0x0000`。

---

## 三、常用功能码与报文帧结构

### 1. 常用功能码列表（Function Codes）

| 功能码（十进制） | 16 进制 | 操作对象 | 功能说明 |
| --- | --- | --- | --- |
| **01** | `0x01` | 线圈 (Coils) | 读一组线圈开关状态（1~2000 个点） |
| **02** | `0x02` | 离散输入 (Discrete Inputs) | 读一组离散开关量状态（1~2000 个点） |
| **03** | `0x03` | 保持寄存器 (Holding Registers) | 连续读取 1 个或多个保持寄存器（1~125 个字） |
| **04** | `0x04` | 输入寄存器 (Input Registers) | 连续读取 1 个或多个输入寄存器（1~125 个字） |
| **05** | `0x05` | 单个线圈 (Single Coil) | 强制写入单个线圈（`0xFF00` 表示 ON，`0x0000` 表示 OFF） |
| **06** | `0x06` | 单个保持寄存器 (Single Register) | 向单个保持寄存器写入 16 位整数 |
| **15** | `0x0F` | 多个线圈 (Multiple Coils) | 批量写入多个线圈开关状态 |
| **16** | `0x10` | 多个保持寄存器 (Multiple Registers) | 批量写入多个保持寄存器（如写入 32 位浮点数） |

### 2. 报文帧结构剖析（以读取保持寄存器 FC 03 为例）

#### Modbus RTU 帧结构

```text
┌──────────────┬──────────────┬────────────────────────┬─────────────┐
│ 从站地址 (1B) │ 功能码 (1B)  │  数据字段 (N 字节)      │ CRC-16 (2B) │
│ 0x01 ~ 0xF7  │ 0x03         │ 起始地址(2B) + 长度(2B)│ 低前高后    │
└──────────────┴──────────────┴────────────────────────┴─────────────┘

```

* **请求报文**（主机读取从站 `01` 的 `40001` 开始的 2 个寄存器）：
`01 03 00 00 00 02 C4 0B`
* `01`：从站地址
* `03`：功能码
* `00 00`：起始寄存器物理地址 0
* `00 02`：读取寄存器数量（2 个字，4 字节）
* `C4 0B`：CRC16 校验码（低字节在先）


* **正常响应**：
`01 03 04 41 A0 00 00 3E 45`
* `04`：后续数据字节数（4 字节）
* `41 A0 00 00`：数据内容（IEEE-754 浮点数 `20.0`）
* `3E 45`：CRC16 校验



#### Modbus TCP 帧结构（MBAP 头部替代了从站地址与 CRC）

```text
┌──────────────────────────────────────────────┬────────────┬────────────────────────┐
│           MBAP 报文头 (7 字节)                │ 功能码(1B) │  数据字段 (N 字节)      │
│ 传输标识(2B) + 协议标识(2B) + 长度(2B) + 单元ID(1B)│ 0x03       │ 起始地址(2B) + 长度(2B)│
└──────────────────────────────────────────────┴────────────┴────────────────────────┘

```

* **传输标识符**（Transaction ID）：用于主从并发请求与响应的配对标识。
* **协议标识符**（Protocol ID）：固定为 `0x0000` 表示 Modbus 协议。
* **单元标识符**（Unit ID / Slave ID）：在网关模式下用于路由寻址后级串行总线上的特定从站。

---

## 四、软件栈与程控实现（Python 示例）

在工业自动化上位机开发中，通常基于标准库 `pymodbus`（全面支持 RTU/TCP 异步）或 `minimalmodbus`（针对 RTU 串行控制更轻量）实现。

### 1. Modbus RTU 串口通信（以 `pymodbus` 控制旋转台/传感器为例）

```python
from pymodbus.client import ModbusSerialClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder

# 1. 建立串口连接 (典型配置: 9600-8-N-1)
client = ModbusSerialClient(
    port="COM3",
    baudrate=9600,
    bytesize=8,
    parity="N",
    stopbits=1,
    timeout=1.0  # 秒
)

if not client.connect():
    raise ConnectionError("无法连接至 Modbus RTU 串口设备")

# 2. 读取保持寄存器 (FC 03: 从站 1，地址 0，读取 2 个寄存器构成 32 位浮点数)
response = client.read_holding_registers(address=0, count=2, slave=1)

if not response.isError():
    # 对获取的 2 个 16 位寄存器进行大端/字交换解码为 Float32
    decoder = BinaryPayloadDecoder.fromRegisters(
        response.registers, 
        byteorder=Endian.BIG, 
        wordorder=Endian.BIG
    )
    current_angle = decoder.decode_32bit_float()
    print(f"当前旋转台角度: {current_angle:.2f}°")
else:
    print(f"Modbus 响应异常: {response}")

# 3. 写入单个保持寄存器 (FC 06: 控制目标电流源设定值)
client.write_register(address=10, value=2500, slave=1)  # 写入 25.00A (带缩放因子)

client.close()

```

### 2. Modbus TCP 以太网通信

```python
from pymodbus.client import ModbusTcpClient

# 建立 TCP 连接 (默认端口 502)
tcp_client = ModbusTcpClient(host="192.168.1.50", port=502, timeout=2.0)
tcp_client.connect()

# 读取输入寄存器 (FC 04: 获取传感器只读数据)
result = tcp_client.read_input_registers(address=0, count=4, slave=1)
if not result.isError():
    print("采集通道原始值:", result.registers)

# 控制线圈输出 (FC 05: 闭合继电器使能功放供电)
tcp_client.write_coil(address=0, value=True, slave=1)

tcp_client.close()

```

---

## 五、工程调试与现场排查要点

* **寄存器基址偏移问题（“差 1” 陷阱）**
* 不同厂商的说明书编制口径不一：部分文档提供的是逻辑地址（如 `40001`、`30005`），部分提供的是 PDU 物理偏移地址（如 `0x0000` 或直接标十进制 `0`）。
* **排查技巧**：若下发读取指令后返回的数值呈现“整体后移一位”，通常是将逻辑地址直接填入协议地址所致；在上位机配置时需统一确认驱动层是否自带 `-1` 偏移处理。


* **32 位数据类型的字节序与字序（Endianness & Word Swap）**
* Modbus 原生仅定义了单个 16 位寄存器的大端传输（高字节在前）。当传输 32 位浮点数（Float32）或 32 位双字整数时，需要使用两个连续寄存器。不同厂商在两个字的组合顺序上存在严重分歧：
* **ABCD（Big-Endian）**：高字在前，大端（网络序）；
* **CDAB（Little-Endian with Word Swap）**：低字在前，大端（**绝大多数工业仪表采用此格式**）；
* **BADC / DCBA**：包含字节内交换的变体。


* **排查技巧**：读取浮点数出现极大极小值（如 `NaN`、`1.23e-38` 等非法数值）时，不要随意更改标定参数，优先尝试调换“高低字顺序（Word Swap）”。


* **RS-485 差分总线接线极性反接（A/B 倒置）**
* Modbus RTU 多运行在 RS-485 总线上。不同厂商对 A、B 线的标识混乱：
* 部分标准定义：`A = Data- (负)`，`B = Data+ (正)`；
* 部分厂商反标：`A = Data+`，`B = Data-`。


* **现场判定技巧**：总线空闲未通信时，用万用表直流档测量两线电平：**电压较高的线必定是正逻辑信号线（Data+）**。若接错会导致总线常态死锁，上位机全部超时。


* **RS-485 终端匹配电阻与拓扑结构**
* 在长距离传输（$>50\text{ m}$）或高波特率（$\ge 115200\text{ bps}$）下，RS-485 总线**两端物理最末端**的设备上必须并联 **$120\,\Omega$ 终端匹配电阻**，以消除高频反射波。
* 总线必须严格布放为“手拉手”菊花链拓扑，禁止出现过长的星型分支引线（Stub 长度尽量 $<30\text{ cm}$）。


* **RTU 帧间隔时序（3.5T 规则）与响应超时**
* Modbus RTU 依靠 $\ge 3.5$ 个字符时间的空闲无信号状态识别一帧的结束。上位机发送请求后，必须留给低算力从站（如 8 位单片机温控表）足够的处理时间（建议串口超时配置不低于 $200\text{ ms} \sim 500\text{ ms}$）。
* 主站不可发起背靠背瞬时连续轮询，相邻两次查询之间必须加入微小延时（如 $10\text{ ms} \sim 20\text{ ms}$），否则从站内部串口中断未完成重置会导致连续丢包。

</details>

#### 1. 信号发生器驱动模块

* **适配设备**：
* Keysight N5171B-501（高频/TEM/GTEM：9 kHz～1 GHz）
* Keysight N5173B-520 选件 1E1（暗室：10 MHz～20 GHz）
* RIGOL DG811（工频磁场频响：20 Hz～1 MHz）


* **工作内容**：
* 基于 PyVISA 封装标准 SCPI 指令集。
* 实现核心方法：`set_frequency(freq_hz)`、`set_amplitude(amp_dbm_or_v)`、`output_on()`、`output_off()`、`get_rf_status()`。
* 实现频率/功率越界硬件软保护（对比设备最大允许值，超限拦截）。
* 异常处理：超时重试机制（默认重试 3 次）、输出状态回读强校验。



#### 2. 功率计与高频毫伏计驱动模块

* **适配设备**：
* Keysight N1914A 双通道功率计 + E9304A-118 探头（9 kHz～18 GHz）
* QF2281A 高频毫伏计及探头（9 kHz～1 GHz，10 mV～2 V）


* **工作内容**：
* 封装功率计 SCPI 接口：零点校准（Zero/Cal）、探头频点自动补偿设置（`set_freq_compensation`）、量程配置、触发连续采集。
* 封装毫伏计接口（串口/GPIB）：量程切换（`set_range`）、交流毫伏读数读取。
* 实现测量读数滤波与数据平稳性判定算法（`wait_stable(timeout, tolerance)`），返回平均值与抖动方差。



#### 3. 数字多用表与恒流源驱动模块（工频/低频）

* **适配设备**：
* Keysight 34461A 6 位半数字多用表（工频电/磁场：交流电压/电流测量）
* 10020 可编程交流恒流电流源（0～20 A 程控可调）


* **工作内容**：
* 34461A 驱动：配置 ACV / ACI 测量模式、采样速率（NPLC）、量程设置（`CONF:VOLT:AC`）、数据读取（`READ?`）。
* 10020 电流源驱动：基于 RS232/Modbus 协议，封装目标电流设定（`set_current_a`）、频率设定（`set_frequency_hz`）、恒流输出开闭控制与输出电流回读校验。
* 工频小负载采样电阻（GL-DZ5W1，500Ω）的欧姆定律电压-电流转换中间计算封装。



#### 4. 功率放大器与射频开关控制模块

* **适配设备**：
* 高频功放：CL10R2-100W（10 kHz～500 MHz）、CL100R1-100W（10 MHz～1 GHz）
* 暗室微波功放：CL1GR4-200W（1 GHz～4 GHz）、CL4GR18-100W（4 GHz～18 GHz）
* 低频功放：CL002R3-100W（20 Hz～300 kHz）
* 同轴射频微波开关：SP1T-8T（1 进 8 出，1 GHz～18 GHz）


* **工作内容**：
* 功放通信控制（RS232/LAN）：功放联锁状态读取、增益监控、复位控制、过功率与过温保护预警拦截。
* 暗室双频段功放切换联动：配合射频开关实现 1～4 GHz 与 4～18 GHz 信号通路自动切换与安全下电逻辑（先切断信号源输出 $\rightarrow$ 切换微波开关 $\rightarrow$ 切换功放 $\rightarrow$ 恢复信号输出）。



#### 5. 机械运动与定位控制驱动模块

* **适配设备**：
* FC1-XZ-XZ01 自动旋转装置（TEM 室 360° 各向同性校准）
* FCI-XZZJ-002 自动对准支架（暗室：水平 0.8 m、上下 0.5 m、旋转）


* **工作内容**：
* 基于串口/Modbus RTU 封装运动指令：原点复位（`home`）、绝对/相对角度旋转（`move_to_angle`）、步进扫描、高程升降控制（`move_z`）、水平移动（`move_x`）。
* 运动控制强保护：软件限位约束、到位判定轮询（`wait_in_position`）、紧急停机（`stop`）。
* 暗室 1 米轴线对齐辅助逻辑：支持结合红外水平仪反馈值计算对准偏移。



#### 6. 传递标准与参考场强仪驱动模块

* **适配设备**：
* Narda FieldMan 场强仪（EFI-0691 探头：9 kHz～6 GHz，EFI-1891 探头：10 MHz～18 GHz）
* FCT-SP0110 场强传递标准（10 MHz～1 GHz）
* Narda EHP-50F 低频场强仪（1 Hz～400 kHz）


* **工作内容**：
* 基于厂商 USB-SDK 或虚拟串口通信协议，解析厂商私有二进制/ASCII 数据流。
* 实现方法：`read_field()`（读取综合场强值及 X/Y/Z 三轴分量）、`get_frequency()`、`get_battery()`、单位自动解析。



#### 7. 虚拟仿真驱动套件（Mock Drivers，核心支撑）

* **工作内容**：
* 为上述所有设备开发 Mock 驱动实现，在上层各业务组缺乏真实物理硬件时，模拟真实仪器的通信时延、SCPI 交互、数据噪声及偶发异常。
* 保障各业务组在第 2 周至第 4 周能够脱机完成 UI 和状态机联调。



---

### 二、机器视觉与 OCR 识别库开发（视觉读数层）

针对现场监控装置（FCI-SZXJ-001、FCI-SZSX-001、FCI-SZSX-003），替代人工抄录被校场强仪显示屏读数：

#### 1. 图像采集与相机 SDK 封装

* **工作内容**：
* 支持 UVC / USB3.0 / RTSP 工业相机视频流统一接入（基于 OpenCV VideoCapture / 厂商 SDK）。
* 实现单帧抓拍（`capture_frame`）、曝光与白平衡参数软件配置。
* 线程安全设计：视频流后台守护采集，避免阻塞业务控制线程。



#### 2. ROI 标注与图像预处理管线

* **工作内容**：
* 提供 ROI（感兴趣区域）配置保存与加载接口（支持按被检场强仪型号持久化为 JSON 模板）。
* 针对液晶屏（LCD）、LED 数码管实现定制预处理链路：
* 倾斜矫正（基于透视变换 Perspective Transform）；
* 对比度增强（CLAHE）、自适应二值化（Adaptive Otsu Thresholding）；
* 反光与网纹去噪（形态学开闭运算）。





#### 3. 字符与单位识别引擎（基于 PaddleOCR / 轻量 CRNN）

* **工作内容**：
* 定制字符字典：专门针对数字（`0-9`）、小数点（`.`）、正负号（`+`、`-`）及电磁场单位（`V/m`、`kV/m`、`dBμV/m`、`A/m`、`μT`、`mT`）进行模型微调或正则表达式后处理。
* 输出标准化数据结构：
```python
class OCRResult:
    raw_text: str          # 原始识别文本
    numeric_value: float   # 提取的数值
    unit: str              # 识别单位
    confidence: float      # 置信度 (0.0~1.0)
    bounding_box: list     # 坐标框
    is_valid: bool         # 格式校验通过标志

```





#### 4. 视觉质量门控与连续帧一致性校验

* **工作内容**：
* **连续 3 帧一致性算法**：自动触发连续 3 帧抓拍与识别，判定阈值：

$$\vert{}\text{Value}_i - \text{Value}_j\vert{} \le \varepsilon \quad \text{且} \quad \text{Unit}_i = \text{Unit}_j$$


* 若置信度低于阈值（如 $<0.85$）或 3 帧不一致，触发质量报警并打标 `review_status="NEED_CONFIRM"`，通知业务层暂停并留存当前图像切片供人工复核。
* 建立测试数据集：收集整理不少于 50 张真实仪表显示屏图片，输出字符级识别率与整条读数识别率统计报告（合格标准 $\ge 95\%$，优秀 $\ge 99\%$）。



---

### 三、计量核心算法库开发（计算核心层）

算法必须严格遵循电磁场计量规程，提供无副作用的纯计算函数与单元测试用例：

#### 1. 标准场强与磁场生成计算模块

* **TEM 室 / µTEM 室标准场强计算**：
* 根据输入净功率 $P_{net}$（由功率计读数结合双定向耦合器耦合度、衰减器损耗、同轴线缆损耗换算得到）及芯板高度 $d$ 计算标准场强：

$$E = \frac{\sqrt{P_{net} \cdot Z_0}}{d} \quad (Z_0 \approx 50\,\Omega)$$




* **GTEM 室定标模型**：
* 基于参考场强计定标数据建立频率插值网格，生成 GTEM 场强传递修正矩阵。


* **暗室微波射频电场计算（1 GHz～18 GHz 喇叭天线 1m 法）**：
* 根据标准角锥喇叭/双管喇叭天线增益曲线 $G(f)$（加载天线校准证书离散点进行三次样条或线性插值），结合 1 米同轴距离 $r=1.0\,\text{m}$ 计算：

$$E = \frac{\sqrt{30 \cdot P_{in} \cdot G}}{r}$$




* **工频/低频亥姆赫兹线圈标准磁场计算**：
* 适配线圈常数（FCI-8800 直径 0.8m，PCI-H300 直径 0.3m）：

$$B = \mu_0 \left(\frac{4}{5}\right)^{3/2} \frac{N \cdot I}{R}$$


* 支持背景磁场矢量/标量扣除：$H_{corrected} = \sqrt{H_{meas}^2 - H_{bg}^2}$ 或差值基线扣除。
* 单位换算工具：

$$1\text{ A/m} = 4\pi \times 10^{-1}\text{ }\mu\text{T} \approx 1.2566\text{ }\mu\text{T}, \quad 1\text{ }\mu\text{T} \approx 0.7958\text{ A/m}$$





#### 2. 校准因子与各向同性度算法模块

* **场强校准因子（Calibration Factor, $K$）**：

$$K = \frac{E_{std}}{E_{eut}} \quad \text{或} \quad K(\text{dB}) = 20\lg E_{std} - 20\lg E_{eut}$$


* **各向同性度计算（Isotropy Evaluation）**：
* 输入全角度（$0^\circ \sim 360^\circ$）扫描测量序列，计算圆周最大值、最小值、算术平均值及各向同性偏差：

$$\Delta_{iso} = \pm 20\lg\left(\frac{E_{max}}{E_{min}}\right) \Big/ 2 \quad \text{或各向同性响应标准差}$$


* 生成供 UI 绘制极坐标方向图的极坐标插值平滑数据点阵。



#### 3. GUM 规范测量不确定度评定引擎

* **A 类不确定度评定**：
* 基于单频点单状态多次独立重复测量序列，利用贝塞尔公式自动计算实验标准偏差及平均值的标准不确定度：

$$s = \sqrt{\frac{\sum_{i=1}^n (x_i - \bar{x})^2}{n - 1}}, \quad u_A = \frac{s}{\sqrt{n}}$$




* **B 类不确定度库与灵敏度系数计算**：
* 功率计校准证书引入的不确定度分量 $u_{B,pm}$；
* 天线增益/线圈常数证书分量 $u_{B,ant}$；
* 阻抗失配分量 $u_{B,mis}$；
* 几何定位与 1m 距离测量误差分量 $u_{B,dist}$；
* 场强仪显示分辨率/OCR 量化分量（矩形分布，$\frac{\delta}{2\sqrt{3}}$）；
* 场分布均匀性分量。


* **合成与扩展不确定度**：
* 合成标准不确定度：$u_c = \sqrt{\sum c_i^2 u_i^2}$
* 扩展不确定度：$U = k \cdot u_c$（包含因子默认 $k=2$）。



---

### 四、统一数据模型与持久化管理（数据底座层）

负责全项目的数据结构定义、本地存储、数据对齐与文件导出：

#### 1. 统一数据结构定义（基于 Pydantic / Dataclasses）

冻结跨模块数据契约，严格约束各字段类型、精度及单位：

```python
# 核心数据模型草案示例
@dataclass
class CalibrationTask:
    task_id: str             # 任务唯一编号 (UUID/时间戳)
    system_type: str         # TEM / GTEM / Chamber / Helmholtz
    operator: str            # 校验人员
    temperature: float       # 环境温度
    humidity: float          # 环境湿度
    eut_model: str           # 被校仪表型号
    eut_sn: str              # 被校仪表序列号

@dataclass
class MeasurementRecord:
    task_id: str
    point_id: str            # 频点/角度/幅值组合唯一键
    timestamp: float         # 毫秒级时间戳 (time.time())
    freq_hz: float           # 设定频率
    source_amp: float        # 信号源设定幅值 (dBm/V)
    power_value: float       # 功率计读数 (W/dBm)
    voltage_value: float     # 毫伏计/万用表电压读数
    current_a: float         # 电流源设定/读数 (A)
    angle_deg: float         # 旋转台当前角度
    ocr_raw_text: str        # OCR 原文
    ocr_val: float           # OCR 读数值
    ocr_unit: str            # OCR 识别单位
    ocr_conf: float          # OCR 置信度
    std_field: float         # 算法计算的标准场强
    cal_factor: float        # 校准因子
    uc: float                # 合成标准不确定度
    U: float                 # 扩展不确定度 (k=2)
    status: str              # SUCCESS / WARNING / ERROR

```

#### 2. 时间戳对齐与多源数据汇聚服务

* **工作内容**：
* 设计时钟同步采集机制：针对“功率计读数 + 机械旋转到位反馈 + 相机 OCR 读数”三种异步数据源，提供时间戳窗口对齐器（`DataAligner`）。
* 设定合理配对容差时间窗口（结合设备响应延时，如 $\Delta t \le 200\text{ ms}$），超时未配对则打标异常。



#### 3. SQLite 本地数据库持久化引擎

* **设计并初始化数据库 Schema**：
* `t_task`：校准任务表（任务元信息、环境信息、执行人员、配置快照）；
* `t_raw_record`：原始数据流水表（**追加式写入，只读不可变，保证原始数据防篡改与计量可追溯**）；
* `t_calib_result`：计算结果表（校准点位、标准场强、校准因子、扩展不确定度）；
* `t_gtem_calib_file`：µTEM/GTEM 专用参考校准文件存储表；
* `t_device_log`：底层通信与驱动异常日志表。


* 提供简洁易用的 ORM / 数据访问接口（DAO），上层流程引擎仅需调用 `save_record()`、`query_task_data()`。

#### 4. 统一 CSV / Excel 导出工具集

* **工作内容**：
* 遵循实施方案第 4.3 节统一字段标准，实现标准 CSV 导出组件（强制 UTF-8 带 BOM 编码，防止中文 Excel 乱码）。
* 导出前进行行数校验、空值清洗、数值有效位数格式化（避免浮点数精度泄露），并校验导出行数与 SQLite 数据库记录完全一致。



#### 5. µTEM/GTEM 校准文件管理服务

* **工作内容**：
* 定义参考场强计定标文件的标准结构（包含版本号、设备 SN、生成时间、频率列表、参考场强修正矩阵、CRC 校验码）。
* 实现校准文件的保存、签名校验与合法性解析（`load_calibration_file`）。
* 被校仪表校准前，若加载的校准文件频段不匹配或缺字段，主动抛出强类型异常并阻止流程启动。



---

### 五、公共基础设施与工程化交付（架构支撑层）

作为基础库，需要为上层各组提供规范化的集成体验与开发工具支持：

#### 1. 结构化统一日志与异常框架

* **工作内容**：
* 基于 `loguru` 或 Python `logging` 封装统一日志模块，强行绑定上下文：`[时间戳] [模块名] [TaskID] [DeviceID] [Level] [Action] - Message`。
* 制定错误码规范（Error Code）：
* `1000~1999`：底层硬件通信异常（超时、断开、CRC 校验失败）；
* `2000~2999`：视觉与 OCR 异常（相机断流、置信度不足、连续帧不一致）；
* `3000~3999`：计量算法计算异常（除零、插值超出量程、负方根）；
* `4000~4999`：数据持久化与校准文件校验失败。





#### 2. 公共底层库的打包与版本管理

* **工作内容**：
* 建立统一代码仓库与分支管理策略，配置 `pyproject.toml` / `setup.py`，将底座库打包为 wheel 包（如 `calib_core-1.0.0-py3-none-any.whl`）。
* 严格执行语义化版本规范（Semantic Versioning），禁止上层业务软件直接修改底座源码。
* 通过 PyPI 私有源或本地 pip 依赖方式供 4 个业务组调用。



#### 3. 开发者 API 文档与技术支持

* **工作内容**：
* 编写《`calib_core` 底座库开发者指南及接口字典》，提供每个驱动、OCR 管道、算法函数的使用示例代码（Jupyter Notebook 或 QuickStart 脚本）。
* 负责接口变更评审与各业务组的联调支持。



---

### 六、各实施阶段交付物清单与时间节点对照表

依据项目 8 周周期规划，底座库工作的各节点输出物如下：

| 阶段 / 周期 | 核心交付物 | 详细验收内容 |
| --- | --- | --- |
| **第 1 周：架构与接口草案** | 接口规范 V0.1、Mock 驱动库初版 | 1. 冻结 `BaseDriver` 基类与接口规范草案<br>

<br>2. 输出信号源/功率计 Mock 虚拟驱动，供上层并行联调 |
| **第 2 周：接口与数据冻结** | `calib_core` V1.0 Wheel 包、数据模型规范 | 1. 冻结统一数据字段与 CSV 格式规范 V1.0<br>

<br>2. 冻结 SQLite 数据库表结构并实现 DAO 访问层<br>

<br>3. 完成主流仪表驱动（N5171B、N1914A、34461A）真实通信测试 |
| **第 3～4 周：最小闭环支持** | OCR 库初版、运动控制、基础算法 | 1. 交付 FCI-XZ-XZ01 旋转台驱动（带到位判定与步进控制）<br>

<br>2. 交付 OCR 模块与 $\ge 50$ 张样本初测报告（字符识别率 $\ge 95\%$）<br>

<br>3. 交付 TEM 标准场强计算公式与单元测试，协助打通 TEM 室端到端最小闭环 |
| **第 5～6 周：全量能力收口** | 完整算法库、校准文件组件、全量驱动 | 1. 交付暗室喇叭天线插值算法、线圈磁场模型与 GUM 不确定度评定引擎（提供手算算例对比验证）<br>

<br>2. 交付 µTEM/GTEM 校准文件管理与校验模块<br>

<br>3. 交付所有功放、开关、高频毫伏计、参考场强计适配驱动 |
| **第 7 周：现场硬件联调** | `calib_core` 现场适配稳定版 | 1. 配合各业务组在 TEM 室、暗室、工频磁场实验室真实设备上排查通信协议时延、光纤衰减、多设备总线冲突等硬件问题<br>

<br>2. 修复驱动级缺陷，消除通信丢包 |
| **第 8 周：验收交付** | 最终 Wheel 包、API 文档、算法报告 | 1. 输出完整单元测试覆盖报告（核心算法测试覆盖率 100%）<br>

<br>2. 输出《计量算法验证与算例对照报告》（手算 vs 程序输出）<br>

<br>3. 输出《OCR 精度统计报告》与底座最终代码打包交割 |
