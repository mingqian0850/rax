# 给接续 agent 的说明

记录：2026-11-05。先看本文件，再读 outputs 下的机制报告和阅读台账。

## 用户目标与当前选择

用户让我们克隆其 fork，阅读对应论文和全部仓库代码，记录过程和结论，持续回答作者怎样适配新本体/场景，并帮助本地尝试。用户确认 GPU 为 **RTX 4070 Laptop**，先使用已有仿真 benchmark。后续授权把研究内容保存到 fork 并推送，并明确要求节省存储：只保留必要部分，不保存全部上游源码。远端只保留 main 研究入口；实现按官方 commit 获取。

当前选择 **LIBERO-PRO native**。它能先验证同一本体上的布局适配；swap 实验不能证明跨本体迁移。没有必要先部署更重的人形机器人或 BEHAVIOR 环境。

## 最值得保留的结论

1. 新本体需人工实现 backend、接入控制/运动学、标定传感器并提供实测接口说明。模型保持冻结，在线学习产物是任务代码、记忆和技能。
2. `services/adaptation.py` 的兼容目标是同任务或其 `_random` 版本，不是任意机器人/任务转换。LIBERO 的第二阶段探索 collection 6、测试 collection 2。
3. 当前适配优先导入探索结束时的冻结 checkpoint，不导入之后 formal 的结果；默认携带 memory/code/handoff，可控制会话上下文。
4. 公开 skills-lib 的 5 个 Franka 和 6 个 RB-Y1 技能都标 draft。技能库验证是文件与证据记录检查，不会自动重跑硬件。已检查的 simulation 快照没有 LIBERO 策略全集。
5. LIBERO 无动作演示但有 3 张完成图；HumanoidArena 主设置还涉及动作演示与冻结低层跟踪器。不能把所有设置统称为完全无先验。
6. `qualifying_rehearsal` 要求干净执行和评价，不要求任务成功。论文的 241 倍是推理开销加速，不是机器人总耗时。
7. 主分支 Rainbow 接口示例与当前代码默认控制模式有差别；优先引用固定 commit 的实际分派路径。

## 已经做完和没有做完的事

- 拉取 main + 10 个实现分支，完整索引 2940 个分支文件条目；按内容去重为 761 个代码文件版本/150255 行。
- 保守的阅读状态是 36 个全文、9 个局部、716 个仅索引。**全仓逐行精读未完成。** 全文标记可按相同哈希传播，但不同版本不能自动继承。后续从 `outputs/阅读覆盖.md` 的队列继续。
- 论文正文和相关附录已围绕研究问题阅读。未重算所有表格、完整检查所有图/视频或追读所有引用。
- 作者主环境的 LIBERO 核心测试 81 passed；真实分支离线单元测试 Franka 147 passed/4 skipped，Rainbow 159 passed/1 skipped。后两者使用 Python 3.14 阅读环境和模拟硬件，不是硬件复现。
- 自写 `outputs/verify_adaptation_offline.py` 调用真实适配导入实现，合成输入的 8 项条件通过。它不使用 GPU 或模型，不产生机器人任务成功率。
- 主/模拟器环境安装完成，pip check、模拟器模块导入、goal_1 的五组初态读取通过。没有成功启动渲染 episode，没有生成完成图，没有启动模型探索。

## 当前两个阻塞

**GPU：**nvidia-smi 失败。运行中驱动 595.91.07，磁盘内核模块 595.99.02，NVML 595.99。推测是驱动更新后未重启；需用户安排重启再检查。不要自动重启，也不要伪造 GPU 查询绕过。具体证据见 outputs/host-doctor.log、simulator-doctor.log 和 `libero-first-doctor/doctor-report.json`。

**模型认证：**检测到 Codex CLI 0.166.0-alpha.6；默认 OpenRouter key 未找到。没有读取/复制私有认证文件，未验证其他 profile。用户尚未选定模型服务；需要运行探索时再沿当前认证设置处理。episode 数不等于 API 费用限制。

## 环境恢复与可移植命令

原工作区：`/home/mingqian/Documents/Codex/2026-11-05/https-github-com-robot-agent-exploration`。其中 `rax/runtime → ../work/runtime`，`rax/LIBERO-PRO → ../work/LIBERO-PRO`。原环境仍在，可优先复用。新克隆先执行 README 的恢复命令，设置 `RAX_STUDY` 和 `RAX_SOURCE_REPO`，然后在 `$RAX_SOURCE_REPO` 运行：

```bash
bash scripts/bootstrap_sources.sh
bash scripts/setup_host_env.sh
bash scripts/setup_libero_pro_env.sh
runtime/envs/host/bin/python scripts/setup_libero_pro_data.py
```

第一次机器上遇到并解决的问题：

- 没有 curl：用 Python urllib 下载 dependencies.lock 指定的 Miniforge 安装器，核验其中固定 SHA256，批量安装到 runtime/miniforge3 后再执行主环境脚本。
- 没有 make/编译器：在模拟器环境中通过 conda-forge 安装 make、gcc_linux-64、gxx_linux-64，运行安装脚本时指定其 CC/CXX。无需修改系统或已有 Isaac Sim 环境。
- torch 1.11 CPU wheel 在 glibc 2.43 上的 GNU_STACK 标记导致导入失败：备份后 `patchelf --clear-execstack`；目标和前后哈希在 outputs/torch-compat-patch.json。它是本地二进制兼容修复，不是上游代码变更，也不该在无此错误的平台盲目应用。
- 官方扰动数据脚本 320 文件均显示 unverified；改用相同固定 HF revision 的 Git blob/LFS 哈希独立验证，全数一致。原始 HF tree 保存在 work/hf_tree_page.json。

不需要重新跑已通过的所有测试，除非变更环境/实现或出现新故障。接续优先检查当前 GPU 状态；通过后按原本地指南执行最小 doctor 和 4 阶段试验：原探索/原测试 A，冻结原程序交换测试 B，交换布局少量追加探索 C，适配程序原场景回归 D。首次使用一个探索环境、一个 formal worker；5 个测试初态只做流程验证。

## 阅读与记录的继续方式

1. 查看 outputs/code_inventory.json 中的 review 状态，沿 Supervisor/Gateway/Sandbox/formal_worker、checkpoint/provider、各 benchmark 后端的顺序继续。
2. 恢复阅读快照：`python3 research/rax-adaptation/scripts/restore_reading_sources.py --all --include-skills`。
3. 原始 inventory 脚本从研究目录运行：`cd research/rax-adaptation`，然后 `python3 work/build_reading_ledger.py`。该脚本重用现有 JSON，不扫描运行环境。修改全文/局部白名单前确实阅读对应文件；不要用测试通过代替阅读。
4. outputs/verify_adaptation_offline.py 支持 `RAX_SOURCE_REPO` 环境变量、默认恢复目录和原工作区布局。旧报告内绝对路径是历史记录；新机器命令以 README 中的位置为准。
5. 记录每个适配试验的源/目标 collection、种子、模型、完成图与视觉设置、bundle 哈希、代码 diff、任务失败和基础设施错误、耗时与成本。不要把 B 的正式测试反馈喂给 C。

## 工具与远端保存注意

本次会话的 functions.exec 曾持续返回 IPC 解码错误，但内部工具实际执行成功；使用 notify 输出拿到了结果。若类似错误再次出现，先检查实际状态，不要盲目重复提交或其他写操作。

本机 Git HTTPS 没有推送认证，使用已连接的 GitHub 插件写入远端。任何后续推送仍应针对 `mingqian0850/rax`，不要写到作者上游。更新远端分支用预期 head 检查，避免覆盖其他 agent 的修改。

## 本次精简归档

只将研究笔记、阅读台账、论文阅读材料、验证脚本、日志和来源锁提交到 main；不推送本地 study 分支，也不镜像 10 个上游实现分支。原工作区约 9 GB 环境及缓存保留在本地。历史文档里的源码位置仍是当时的定位，不代表这些源码已放进 fork。代码索引是符号/阅读状态元数据，不是源码副本。Git 会压缩这些文本。
