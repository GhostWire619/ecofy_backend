from google import genai
from google.genai import types
import pathlib
# from app.core.config import settings # Commented out as settings was not defined in the user snippet
import os
import requests.exceptions

# api_key = getattr(settings, "GOOGLE_GEMINI_API_KEY", None) or os.getenv("GOOGLE_API_KEY")


client = genai.Client(api_key="AIzaSyD69R8BwdIiV2Rg3NfkyQOB32Di3vq3oMM")

filepath = pathlib.Path('sw-1621854270-Wholesale prices Report  21st May, 2021.pdf')
prompt = f"read the data  i have uploaded and extract all tables in JSON format with headers and rows {filepath.read_bytes()}"
response = client.models.generate_content(
  model="gemini-3-pro-preview",
  contents=[
      types.Part.from_bytes(
        data=filepath.read_bytes(),
        mime_type='application/pdf',
      ),
      prompt])
print(response.text)