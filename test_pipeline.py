import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from products.models import Product, ClassificationResult
from products.tasks import classify_product_task

def run_test():
    print("--- Starting Product Pipeline Test ---")
    
    test_img_path = r"C:\Users\riswa\product-classification-ai\test_shoe.jpg"
    with open(test_img_path, "rb") as f:
        uploaded_file = SimpleUploadedFile(
            name="test_shoe_upload.jpg",
            content=f.read(),
            content_type="image/jpeg"
        )
    
    product = Product.objects.create(
        name="Test Running Shoes",
        description="Comfortable sports running shoes for athletic training",
        brand="TestBrand",
        product_type="Shoes",
        image=uploaded_file
    )
    
    print(f"Product Created ID: {product.id}")
    print(f"Product Image Name: {product.image.name}")
    print(f"Product Image Path: {product.image.path}")
    
    # Verify file physically exists on disk
    file_exists = os.path.exists(product.image.path)
    print(f"Image File Exists On Disk: {file_exists}")
    assert file_exists, "Uploaded image does not exist on disk!"
    
    # Run classification task synchronously
    print("Executing classify_product_task...")
    classify_product_task(product.id)
    
    # Reload product from DB
    product.refresh_from_db()
    print(f"Product Status After Task: {product.status}")
    assert product.status == "completed", f"Expected completed status, got {product.status}"
    
    # Check ClassificationResult
    result = ClassificationResult.objects.get(product=product)
    print(f"Classification Category: {result.category}")
    print(f"Shopify GID: {result.shopify_gid}")
    print(f"Confidence Score: {result.confidence}")
    print(f"Manual Review Flag: {result.manual_review}")
    
    print("--- PIPELINE TEST SUCCESSFUL ---")

if __name__ == "__main__":
    run_test()
