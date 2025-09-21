# serializers.py

from django.db import transaction

from rest_framework import serializers

from superbill.models import (
    EDIPayer,
    EDIProvider, 
    EDIPayerPayload, 
    EDIPayerEndpoint,
    EDIClaimDiagnosis,
    EDIServiceModifier,
    EDIMedicationLine,
    EDIServiceLineDiagnosisPointer,
    EDIServiceLine,
    EDIClaim
)

class EDIPayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = EDIPayer
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class EDIProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = EDIProvider
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class EDIPayerPayloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = EDIPayerPayload
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class EDIPayerEndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = EDIPayerEndpoint
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class EDIClaimDiagnosisSerializer(serializers.ModelSerializer):
    claim = serializers.PrimaryKeyRelatedField(
        read_only=True 
    )
    class Meta:
        model = EDIClaimDiagnosis
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'claim')


class EDIServiceModifierSerializer(serializers.ModelSerializer):
    service_line = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = EDIServiceModifier
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'service_line')

class EDIMedicationLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = EDIMedicationLine
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'service_line')


class EDIServiceLineDiagnosisPointerSerializer(serializers.ModelSerializer):
    class Meta:
        model = EDIServiceLineDiagnosisPointer
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class EDIServiceLineSerializer(serializers.ModelSerializer):
    modifiers = EDIServiceModifierSerializer(many=True, required=False)
    medications = EDIMedicationLineSerializer(many=True, required=False)
    diagnosis_pointers = EDIServiceLineDiagnosisPointerSerializer(many=True, required=False)

    class Meta:
        model = EDIServiceLine
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'claim')


 
     
class EDIClaimSerializer(serializers.ModelSerializer):
    diagnoses = EDIClaimDiagnosisSerializer(many=True, required=False)
    service_lines = EDIServiceLineSerializer(many=True, required=False)

    class Meta:
        model = EDIClaim
        fields = [
            'id', 'claim_number', 'patient_id', 'patient_first_name',
            'patient_middle_name', 'patient_last_name', 'date_of_service',
            'total_amount', 'claim_type', 'billing_provider_npi',
            'payer', 'transaction_id', 'encounter_id',
            'diagnoses', 'service_lines'
        ]

    def create(self, validated_data):
        diagnoses_data = validated_data.pop('diagnoses', [])
        service_lines_data = validated_data.pop('service_lines', [])

        # Create the main claim
        claim = EDIClaim.objects.create(**validated_data)

        # Create nested diagnoses
        for diag_data in diagnoses_data:
            EDIClaimDiagnosis.objects.create(claim=claim, **diag_data)

        # Create nested service lines and their nested objects
        for line_data in service_lines_data:
            modifiers_data = line_data.pop("modifiers", [])
            medications_data = line_data.pop("medications", [])
            pointers_data = line_data.pop("diagnosis_pointer_links", [])

            line = EDIServiceLine.objects.create(claim=claim, **line_data)

            for mod_data in modifiers_data:
                EDIServiceModifier.objects.create(service_line=line, **mod_data)
            for med_data in medications_data:
                EDIMedicationLine.objects.create(service_line=line, **med_data)
            for ptr_data in pointers_data:
                EDIServiceLineDiagnosisPointer.objects.create(service_line=line, **ptr_data)

        return claim

    def update(self, instance, validated_data):
        # --- Pop nested data ---
        diagnoses_data = validated_data.pop('diagnoses', [])
        service_lines_data = validated_data.pop('service_lines', [])

        # --- Update claim fields ---
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # --- Update or create diagnoses ---
        for diag_data in diagnoses_data:
            EDIClaimDiagnosis.objects.update_or_create(
                claim=instance,
                diagnosis_code=diag_data['diagnosis_code'],
                defaults=diag_data
            )

        # --- Update or create service lines ---
        for line_data in service_lines_data:
            modifiers_data = line_data.pop("modifiers", [])
            medications_data = line_data.pop("medications", [])
            pointers_data = line_data.pop("diagnosis_pointer_links", [])

            # Use line_number + claim to uniquely identify service line
            print(line_data, 'linedata')
            line, created = EDIServiceLine.objects.update_or_create(
                claim=instance,
                line_number=line_data.get('line_number'),
                defaults=line_data
            )

            # --- Update or create modifiers ---
            for mod_data in modifiers_data:
                EDIServiceModifier.objects.update_or_create(
                    service_line=line,
                    modifier_code=mod_data['modifier_code'],
                    defaults=mod_data
                )

            # --- Update or create medications ---
            for med_data in medications_data:
                EDIMedicationLine.objects.update_or_create(
                    service_line=line,
                    ndc_code=med_data['ndc_code'],
                    defaults=med_data
                )

            # --- Update or create diagnosis pointers ---
            for ptr_data in pointers_data:
                EDIServiceLineDiagnosisPointer.objects.update_or_create(
                    service_line=line,
                    pointer_code=ptr_data.get('pointer_code'),  # Use a unique field for pointers
                    defaults=ptr_data
                )

        return instance

 