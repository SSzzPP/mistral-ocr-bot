# mistral-ocr-bot

Use the Mistral OCR for processing PDFs and images to markdown.

## Installation

Install the required dependencies:

```bash
pip install mistralai
```

## Usage

1. Set up your Mistral API key
2. Edit environment variable and replace "Your_API_KEY"
3. Run the script

```python
python mistral_ocr.py
```

## Output Files

The script will create a folder named `ocr_results_[PDF filename]` in the working directory, containing:

- `complete.md`: The extracted text content in markdown format
- `images/`: (if images are found): A directory containing any extracted images
