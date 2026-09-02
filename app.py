import io
import json
import re
import nbformat as nbf
import streamlit as st

# Page setup
st.set_page_config(
    page_title="DocuPy - Document Converter",
    page_icon="📚",
    layout="centered",
)


def fix_math_equations(text: str) -> str:
    r"""Converts LaTeX delimiters to standard Markdown math formatting:
    \[...\] -> $$...$$ (Display block equation)
    \(...\) -> $...$   (Inline equation)
    """
    text = re.sub(r"\\\[(.*?)\\\]", r"$$\1$$", text, flags=re.DOTALL)
    text = re.sub(r"\\\((.*?)\\\)", r"$\1$", text, flags=re.DOTALL)
    return text


def build_ipynb_bytes(files_ordered: list) -> bytes:
    """Combines text files in priority order (0 to N) and converts them into an .ipynb file in memory."""
    combined_text = ""

    for idx, uploaded_file in enumerate(files_ordered):
        content = uploaded_file.getvalue().decode("utf-8")
        combined_text += f"\n\n<!-- Priority Index {idx}: {uploaded_file.name} -->\n\n" + content

    cleaned_text = fix_math_equations(combined_text)

    nb = nbf.v4.new_notebook()
    cells = []

    pattern = r"```([a-zA-Z0-9_\-\+]*)\n(.*?)```"
    last_end = 0
    CODE_LANGUAGES = {"python", "py"}

    for match in re.finditer(pattern, cleaned_text, re.DOTALL):
        start, end = match.span()
        lang = match.group(1).strip().lower()
        code_content = match.group(2).strip()

        markdown_text = cleaned_text[last_end:start].strip()
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
    if remaining_text:
        cells.append(nbf.v4.new_markdown_cell(remaining_text))

    nb["cells"] = cells
    return nbf.writes(nb).encode("utf-8")


def build_md_bytes(files_ordered: list) -> bytes:
    """Combines text/markdown files in priority order (0 to N) directly into a Markdown file in memory."""
    combined_text = ""

    for idx, uploaded_file in enumerate(files_ordered):
        content = uploaded_file.getvalue().decode("utf-8")
        combined_text += f"\n\n<!-- Priority Index {idx}: {uploaded_file.name} -->\n\n" + content

    cleaned_text = fix_math_equations(combined_text)
    return cleaned_text.encode("utf-8")


# --- UI Layout ---
st.title("📚 DocuPy Converter")
st.markdown("Upload single or multiple files to combine and convert them to **Jupyter Notebook (`.ipynb`)** or **Markdown (`.md`)**.")

# 1. Multi-file uploader
uploaded_files = st.file_uploader(
    "Choose text/markdown files", type=["txt", "md"], accept_multiple_files=True
)

if uploaded_files:
    st.subheader("⚙️ Settings & Priority")
    st.caption(
        "Files are merged from top to bottom. The file at **Index 0** will have highest priority and appear first."
    )

    current_names = [f.name for f in uploaded_files]
    file_map = {f.name: f for f in uploaded_files}

    # 2. Re-order priority control
    ordered_names = st.multiselect(
        "Re-order files to set priority (First item selected = Index 0):",
        options=current_names,
        default=current_names,
    )

    ordered_files = [file_map[name] for name in ordered_names if name in file_map]

    if ordered_files:
        st.write("---")

        # 3. Target Output Format Selection
        export_format = st.radio(
            "Select Output Format:",
            options=["Jupyter Notebook (.ipynb)", "Markdown (.md)"],
            horizontal=True,
        )

        default_name = "Combined_Notes.ipynb" if export_format == "Jupyter Notebook (.ipynb)" else "Combined_Notes.md"
        output_filename = st.text_input("Output File Name", value=default_name)

        if st.button("🚀 Process & Convert", type="primary"):
            with st.spinner("Processing files and formatting equations..."):
                if export_format == "Jupyter Notebook (.ipynb)":
                    if not output_filename.endswith(".ipynb"):
                        output_filename += ".ipynb"
                    file_bytes = build_ipynb_bytes(ordered_files)
                    mime_type = "application/x-ipynb+json"
                else:
                    if not output_filename.endswith(".md"):
                        output_filename += ".md"
                    file_bytes = build_md_bytes(ordered_files)
                    mime_type = "text/markdown"

            st.success(f"Successfully processed {len(ordered_files)} file(s)!")

            # 4. Download output file
            st.download_button(
                label=f"📥 Download {export_format.split()[0]} File",
                data=file_bytes,
                file_name=output_filename,
                mime=mime_type,
            )
else:
    st.info("Please upload at least one `.txt` or `.md` file to begin.")