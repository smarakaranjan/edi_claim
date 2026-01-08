# # # superbill/management/commands/populate_payer_rules.py
# # from django.core.management.base import BaseCommand
# # from superbill.models import EDIPayer, EDISegment, EDIElement, EDILoop, EDIPayerRule

# # # Example constants for elements
# # ELEMENT_CONSTANTS = {
# #     # ISA elements
# #     "ISA01": "00",
# #     "ISA02": "          ",
# #     "ISA03": "00",
# #     "ISA04": "          ",
# #     "ISA05": "ZZ",
# #     "ISA06": "SENDERID       ",
# #     "ISA07": "ZZ",
# #     "ISA08": "RECEIVERID     ",
# #     "ISA09": "260101",
# #     "ISA10": "1230",
# #     "ISA11": "U",
# #     "ISA12": "00501",
# #     "ISA13": "000000001",
# #     "ISA14": "0",
# #     "ISA15": "P",
# #     "ISA16": ":",
# #     # GS elements
# #     "GS01": "HC",
# #     "GS02": "SENDERID",
# #     "GS03": "RECEIVERID",
# #     "GS04": "20260101",
# #     "GS05": "1230",
# #     "GS06": "1",
# #     "GS07": "X",
# #     "GS08": "005010X222A1",
# #     # ST elements
# #     "ST01": "837",
# #     "ST02": "0001",
# #     "ST03": "005010X222A1",
# #     # SE elements
# #     "SE01": "0",  # will calculate dynamically
# #     "SE02": "0001",
# #     # BHT elements
# #     "BHT01": "0019",
# #     "BHT02": "00",
# #     "BHT03": "0001",
# #     "BHT04": "20260101",
# #     "BHT05": "1230",
# #     "BHT06": "CH",
# #     # HI segment example
# #     "HI01": "A123",
# #     # Subscriber info 2010BA
# #     "NM109": "SUBSCRIBER001",
# #     "N301": "123 Main St",
# #     "N401": "Anytown",
# #     "N402": "CA",
# #     "N403": "90001",
# #     "DMG02": "19800101",
# #     "DMG01": "D8",
# #     "DMG03": "M",
# # }

# # class Command(BaseCommand):
# #     help = "Populate EDIPayerRule for all elements with constant values"

# #     def handle(self, *args, **kwargs):
# #         payer, _ = EDIPayer.objects.get_or_create(name="TEST PAYER")
# #         self.stdout.write(f"Using payer: {payer.name}")

# #         # Iterate over all segments
# #         for segment in EDISegment.objects.all():
# #             for element in segment.elements.all():
# #                 value = ELEMENT_CONSTANTS.get(element.x12_id, "X")
# #                 rule, created = EDIPayerRule.objects.get_or_create(
# #                     payer=payer,
# #                     element=element,
# #                     target_type="ELEMENT",
# #                     defaults={
# #                         "rule_type": "CONSTANT",
# #                         "constant_value": value,
# #                         "max_length": element.length or 50
# #                     }
# #                 )
# #                 if created:
# #                     self.stdout.write(f"Created rule for {element.segment.name}-{element.x12_id}")

# #         # Generate multiple 2400 service lines
# #         service_loop = EDILoop.objects.filter(code="2400").first()
# #         if service_loop:
# #             for i in range(1, 4):  # create 3 service lines
# #                 for segment in service_loop.segments.all():
# #                     for element in segment.elements.all():
# #                         val = ELEMENT_CONSTANTS.get(element.x12_id, f"{element.x12_id}{i}")
# #                         rule, _ = EDIPayerRule.objects.get_or_create(
# #                             payer=payer,
# #                             element=element,
# #                             target_type="ELEMENT",
# #                             defaults={
# #                                 "rule_type": "CONSTANT",
# #                                 "constant_value": val,
# #                                 "max_length": element.length or 50
# #                             }
# #                         )

# #         # HI diagnosis codes
# #         hi_loop = EDILoop.objects.filter(segments__name="HI").first()
# #         if hi_loop:
# #             for segment in hi_loop.segments.all():
# #                 for element in segment.elements.all():
# #                     val = ELEMENT_CONSTANTS.get(element.x12_id, "A123")
# #                     rule, _ = EDIPayerRule.objects.get_or_create(
# #                         payer=payer,
# #                         element=element,
# #                         target_type="ELEMENT",
# #                         defaults={
# #                             "rule_type": "CONSTANT",
# #                             "constant_value": val,
# #                             "max_length": element.length or 50
# #                         }
# #                     )

# #         # Subscriber info (2010BA)
# #         subscriber_loop = EDILoop.objects.filter(code="2010BA").first()
# #         if subscriber_loop:
# #             for segment in subscriber_loop.segments.all():
# #                 for element in segment.elements.all():
# #                     val = ELEMENT_CONSTANTS.get(element.x12_id, f"{element.x12_id}_VAL")
# #                     rule, _ = EDIPayerRule.objects.get_or_create(
# #                         payer=payer,
# #                         element=element,
# #                         target_type="ELEMENT",
# #                         defaults={
# #                             "rule_type": "CONSTANT",
# #                             "constant_value": val,
# #                             "max_length": element.length or 50
# #                         }
# #                     )

# #         self.stdout.write(self.style.SUCCESS("EDIPayerRules populated successfully!"))




# import json
# from django.core.management.base import BaseCommand
# from superbill.models import EDIPayer, EDILoop, EDISegment, EDIElement, EDIPayerRule

# # Update this to the JSON path containing your EDI definition
# EDI_JSON_PATH = "/home/smarak/Desktop/DataTerrain/edi_claim/edi_claim/superbill/edi.json"


# class Command(BaseCommand):
#     help = "Populate EDIPayerRule for all loops, segments, and elements from EDI JSON"

#     def add_arguments(self, parser):
#         parser.add_argument(
#             "--payer", type=str, required=True, help="EDIPayer ID or name"
#         )
#         parser.add_argument(
#             "--force", action="store_true", help="Overwrite existing rules"
#         )
#         parser.add_argument(
#             "--json", type=str, default=EDI_JSON_PATH, help="Path to EDI JSON file"
#         )

#     def handle(self, *args, **options):
#         payer_identifier = options["payer"]
#         force = options["force"]
#         json_path = options["json"]

#         # Get payer instance
#         try:
#             if payer_identifier.isdigit():
#                 payer = EDIPayer.objects.get(id=int(payer_identifier))
#             else:
#                 payer = EDIPayer.objects.get(name=payer_identifier)
#         except EDIPayer.DoesNotExist:
#             self.stderr.write(self.style.ERROR(f"Payer '{payer_identifier}' not found"))
#             return

#         # Load JSON
#         with open(json_path) as f:
#             edi_def = json.load(f)

#         # Helper to create rule
#         def create_element_rule(element):
#             rule, created = EDIPayerRule.objects.get_or_create(
#                 payer=payer,
#                 target_type="ELEMENT",
#                 element=element,
#                 defaults={
#                     "rule_type": "CONSTANT",
#                     "constant_value": "",
#                     "order": 1,
#                 },
#             )
#             if not created and force:
#                 rule.rule_type = "CONSTANT"
#                 rule.constant_value = ""
#                 rule.save()

#         def create_loop_rule(loop):
#             rule, created = EDIPayerRule.objects.get_or_create(
#                 payer=payer,
#                 target_type="LOOP",
#                 loop=loop,
#                 defaults={
#                     "rule_type": "FIELD",
#                     "order": 1,
#                     "data_key": None,  # can be assigned later if needed
#                 },
#             )
#             if not created and force:
#                 rule.rule_type = "FIELD"
#                 rule.data_key = None
#                 rule.save()

#         # Process envelopes (optional if you want rules for ISA/GS/ST/SE)
#         for seg_name, seg_data in edi_def.get("envelopes", {}).items():
#             try:
#                 segment = EDISegment.objects.get(loop__isnull=True, name=seg_name)
#             except EDISegment.DoesNotExist:
#                 self.stdout.write(self.style.WARNING(f"Segment {seg_name} not found"))
#                 continue
#             for el_name, el_data in seg_data.get("elements", {}).items():
#                 try:
#                     element = EDIElement.objects.get(segment=segment, name=el_data["name"])
#                     create_element_rule(element)
#                 except EDIElement.DoesNotExist:
#                     self.stdout.write(self.style.WARNING(f"Element {el_data['name']} not found"))

#         # Process loops recursively
#         def process_loop(loop_code, loop_data, parent_loop=None):
#             try:
#                 loop = EDILoop.objects.get(code=loop_code)
#             except EDILoop.DoesNotExist:
#                 self.stdout.write(self.style.WARNING(f"Loop {loop_code} not found"))
#                 return

#             create_loop_rule(loop)

#             # Process segments
#             for seg_name, seg_data in loop_data.get("segments", {}).items():
#                 try:
#                     segment = EDISegment.objects.get(loop=loop, name=seg_name)
#                 except EDISegment.DoesNotExist:
#                     self.stdout.write(self.style.WARNING(f"Segment {seg_name} in loop {loop_code} not found"))
#                     continue
#                 for el_name, el_data in seg_data.get("elements", {}).items():
#                     try:
#                         element = EDIElement.objects.get(segment=segment, name=el_data["name"])
#                         create_element_rule(element)
#                     except EDIElement.DoesNotExist:
#                         self.stdout.write(self.style.WARNING(f"Element {el_data['name']} not found in segment {seg_name}"))

#             # Process subloops
#             for subloop_code, subloop_data in loop_data.get("subloops", {}).items():
#                 process_loop(subloop_code, subloop_data, parent_loop=loop)

#         for loop_code, loop_data in edi_def.get("loops", {}).items():
#             process_loop(loop_code, loop_data)

#         self.stdout.write(self.style.SUCCESS(f"EDIPayerRule scaffold created for payer '{payer.name}'"))




import json
from django.core.management.base import BaseCommand
from superbill.models import (
    EDIPayer, EDILoop, EDISegment, EDIElement, EDIPayerRule
)

# Path to your JSON file
JSON_PATH = "/home/smarak/Desktop/DataTerrain/edi_claim/edi_claim/superbill/edi.json"  # <-- update this


class Command(BaseCommand):
    help = "Populate EDIPayerRule, EDILoop, EDISegment, EDIElement from JSON"

    def handle(self, *args, **options):
        with open(JSON_PATH) as f:
            edi_json = json.load(f)

        payer, _ = EDIPayer.objects.get_or_create(name="DEFAULT PAYER")
        self.stdout.write(f"Using payer: {payer.name}")

        # --- POPULATE ENVELOPES ---
        for env_name, env_data in edi_json.get("envelopes", {}).items():
            segment, _ = EDISegment.objects.get_or_create(
                name=env_name,
                loop=None
            )
            for el_pos, el_data in env_data.get("elements", {}).items():
                element, _ = EDIElement.objects.get_or_create(
                    segment=segment,
                    position=int(el_pos),
                    defaults={
                        "name": el_data.get("name"),
                        "data_type": el_data.get("data_type"),
                        "required": el_data.get("required", False),
                    }
                )
                EDIPayerRule.objects.get_or_create(
                    payer=payer,
                    element=element,
                    target_type="ELEMENT",
                    defaults={
                        "rule_type": "CONSTANT",
                        "constant_value": "",
                        "order": 1,
                    }
                )

        # --- POPULATE LOOPS, SEGMENTS, ELEMENTS ---
        for loop_code, loop_data in edi_json.get("loops", {}).items():
            loop, _ = EDILoop.objects.get_or_create(
                code=loop_code,
                defaults={"name": loop_data.get("name")}
            )

            # Loop-level rule
            EDIPayerRule.objects.get_or_create(
                payer=payer,
                target_type="LOOP",
                constant_value=loop_code,
                defaults={
                    "rule_type": "CONSTANT",
                    "order": 1
                }
            )

            for seg_name, seg_data in loop_data.get("segments", {}).items():
                segment, _ = EDISegment.objects.get_or_create(
                    name=seg_name,
                    loop=loop
                )
                for el_pos, el_data in seg_data.get("elements", {}).items():
                    element, _ = EDIElement.objects.get_or_create(
                        segment=segment,
                        position=int(el_pos),
                        defaults={
                            "name": el_data.get("name"),
                            "data_type": el_data.get("data_type"),
                            "required": el_data.get("required", False),
                        }
                    )
                    EDIPayerRule.objects.get_or_create(
                        payer=payer,
                        element=element,
                        target_type="ELEMENT",
                        defaults={
                            "rule_type": "CONSTANT",
                            "constant_value": "",
                            "order": 1,
                        }
                    )

        self.stdout.write(self.style.SUCCESS("✅ All EDIPayerRules populated successfully!"))
