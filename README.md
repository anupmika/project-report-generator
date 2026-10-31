<<<<<<< HEAD
# project-report-generator
Generate professional project reports automatically by uploading predefined templates or formats and populating them with project-specific information.
=======
# Project Report Generator

A Python tool to generate comprehensive project reports from GitHub repository links strictly according to a custom DOCX format template. Reports are generated in **DOCX** and **PDF** formats only. All dependencies are managed using [uv](https://docs.astral.sh/uv/) in a local virtual environment - nothing is installed system-wide.

## Features

- Clone or analyze GitHub repositories
- Upload custom project report format template in **DOCX** format only
- Generate reports strictly according to the provided template
- Support for **DOCX** and **PDF** output formats
- Streamlit web UI for easy use
- CLI interface also available

## Setup with uv (No system installation)

This project uses `uv` for dependency management without installing packages globally:

```bash
# Create a virtual environment in the project
uv venv

# Activate the virtual environment
source .venv/bin/activate  # On Linux/macOS
# or
.venv\Scripts\activate     # On Windows

# Install dependencies from pyproject.toml
uv sync

# Or add dependencies individually
uv add httpx gitpython pydantic rich jinja2 click pygithub python-docx weasyprint markdown streamlit
```

**Note:** All packages are installed only in the local `.venv` directory. Never use `pip install` globally.

## Usage

### Streamlit Web UI (Recommended)

```bash
# Run the Streamlit app
streamlit run app.py
```

The UI allows you to:
1. Enter a GitHub repository URL
2. Upload your project report format template (DOCX only)
3. Select output format (DOCX or PDF)
4. Generate and download the final report

### Command Line Interface

```bash
# Generate a DOCX report from template
python -m project_report https://github.com/owner/repo -t template.docx -f docx -o report.docx

# Generate a PDF report from template
python -m project_report https://github.com/owner/repo -t template.docx -f pdf -o report.pdf
```

## Template Placeholders

Use these placeholders in your DOCX template to be replaced with actual data:

- `{{REPO_NAME}}` - Repository name (owner/repo)
- `{{REPO_URL}}` - Repository URL
- `{{GENERATED_DATE}}` - Report generation date/time
- `{{COMMIT_SHA}}` - Latest commit SHA
- `{{COMMIT_MESSAGE}}` - Latest commit message
- `{{AUTHOR}}` - Commit author
- `{{COMMIT_DATE}}` - Commit date
- `{{BRANCH}}` - Active branch
- `{{COMMIT_COUNT}}` - Total commits
- `{{TOTAL_FILES}}` - Total files
- `{{TOTAL_SIZE}}` - Total repository size

## Project Structure

```
project-report/
├── pyproject.toml      # Project configuration and dependencies (managed by uv)
├── README.md           # This file
├── app.py              # Streamlit web UI
├── src/
│   └── project_report/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py      # Command-line interface
│       ├── analyzer.py # Repository analysis logic
│       ├── generator.py # Report generation (DOCX/PDF from template)
│       ├── formatter.py # Template parsing
│       └── utils.py    # Utility functions
└── .venv/              # Local virtual environment (created by uv, gitignored)
```

## Dependencies

All dependencies are managed locally with uv - see `pyproject.toml` for details.


>>>>>>> 1c37aef (refactor: move package from src/project_report to src)
