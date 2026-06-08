# 架构说明

## 模块

```text
Telegram / Hermes / CLI
        |
        v
ai_dub_detector.cli
        |
        v
ai_dub_detector.analyzer
        |
        +-- media.py        ffmpeg 抽音频
        +-- segmentation.py 片段切分
        +-- model.py        Hugging Face 模型推理
        +-- report.py       文本和 JSON 报告
```

## 分析流程

1. 接收本地文件路径。
2. 用 `ffmpeg` 抽取音频。
3. 转成 `16kHz mono wav`。
4. 读取 wav。
5. 按能量切出活跃音频片段。
6. 每段送入音频分类模型。
7. 把模型标签映射成 AI 嫌疑分。
8. 聚合片段分数。
9. 输出文本或 JSON。

默认运行数据都留在项目目录：

- 模型缓存：`.cache/huggingface`
- Telegram 下载和工作目录：`_work/`
- 临时抽音频目录：`_work/tmp`

## Telegram bot

Telegram 入口只负责通信：

1. 接收用户发来的文件。
2. 下载到 `_work/`。
3. 调用 `analyze_file()`。
4. 把文本报告发回 Telegram。
5. 删除临时文件。

这个设计方便后续替换入口。Hermes、NAS Webhook、网页上传接口都可以复用同一个核心分析函数。

## Hermes

Hermes 推荐只调用 CLI：

```bash
ai-dub-detector analyze "$FILE_PATH"
```

原因很简单：Hermes 本身已经负责 agent 调度和 Telegram 消息上下文，检测工具没必要知道 Hermes 的内部状态。

## 模型层

`model.py` 使用 `AutoFeatureExtractor` 和 `AutoModelForAudioClassification`。只要模型是 Hugging Face 的音频分类模型，大多可以直接替换：

```bash
ai-dub-detector analyze sample.mp4 --model-id your-org/your-model
```

标签映射逻辑：

- 标签包含 `fake`、`spoof`、`synthetic`、`generated`、`ai`、`clone`、`tts` 时计入假声分。
- 标签包含 `real`、`human`、`genuine`、`bonafide`、`authentic` 时，用 `1 - real_score`。
- 如果只有 `LABEL_0` / `LABEL_1`，暂时把第二类当成假声分。

最后一条只是兼容兜底。换模型后要看一次 `model_labels`。

## 后续可替换点

- VAD：换成 Silero VAD 或 pyannote。
- 模型：接入 AASIST2、WavLM、VoiceWukong 里表现较好的检测器。
- 聚合：从简单阈值升级成校准后的 ensemble。
- 部署：增加 Dockerfile 和 NAS compose。
