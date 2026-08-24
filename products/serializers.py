from rest_framework import serializers

from .models import (
    Product,
    ClassificationResult,
    ClassificationJob,
)


class ClassificationResultSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClassificationResult
        fields = [
            "category",
            "shopify_gid",
            "confidence",
            "ai_analysis",
            "alternatives",
            "manual_review",
            "approved",
            "ranking_reason",
            "created_at",
            "updated_at",
        ]


class ProductSerializer(serializers.ModelSerializer):

    classification = ClassificationResultSerializer(
        read_only=True
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "brand",
            "product_type",
            "image",
            "status",
            "error_message",
            "classification",
            "created_at",
            "updated_at",
        ]


class ProductCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "brand",
            "product_type",
            "image",
        ]

        extra_kwargs = {
            "description": {
                "required": False,
                "allow_blank": True,
            },
            "brand": {
                "required": False,
                "allow_blank": True,
            },
            "product_type": {
                "required": False,
                "allow_blank": True,
            },
            "image": {
                "required": False,
                "allow_null": True,
            },
        }


class ClassificationJobSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClassificationJob
        fields = [
            "id",
            "status",
            "total_products",
            "processed_products",
            "failed_products",
            "error_message",
            "created_at",
            "started_at",
            "completed_at",
        ]