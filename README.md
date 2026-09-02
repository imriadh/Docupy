# DocuPy

DocuPy converts AI-generated text into Markdown, PDF, or Jupyter notebooks, and also converts Jupyter notebooks back into Markdown or PDF.

## Features

- Text or file input for AI-generated content
- Direct export to `.md`, `.pdf`, or `.ipynb`
- Converts fenced Python code into notebook code cells
- Preserves non-Python fenced code as Markdown
- Converts `.ipynb` files into `.md` or `.pdf`
- Optional output extraction for notebook stream outputs

## Project Structure

```text
DocuPy/
├── core/
│   ├── __init__.py
│   ├── parsers.py
│   └── converters.py
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy

This app is ready for Streamlit Community Cloud.

Set the app entry point to `app.py` and include `requirements.txt` in the repository root.
# Docupy
# Docupy
