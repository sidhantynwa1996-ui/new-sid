#!/usr/bin/env python3
"""Skill: Convert files to Markdown using Microsoft's MarkItDown library.

Supports PDF, DOCX, PPTX, XLSX, HTML, images, audio, and more.

Usage:
    python convert_to_markdown.py <input_file> [-o output_file]

If no output file is specified, prints to stdout.
"""

import argparse
import sys
from pathlib import Path

from markitdown import MarkItDown


def convert_file(input_path: str, output_path: str | None = None) -> str:
    md = MarkItDown()
    result = md.convert(input_path)
    text = result.text_content

    if output_path:
        Path(output_path).write_text(text, encoding="utf-8")
        print(f"Converted '{input_path}' -> '{output_path}'")
    else:
        print(text)

    return text


def main():
    parser = argparse.ArgumentParser(
        description="Convert files to Markdown using MarkItDown."
    )
    parser.add_argument("input", help="Path to the input file to convert")
    parser.add_argument("-o", "--output", help="Path to save the markdown output")
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"Error: File '{args.input}' not found.", file=sys.stderr)
        sys.exit(1)

    convert_file(args.input, args.output)


if __name__ == "__main__":
    main()
