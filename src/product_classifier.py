import json

try:
    from src.qwen_client import QwenClient
    from src.classification_engine import ClassificationEngine
except ImportError:
    from qwen_client import QwenClient
    from classification_engine import ClassificationEngine


class ProductClassifier:

    def __init__(self):
        self.qwen = QwenClient()
        self.engine = ClassificationEngine()

    def classify(self, product):

        # ---------------------------------------------------------
        # STEP 1: Qwen understands the product
        # Text + image if available
        # ---------------------------------------------------------

        ai_info = self.qwen.analyze_product(
            product_name=product.get(
                "product_name",
                ""
            ),
            description=product.get(
                "description",
                ""
            ),
            brand=product.get(
                "brand",
                ""
            ),
            product_type=product.get(
                "product_type",
                ""
            ),
            image_path=product.get(
                "image_path"
            )
        )

        if "error" in ai_info:
            print(f"[ProductClassifier Warning] AI analysis unavailable ({ai_info['error']}). Falling back to taxonomy matching on product metadata.")
            ai_info = {
                "product_name": product.get("product_name", ""),
                "product_type": product.get("product_type", ""),
                "specific_type": product.get("product_name", ""),
                "intended_use": product.get("description", ""),
                "key_features": [],
                "target_audience": "",
                "ai_error": ai_info["error"]
            }

        # ---------------------------------------------------------
        # STEP 2: Shopify taxonomy classification
        # ---------------------------------------------------------

        classification = self.engine.classify(
            ai_info
        )

        # ---------------------------------------------------------
        # STEP 3: Return result
        # ---------------------------------------------------------

        return {
            "success": True,
            "product": product,
            "ai_analysis": ai_info,
            "classification": classification
        }

if __name__ == "__main__":

    classifier = ProductClassifier()

    product = {
        "product_name": "Brown Casual Shoes",
        "description": "A pair of brown lace-up shoes with white soles.",
        "brand": "",
        "product_type": "",
        "image_path": r"C:\Users\riswa\product-classification-ai\test_shoe.jpg"
    }

    result = classifier.classify(product)

    print(json.dumps(result, indent=2))