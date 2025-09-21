# views.py
from rest_framework import viewsets
from rest_framework import viewsets, status
from rest_framework.response import Response

from superbill.models import (
    EDIPayer,
    EDIProvider, 
    EDIPayerPayload, 
    EDIPayerEndpoint,
    EDIClaim
)
from superbill.serializers import (
    EDIPayerSerializer,
    EDIProviderSerializer, 
    EDIPayerPayloadSerializer, 
    EDIPayerEndpointSerializer,
    EDIClaimSerializer
)

class EDIProviderViewSet(viewsets.ModelViewSet):
    queryset = EDIProvider.objects.all()
    serializer_class = EDIProviderSerializer

class EDIPayerEndpointViewSet(viewsets.ModelViewSet):
    queryset = EDIPayerEndpoint.objects.all()
    serializer_class = EDIPayerEndpointSerializer

class EDIPayerPayloadViewSet(viewsets.ModelViewSet):
    queryset = EDIPayerPayload.objects.all()
    serializer_class = EDIPayerPayloadSerializer

class EDIPayerViewSet(viewsets.ModelViewSet):
    """
    API endpoint to manage EDI Payers.
    Supports list, retrieve, create, update, and delete.
    """
    queryset = EDIPayer.objects.all()
    serializer_class = EDIPayerSerializer


class EDIClaimViewSet(viewsets.ViewSet):
    """
    Explicit ViewSet for EDI Claims with nested service lines,
    diagnoses, medications, modifiers, and diagnosis_pointer_links.
    """

    def list(self, request):
        claims = EDIClaim.objects.all()
        serializer = EDIClaimSerializer(claims, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            claim = EDIClaim.objects.get(pk=pk)
        except EDIClaim.DoesNotExist:
            return Response({"message": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = EDIClaimSerializer(claim)
        return Response(serializer.data)

    def create(self, request):
        serializer = EDIClaimSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        claim = serializer.save()
        return Response(EDIClaimSerializer(claim).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        try:
            claim = EDIClaim.objects.get(pk=pk)
        except EDIClaim.DoesNotExist:
            return Response({"message": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = EDIClaimSerializer(claim, data=request.data)
        serializer.is_valid(raise_exception=True)
        claim = serializer.save()
        return Response(EDIClaimSerializer(claim).data)

    def partial_update(self, request, pk=None):
        try:
            claim = EDIClaim.objects.get(pk=pk)
        except EDIClaim.DoesNotExist:
            return Response({"message": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = EDIClaimSerializer(claim, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        claim = serializer.save()
        return Response(EDIClaimSerializer(claim).data)
        
    def destroy(self, request, pk=None):
        try:
            claim = EDIClaim.objects.get(pk=pk)
        except EDIClaim.DoesNotExist:
            return Response({"message": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        claim.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
