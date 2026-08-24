from django.contrib import admin
from .models import Product, ClassificationResult, ClassificationJob

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "brand", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "brand", "description")

@admin.register(ClassificationResult)
class ClassificationResultAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "category", "confidence", "manual_review", "approved")
    list_filter = ("manual_review", "approved")
    search_fields = ("category", "shopify_gid")

@admin.register(ClassificationJob)
class ClassificationJobAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "total_products", "processed_products", "failed_products", "created_at")
    list_filter = ("status",)

