# urls.py
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from superbill.views import (
    EDIProviderViewSet, 
    EDIPayerEndpointViewSet, 
    EDIPayerPayloadViewSet,
    EDIClaimViewSet,
    Generate837ClaimAPIView
)

router = DefaultRouter()
router.register(r"providers", EDIProviderViewSet)
router.register(r"payer-endpoints", EDIPayerEndpointViewSet)
router.register(r"payer-payloads", EDIPayerPayloadViewSet)
router.register(r"claim", EDIClaimViewSet, basename="claims")
router.register(r"generate-claim-edi", Generate837ClaimAPIView, basename="generate-claims")

urlpatterns = [
    path("", include(router.urls)),
]
