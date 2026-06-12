# Hermes 接入说明

这个项目不直接改 Hermes。第一版用 CLI 接入，路径清楚，出问题也容易查。

## 基本命令

```bash
/Users/eric/个人/AI配音识别器/.venv/bin/ai-dub-detector analyze "$FILE_PATH" --device cpu --calibration conservative
```

`$FILE_PATH` 是 Hermes 保存到本机的视频或音频文件。

## 建议给 Hermes 的工具说明

可以把下面这段作为 Hermes 的本地命令说明：

```text
当用户发送视频、语音或音频，并要求判断是否 AI 配音时：
1. 先把文件下载到本地。
2. 调用：
   /Users/eric/个人/AI配音识别器/.venv/bin/ai-dub-detector analyze "<本地文件路径>" --device cpu --calibration conservative
3. 把命令输出原样回复给用户。
4. 不要把结果说成定论，只说“嫌疑”或“筛查结果”。
```

## 保持 MacBook 在线

如果需要临时保持 Mac 不睡眠：

```bash
caffeinate -dimsu
```

也可以只在启动 Telegram bot 时保持：

```bash
caffeinate -dimsu /Users/eric/个人/AI配音识别器/.venv/bin/ai-dub-detector telegram
```

## 常见问题

### Hermes 已经有 Telegram bot，还需要本项目的 Telegram bot 吗？

不一定。Hermes 如果能下载 Telegram 文件并调用本地命令，就用 Hermes。这样消息入口只有一个。

本项目自带 Telegram bot 是备用方案。它适合不走 Hermes，直接让检测工具自己收文件和回复。

### MacBook 在外地能用吗？

能。Telegram bot 长轮询是主动连 Telegram 服务器，不需要公网 IP。酒店 Wi-Fi、手机热点、公司网络通常都能用。

### 结果为什么不写“确定是 AI”？

因为真实视频里的压缩、BGM、剪辑和降噪会影响模型。工具给的是筛查分数，适合帮你定位可疑片段。
