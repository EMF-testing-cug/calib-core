# calib-core
公共底座库：仪器驱动、OCR、算法、数据模型

难点：GPIB的驱动（只有一个设备是）


# 电磁场测量自动校准软件系统开发与协同指南

本项目面向电磁场测量设备校准的自动化控制与数据管理，采用“核心公共底座库（`calib_core`）+ 4 套独立业务前端”的架构体系。为保证 50 人团队协作高效、代码质量可控且互不冲突，所有成员必须严格遵守本规范，严禁直接向 `main` 或 `develop` 分支推送代码。

---

## 一、 项目仓库与团队职责矩阵

系统由 6 个独立私有仓库组成，请严格按照各自分组在对应仓库下开展开发，严禁跨权限修改其他业务仓库：

| 仓库名称

 | 仓库克隆地址 (HTTPS) | 职责范围与关键交付物

 | 主责团队

 |
| --- | --- | --- | --- |
| **`calib-core`** | `[https://github.com/EMF-testing-cug/calib-core.git](https://github.com/EMF-testing-cug/calib-core.git)` | 通用仪器 SCPI 驱动、PaddleOCR 识别与三帧防抖、SQLite 存储、GUM 不确定度评定引擎及 CSV 导出

 | 底层核心支撑组 |
| **`app-tem`** | `[https://github.com/EMF-testing-cug/app-tem.git](https://github.com/EMF-testing-cug/app-tem.git)` | TEM 室 10kHz~300MHz 频段各向同性校准、场强幅值与频响测试业务前端

 | TEM 室开发组 |
| **`app-gtem`** | `[https://github.com/EMF-testing-cug/app-gtem.git](https://github.com/EMF-testing-cug/app-gtem.git)` | µTEM/GTEM 室 10MHz~1GHz 参考场强计定标、校准文件生成与被检表校准前端

 | µTEM/GTEM 组 |
| **`app-chamber`** | `[https://github.com/EMF-testing-cug/app-chamber.git](https://github.com/EMF-testing-cug/app-chamber.git)` | 暗室 1GHz~18GHz 射频校准前端，控制 1m 轴线对准、双功放频段路由及各向同性步进

 | 暗室射频开发组 |
| **`app-magnetic`** | `[https://github.com/EMF-testing-cug/app-magnetic.git](https://github.com/EMF-testing-cug/app-magnetic.git)` | 亥姆赫兹线圈工频磁场线性度与频响校准前端，实现背景磁场扣除与 A/m、µT 换算

 | 工频磁场开发组 |
| **`calib-integration`** | `[https://github.com/EMF-testing-cug/calib-integration.git](https://github.com/EMF-testing-cug/calib-integration.git)` | 虚拟仪器（Mock）服务、多系统联调测试用例、PyInstaller 独立离线安装包打包工程

 | 总装集成组 |

---

## 二、 首次环境初始化（仅需执行一次）

### 1. 配置 Git 基础身份

打开本地终端（PowerShell 或 Git Bash），配置统一的姓名与邮箱（与 GitHub 注册信息保持一致）：

```bash
git config --global user.name "你的GitHub用户名"
git config --global user.email "你的GitHub注册邮箱"

```

### 2. 启用系统凭据管理器

避免每次拉取和推送重复输入凭据：

```bash
git config --global credential.helper manager

```

> **网络提示**：如遇到 `Connection was reset` 或推送超时，请开启实验室推荐网络加速工具（如 Watt Toolkit 开启 GitHub 终端与网页加速），确保与 GitHub 通信顺畅。

---

## 三、 标准日常开发流程（6 步工作流）

### 步骤 1：拉取最新代码并切入开发主干

以负责 TEM 室开发的成员为例：

```bash
# 1. 克隆对应仓库到本地
git clone https://github.com/EMF-testing-cug/app-tem.git
cd app-tem

# 2. 切换到日常开发主干 develop 分支并更新
git checkout develop
git pull origin develop

```

### 步骤 2：创建专属功能分支（Feature Branch）

分支命名规则统一为：`feature/姓名拼音-功能模块`，禁止多人共用同一个分支：

```bash
# 示例：张三开发信号源驱动
git checkout -b feature/zhangsan-driver-n5171b

```

### 步骤 3：安装依赖并开始编码

```bash
pip install -r requirements.txt
pip install ruff pytest

```

* **编码约束 1**：在预留的目录和文件骨架中实现功能，**严禁私自修改公共类名与公共函数签名**。


* **编码约束 2**：所有仪器驱动必须实现 `mock_mode` 参数，当为 `True` 时返回仿真物理量，保证离线状态下前端业务逻辑与 UI 可正常调试。


* **编码约束 3**：严禁硬编码本机文件绝对路径（如 `D:\test\...`）或测试账密。

### 步骤 4：本地质量自检（CI 门禁预演）

在执行提交前，**必须在本地终端运行以下命令并通过检查**；若存在格式错误或逻辑断言失败，云端流水线将直接标红拦截：

```bash
# 1. 自动格式化代码排版与引用排序（必做）
python -m ruff check --fix .
python -m ruff format .

# 2. 运行自动化单元测试，确保逻辑正确（必做）
pytest tests/

```

*终端输出全部测试通过（如 `x passed` 绿字）后，方可执行提交。*

### 步骤 5：提交修改并推送至远程专属分支

```bash
# 1. 暂存改动
git add .

# 2. 提交说明必须清晰（规范：feat/fix/test/chore: 描述）
git commit -m "feat(driver): 实现 N5171B 信号源设频设幅值与安全切断输出"

# 3. 推送到云端专属开发分支
git push -u origin feature/zhangsan-driver-n5171b

```

### 步骤 6：在 GitHub 发起 Pull Request (PR) 并由组长审核

1. 打开浏览器进入仓库主页，点击弹出的 **Compare & pull request** 绿色按钮。
2. **核对目标分支（至关重要）**：
* **base（合并目标）**：必须选择 **`develop`**（严禁直接选 `main`）。
* **compare（来源分支）**：选择刚推送的 `feature/zhangsan-driver-n5171b`。


3. 简要说明改动内容，点击 **Create pull request**。
4. **观察 Checks 自动化安检状态**：


* ❌ **红叉（All checks have failed）**：说明代码格式未达标或测试断言报错。点击 `Details` 查看错误原因，在本地修改后重新执行“步骤 4 $\to$ 步骤 5（重新 `git push`）”，页面将自动重新质检。


* ✔️ **绿勾（All checks have passed）**：说明自动化质检完全通过。




5. 自动化测试全绿后，通知本组研究生组长进行网页端 Code Review；组长点击 **Approve** 后，该 PR 正式合入主干。



---

## 四、 常见问题与避坑指南 (FAQ)

### Q1：克隆或推送时报 `fatal: Authentication failed` 怎么办？

* **原因**：GitHub 已停止支持明文密码操作。
* **解决**：在弹出的浏览器窗口中点击绿色的 **Authorize**；或进入 GitHub 网页端 `Settings` $\to$ `Developer settings` $\to$ `Personal access tokens (classic)` 生成一个勾选了 `repo` 权限的 Token，在密码处输入该 Token。

### Q2：写代码期间，别人的代码先合并进了 `develop`，我该如何同步？

在发起 PR 前，如果需要合入主干最新更新，在本地终端执行：

```bash
# 1. 切回 develop 并更新最新代码
git checkout develop
git pull origin develop

# 2. 切回个人功能分支并合入 develop
git checkout feature/你的分支名
git merge develop

```

若有冲突，根据 VS Code / PyCharm 提示解决冲突标记（保留正确代码），本地重新跑通 `pytest tests/` 后再次 `git push` 即可。

### Q3：改乱了代码还没提交，如何一键恢复到修改前状态？

```bash
git restore .

```
