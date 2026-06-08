# GitHub 发布前检查

## 发布前

- [ ] 确认 `.env` 没有提交。
- [ ] 确认没有提交测试视频、音频、模型缓存。
- [ ] 运行 `pytest`。
- [ ] 运行 `ruff check .`。
- [ ] 用一个短视频跑一次 CLI。
- [ ] 用 Telegram bot 收发一次文件。
- [ ] README 里不要写“准确识别”。
- [ ] README 里保留误判说明。

## 建议仓库设置

- Visibility: Public
- License: MIT
- Topics:
  - `audio-deepfake-detection`
  - `ai-voice-detection`
  - `telegram-bot`
  - `ffmpeg`
  - `chinese-audio`

## 建议仓库简介

```text
Local AI voice-over suspicion checker for videos and Telegram bot workflows.
```

## 首次提交建议

```bash
git init
git add .
git commit -m "Initial AI dub detector"
```

然后在 GitHub 创建 public repo，再加远端：

```bash
git remote add origin git@github.com:<user>/<repo>.git
git branch -M main
git push -u origin main
```
