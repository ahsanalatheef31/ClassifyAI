import os
import pandas as pd
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from products.bulk_processor import read_product_file

def test_parser():
    print("--- Testing Bulk Excel Parser ---")
    data = {
        "Product Number": ["EEI-1010-WHI"],
        "Model Number": ["EEI-1010"],
        "Product Category": ["Living Room"],
        "Product Sub Category": ["Armchairs"],
        "Collection Name": ["Modway Collection"],
        "Color Collection": ["White"],
        "Product Color": ["White"],
        "Product Name": ["Modway Empress Upholstered Leather Armchair"],
        "Product Description": ["Deep tufted buttons and classic armrests offer vintage charm."],
        "Bullets": ["Genuine Leather, Solid Wood Legs, Padded Cushions"],
        "Set Includes": ["1 Armchair"],
        "Materials": ["Leather, Wood"],
        "Product Dimensions": ["35.5L x 35.5W x 34.5H"],
        "Country Of Origin": ["EE"],
        "Image 1": ["https://modwayfurniture.com/images/variant/large/EEI-1010-WHI_1_.jpg"],
        "Product URL": ["https://modwayfurniture.com/product/EEI-1010-WHI"]
    }
    df = pd.DataFrame(data)
    test_excel_path = "test_product_list_sample.xlsx"
    df.to_excel(test_excel_path, index=False)
    print(f"Created sample Excel file at {test_excel_path}")

    products = read_product_file(test_excel_path)
    print(f"Parsed {len(products)} products from Excel file:")
    for p in products:
        print(f"Name: {p['name']}")
        print(f"Category: {p['product_type']}")
        print(f"Image URL: {p['image_url']}")
        print(f"Enriched Description:\n{p['description']}\n")

    if os.path.exists(test_excel_path):
        os.remove(test_excel_path)

    print("--- Excel Parser Test Passed ---")

if __name__ == "__main__":
    test_parser()
