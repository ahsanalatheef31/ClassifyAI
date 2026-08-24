from pathlib import Path

from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Product, ClassificationJob

from .serializers import (
    ProductSerializer,
    ProductCreateSerializer,
    ClassificationJobSerializer,
)

from .tasks import (
    classify_product_task,
    process_classification_job,
)


class ProductListCreateView(APIView):

    def get(self, request):

        products = Product.objects.all().order_by(
            "-created_at"
        )

        serializer = ProductSerializer(
            products,
            many=True,
            context={"request": request}
        )

        return Response(
            serializer.data
        )

    def post(self, request):

        serializer = ProductCreateSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        with transaction.atomic():
            product = serializer.save()

            # Send product to Celery after DB commit
            transaction.on_commit(
                lambda: classify_product_task.delay(
                    product.id
                )
            )

        return Response(
            ProductSerializer(
                product,
                context={"request": request}
            ).data,
            status=status.HTTP_201_CREATED
        )


class ProductDetailView(APIView):

    def get(self, request, pk):

        try:
            product = Product.objects.get(
                pk=pk
            )

        except Product.DoesNotExist:

            return Response(
                {
                    "error": "Product not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            ProductSerializer(
                product,
                context={"request": request}
            ).data
        )

    def post(self, request, pk):
        return ProductApproveView().post(request, pk)

    def patch(self, request, pk):
        return ProductApproveView().post(request, pk)



class ProductApproveView(APIView):

    def post(self, request, pk):

        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not hasattr(product, "classification") or not product.classification:
            return Response(
                {"error": "Product has no classification result to approve."},
                status=status.HTTP_400_BAD_REQUEST
            )

        classification = product.classification
        approved = request.data.get("approved", True)
        new_category = request.data.get("category")
        new_gid = request.data.get("shopify_gid")

        if new_category:
            classification.category = new_category
            if new_gid:
                classification.shopify_gid = new_gid
            else:
                classification.shopify_gid = ""

        classification.approved = bool(approved)
        if classification.approved:
            classification.manual_review = False
        else:
            classification.manual_review = True

        classification.save()

        return Response(
            ProductSerializer(
                product,
                context={"request": request}
            ).data
        )



class ClassificationJobListView(APIView):

    def get(self, request):

        jobs = ClassificationJob.objects.all().order_by(
            "-created_at"
        )

        serializer = ClassificationJobSerializer(
            jobs,
            many=True
        )

        return Response(
            serializer.data
        )


class ClassificationJobDetailView(APIView):

    def get(self, request, pk):

        try:
            job = ClassificationJob.objects.get(
                pk=pk
            )

        except ClassificationJob.DoesNotExist:

            return Response(
                {
                    "error": "Job not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            ClassificationJobSerializer(job).data
        )


class BulkUploadView(APIView):

    def post(self, request):

        uploaded_file = request.FILES.get(
            "file"
        )

        if not uploaded_file:

            return Response(
                {
                    "error": "No file uploaded."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        extension = Path(
            uploaded_file.name
        ).suffix.lower()

        if extension not in [
            ".csv",
            ".xlsx"
        ]:

            return Response(
                {
                    "error":
                    "Only CSV and XLSX files are supported."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save uploaded Excel/CSV file
        from django.core.files.storage import default_storage

        file_path = default_storage.save(
            f"uploads/{uploaded_file.name}",
            uploaded_file
        )

        absolute_path = default_storage.path(
            file_path
        )

        # Create classification job
        job = ClassificationJob.objects.create(
            status="pending"
        )

        # Send job to Celery
        process_classification_job.delay(
            job.id,
            absolute_path
        )

        return Response(
            {
                "success": True,
                "job_id": job.id,
                "filename": uploaded_file.name,
                "status": "pending",
            },
            status=status.HTTP_202_ACCEPTED
        )