import sys
from pathlib import Path
import streamlit as st

# Path resolution for .core folder imports
sys.path.append(str(Path(__file__).parent / ".core"))

from core.converters import (
    build_ipynb_bytes,
    build_md_bytes,
    build_md_from_ipynb_bytes,
)

st.set_page_config(
    page_title="DocuPy - Document Converter",
    page_icon="📚",
    layout="centered",
)

st.title("📚 DocuPy Converter")
st.markdown("Upload files to merge and convert between **Jupyter Notebook (`.ipynb`)** and **Markdown (`.md`)** formats.")

uploaded_files = st.file_uploader(
    "Choose text, markdown, or notebook files",
    type=["txt", "md", "ipynb"],
    accept_multiple_files=True,
)

if uploaded_files:
    st.subheader("⚙️ Settings & Priority")
    st.caption("Files are merged from top to bottom. The file at **Index 0** will have highest priority.")

    current_names = [f.name for f in uploaded_files]
    file_map = {f.name: f for f in uploaded_files}

    ordered_names = st.multiselect(
        "Re-order files to set priority (First item selected = Index 0):",
        options=current_names,
        default=current_names,
    )

    ordered_files = [file_map[name] for name in ordered_names if name in file_map]

    if ordered_files:
        st.write("---")

        has_ipynb = any(f.name.endswith(".ipynb") for f in ordered_files)
        has_txt_md = any(f.name.endswith((".txt", ".md")) for f in ordered_files)

        if has_ipynb and has_txt_md:
            st.warning("⚠️ You uploaded both `.ipynb` and `.txt`/`.md` files. Please upload files of the same type for uniform conversion.")
        else:
            options = ["Markdown (.md)"] if has_ipynb else ["Jupyter Notebook (.ipynb)", "Markdown (.md)"]

            export_format = st.radio(
                "Select Output Format:",
                options=options,
                horizontal=True,
            )

            default_name = (
                "disaster_tweet_nlp.ipynb"
                if export_format == "Jupyter Notebook (.ipynb)"
                else "disaster_tweet_nlp.md"
            )
            output_filename = st.text_input("Output File Name", value=default_name)

            if st.button("🚀 Process & Convert", type="primary"):
                with st.spinner("Processing files and formatting content..."):
                    try:
                        if export_format == "Jupyter Notebook (.ipynb)":
                            if not output_filename.endswith(".ipynb"):
                                output_filename += ".ipynb"
                            file_bytes = build_ipynb_bytes(ordered_files)
                            mime_type = "application/x-ipynb+json"
                        else:
                            if not output_filename.endswith(".md"):
                                output_filename += ".md"

                            if has_ipynb:
                                file_bytes = build_md_from_ipynb_bytes(ordered_files)
                            else:
                                file_bytes = build_md_bytes(ordered_files)

                            mime_type = "text/markdown"

                        st.success(f"Successfully processed {len(ordered_files)} file(s)!")

                        st.download_button(
                            label=f"📥 Download {export_format.split()[0]} File",
                            data=file_bytes,
                            file_name=output_filename,
                            mime=mime_type,
                        )
                    except Exception as e:
                        st.error(f"An error occurred during conversion: {str(e)}")
else:
    st.info("Please upload at least one `.txt`, `.md`, or `.ipynb` file to begin.")