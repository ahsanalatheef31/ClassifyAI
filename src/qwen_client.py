import base64
import io
import json
import mimetypes
from pathlib import Path
from PIL import Image

import requests


QWEN_URL = "http://127.0.0.1:8080/v1/chat/completions"

QWEN_MODEL = "Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf"


class QwenClient:

    def __init__(self):
        self.url = QWEN_URL

    # ---------------------------------------------------------
    # TEXT + IMAGE PRODUCT ANALYSIS
    # ---------------------------------------------------------

    def analyze_product(
        self,
        product_name,
        description="",
        brand="",
        product_type="",
        image_path=None,
    ):

        prompt = f"""Identify this product and return ONLY JSON.

Name: {product_name}
Description: {description}
Brand: {brand}
Type: {product_type}

Return:
{{
  "product_name": "...",
  "product_type": "...",
  "specific_type": "...",
  "intended_use": "..."
}}

Rules:
- product_type = general product kind.
- specific_type = actual subtype.
- Do not invent information.
- If subtype is unknown, use "".
- intended_use = what the product is used for.
- Return ONLY JSON.
"""

        try:
            content = self._build_content(
                prompt,
                image_path
            )

            payload = {
                "model": QWEN_MODEL,

                "messages": [
                    {
                        "role": "user",
                        "content": content
                    }
                ],

                "temperature": 0,

                # We only need four small JSON fields.
                "max_tokens": 100,

                # Prevent unnecessary long generation.
                "stream": False,
            }

            timeout = 45 if image_path else 20

            response = requests.post(
                self.url,
                json=payload,
                timeout=timeout
            )

            if response.status_code != 200:
                raise RuntimeError(
                    f"Qwen request failed with status {response.status_code}: {response.text}"
                )

            data = response.json()

            result_content = (
                data["choices"][0]["message"]["content"]
            )

            return self._parse_json(
                result_content
            )

        except Exception as exc:
            if image_path:
                print(f"[QwenClient Warning] Vision analysis failed/timed out: {exc}. Falling back to text-only analysis.")
                return self.analyze_product(
                    product_name=product_name,
                    description=description,
                    brand=brand,
                    product_type=product_type,
                    image_path=None
                )
            else:
                return {
                    "error": f"Qwen request failed: {exc}"
                }

    # ---------------------------------------------------------
    # BUILD QWEN MESSAGE
    # ---------------------------------------------------------

    def _build_content(
        self,
        prompt,
        image_path=None
    ):

        # Text-only request
        if not image_path:
            return prompt

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        # Pre-process image with PIL to downscale tokens & memory overhead
        with Image.open(image_path) as img:
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Downscale max dimension to 384px
            img.thumbnail((384, 384), Image.Resampling.LANCZOS)

            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=85)
            image_bytes = buffer.getvalue()

        encoded_image = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        image_url = f"data:image/jpeg;base64,{encoded_image}"

        return [
            {
                "type": "text",
                "text": prompt
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": image_url
                }
            }
        ]

    # ---------------------------------------------------------
    # JSON PARSER
    # ---------------------------------------------------------

    def _parse_json(
        self,
        content
    ):

        content = content.strip()

        if content.startswith("```"):

            lines = content.splitlines()

            if (
                lines
                and lines[0].startswith("```")
            ):
                lines = lines[1:]

            if (
                lines
                and lines[-1].strip() == "```"
            ):
                lines = lines[:-1]

            content = "\n".join(
                lines
            ).strip()

        try:

            return json.loads(
                content
            )

        except json.JSONDecodeError:

            return {
                "error":
                    "Qwen returned invalid JSON",

                "raw_response":
                    content
            }


# -------------------------------------------------------------
# TEST
# -------------------------------------------------------------

if __name__ == "__main__":

    client = QwenClient()

    result = client.analyze_product(
        product_name="Brown Casual Shoes",

        description=(
            "A pair of brown lace-up shoes "
            "with white soles."
        ),

        brand="",

        image_path=(
            r"C:\Users\riswa\product-classification-ai"
            r"\test_shoe.jpg"
        )
    )

    print("Qwen Vision Result:")

    print(
        json.dumps(
            result,
            indent=2
        )
    )