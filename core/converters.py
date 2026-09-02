import json
import os
import re
import nbformat as nbf


def fix_math_equations(text: str) -> str:
    r"""Converts LaTeX delimiters to standard Markdown math formatting:
    \[...\]
-> $$...$$ (Display block equation)
    \(...\) -> $...$   (Inline equation)
    """
    text = re.sub(r"\\\[(.*?)\\\]", r"$$\1$$", text, flags=re.DOTALL)
    text = re.sub(r"\\\((.*?)\\\)", r"$\1$", text, flags=re.DOTALL)
    return text


def build_ipynb_bytes(files_ordered: list) -> bytes:
    """Combines Streamlit uploaded files into Jupyter Notebook bytes using exact code parsing logic."""
    combined_text = ""

    for idx, uploaded_file in enumerate(files_ordered):
        content = uploaded_file.getvalue().decode("utf-8")
        combined_text += f"\n\n<!-- Priority Index {idx}: {uploaded_file.name} -->\n\n" + content

    # 1. Normalize line endings (\r\n -> \n) so Windows files match regex correctly
    combined_text = combined_text.replace("\r\n", "\n").replace("\r", "\n")

    cleaned_text = fix_math_equations(combined_text)

    nb = nbf.v4.new_notebook()
    cells = []

    # Updated pattern to handle optional whitespace before newlines in fenced blocks
    pattern = r"```([a-zA-Z0-9_\-\+]*)\s*\n(.*?)```"
    last_end = 0
    CODE_LANGUAGES = {"python", "py", ""}

    for match in re.finditer(pattern, cleaned_text, re.DOTALL):
        start, end = match.span()
        lang = match.group(1).strip().lower()
        code_content = match.group(2).strip()

        # Add preceding Markdown text (and strip top-level Cell headers if present)
        markdown_text = cleaned_text[last_end:start].strip()
        markdown_text = re.sub(r"^#{1,6}\s*\*\*Cell\s*\d+:?.*?\*\*\n?", "", markdown_text, flags=re.IGNORECASE).strip()

        if markdown_text:
            cells.append(nbf.v4.new_markdown_cell(markdown_text))

        # Separate executable Python code cells from standard Markdown code blocks
        if lang in CODE_LANGUAGES:
            cells.append(nbf.v4.new_code_cell(code_content))
        else:
            lang_str = lang if lang else ""
            cells.append(
                nbf.v4.new_markdown_cell(f"```{lang_str}\n{code_content}\n```")
            )

        last_end = end

    # Add remaining text after the last code block
    remaining_text = cleaned_text[last_end:].strip()
    remaining_text = re.sub(r"^#{1,6}\s*\*\*Cell\s*\d+:?.*?\*\*\n?", "", remaining_text, flags=re.IGNORECASE).strip()

    if remaining_text:
        cells.append(nbf.v4.new_markdown_cell(remaining_text))

    if not cells and cleaned_text.strip():
        cells.append(nbf.v4.new_markdown_cell(cleaned_text.strip()))

    nb["cells"] = cells

    # Attach Google Colab & Kaggle compatibility metadata
    nb["metadata"] = {
        "colab": {"provenance": []},
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.10.0",
        },
    }

    return nbf.writes(nb).encode("utf-8")


def convert_txt_to_ipynb(
    input_files=["guide.txt"], output_ipynb_file="disaster_tweet_nlp1.ipynb"
):
    """Local CLI converter function directly using filesystem paths."""
    if isinstance(input_files, str):
        input_files = [input_files]

    combined_text = ""
    processed_count = 0

    for idx, file_path in enumerate(input_files):
        if not os.path.exists(file_path):
            print(f"⚠️ Warning: File '{file_path}' not found. Skipping...")
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            combined_text += f"\n\n<!-- Priority Index {idx}: {file_path} -->\n\n" + content
            processed_count += 1

    if processed_count == 0:
        print("❌ Error: None of the specified text files were found!")
        return

    combined_text = combined_text.replace("\r\n", "\n").replace("\r", "\n")
    cleaned_text = fix_math_equations(combined_text)

    nb = nbf.v4.new_notebook()
    cells = []

    pattern = r"```([a-zA-Z0-9_\-\+]*)\s*\n(.*?)```"
    last_end = 0
    CODE_LANGUAGES = {"python", "py", ""}

    for match in re.finditer(pattern, cleaned_text, re.DOTALL):
        start, end = match.span()
        lang = match.group(1).strip().lower()
        code_content = match.group(2).strip()

        markdown_text = cleaned_text[last_end:start].strip()
        markdown_text = re.sub(r"^#{1,6}\s*\*\*Cell\s*\d+:?.*?\*\*\n?", "", markdown_text, flags=re.IGNORECASE).strip()

        if markdown_text:
            cells.append(nbf.v4.new_markdown_cell(markdown_text))

        if lang in CODE_LANGUAGES:
            cells.append(nbf.v4.new_code_cell(code_content))
        else:
            lang_str = lang if lang else ""
            cells.append(
                nbf.v4.new_markdown_cell(f"```{lang_str}\n{code_content}\n```")
            )

        last_end = end

    remaining_text = cleaned_text[last_end:].strip()
    remaining_text = re.sub(r"^#{1,6}\s*\*\*Cell\s*\d+:?.*?\*\*\n?", "", remaining_text, flags=re.IGNORECASE).strip()

    if remaining_text:
        cells.append(nbf.v4.new_markdown_cell(remaining_text))

    nb["cells"] = cells

    with open(output_ipynb_file, "w", encoding="utf-8") as f:
        nbf.write(nb, f)

    print(
        f"✅ Success! Combined {processed_count} file(s) into '{output_ipynb_file}' with {len(cells)} cells."
    )


def build_md_from_ipynb_bytes(files_ordered: list) -> bytes:
    """Extracts Markdown and Python code blocks from uploaded .ipynb files into Markdown bytes."""
    md_content = []

    for idx, uploaded_file in enumerate(files_ordered):
        nb_data = json.loads(uploaded_file.getvalue().decode("utf-8"))
        md_content.append(f"<!-- Priority Index {idx}: {uploaded_file.name} -->\n\n")

        for cell in nb_data.get("cells", []):
            cell_type = cell.get("cell_type")
            source = "".join(cell.get("source", []))

            if cell_type == "markdown":
                md_content.append(source + "\n\n")
            elif cell_type == "code":
                md_content.append(f"```python\n{source}\n```\n\n")

    return "".join(md_content).encode("utf-8")


def build_md_bytes(files_ordered: list) -> bytes:
    """Combines text/markdown files directly into a Markdown file in memory."""
    combined_text = ""

    for idx, uploaded_file in enumerate(files_ordered):
        content = uploaded_file.getvalue().decode("utf-8")
        combined_text += f"\n\n<!-- Priority Index {idx}: {uploaded_file.name} -->\n\n" + content

    combined_text = combined_text.replace("\r\n", "\n").replace("\r", "\n")
    cleaned_text = fix_math_equations(combined_text)
    return cleaned_text.encode("utf-8")


if __name__ == "__main__":
    files_to_combine = ["guide.txt"]
    convert_txt_to_ipynb(files_to_combine, "disaster_tweet_nlp1.ipynb")