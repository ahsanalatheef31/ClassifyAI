import pandas as pd


def _clean_str(val):
    if pd.isna(val) or val is None:
        return ""
    s = str(val).strip()
    return "" if s.lower() == "nan" else s


def _find_column(columns_dict, candidates):
    """
    Find matching column name from normalized columns dictionary.
    candidates is a list of normalized candidate names.
    """
    for candidate in candidates:
        if candidate in columns_dict:
            return columns_dict[candidate]
    return None


def read_product_file(file_path):
    file_name = str(file_path).lower()

    if file_name.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_name.endswith(".xlsx") or file_name.endswith(".xls"):
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Only CSV and XLSX files are supported.")

    # Create mapping of normalized column names -> original column names
    # e.g., "product name" -> "Product Name"
    norm_map = {}
    for col in df.columns:
        col_str = str(col).strip().lower()
        # also normalize underscores/extra spaces
        norm_key = " ".join(col_str.replace("_", " ").split())
        norm_map[col_str] = col
        norm_map[norm_key] = col

    # Candidate column names for each field
    name_col = _find_column(norm_map, ["product name", "product_name", "name", "title", "product title"])
    desc_col = _find_column(norm_map, ["product description", "description", "desc", "details"])
    cat_col = _find_column(norm_map, ["product category", "category", "product_type", "type"])
    img_col = _find_column(norm_map, ["image 1", "image_1", "image1", "primary image", "image url", "image_url", "image"])
    brand_col = _find_column(norm_map, ["brand", "brand name", "manufacturer"])

    # Metadata & Context candidate columns
    subcat_col = _find_column(norm_map, ["product sub category", "sub category", "subcategory", "product subcategory"])
    bullets_col = _find_column(norm_map, ["bullets", "bullet points", "features", "key features"])
    set_col = _find_column(norm_map, ["set includes", "includes", "set_includes"])
    materials_col = _find_column(norm_map, ["materials", "material", "fabric"])
    dims_col = _find_column(norm_map, ["product dimensions", "dimensions", "size"])
    collection_col = _find_column(norm_map, ["collection name", "collection", "collection_name"])
    color_col = _find_column(norm_map, ["product color", "color collection", "color"])
    origin_col = _find_column(norm_map, ["country of origin", "origin", "country"])
    model_col = _find_column(norm_map, ["model number", "model", "model_number"])
    prod_num_col = _find_column(norm_map, ["product number", "product_number", "sku", "item number"])
    url_col = _find_column(norm_map, ["product url", "url", "link"])

    if not name_col:
        raise ValueError("Excel file must contain a 'Product Name' column.")

    df = df.fillna("")

    products = []

    for _, row in df.iterrows():
        name_val = _clean_str(row.get(name_col))
        if not name_val:
            continue

        base_desc = _clean_str(row.get(desc_col)) if desc_col else ""
        brand_val = _clean_str(row.get(brand_col)) if brand_col else ""
        cat_val = _clean_str(row.get(cat_col)) if cat_col else ""
        img_val = _clean_str(row.get(img_col)) if img_col else ""

        # Build rich description / AI context
        context_parts = []
        if base_desc:
            context_parts.append(base_desc)

        if subcat_col and _clean_str(row.get(subcat_col)):
            context_parts.append(f"Subcategory: {_clean_str(row.get(subcat_col))}")

        if collection_col and _clean_str(row.get(collection_col)):
            context_parts.append(f"Collection: {_clean_str(row.get(collection_col))}")

        if color_col and _clean_str(row.get(color_col)):
            context_parts.append(f"Color: {_clean_str(row.get(color_col))}")

        if bullets_col and _clean_str(row.get(bullets_col)):
            context_parts.append(f"Key Features: {_clean_str(row.get(bullets_col))}")

        if set_col and _clean_str(row.get(set_col)):
            context_parts.append(f"Set Includes: {_clean_str(row.get(set_col))}")

        if materials_col and _clean_str(row.get(materials_col)):
            context_parts.append(f"Materials: {_clean_str(row.get(materials_col))}")

        if dims_col and _clean_str(row.get(dims_col)):
            context_parts.append(f"Dimensions: {_clean_str(row.get(dims_col))}")

        if origin_col and _clean_str(row.get(origin_col)):
            context_parts.append(f"Country of Origin: {_clean_str(row.get(origin_col))}")

        if model_col and _clean_str(row.get(model_col)):
            context_parts.append(f"Model Number: {_clean_str(row.get(model_col))}")

        if prod_num_col and _clean_str(row.get(prod_num_col)):
            context_parts.append(f"Product Number: {_clean_str(row.get(prod_num_col))}")

        if url_col and _clean_str(row.get(url_col)):
            context_parts.append(f"Product URL: {_clean_str(row.get(url_col))}")

        enriched_description = "\n".join(context_parts)

        products.append({
            "name": name_val,
            "description": enriched_description,
            "brand": brand_val,
            "product_type": cat_val,
            "image_url": img_val,
        })

    return products