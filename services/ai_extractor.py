from google import genai
from google.genai import types
import json
import os
import base64
from dotenv import load_dotenv
from PIL import Image
import io

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PROMPT = """
Analyze this PDF page carefully. It may contain tables, text, images, or a mix.

Extract ALL content and return ONLY a JSON object like this:

{
  "content_type": "table" or "text" or "image" or "mixed",
  "tables": [
    {
      "headers": ["col1", "col2", "col3"],
      "rows": [
        ["val1", "val2", "val3"],
        ["val1", "val2", "val3"]
      ]
    }
  ],
  "text": "any paragraph or plain text content here",
  "images": ["description of image 1", "description of image 2"]
}

Rules:
- If page has table → fill "tables" array
- If page has text → fill "text" field
- If page has images → fill "images" array with descriptions
- If page has mix → fill all relevant fields
- content_type should reflect what's on the page
- Return ONLY valid JSON, no explanation
"""

def extract_page_content(image: Image.Image, page_num: int) -> dict:
    """
    Ek page ki image Gemini ko do — wo decide karega kya hai.
    """
    try:
        # Image ko bytes mein convert karo
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()
        image_b64 = base64.b64encode(image_bytes).decode()
        # yaha se change kiye hain
        print("=" * 80)
        print("Sending request to Gemini...")
        print(f"Page Number: {page_num}")
        print(f"Image Size: {image.size}")
        print(f"Image Bytes: {len(image_bytes)}")
        print("=" * 80)
        # yaha tak

        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=[
                {
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": image_b64
                            }
                        },
                        {"text": PROMPT}
                    ]
                }
            ]
        )

        raw = response.text.strip()

        # JSON clean karo
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        result = json.loads(raw)
        result["page_number"] = page_num
        return result

    # except Exception as e:
    #     # Error pe bhi kuch return karo
    #     return {
    #         "content_type": "error",
    #         "text": f"Page {page_num} extract nahi ho saka: {str(e)}",
    #         "tables": [],
    #         "images": [],
    #         "page_number": page_num
    #     }

    except Exception as e:
        import traceback

        print("\n" + "=" * 80)
        print("GEMINI ERROR")
        print(f"Error Type : {type(e).__name__}")
        print(f"Error      : {str(e)}")
        print("\nFull Traceback:")
        traceback.print_exc()
        print("=" * 80 + "\n")

        return {
            "content_type": "error",
            "text": f"Page {page_num} extract nahi ho saka: {str(e)}",
            "tables": [],
            "images": [],
            "page_number": page_num
        }
