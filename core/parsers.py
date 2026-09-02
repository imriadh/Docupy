from __future__ import annotations

import re


def fix_math_equations(text: str) -> str:
    """Convert common LaTeX delimiters into Markdown-friendly math."""
    text = re.sub(r"\\\[(.*?)\\\]", r"$$\1$$", text, flags=re.DOTALL)
    text = re.sub(r"\\\((.*?)\\\)", r"$\1$", text, flags=re.DOTALL)
    return text


def parse_ai_text_blocks(raw_text: str) -> list[dict[str, str]]:
    """
    Split AI-generated text into alternating markdown and code blocks.

    Code fences are preserved, while everything else becomes markdown.
    """
    cleaned_text = fix_math_equations(raw_text)
    pattern = r"```([a-zA-Z0-9_\-\+]*)\n(.*?)```"

    blocks: list[dict[str, str]] = []
    last_end = 0

    for match in re.finditer(pattern, cleaned_text, re.DOTALL):
        start, end = match.span()
        lang = match.group(1).strip().lower()
        content = match.group(2).strip()

        markdown_text = cleaned_text[last_end:start].strip()
        if markdown_text:
            blocks.append({"type": "markdown", "content": markdown_text})

        blocks.append({"type": "code", "lang": lang, "content": content})
        last_end = end

    remaining_text = cleaned_text[last_end:].strip()
    if remaining_text:
        blocks.append({"type": "markdown", "content": remaining_text})

    return blocks

