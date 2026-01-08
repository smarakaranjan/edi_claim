# # superbill/management/commands/populate_payer_rules.py
# from django.core.management.base import BaseCommand
# from superbill.models import EDIPayer, EDISegment, EDIElement, EDILoop, EDIPayerRule

# # Example constants for elements
# ELEMENT_CONSTANTS = {
#     # ISA elements
#     "ISA01": "00",
#     "ISA02": "          ",
#     "ISA03": "00",
#     "ISA04": "          ",
#     "ISA05": "ZZ",
#     "ISA06": "SENDERID       ",
#     "ISA07": "ZZ",
#     "ISA08": "RECEIVERID     ",
#     "ISA09": "260101",
#     "ISA10": "1230",
#     "ISA11": "U",
#     "ISA12": "00501",
#     "ISA13": "000000001",
#     "ISA14": "0",
#     "ISA15": "P",
#     "ISA16": ":",
#     # GS elements
#     "GS01": "HC",
#     "GS02": "SENDERID",
#     "GS03": "RECEIVERID",
#     "GS04": "20260101",
#     "GS05": "1230",
#     "GS06": "1",
#     "GS07": "X",
#     "GS08": "005010X222A1",
#     # ST elements
#     "ST01": "837",
#     "ST02": "0001",
#     "ST03": "005010X222A1",
#     # SE elements
#     "SE01": "0",  # will calculate dynamically
#     "SE02": "0001",
#     # BHT elements
#     "BHT01": "0019",
#     "BHT02": "00",
#     "BHT03": "0001",
#     "BHT04": "20260101",
#     "BHT05": "1230",
#     "BHT06": "CH",
#     # HI segment example
#     "HI01": "A123",
#     # Subscriber info 2010BA
#     "NM109": "SUBSCRIBER001",
#     "N301": "123 Main St",
#     "N401": "Anytown",
#     "N402": "CA",
#     "N403": "90001",
#     "DMG02": "19800101",
#     "DMG01": "D8",
#     "DMG03": "M",
# }

# class Command(BaseCommand):
#     help = "Populate EDIPayerRule for all elements with constant values"

#     def handle(self, *args, **kwargs):
#         payer, _ = EDIPayer.objects.get_or_create(name="TEST PAYER")
#         self.stdout.write(f"Using payer: {payer.name}")

#         # Iterate over all segments
#         for segment in EDISegment.objects.all():
#             for element in segment.elements.all():
#                 value = ELEMENT_CONSTANTS.get(element.x12_id, "X")
#                 rule, created = EDIPayerRule.objects.get_or_create(
#                     payer=payer,
#                     element=element,
#                     target_type="ELEMENT",
#                     defaults={
#                         "rule_type": "CONSTANT",
#                         "constant_value": value,
#                         "max_length": element.length or 50
#                     }
#                 )
#                 if created:
#                     self.stdout.write(f"Created rule for {element.segment.name}-{element.x12_id}")

#         # Generate multiple 2400 service lines
#         service_loop = EDILoop.objects.filter(code="2400").first()
#         if service_loop:
#             for i in range(1, 4):  # create 3 service lines
#                 for segment in service_loop.segments.all():
#                     for element in segment.elements.all():
#                         val = ELEMENT_CONSTANTS.get(element.x12_id, f"{element.x12_id}{i}")
#                         rule, _ = EDIPayerRule.objects.get_or_create(
#                             payer=payer,
#                             element=element,
#                             target_type="ELEMENT",
#                             defaults={
#                                 "rule_type": "CONSTANT",
#                                 "constant_value": val,
#                                 "max_length": element.length or 50
#                             }
#                         )

#         # HI diagnosis codes
#         hi_loop = EDILoop.objects.filter(segments__name="HI").first()
#         if hi_loop:
#             for segment in hi_loop.segments.all():
#                 for element in segment.elements.all():
#                     val = ELEMENT_CONSTANTS.get(element.x12_id, "A123")
#                     rule, _ = EDIPayerRule.objects.get_or_create(
#                         payer=payer,
#                         element=element,
#                         target_type="ELEMENT",
#                         defaults={
#                             "rule_type": "CONSTANT",
#                             "constant_value": val,
#                             "max_length": element.length or 50
#                         }
#                     )

#         # Subscriber info (2010BA)
#         subscriber_loop = EDILoop.objects.filter(code="2010BA").first()
#         if subscriber_loop:
#             for segment in subscriber_loop.segments.all():
#                 for element in segment.elements.all():
#                     val = ELEMENT_CONSTANTS.get(element.x12_id, f"{element.x12_id}_VAL")
#                     rule, _ = EDIPayerRule.objects.get_or_create(
#                         payer=payer,
#                         element=element,
#                         target_type="ELEMENT",
#                         defaults={
#                             "rule_type": "CONSTANT",
#                             "constant_value": val,
#                             "max_length": element.length or 50
#                         }
#                     )

#         self.stdout.write(self.style.SUCCESS("EDIPayerRules populated successfully!"))




# superbill/management/commands/populate_837p_rules.py
from django.core.management.base import BaseCommand
from django.db import transaction

from superbill.models import EDIPayer, EDISegment, EDIElement, EDIPayerRule

class Command(BaseCommand):
    help = "Populate ALL 837P EDIPayerRules with CONSTANT values for format validation only"

    BASE_PAYER_NAME = "Default Payer"

    # (loop, segment, position) → CONSTANT VALUE
    CONSTANTS = {
        # =========================
        # ISA – Interchange Control Header
        # =========================
        ("ISA", "ISA", 1): "00",
        ("ISA", "ISA", 2): "          ",
        ("ISA", "ISA", 3): "00",
        ("ISA", "ISA", 4): "          ",
        ("ISA", "ISA", 5): "ZZ",
        ("ISA", "ISA", 6): "SENDERID      ",
        ("ISA", "ISA", 7): "ZZ",
        ("ISA", "ISA", 8): "RECEIVERID    ",
        ("ISA", "ISA", 9): "260105",
        ("ISA", "ISA", 10): "1133",
        ("ISA", "ISA", 11): "U",
        ("ISA", "ISA", 12): "00501",
        ("ISA", "ISA", 13): "000000001",
        ("ISA", "ISA", 14): "0",
        ("ISA", "ISA", 15): "P",
        ("ISA", "ISA", 16): ":",

        # =========================
        # GS – Functional Group Header
        # =========================
        ("GS", "GS", 1): "HC",
        ("GS", "GS", 2): "SENDERID",
        ("GS", "GS", 3): "RECEIVERID",
        ("GS", "GS", 4): "20260105",
        ("GS", "GS", 5): "1133",
        ("GS", "GS", 6): "1",
        ("GS", "GS", 7): "X",
        ("GS", "GS", 8): "005010X222A1",

        # =========================
        # ST – Transaction Set Header
        # =========================
        ("ST", "ST", 1): "837",
        ("ST", "ST", 2): "0001",
        ("ST", "ST", 3): "005010X222A1",

        # =========================
        # BHT – Beginning Hierarchical Transaction
        # =========================
        ("BHT", "BHT", 1): "0019",
        ("BHT", "BHT", 2): "00",
        ("BHT", "BHT", 3): "0001",
        ("BHT", "BHT", 4): "20260105",
        ("BHT", "BHT", 5): "1133",
        ("BHT", "BHT", 6): "CH",

        # =========================
        # 1000A – Submitter
        # =========================
        ("1000A", "NM1", 1): "41",
        ("1000A", "NM1", 2): "2",
        ("1000A", "NM1", 3): "TESTSUBMITTER",
        ("1000A", "NM1", 8): "46",
        ("1000A", "NM1", 9): "123456",

        ("1000A", "PER", 1): "IC",
        ("1000A", "PER", 2): "JOHNDOE",
        ("1000A", "PER", 3): "TE",
        ("1000A", "PER", 4): "8005551212",

        # =========================
        # 1000B – Receiver
        # =========================
        ("1000B", "NM1", 1): "40",
        ("1000B", "NM1", 2): "2",
        ("1000B", "NM1", 3): "TESTPAYER",
        ("1000B", "NM1", 8): "46",
        ("1000B", "NM1", 9): "99999",

        # =========================
        # 2010AA – Billing Provider
        # =========================
        ("2010AA", "NM1", 1): "85",
        ("2010AA", "NM1", 2): "2",
        ("2010AA", "NM1", 3): "BILLINGPROVIDER",
        ("2010AA", "NM1", 8): "XX",
        ("2010AA", "NM1", 9): "1234567893",

        ("2010AA", "N3", 1): "123 MAIN ST",
        ("2010AA", "N4", 1): "DALLAS",
        ("2010AA", "N4", 2): "TX",
        ("2010AA", "N4", 3): "75001",
        ("2010AA", "REF", 1): "EI",
        ("2010AA", "REF", 2): "987654321",

        # =========================
        # 2400 – Service Line
        # =========================
        ("2400", "LX", 1): "1",
        ("2400", "SV1", 1): "HC",
        ("2400", "SV1", 2): "99213",
        ("2400", "SV1", 3): "100",
        ("2400", "SV1", 4): "UN",
        ("2400", "DTP", 1): "472",
        ("2400", "DTP", 2): "D8",
        ("2400", "DTP", 3): "20240101",
        ("2400", "HI", 1): "ABK",
        ("2400", "HI", 2): "J109",

        # =========================
        # IEA – Interchange Control Trailer
        # =========================
        ("IEA", "IEA", 1): "1",
        ("IEA", "IEA", 2): "1",

        # =========================
        # GE – Functional Group Trailer
        # =========================
        ("GE", "GE", 1): "1",
        ("GE", "GE", 2): "1",
    }

    ENVELOPE_SEGMENTS = ["ISA", "GS", "ST", "SE", "GE", "IEA"]

    @transaction.atomic
    def handle(self, *args, **options):
        payer, _ = EDIPayer.objects.get_or_create(
            name=self.BASE_PAYER_NAME,
            defaults={
                "transaction_set": "837P",
                "version": "005010X222A1",
            },
        )
        self.stdout.write(self.style.SUCCESS(f"Using payer: {payer.name}"))

        created, skipped = 0, 0

        # Iterate all elements
        for element in EDIElement.objects.select_related("segment"):
            seg = element.segment

            # Envelope segments use seg.name as loop
            if seg.name in self.ENVELOPE_SEGMENTS:
                key = (seg.name, seg.name, element.position)
            else:
                key = (getattr(seg, "loop_code", None), seg.name, element.position)

            value = self.CONSTANTS.get(key, "X")  # fallback to "X"

            _, was_created = EDIPayerRule.objects.get_or_create(
                payer=payer,
                element=element,
                defaults={
                    "rule_type": EDIPayerRule.EDIRuleType.CONSTANT,
                    "constant_value": value,
                    "min_length": None,
                    "max_length": element.length,
                    "pad_char": " ",
                    "pad_side": "right",
                    "required": True,
                    "order": 0,
                },
            )

            created += int(was_created)
            skipped += int(not was_created)

        self.stdout.write(self.style.SUCCESS(
            f"FORMAT-ONLY rules populated successfully | created={created}, skipped={skipped}"
        ))
