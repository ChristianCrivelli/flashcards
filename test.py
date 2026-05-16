from dotenv import load_dotenv
from google import genai

import os

load_dotenv()

client = genai.Client(api_key=os.getenv("gemini_key"))

for model in client.models.list():
    print(model.name)