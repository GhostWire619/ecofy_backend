import os
from google.cloud import documentai_v1 as docai
from google import genai
from google.genai import types
from dotenv import load_dotenv
import concurrent.futures
import time

# Load environment variables from .env file
load_dotenv()

class DocumentProcessingService:
    def __init__(self, project_id, location, processor_id, gemini_api_key):
        self.project_id = project_id
        self.location = location
        self.processor_id = processor_id
        
        # Initialize Document AI Client
        self.docai_client = docai.DocumentProcessorServiceClient()
        self.resource_name = self.docai_client.processor_path(project_id, location, processor_id)
        
        # Initialize Gemini Client
        self.gemini_client = genai.Client(api_key=gemini_api_key)

    def extract_text_with_docai(self, file_path, mime_type="application/pdf"):
        """Extracts raw text from a document using Document AI."""
        with open(file_path, "rb") as image:
            image_content = image.read()

        raw_document = docai.RawDocument(content=image_content, mime_type=mime_type)
        request = docai.ProcessRequest(name=self.resource_name, raw_document=raw_document)
        
        result = self.docai_client.process_document(request=request)
        return result.document.text

    def get_csv_from_gemini(self, extracted_text):
        """Passes extracted text to Gemini to format as CSV."""
        prompt = (
            "You are a data extraction assistant. Below is text extracted from a document via OCR. "
            "Identify the key data points (e.g., dates, amounts, items) and return them strictly in CSV format. "
            "Do not include any conversational text or markdown blocks, just the raw CSV content.\n\n"
            f"Extracted Text:\n{extracted_text}"
        )

        response = self.gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text

    def process_to_csv(self, input_path, output_csv_path):
        """Orchestrates the full workflow."""
        print(f"--- Extracting text from {input_path} ---")
        text = self.extract_text_with_docai(input_path)
        
        print("--- Converting text to CSV via Gemini ---")
        csv_data = self.get_csv_from_gemini(text)
        
        with open(output_csv_path, "w", encoding="utf-8") as f:
            f.write(csv_data)
        
        print(f"--- Successfully saved output to {output_csv_path} ---")

    def bulk_process_to_csv(self, input_paths, output_csv_paths, max_workers=5):
        """Processes multiple documents in parallel and saves each to a CSV."""
        if len(input_paths) != len(output_csv_paths):
            raise ValueError("Input paths and output paths must have the same length.")
        
        def process_single(input_path, output_path):
            try:
                print(f"--- Processing {input_path} ---")
                text = self.extract_text_with_docai(input_path)
                csv_data = self.get_csv_from_gemini(text)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(csv_data)
                print(f"--- Saved {output_path} ---")
                time.sleep(1)  # Small delay to respect API limits
            except Exception as e:
                print(f"--- Error processing {input_path}: {e} ---")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_single, inp, out) for inp, out in zip(input_paths, output_csv_paths)]
            for future in concurrent.futures.as_completed(futures):
                future.result()  # Raise any exceptions
        
        print("--- Bulk processing complete ---")

# --- Usage Example ---
if __name__ == "__main__":
    # Load configuration from environment variables
    SERVICE = DocumentProcessingService(
        project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("DOCUMENT_AI_LOCATION", "us"),  # Default to 'us' if not set
        processor_id=os.getenv("DOCUMENT_AI_PROCESSOR_ID"),
        gemini_api_key=os.getenv("GOOGLE_API_KEY")
    )

    # Bulk process all PDFs in uploads/viwanda and save CSVs to uploads/viwanda_csv
    input_dir = "uploads/viwanda"
    output_dir = "uploads/viwanda_csv"
    os.makedirs(output_dir, exist_ok=True)  # Ensure output dir exists

    input_files = []
    output_files = []
    for file in os.listdir(input_dir):
        if file.lower().endswith('.pdf'):
            input_files.append(os.path.join(input_dir, file))
            base_name = os.path.splitext(file)[0]
            output_files.append(os.path.join(output_dir, f"{base_name}.csv"))

    if input_files:
        print(f"Found {len(input_files)} PDF files to process.")
        SERVICE.bulk_process_to_csv(input_files, output_files, max_workers=5)
    else:
        print("No PDF files found in the input directory.")