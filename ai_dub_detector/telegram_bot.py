import asyncio
import os
import tempfile
from pathlib import Path
from typing import Optional

from .analyzer import analyze_file
from .report import to_text


def run_bot(
    model_id: str,
    work_dir: Path,
    max_duration: float,
    max_segments: int,
    device: str,
    calibration: str,
) -> None:
    try:
        from telegram import Update
        from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("缺少 Telegram 依赖。请安装: pip install -e '.[telegram]'") from exc

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("缺少 TELEGRAM_BOT_TOKEN。请先在环境变量或 .env 里配置。")

    allowed_users = _allowed_users(os.getenv("AI_DUB_ALLOWED_USER_IDS"))
    work_dir = work_dir.expanduser().resolve()
    work_dir.mkdir(parents=True, exist_ok=True)

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not _is_allowed(update, allowed_users):
            return
        await update.message.reply_text(
            "发一段视频、语音或音频文件过来，我会回传 AI 配音嫌疑报告。"
        )

    async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not _is_allowed(update, allowed_users):
            return

        message = update.message
        media = message.video or message.voice or message.audio or message.document
        if media is None:
            await message.reply_text("请发送视频、语音、音频文件，或把视频当文件发过来。")
            return

        status = await message.reply_text(
            "收到，正在下载和分析。第一次运行会下载模型，可能慢一些。"
        )
        file = await context.bot.get_file(media.file_id)
        suffix = _suffix_from_media(media)
        with tempfile.NamedTemporaryFile(dir=work_dir, suffix=suffix, delete=False) as tmp:
            input_path = Path(tmp.name)

        try:
            await file.download_to_drive(custom_path=str(input_path))
            result = await asyncio.to_thread(
                analyze_file,
                input_path,
                model_id,
                max_duration,
                max_segments,
                None,
                device,
                calibration,
            )
            await status.edit_text(to_text(result)[:3900])
        except Exception as exc:
            await status.edit_text(f"分析失败：{exc}")
        finally:
            input_path.unlink(missing_ok=True)

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(
            filters.VIDEO | filters.VOICE | filters.AUDIO | filters.Document.ALL,
            handle_media,
        )
    )
    application.run_polling(allowed_updates=Update.ALL_TYPES)


def _allowed_users(raw: Optional[str]) -> set[int]:
    if not raw:
        return set()
    users = set()
    for item in raw.split(","):
        item = item.strip()
        if item:
            users.add(int(item))
    return users


def _is_allowed(update, allowed_users: set[int]) -> bool:
    if not allowed_users:
        return True
    user = update.effective_user
    return bool(user and user.id in allowed_users)


def _suffix_from_media(media) -> str:
    name = getattr(media, "file_name", None)
    if name and "." in name:
        return "." + name.rsplit(".", 1)[-1]
    mime = getattr(media, "mime_type", None) or ""
    if "ogg" in mime:
        return ".ogg"
    if "mp4" in mime:
        return ".mp4"
    if "mpeg" in mime or "mp3" in mime:
        return ".mp3"
    if "wav" in mime:
        return ".wav"
    return ".bin"
