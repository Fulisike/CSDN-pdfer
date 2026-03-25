# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python tool that converts CSDN blog HTML content to both Markdown and PDF formats. It downloads embedded images locally and replaces their references in the output.

## Core Architecture

**Main class: `HtmlToMdPdfConverter`** (main.py:10-142)

The conversion pipeline:
1. HTML parsing via BeautifulSoup with a CSS selector to extract target content
2. Image discovery and download to `output_dir/images/` (named by MD5 hash)
3. HTML to Markdown conversion using markdownify
4. Markdown to styled HTML for PDF generation
5. PDF output via pdfkit (wrapping wkhtmltopdf)

## Dependencies

Install required packages:
```bash
pip install requests beautifulsoup4 markdownify markdown pdfkit
```

External dependency: **wkhtmltopdf** must be installed separately. On Windows, provide the path in `HtmlToMdPdfConverter.__init__()`.

## Running the Script

The script reads from `example.html` and outputs to the `results/` directory:

```bash
python main.py
```

To process different HTML, modify the `if __name__ == "__main__"` section in main.py:165-179.

## Key Configuration

- **wkhtmltopdf path**: Must be provided on Windows (line 165)
- **CSS selector**: Default is `#content_views` for CSDN articles (line 177)
- **Output directory**: Defaults to `results/` (line 168)
- **Images**: Stored in `results/images/` with MD5-based filenames

## Notes

- The target HTML format is specifically designed for CSDN blog posts (`#content_views` selector)
- Image URLs can be relative or absolute - `urljoin` handles both
- PDF styling is embedded directly in the Python string (lines 111-127)
