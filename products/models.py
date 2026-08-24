from django.db import models


class Product(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    name = models.CharField(max_length=500)
    description = models.TextField(blank=True, default="")
    brand = models.CharField(max_length=255, blank=True, default="")
    product_type = models.CharField(max_length=255, blank=True, default="")
    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True
    )

    classification_job = models.ForeignKey(
    "ClassificationJob",
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="products",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    error_message = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    

    def __str__(self):
        return self.name


class ClassificationResult(models.Model):

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="classification"
    )

    category = models.TextField(blank=True, default="")
    shopify_gid = models.CharField(max_length=500, blank=True, default="")

    confidence = models.FloatField(default=0.0)

    ai_analysis = models.JSONField(default=dict)
    alternatives = models.JSONField(default=list)

    manual_review = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)

    ranking_reason = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.category}"


class ClassificationJob(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    total_products = models.PositiveIntegerField(default=0)
    processed_products = models.PositiveIntegerField(default=0)
    failed_products = models.PositiveIntegerField(default=0)

    error_message = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Job {self.id} - {self.status}"