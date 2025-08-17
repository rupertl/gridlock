"""Use a Gemini LLM to extract text from an image."""


import os
import sys
import time
from google import genai


def ocr_gemini(image_file, model, prompt, debug):
    """Extract text from the guven image file.."""
    key = os.environ.get("GEMINI_API_KEY")
    if key is None:
        print('Please set GEMINI_API_KEY')
        sys.exit(1)

    # exceptions: raise ServerError
    start_time = time.time()
    end_time = start_time
    text = ""
    client = genai.Client(api_key=key)
    image = client.files.upload(file=image_file)
    response = client.models.generate_content(
        model=model,
        contents=[image, prompt])
    end_time = time.time()
    if response.text:
        text = response.text
    else:
        if debug:
            print('No text in response. Response was:', file=sys.stderr)
            print(response, file=sys.stderr)

    # Remove markdown quotes, if any
    text = text.replace("```\n", "")
    text = text.replace("```text\n", "").replace("```", "")
    # Remove trailing blank line if any
    if len(text) > 2 and text[-1] == '\n' and text[-2] == '\n':
        text = text[0:-1]
    if debug:
        print(f"Model: {model}", file=sys.stderr)
        print("Tokens: ", response.usage_metadata, file=sys.stderr)
        elapsed_time = end_time - start_time
        print(f"Elapsed time: {elapsed_time:.2f} s", file=sys.stderr)
    return text
