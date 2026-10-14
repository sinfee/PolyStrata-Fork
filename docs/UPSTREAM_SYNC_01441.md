# Strata 0.1.44.1 同步记录

本分支基于 PolyStrata-Fork 的 `f0617d852f33bd2494ce7403d4275033cd8bc714`，合入 Strata `v0.1.43.1` 至 `v0.1.44.1` 的差异。目标标签提交为 `296b59d`，原始补丁与冲突记录保存在本地评测目录。

保留 `src/poly` 的 GLM、Qwen3.6、Gemma 与其他架构，以及 GLM 图像标记、图像嵌入、停止标记、工具协议、多模型切换、预热和 CPU 配额统计。IQ CUDA 内核同时保留 PolyStrata 的多矩阵槽位函数和上游新增的缩放参数。

安装器保留已有 PolyStrata 家族的路径。上游新增的同名 Qwen3.6 路径只用于没有已有家族定义的情形，避免遮蔽原来的安装流程。

增加 GLM 专用的 API 思考档位归一化：`high` 保持 `high`，`max` 保持 `max`，不再经 Qwen 的 `xhigh` 映射而意外升级到 Max。GLM 不提供 medium，显式 medium 归入 high；关闭思考的请求保持关闭。

CUDA 构建使用 VS 2022 Professional/MSVC 14.44、CUDA 13.4、sm_120，以及上游固定 ggml 修订 `3cf03257f219afbe7334045ff7c6a06ac68c627d`。CPU 专家线程池的 4000 项检查通过。API 与 GLM 安装流程的测试、模型实测和限制详见工作区的 `ai-stack/POLYSTRATA-LOCAL-GLM.md`。本次没有构建 HIP、SYCL、Metal 后端。

GLM 的生产源码和程序应独立于主 Strata 发布目录。不要用主 Strata 的 Python 服务端启动旧 PolyStrata 引擎；它会向 GLM 引擎添加不支持的 `--vision` 参数。
