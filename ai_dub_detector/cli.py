import argparse
import os
import sys
from pathlib import Path

from .analyzer import analyze_file
from .model import DEFAULT_MODEL_ID
from .report import save_json, to_json, to_text


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="ai-dub-detector",
        description="分析视频或音频里的 AI 配音嫌疑。",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="分析一个本地视频或音频文件")
    analyze_parser.add_argument("input", type=Path)
    analyze_parser.add_argument(
        "--model-id",
        default=os.getenv("AI_DUB_MODEL_ID", DEFAULT_MODEL_ID),
    )
    analyze_parser.add_argument("--max-duration", type=float, default=90.0)
    analyze_parser.add_argument("--max-segments", type=int, default=12)
    analyze_parser.add_argument("--device", default="auto", help="auto, cpu, mps 或 cuda")
    analyze_parser.add_argument("--json", action="store_true", help="只输出 JSON")
    analyze_parser.add_argument("--output-json", type=Path, help="保存 JSON 报告")
    analyze_parser.add_argument("--keep-wav", type=Path, help="保留抽取后的 16k mono wav")

    telegram_parser = subparsers.add_parser("telegram", help="启动 Telegram bot")
    telegram_parser.add_argument(
        "--model-id",
        default=os.getenv("AI_DUB_MODEL_ID", DEFAULT_MODEL_ID),
    )
    telegram_parser.add_argument(
        "--work-dir",
        type=Path,
        default=Path(os.getenv("AI_DUB_WORK_DIR", "./_work")),
    )
    telegram_parser.add_argument("--max-duration", type=float, default=90.0)
    telegram_parser.add_argument("--max-segments", type=int, default=12)
    telegram_parser.add_argument("--device", default="auto")

    args = parser.parse_args(argv)

    try:
        if args.command == "analyze":
            result = analyze_file(
                args.input,
                model_id=args.model_id,
                max_duration=args.max_duration,
                max_segments=args.max_segments,
                keep_wav=args.keep_wav,
                device=args.device,
            )
            if args.output_json:
                save_json(result, args.output_json)
            print(to_json(result) if args.json else to_text(result))
            return 0

        if args.command == "telegram":
            from .telegram_bot import run_bot

            run_bot(
                model_id=args.model_id,
                work_dir=args.work_dir,
                max_duration=args.max_duration,
                max_segments=args.max_segments,
                device=args.device,
            )
            return 0
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
