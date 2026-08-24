import os
import io
import requests
from PIL import Image
from celery import shared_task
from django.utils import timezone
from django.core.files.base import ContentFile

from .models import (
    Product,
    ClassificationResult,
    ClassificationJob,
)

from .bulk_processor import read_product_file
from src.product_classifier import ProductClassifier


def download_and_save_image(product, image_url):
    """
    Download Image 1 URL, validate image content, and save using Django ImageField storage.
    Returns True if downloaded and verified on disk, False otherwise.
    """
    if not image_url or not isinstance(image_url, str):
        return False
    image_url = image_url.strip()
    if not (image_url.startswith("http://") or image_url.startswith("https://")):
        return False

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(image_url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"[Image Download Warning] URL {image_url} returned status {response.status_code}")
            return False

        content = response.content
        if not content:
            return False

        # Validate image format using PIL
        try:
            img = Image.open(io.BytesIO(content))
            fmt = (img.format or "").upper()
            if fmt not in ["JPEG", "PNG", "WEBP", "JPG", "GIF", "MPO"]:
                print(f"[Image Download Warning] Unsupported image format '{fmt}' from {image_url}")
                return False
        except Exception as img_err:
            print(f"[Image Download Warning] Invalid image content from {image_url}: {img_err}")
            return False

        ext = "jpg" if fmt in ["JPEG", "MPO"] else fmt.lower()
        filename = f"product_{product.id}_primary.{ext}"

        # Save through Django's ImageField storage mechanism
        product.image.save(filename, ContentFile(content), save=True)

        # Verify physical disk file existence
        if product.image and os.path.exists(product.image.path):
            print(f"[Image Download Success] Product {product.id} image saved to {product.image.path}")
            return True
        else:
            print(f"[Image Download Warning] Product {product.id} image file does not exist after save.")
            return False

    except Exception as exc:
        print(f"[Image Download Warning] Failed to download image from {image_url}: {exc}")
        return False


def update_job_progress(job_id):
    """
    Update the parent ClassificationJob based on
    the current status of all products.
    """

    job = ClassificationJob.objects.get(
        id=job_id
    )

    products = Product.objects.filter(
        classification_job_id=job_id
    )

    total = products.count()

    completed = products.filter(
        status="completed"
    ).count()

    failed = products.filter(
        status="failed"
    ).count()

    job.total_products = total
    job.processed_products = completed
    job.failed_products = failed

    finished = completed + failed

    if total > 0 and finished >= total:

        job.status = "completed"

        if not job.completed_at:
            job.completed_at = timezone.now()

    else:

        job.status = "processing"

    job.save(
        update_fields=[
            "status",
            "total_products",
            "processed_products",
            "failed_products",
            "completed_at",
        ]
    )


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def classify_product_task(
    self,
    product_id,
    job_id=None,
    image_url=None
):

    product = Product.objects.get(
        id=product_id
    )

    # ---------------------------------------------------------
    # Mark product as processing
    # ---------------------------------------------------------

    product.status = "processing"
    product.error_message = ""

    product.save(
        update_fields=[
            "status",
            "error_message",
            "updated_at",
        ]
    )

    try:

        # -----------------------------------------------------
        # Download Image 1 if present and product has no image
        # -----------------------------------------------------

        if not product.image and image_url:
            img_success = download_and_save_image(product, image_url)
            if not img_success:
                print(f"[Product Task] Product {product.id} image download skipped or failed; using text classification.")

        # -----------------------------------------------------
        # Create classifier
        # -----------------------------------------------------

        classifier = ProductClassifier()

        # -----------------------------------------------------
        # Prepare product information
        # -----------------------------------------------------

        product_data = {
            "product_name": product.name,
            "description": product.description,
            "brand": product.brand,
            "product_type": product.product_type,
            "image_path": None,
        }

        # -----------------------------------------------------
        # Add uploaded image path
        # -----------------------------------------------------

        if product.image:

            try:
                img_path = product.image.path
                if os.path.exists(img_path):
                    product_data["image_path"] = img_path
                else:
                    product_data["image_path"] = None

            except ValueError:

                # Image field exists but has no usable file
                product_data["image_path"] = None

        # -----------------------------------------------------
        # Run AI classification
        # -----------------------------------------------------

        result = classifier.classify(
            product_data
        )

        # -----------------------------------------------------
        # Check classification result
        # -----------------------------------------------------

        if not result.get("success"):

            raise Exception(
                result.get(
                    "error",
                    "Classification failed"
                )
            )

        classification = result[
            "classification"
        ]

        # -----------------------------------------------------
        # Save classification
        # -----------------------------------------------------

        ClassificationResult.objects.update_or_create(

            product=product,

            defaults={

                "category": classification.get(
                    "category",
                    ""
                ),

                "shopify_gid": classification.get(
                    "shopify_gid",
                    ""
                ),

                "confidence": classification.get(
                    "confidence",
                    0.0
                ),

                "ai_analysis": result.get(
                    "ai_analysis",
                    {}
                ),

                "alternatives": classification.get(
                    "alternatives",
                    []
                ),

                "manual_review": classification.get(
                    "manual_review",
                    True
                ),

                "ranking_reason": classification.get(
                    "ranking_reason",
                    ""
                ),
            },
        )

        # -----------------------------------------------------
        # Mark product completed
        # -----------------------------------------------------

        product.status = "completed"
        product.error_message = ""

        product.save(
            update_fields=[
                "status",
                "error_message",
                "updated_at",
            ]
        )

        # -----------------------------------------------------
        # Update parent job
        # -----------------------------------------------------

        if job_id:

            update_job_progress(
                job_id
            )

        return {

            "success": True,

            "product_id": product.id,

            "category": classification.get(
                "category"
            ),

            "confidence": classification.get(
                "confidence"
            ),

            "manual_review": classification.get(
                "manual_review",
                True
            ),
        }

    except Exception as exc:

        # -----------------------------------------------------
        # Mark product failed
        # -----------------------------------------------------

        product.status = "failed"
        product.error_message = str(exc)

        product.save(
            update_fields=[
                "status",
                "error_message",
                "updated_at",
            ]
        )

        # -----------------------------------------------------
        # Update parent job
        # -----------------------------------------------------

        if job_id:

            update_job_progress(
                job_id
            )

        raise


@shared_task
def process_classification_job(
    job_id,
    file_path
):

    job = ClassificationJob.objects.get(
        id=job_id
    )

    # ---------------------------------------------------------
    # Mark job as processing
    # ---------------------------------------------------------

    job.status = "processing"
    job.started_at = timezone.now()

    job.save(
        update_fields=[
            "status",
            "started_at",
        ]
    )

    try:

        # -----------------------------------------------------
        # Read CSV/XLSX
        # -----------------------------------------------------

        products_data = read_product_file(
            file_path
        )

        # -----------------------------------------------------
        # Set job totals
        # -----------------------------------------------------

        job.total_products = len(
            products_data
        )

        job.processed_products = 0
        job.failed_products = 0

        job.save(
            update_fields=[
                "total_products",
                "processed_products",
                "failed_products",
            ]
        )

        if len(products_data) == 0:
            job.status = "completed"
            job.completed_at = timezone.now()
            job.save(update_fields=["status", "completed_at"])
            return {"success": True, "job_id": job.id, "total_products": 0}

        # -----------------------------------------------------
        # Create products and queue tasks immediately
        # -----------------------------------------------------

        for product_data in products_data:

            product = Product.objects.create(

                name=product_data.get(
                    "name",
                    ""
                ),

                description=product_data.get(
                    "description",
                    ""
                ),

                brand=product_data.get(
                    "brand",
                    ""
                ),

                product_type=product_data.get(
                    "product_type",
                    ""
                ),

                status="pending",

                classification_job=job,
            )

            # -------------------------------------------------
            # Queue classification immediately with image_url
            # -------------------------------------------------

            classify_product_task.delay(
                product.id,
                job.id,
                product_data.get("image_url", ""),
            )

        return {

            "success": True,

            "job_id": job.id,

            "total_products":
                job.total_products,
        }

    except Exception as exc:

        job.status = "failed"
        job.error_message = str(exc)

        job.save(
            update_fields=[
                "status",
                "error_message",
            ]
        )

        raise
