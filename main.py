"""
CLI for the Markdown → HTML Static Site Generator.
Usage:
    python main.py input.md output.html [--css style.css] [--in-enc utf-8] [--out-enc utf-8]
"""

import argparse
from converter import run


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="M323 Static Site Generator — Markdown to HTML"
    )
    parser.add_argument("input",  help="Path to input Markdown file")
    parser.add_argument("output", help="Path for output HTML file")
    parser.add_argument("--css",     default=None, help="Optional CSS file to inline")
    parser.add_argument("--in-enc",  default="utf-8", dest="in_enc",  help="Input encoding (default: utf-8)")
    parser.add_argument("--out-enc", default="utf-8", dest="out_enc", help="Output encoding (default: utf-8)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run(
        input_path=args.input,
        output_path=args.output,
        css_path=args.css,
        input_encoding=args.in_enc,
        output_encoding=args.out_enc,
    )


if __name__ == "__main__":
    main()