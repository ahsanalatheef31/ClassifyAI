from django.urls import path

from .views import (
    ProductListCreateView,
    ProductDetailView,
    ProductApproveView,
    ClassificationJobListView,
    ClassificationJobDetailView,
    BulkUploadView,
)



urlpatterns = [

    path(
        "products/",
        ProductListCreateView.as_view()
    ),

    path(
        "products/<int:pk>/approve/",
        ProductApproveView.as_view()
    ),

    path(
        "products/<int:pk>/approve",
        ProductApproveView.as_view()
    ),

    path(
        "products/<int:pk>/",
        ProductDetailView.as_view()
    ),

    path(
        "jobs/",
        ClassificationJobListView.as_view()
    ),

    path(
        "jobs/<int:pk>/",
        ClassificationJobDetailView.as_view()
    ),
    path(
        "upload/",
        BulkUploadView.as_view()
    ),
    path(
        "bulk-upload/",
        BulkUploadView.as_view()
    ),
]