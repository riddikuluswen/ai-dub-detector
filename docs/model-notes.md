# 模型说明

## 默认模型

默认模型是：

```text
Hemgg/Deepfake-audio-detection
```

它是 Hugging Face 上的开源音频分类模型，模型卡写明基于 `facebook/wav2vec2-base` 微调，输入音频约 `16kHz`。模型卡也说明训练数据是 multi-ethnic English dataset，所以中文视频上的表现需要谨慎看。

## 为什么还先用它

第一版需要先把完整链路跑起来：收文件、抽音频、切片、推理、报告、Telegram 回传。默认模型体积不算离谱，能直接用 `transformers` 加载，适合做 MVP。

## 中文检测的后续方向

后续更应该评估这些方向：

- VoiceWukong：覆盖中英文 deepfake voice benchmark。
- ADD 2022 / ADD 2023：中文音频深伪检测挑战。
- Codecfake：面向 codec-based / audio language model 生成语音。
- AASIST2 / WavLM / Wav2Vec2 ensemble：多个模型交叉判断。

## 换模型

命令行：

```bash
ai-dub-detector analyze sample.mp4 --model-id your-org/your-model
```

环境变量：

```bash
AI_DUB_MODEL_ID=your-org/your-model
```

## 看模型标签

JSON 报告里有 `model_labels` 和每段的 `raw_scores`。换模型后先看这两个字段，确认哪一类代表 fake。

如果模型只给 `LABEL_0` / `LABEL_1`，当前代码会把第二类当成 fake。这只是兜底，不应该长期依赖。
