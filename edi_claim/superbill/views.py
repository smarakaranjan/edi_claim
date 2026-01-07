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

from rest_framework.views import APIView
from superbill.models import EDIClaim, EDIPayer
from superbill.edi_engine import Dynamic837ClaimEngine

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




class Generate837ClaimAPIView(viewsets.ViewSet):
    """
    Generate a full 837 EDI claim dynamically for a given claim and payer.
    """

    def create(self, request, *args, **kwargs):
        """
        Expects JSON:
        {
            "claim_id": 123,
            "payer_id": 1
        }
        """
        claim_id = request.data.get("claim_id")
        payer_id = request.data.get("payer_id")

        if not claim_id or not payer_id:
            return Response(
                {"error": "claim_id and payer_id are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            claim = EDIClaim.objects.get(id=claim_id)
        except EDIClaim.DoesNotExist:
            return Response({"error": "Claim not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            payer = EDIPayer.objects.get(id=payer_id, active=True)
        except EDIPayer.DoesNotExist:
            return Response({"error": "Payer not found or inactive."}, status=status.HTTP_404_NOT_FOUND)

        # --- Generate 837 using your Dynamic Engine ---
        engine = Dynamic837ClaimEngine()
        try:
            edi_lines = list(engine.generate(claim, payer))
            edi_string = "".join(edi_lines)
        except Exception as e:
            return Response(
                {"error": f"Failed to generate EDI claim: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            "claim_number": claim.claim_number,
            "payer": payer.name,
            "edi_837": edi_string
        }, status=status.HTTP_200_OK)
