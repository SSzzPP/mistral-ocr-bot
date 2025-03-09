from mistralai import Mistral
from pathlib import Path
import os
import base64
from mistralai import DocumentURLChunk
from mistralai.models import OCRResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
PDF_PATH = os.getenv("PDF_PATH")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

def replace_images_in_markdown(markdown_str: str, images_dict: dict) -> str:
    for img_name, img_path in images_dict.items():
        markdown_str = markdown_str.replace(f"![{img_name}]({img_name})", f"![{img_name}]({img_path})")
    return markdown_str

def save_ocr_results(ocr_response: OCRResponse, output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    all_markdowns = []
    for page in ocr_response.pages:
        page_images = {}
        for img in page.images:
            img_data = base64.b64decode(img.image_base64.split(',')[1])
            img_path = os.path.join(images_dir, f"{img.id}.png")
            with open(img_path, 'wb') as f:
                f.write(img_data)
            page_images[img.id] = f"images/{img.id}.png"
        
        page_markdown = replace_images_in_markdown(page.markdown, page_images)
        all_markdowns.append(page_markdown)
    
    with open(os.path.join(output_dir, "complete.md"), 'w', encoding='utf-8') as f:
        f.write("\n\n".join(all_markdowns))

def process_pdf() -> None:
    if not MISTRAL_API_KEY:
        raise ValueError("API key is not set. Please configure it in environment variables.")

    client = Mistral(api_key=MISTRAL_API_KEY)

    if not PDF_PATH:
        raise ValueError("PDF path is not set. Please configure it in environment variables.")
    
    pdf_file = Path(PDF_PATH)
    if not pdf_file.is_file():
        raise FileNotFoundError(f"PDF file does not exist: {PDF_PATH}")
    
    # Create output directory
    output_dir = f"ocr_results_{pdf_file.stem}"
    
    # Upload & process PDF
    try:
        uploaded_file = client.files.upload(
            file={
                "file_name": pdf_file.name,
                "content": pdf_file.read_bytes(),
            },
            purpose="ocr",
        )
        
        signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)
        pdf_response = client.ocr.process(
            document=DocumentURLChunk(document_url=signed_url.url), 
            model="mistral-ocr-latest", 
            include_image_base64=True
        )
        
        save_ocr_results(pdf_response, output_dir)
        print(f"OCR processing is complete. Results saved to: {output_dir}")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Call the process_pdf function
    process_pdf()