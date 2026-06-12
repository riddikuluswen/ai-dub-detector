# AI 配音识别器

一个本地运行的 AI 配音嫌疑分析工具。它可以分析视频、语音或音频文件，输出“低 / 中 / 高 / 样本不足”的筛查结果，并列出最可疑的时间段。

项目目标很明确：帮你快速判断一段中文视频里的配音是不是很像 AI 配音。它不是法医工具，也不能给出绝对结论。

## 适合做什么

- 从 Telegram 发一段视频给 bot，让 MacBook 本地分析后回传结果。
- 在命令行批量分析视频或音频。
- 作为 Hermes agent 的本地命令，由 Hermes 负责收消息和调度。
- 后续迁移到 NAS、Docker 或手机端。

## 当前版本

- 本地抽音频：`ffmpeg`
- 音频统一格式：`16kHz mono wav`
- 片段切分：基于能量的轻量 VAD
- 模型推理：Hugging Face `transformers`
- 默认模型：`Hemgg/Deepfake-audio-detection`
- Telegram bot：可选功能，使用长轮询，不需要公网 IP
- 模型缓存：默认放在项目内 `.cache/huggingface`

默认模型主要基于英文数据训练。它可以跑中文音频，但结果只能当筛查信号。后续更适合接入 VoiceWukong / ADD / Codecfake 相关模型或自己微调的中文模型。

## 安装

先装 `ffmpeg`：

```bash
brew install ffmpeg
```

创建虚拟环境：

```bash
cd /Users/eric/个人/AI配音识别器
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

如果要用 Telegram bot：

```bash
pip install -e '.[telegram]'
```

## 命令行使用

```bash
ai-dub-detector analyze ./sample.mp4
```

保存 JSON 报告：

```bash
ai-dub-detector analyze ./sample.mp4 --output-json reports/sample.json
```

只输出 JSON：

```bash
ai-dub-detector analyze ./sample.mp4 --json
```

指定模型：

```bash
ai-dub-detector analyze ./sample.mp4 --model-id Hemgg/Deepfake-audio-detection
```

只分析前 60 秒：

```bash
ai-dub-detector analyze ./sample.mp4 --max-duration 60
```

默认使用保守阈值，优先降低真人口播被误报成 AI 的概率。也可以手动切换：

```bash
ai-dub-detector analyze ./sample.mp4 --calibration balanced
ai-dub-detector analyze ./sample.mp4 --calibration sensitive
```

Apple Silicon Mac 如果 `mps` 有兼容问题，可以强制 CPU：

```bash
ai-dub-detector analyze ./sample.mp4 --device cpu
```

## Telegram bot 使用

复制环境变量模板：

```bash
cp .env.example .env
```

把 `.env` 里的 `TELEGRAM_BOT_TOKEN` 换成 BotFather 给你的 token。然后启动：

```bash
source .venv/bin/activate
export $(grep -v '^#' .env | xargs)
ai-dub-detector telegram
```

手机 Telegram 给 bot 发送视频、语音、音频文件即可。

默认临时文件在项目内 `_work/`，模型下载缓存在项目内 `.cache/huggingface`。这两个目录都不会提交到 GitHub。

如果只允许自己的 Telegram 账号使用，设置：

```bash
AI_DUB_ALLOWED_USER_IDS=123456789
```

多个账号用逗号分隔。

## Hermes 接入方式

第一版不绑定 Hermes 内部接口。Hermes 只要能调用本地命令，就可以这样用：

```bash
/Users/eric/个人/AI配音识别器/.venv/bin/ai-dub-detector analyze "$FILE_PATH" --device cpu --calibration conservative
```

`$FILE_PATH` 是 Hermes 下载到本地的视频或音频文件路径。更完整的接入说明在 [docs/hermes.md](docs/hermes.md)。

## 输出示例

```text
AI 配音嫌疑：高

综合分：0.82
最高片段分：0.91
有效人声：38.2 秒
分析片段：5 段
模型：Hemgg/Deepfake-audio-detection

可疑片段：
00:04-00:11  0.89  fake:0.89
00:18-00:26  0.84  fake:0.84
00:31-00:39  0.78  fake:0.78

备注：
- 模型输出是筛查分数，不适合作为单独证据。
```

## 结果怎么看

- `高`：多个片段分数明显偏高，值得人工复核。
- `中`：有可疑信号，但音频质量、BGM、压缩或模型泛化都可能影响结果。
- `低`：当前模型没有发现明显 AI 配音信号。
- `样本不足`：人声太短或太弱，结果没有参考价值。

阈值模式：

- `conservative`：默认模式，降低误报。适合中文真人口播筛查。
- `balanced`：更接近普通二分类阈值。
- `sensitive`：更容易报可疑，适合宁可多查也不想漏掉的场景。

不要把分数当成“AI 概率的真值”。短视频平台的二次压缩、背景音乐、变速、降噪、混响、剪辑都会影响模型。

## 开发

```bash
pip install -e '.[dev,telegram]'
pytest
ruff check .
```

## 后续计划

- 接入多个模型，做 ensemble 分数。
- 增加更好的 VAD 和人声/BGM 分离。
- 支持批量目录分析。
- 增加 Docker 部署文件，方便迁移到 NAS。
- 评估中文数据集上的表现，优先看 VoiceWukong、ADD、Codecfake 相关模型。

## 许可

MIT
