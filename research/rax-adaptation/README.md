# RAX 本体与场景适配研究档案

保存日期：2026-11-05。研究者目标：阅读 RAX 论文和代码，持续回答“作者怎样适配新机器人本体/应用场景”，并在 RTX 4070 Laptop 上使用现成仿真 benchmark 验证。

**接手先读 [HANDOFF.md](HANDOFF.md)。** 本档案保存于 fork 的 `main`。按用户最新要求，只提交研究必需内容；不镜像上游实现分支，不提交源码快照、仿真资源或环境。运行所需代码从官方仓库按固定 commit 单独下载。原机器的 `study/libero-pro-native` 仅为本地工作分支，不推送。

## 主要入口

| 文件 | 用途 |
| --- | --- |
| [适配机制与代码阅读](outputs/RAX适配机制与代码阅读.md) | 核心结论、源码证据和局限 |
| [本地验证指南](outputs/本地验证指南.md) | 原场景、交换布局、追加探索、原场景回归四阶段方案 |
| [环境验收](outputs/环境验收.md) | 安装、修复、测试结果与 GPU 阻塞 |
| [阅读进度](outputs/阅读进度.md) | 已做工作、发现与下一步 |
| [阅读覆盖](outputs/阅读覆盖.md) | 明确区分全文阅读、局部阅读、静态索引 |
| [全代码导航](outputs/全代码导航.md) | 761 个不同代码文件的符号与分支定位 |
| [实验记录模板](outputs/实验记录模板.json) | 试验条件、bundle 哈希、结果和代码变化 |
| [来源版本锁](outputs/source-lock.json) | RAX 各分支、LIBERO、数据、技能库与论文版本 |

`outputs/` 保存上一轮全部交付物，包括原始成功/失败日志、环境包清单、逐文件数据校验和离线检查结果。历史日志中的绝对路径和时间保留原样；它们记录原机器现场，不是新机器的路径配置。新工作区应使用下述相对路径。

## 换一个工作区继续

```bash
git clone https://github.com/mingqian0850/rax.git
cd rax
RAX_REPO="$PWD"
RAX_STUDY="$RAX_REPO/research/rax-adaptation"
python3 "$RAX_STUDY/scripts/restore_reading_sources.py"
export RAX_SOURCE_REPO="$RAX_STUDY/work/upstream-rax"
cd "$RAX_SOURCE_REPO"
```

恢复脚本默认只获取官方 LIBERO-PRO native 固定版本，保存在被 Git 忽略的 `work/upstream-rax/`。不安装环境、不启动模型、不执行机器人动作。`--all` 可恢复全部阅读快照，`--include-skills` 可额外恢复技能库；需要 Python 3.12 或以上。恢复后从 `$RAX_SOURCE_REPO` 运行作者的安装和实验脚本。

如果当前机器仍有先前的环境，`rax/runtime` 已链接到原工作区 `work/runtime`，可以直接运行：

```bash
runtime/envs/host/bin/python "$RAX_STUDY/outputs/verify_adaptation_offline.py"
bash scripts/doctor.sh
```

新机器需要按恢复的官方源码中的 `docs/SETUP.md` 与 `dependencies.lock` 重建环境。主流程为 `bootstrap_sources.sh`、`setup_host_env.sh`、`setup_libero_pro_env.sh`、`setup_libero_pro_data.py`，见 [接续说明中的环境恢复步骤](HANDOFF.md#环境恢复与可移植命令)。安装器校验、编译工具和旧版 torch 兼容问题都有记录。不要把存在包清单解释成模拟器已能运行。

运行原《本地验证指南》时，把其中历史绝对 `cd` 路径改为 `$RAX_SOURCE_REPO`；离线脚本使用 `$RAX_STUDY/outputs/verify_adaptation_offline.py`。其余 RAX 命令从官方源码目录运行。

## 保存范围

| 原工作区内容 | 在 fork 中如何保存 |
| --- | --- |
| 所有 outputs 研究产物 | 本目录 `outputs/`；原始校验清单见 original-output-manifest.json |
| 自写阅读/索引脚本及中间 JSON | `work/inventory.py`、`work/build_reading_ledger.py` 和相关 JSON |
| 论文 HTML 与分节文本 | `work/paper/`，来源、许可证和提取说明见 SOURCES.md |
| 全部 RAX 分支阅读快照 | 只保存官方 URL + commit 锁；`--all` 按需重建被忽略的 `work/branches/` |
| skills-lib 快照 | 固定 commit + 恢复脚本；不重复提交第三方源码和图片 |
| LIBERO 源码与扰动数据 | 固定源码/数据 revision、320 文件校验结果与官方恢复脚本 |
| 约 9 GB 的环境、缓存、安装器、torch 原文件备份 | 留在原机器；保存包锁、下载来源、校验值、修复记录，不直接上传二进制环境 |
| 逐个环境/缓存文件的现场清单 | 仅留原机器 `work/workspace-file-manifest.jsonl.gz`；可再生成的大清单不上传 |

原始工作区未删除。没有把密钥、登录文件或本机 agent 会话目录加入档案。当前没有真实 benchmark 成功率，也没有运行付费模型探索。
