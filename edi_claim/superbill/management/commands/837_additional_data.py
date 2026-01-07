# from django.core.management.base import BaseCommand
# from django.contrib.auth import get_user_model
# from superbill.models import (
#     EDIPayer, EDIProvider, EDIClaim, BillingProcedureCode, BillingPlaceOfService,
#     BillingModifier, BillingICD10Diagnosis, EDILoop, EDISegment, EDIElement,
#     EDIPayerRule, EDIDataKey, EDIServiceLine
# )
# from datetime import date

# User = get_user_model()


# class Command(BaseCommand):
#     help = "Populate sample EDI payer, rules, and claims for testing dynamic 837 engine."

#     def handle(self, *args, **options):
#         self.stdout.write("Starting sample 837 data population...")

#         # --- Create sample user ---
#         user, _ = User.objects.get_or_create(username="admin", defaults={"email": "admin@test.com"})

#         # --- Sample payer ---
#         payer, _ = EDIPayer.objects.get_or_create(name="TestPayer", defaults={"active": True})

#         # --- Sample provider ---
#         provider, _ = EDIProvider.objects.get_or_create(
#             npi="1234567890",
#             defaults={
#                 "name": "Test Provider",
#                 "tax_id": "111111111",
#                 "type": "individual"
#             }
#         )

#         # --- Sample CPT code ---
#         cpt, _ = BillingProcedureCode.objects.get_or_create(
#             cpt_code="99213",
#             defaults={"name": "Office Visit", "description": "Test office visit"}
#         )

#         # --- Sample POS ---
#         pos, _ = BillingPlaceOfService.objects.get_or_create(
#             code="11",
#             defaults={"name": "Office", "description": "Office visit"}
#         )

#         # --- Sample ICD10 ---
#         diag, _ = BillingICD10Diagnosis.objects.get_or_create(
#             code="Z00.00",
#             defaults={"description": "General adult medical examination"}
#         )

#         # --- Create EDIDataKeys ---
#         dk_mapping = {
#             "BILLING_NPI": "billing_provider.npi",
#             "BILLING_NAME": "billing_provider.name",
#             "SUBSCRIBER_LAST": "patient_last_name",
#             "SUBSCRIBER_FIRST": "patient_first_name",
#             "PROCEDURE_CODE": "procedure.cpt_code",
#             "CHARGE_AMOUNT": "charge_amount",
#             "PLACE_OF_SERVICE": "place_of_service.code",
#             "LINE_NUMBER": "line_number",
#         }
#         data_keys = {}
#         for key, extractor in dk_mapping.items():
#             data_keys[key], _ = EDIDataKey.objects.get_or_create(key=key, defaults={"extractor": extractor})

#         # --- Create sample EDILoop segments and elements (assuming already populated) ---
#         isa_loop = EDILoop.objects.get(code="ISA_LOOP")
#         for loop in EDILoop.objects.all():
#             for seg in loop.segments.all():
#                 for elem in seg.elements.all():
#                     # Example: create FIELD rule for payer
#                     EDIPayerRule.objects.get_or_create(
#                         payer=payer,
#                         element=elem,
#                         rule_type="FIELD" if elem.name in dk_mapping else "CONSTANT",
#                         data_key=data_keys.get(elem.name) if elem.name in dk_mapping else None,
#                         constant_value="TEST" if elem.name not in dk_mapping else None,
#                         pad_char=" ",
#                         pad_side="right",
#                         min_length=1,
#                         max_length=elem.length,
#                         required=True,
#                         order=1
#                     )

#         # --- Create a sample claim ---
#         claim = EDIClaim.objects.create(
#             claim_number="C12345",
#             patient_id="P0001",
#             patient_first_name="John",
#             patient_middle_name="A",
#             patient_last_name="Doe",
#             date_of_service=date.today(),
#             total_amount=150.00,
#             claim_type="professional",
#             billing_provider_npi=provider,
#             payer=payer
#         )

#         # --- Add a service line ---
#         service_line = EDIServiceLine.objects.create(
#             claim=claim,
#             rendering_provider=provider,
#             procedure=cpt,
#             line_number=1,
#             charge_amount=150.00,
#             place_of_service=pos,
#             units=1,
#             service_date=date.today(),
#         )

#         self.stdout.write(self.style.SUCCESS("Sample claim and payer rules created successfully."))



from django.core.management.base import BaseCommand
from superbill.models import (
    EDIPayer, EDIPayerRule, EDIDataKey,
    BillingProcedureCode, BillingPlaceOfService,
    BillingICD10Diagnosis, BillingModifier
)

class Command(BaseCommand):
    help = "Populate master data for dynamic 837 claim generation (payers, rules, data keys, billing codes)."

    def handle(self, *args, **options):
        self.stdout.write("Populating master data for 837 claim...")

        # --- Payer ---
        payer, _ = EDIPayer.objects.get_or_create(
            name="Test Payer",
        )

        # --- Data Keys ---
        data_keys = {
            "ISA_LOOP_ISA_6": "submitter.id",
            "1000A_NM1_3": "submitter.name",
            "1000B_NM1_3": "receiver.name",
            "2000A_PRV_2": "billing_provider.npi",
            "2000B_SBR_2": "subscriber.id",
            "2300_CLM_1": "claim.id",
            "2300_CLM_2": "claim.amount",
            "2400_SV1_1": "service.procedure_code",
            "2400_SV1_2": "service.charge_amount",
            "2400_SV1_3": "service.unit_basis",
            "2400_SV1_4": "service.units",
            "2400_SV1_5": "service.place_of_service",
            "2400_SV1_6": "service.modifier1",
            "2400_SV1_7": "service.modifier2",
            "2400_SV1_8": "service.modifier3",
            "2400_SV1_9": "service.modifier4",
        }

        data_key_objs = {}
        for key, path in data_keys.items():
            dk, _ = EDIDataKey.objects.get_or_create(key=key, extractor=path)
            data_key_objs[key] = dk

        # --- EDI Rules (FIELD type) ---
        from superbill.models import EDIElement
        for dk_key, dk in data_key_objs.items():
            try:
                element_name = dk_key.rsplit("_", 2)[0]  # e.g., 2400_SV1
                elem = EDIElement.objects.filter(segment__name__icontains=element_name).first()
                if elem:
                    EDIPayerRule.objects.get_or_create(
                        element=elem,
                        payer=payer,
                        rule_type="FIELD",
                        data_key=dk
                    )
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Skipping {dk_key}: {e}"))

        # --- Billing Procedure Codes ---
        procedures = [
            ("99213", "Office Visit"),
            ("99214", "Extended Office Visit"),
            ("93000", "Electrocardiogram"),
        ]
        for code, desc in procedures:
            BillingProcedureCode.objects.get_or_create(cpt_code=code, description=desc)

        # --- Place of Service ---
        places = [
            ("11", "Office"),
            ("21", "Inpatient Hospital"),
            ("22", "Outpatient Hospital"),
        ]
        for code, desc in places:
            BillingPlaceOfService.objects.get_or_create(code=code, description=desc)

        # --- ICD10 Diagnosis ---
        diagnoses = [
            ("Z00.00", "General checkup"),
            ("E11.9", "Type 2 Diabetes"),
            ("I10", "Essential hypertension"),
        ]
        for code, desc in diagnoses:
            BillingICD10Diagnosis.objects.get_or_create(code=code, description=desc)

        # --- Modifiers ---
        modifiers = [
            ("25", "Significant E/M"),
            ("59", "Distinct Procedural Service"),
            ("TC", "Technical Component"),
        ]
        for code, desc in modifiers:
            BillingModifier.objects.get_or_create(modifier_code=code, description=desc)

        self.stdout.write(self.style.SUCCESS("Master data for payer, rules, data keys, and billing codes populated."))
