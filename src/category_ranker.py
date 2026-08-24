import json
import requests


QWEN_URL = "http://127.0.0.1:8080/v1/chat/completions"

QWEN_MODEL = (
    r"C:\Users\riswa\product-classification-ai"
    r"\models\qwen-gguf"
    r"\Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf"
)


class CategoryRanker:

    def rank(self, product_info, candidates):

        if not candidates:
            return {
                "error": "No candidate categories available"
            }

        candidate_text = "\n".join(
            f"{i + 1}. {candidate['path']}"
            for i, candidate in enumerate(candidates)
        )

        prompt = f"""
You are an expert e-commerce product categorization system.

Your task is to select the MOST SPECIFIC and MOST ACCURATE
Shopify category from the provided candidates.

PRODUCT INFORMATION

Product name:
{product_info.get("product_name", "")}

Description:
{product_info.get("description", "")}

Brand:
{product_info.get("brand", "")}

Product type:
{product_info.get("product_type", "")}

Specific type:
{product_info.get("specific_type", "")}

Intended use:
{product_info.get("intended_use", "")}


AVAILABLE SHOPIFY CATEGORIES

{candidate_text}


CLASSIFICATION RULES

1. Choose ONLY one category from the candidates.

2. Use the complete product information.

3. Prefer the category that describes the actual physical
   product rather than an accessory, component, or related item.

4. Prefer a MORE SPECIFIC category when the product information
   clearly supports it.

5. Pay special attention to the product name and specific type.

6. Do not confuse products that have similar words but belong
   to different product families.

7. For example:
   - A face serum should prefer "Face Serums".
   - A hair serum should prefer "Hair Serums".
   - A soap should prefer the appropriate soap category.
   - A soap accessory should not be classified as soap itself.

8. Do not infer unsupported medical, cosmetic, or technical claims.

9. If the available information is insufficient to confidently
   distinguish between candidates, lower the confidence.

10. Never invent a category.

Return ONLY valid JSON.

Return exactly:

{{
    "selected_index": 1,
    "confidence": 0.0,
    "reason": "short explanation"
}}
"""

        payload = {
            "model": QWEN_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.0,
            "max_tokens": 200
        }

        response = requests.post(
            QWEN_URL,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        content = data["choices"][0]["message"]["content"].strip()

        content = self._clean_response(content)

        try:
            result = json.loads(content)

        except json.JSONDecodeError:
            return {
                "error": "Qwen returned invalid JSON",
                "raw_response": content
            }

        # Validate selected index
        selected_index = result.get("selected_index")

        if not isinstance(selected_index, int):
            return {
                "error": "Invalid selected_index from Qwen",
                "raw_response": content
            }

        if not 1 <= selected_index <= len(candidates):
            return {
                "error": "Qwen selected an invalid category index",
                "raw_response": content
            }

        # Normalize confidence
        try:
            confidence = float(
                result.get("confidence", 0.0)
            )
        except (TypeError, ValueError):
            confidence = 0.0

        confidence = max(
            0.0,
            min(1.0, confidence)
        )

        return {
            "selected_index": selected_index,
            "confidence": round(confidence, 2),
            "reason": result.get(
                "reason",
                ""
            )
        }

    @staticmethod
    def _clean_response(content):

        if content.startswith("```"):

            lines = content.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            content = "\n".join(lines).strip()

        return content


if __name__ == "__main__":

    ranker = CategoryRanker()

    product = {
        "product_name": "Cinnabari Face Serum",
        "description": "Hydrating serum for daily facial skincare.",
        "brand": "Cinnabari",
        "product_type": "Serum",
        "specific_type": "Face Serum",
        "intended_use": "Hydrating for daily facial skincare"
    }

    candidates = [
        {
            "path": (
                "Health & Beauty > Personal Care > Cosmetics "
                "> Skin Care > Face Serums"
            ),
            "gid": (
                "gid://shopify/TaxonomyCategory/"
                "hb-3-2-9-21"
            )
        },
        {
            "path": (
                "Health & Beauty > Personal Care > Cosmetics "
                "> Skin Care > Face Moisturizers"
            ),
            "gid": "example-moisturizer"
        },
        {
            "path": (
                "Health & Beauty > Personal Care > Cosmetics "
                "> Hair Care > Hair Serums"
            ),
            "gid": (
                "gid://shopify/TaxonomyCategory/"
                "hb-3-10-14-3"
            )
        }
    ]

    result = ranker.rank(
        product,
        candidates
    )

    print(
        json.dumps(
            result,
            indent=2
        )
    )