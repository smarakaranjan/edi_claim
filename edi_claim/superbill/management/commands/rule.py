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




# superbill/management/commands/populate_payer_rules.py

# import json
# from django.core.management.base import BaseCommand
# from superbill.models import EDIPayer, EDILoop, EDISegment, EDIElement, EDIPayerRule

# class Command(BaseCommand):
#     help = "Populate EDIPayerRule for all elements and loops from JSON"

#     def add_arguments(self, parser):
#         parser.add_argument(
#             "payer_name",
#             type=str,
#             help="Payer name to assign the rules to"
#         )
#         parser.add_argument(
#             "--json",
#             type=str,
#             required=True,
#             help="Path to JSON file with loops -> segments -> elements"
#         )

#     def handle(self, *args, **options):
#         payer_name = options["payer_name"]
#         json_path = options["json"]

#         try:
#             payer = EDIPayer.objects.get(name=payer_name)
#         except EDIPayer.DoesNotExist:
#             self.stdout.write(self.style.ERROR(f"Payer '{payer_name}' not found"))
#             return

#         with open(json_path) as f:
#             data = json.load(f)

#         # Loop through JSON to create rules
#         loops = data.get("loops", {})
#         for loop_code, loop_data in loops.items():
#             # loop_code = loop_data.get("code")
#             loop_obj, _ = EDILoop.objects.get_or_create(
#                 code=loop_code, defaults={"name": loop_code}
#             )

#             # ---- LOOP level rule ----
#             EDIPayerRule.objects.get_or_create(
#                 payer=payer,
#                 loop=loop_obj,
#                 target_type="LOOP",
#                 defaults={
#                     "rule_type": "CONSTANT",
#                     "constant_value": loop_code,
#                     "order": 1,
#                 }
#             )
            
#             segments = loop_data.get("segments", {})


#             for seg_name, seg_data in segments.items():
#                 print(seg_data["name"], "segdata")
#                 seg_name = seg_data.get("name")
#                 seg_obj, _ = EDISegment.objects.get_or_create(
#                     loop=loop_obj,
#                     name=seg_name,
#                     defaults={"position": seg_data.get("position", 1)}
#                 )

#                 for el_code, el_data in seg_data.get("elements", {}).items():

#                     el_id = el_data.get("id")
                     
#                     el_obj, _ = EDIElement.objects.get_or_create(
#                         segment=seg_obj,
#                         # id=el_id,
#                         defaults={
#                             "name": el_data.get("name", el_id),
#                             "position": el_data.get("position", 1),
#                             "required": el_data.get("required", False)
#                         }
#                     )
                     
#                     # ---- ELEMENT level rule ----
#                     EDIPayerRule.objects.get_or_create(
#                         payer=payer,
#                         element=el_obj,
#                         target_type="ELEMENT",
#                         defaults={
#                             "rule_type": "CONSTANT",
#                             "constant_value": el_data.get("constant_value", ""),
#                             "order": el_data.get("order", 1),
#                             "max_length": el_data.get("max_length"),
#                             "pad_char": el_data.get("pad_char", " "),
#                             "pad_side": el_data.get("pad_side", "right")
#                         }
#                     )

#         self.stdout.write(self.style.SUCCESS("✅ EDIPayerRule population complete!"))


# import json
# from django.core.management.base import BaseCommand
# from superbill.models import (
#     EDIPayer,
#     EDILoop,
#     EDISegment,
#     EDIElement,
#     EDIPayerRule,
# )

# class Command(BaseCommand):
#     help = "Populate EDIPayerRule from JSON (X12-safe, DB-safe)"

#     def add_arguments(self, parser):
#         parser.add_argument("payer_name", type=str)
#         parser.add_argument("--json", type=str, required=True)

#     def handle(self, *args, **options):
#         payer_name = options["payer_name"]
#         json_path = options["json"]

#         try:
#             payer = EDIPayer.objects.get(name=payer_name)
#         except EDIPayer.DoesNotExist:
#             self.stderr.write(f"Payer '{payer_name}' not found")
#             return

#         with open(json_path) as f:
#             data = json.load(f)

#         for loop_code, loop_data in data.get("loops", {}).items():

#             try:
#                 loop = EDILoop.objects.get(code=loop_code)
#             except EDILoop.DoesNotExist:
#                 self.stderr.write(f"❌ Loop {loop_code} not found")
#                 continue

#             for seg_code, seg_data in loop_data.get("segments", {}).items():

#                 try:
#                     segment = EDISegment.objects.get(
#                         loop=loop,
#                         name=seg_code
#                     )
#                 except EDISegment.DoesNotExist:
#                     self.stderr.write(
#                         f"❌ Segment {seg_code} not in loop {loop_code}"
#                     )
#                     continue

#                 for pos_str, el_data in seg_data.get("elements", {}).items():
#                     position = int(pos_str)

#                     element = EDIElement.objects.filter(
#                         segment=segment,
#                         position=position
#                     ).first()

#                     if not element:
#                         self.stderr.write(
#                             f"❌ Element {position} not in {loop_code}-{seg_code}"
#                         )
#                         continue

#                     EDIPayerRule.objects.get_or_create(
#                         payer=payer,
#                         element=element,
#                         target_type="ELEMENT",
#                         defaults={
#                             "rule_type": el_data.get("rule_type", "CONSTANT"),
#                             "constant_value": el_data.get(
#                                 "constant_value", ""
#                             ),
#                             "required": el_data.get(
#                                 "required", element.required
#                             ),
#                             "order": el_data.get(
#                                 "order", element.position
#                             ),
#                             "min_length": el_data.get("min_length"),
#                             "max_length": el_data.get("max_length"),
#                             "pad_char": el_data.get("pad_char", " "),
#                             "pad_side": el_data.get("pad_side", "right"),
#                             "transformation": el_data.get("transformation"),
#                             "condition": el_data.get("condition"),
#                         }
#                     )

#         self.stdout.write(
#             self.style.SUCCESS("✅ EDIPayerRule population complete")
#         )



# import json
# from django.core.management.base import BaseCommand
# from superbill.models import (
#     EDIPayer,
#     EDILoop,
#     EDISegment,
#     EDIElement,
#     EDIPayerRule,
# )


# AUTO_SEGMENTS = {"SE", "GE", "IEA"}
# ENVELOPE_SEGMENTS = ["ISA", "GS", "ST", "BHT", "SE", "GE", "IEA"]


# class Command(BaseCommand):
#     help = "Populate EDIPayerRule for loops + envelope (X12-safe)"

#     def add_arguments(self, parser):
#         parser.add_argument("payer_name", type=str)
#         parser.add_argument("--json", type=str, required=True)

#     def handle(self, *args, **options):
#         payer_name = options["payer_name"]
#         json_path = options["json"]

#         try:
#             payer = EDIPayer.objects.get(name=payer_name)
#         except EDIPayer.DoesNotExist:
#             self.stderr.write(f"❌ Payer '{payer_name}' not found")
#             return

#         with open(json_path) as f:
#             data = json.load(f)

#         # -------------------------------------------------------
#         # LOOP SEGMENTS (JSON-driven)
#         # -------------------------------------------------------
#         for loop_code, loop_data in data.get("loops", {}).items():

#             try:
#                 loop = EDILoop.objects.get(code=loop_code)
#             except EDILoop.DoesNotExist:
#                 self.stderr.write(f"❌ Loop {loop_code} not found")
#                 continue

#             for seg_code, seg_data in loop_data.get("segments", {}).items():

#                 try:
#                     segment = EDISegment.objects.get(loop=loop, name=seg_code)
#                 except EDISegment.DoesNotExist:
#                     self.stderr.write(
#                         f"❌ Segment {seg_code} not in loop {loop_code}"
#                     )
#                     continue

#                 for pos_str, el_data in seg_data.get("elements", {}).items():
#                     position = int(pos_str)

#                     element = EDIElement.objects.filter(
#                         segment=segment,
#                         position=position
#                     ).first()

#                     if not element:
#                         self.stderr.write(
#                             f"❌ Element {position} not in {loop_code}-{seg_code}"
#                         )
#                         continue

#                     EDIPayerRule.objects.get_or_create(
#                         payer=payer,
#                         element=element,
#                         target_type="ELEMENT",
#                         defaults={
#                             "rule_type": el_data.get("rule_type", "CONSTANT"),
#                             "constant_value": el_data.get("constant_value", ""),
#                             "required": el_data.get(
#                                 "required", element.required
#                             ),
#                             "order": el_data.get(
#                                 "order", element.position
#                             ),
#                             "min_length": el_data.get("min_length"),
#                             "max_length": el_data.get("max_length"),
#                             "pad_char": el_data.get("pad_char", " "),
#                             "pad_side": el_data.get("pad_side", "right"),
#                             "transformation": el_data.get("transformation"),
#                             "condition": el_data.get("condition"),
#                         }
#                     )

#         # -------------------------------------------------------
#         # ENVELOPE SEGMENTS (DEFAULT SAFE RULES)
#         # -------------------------------------------------------
#         for seg_name in ENVELOPE_SEGMENTS:

#             try:
#                 segment = EDISegment.objects.get(
#                     loop__isnull=True,
#                     name=seg_name
#                 )
#             except EDISegment.DoesNotExist:
#                 self.stderr.write(f"❌ Envelope segment {seg_name} missing")
#                 continue

#             for element in segment.elements.all():

#                 EDIPayerRule.objects.get_or_create(
#                     payer=payer,
#                     element=element,
#                     target_type="ELEMENT",
#                     defaults={
#                         "rule_type": "CONSTANT",
#                         "constant_value": "",
#                         "required": False if seg_name in AUTO_SEGMENTS else element.required,
#                         "order": element.position,
#                         "max_length": element.length,
#                         "pad_char": " ",
#                         "pad_side": "right",
#                     }
#                 )

#         self.stdout.write(
#             self.style.SUCCESS(
#                 "✅ EDIPayerRule populated (loops + envelope)"
#             )
#         )


# import json
# from django.core.management.base import BaseCommand
# from superbill.models import (
#     EDIPayer,
#     EDILoop,
#     EDISegment,
#     EDIElement,
#     EDIPayerRule,
# )

# # ---------------------------
# # Envelope defaults for 837P
# # ---------------------------
# ENVELOPE_DEFAULTS = {
#     "ISA": {
#         1: "00",
#         2: "          ",  # 10 spaces
#         3: "00",
#         4: "          ",
#         5: "ZZ",
#         6: "SENDERID       ",  # 15 chars
#         7: "ZZ",
#         8: "RECEIVERID     ",  # 15 chars
#         9: "250101",  # YYMMDD placeholder
#         10: "1200",    # HHMM placeholder
#         11: "^",
#         12: "00501",
#         13: "000000001",  # control number
#         14: "0",
#         15: "T",
#         16: ":",
#     },
#     "GS": {
#         1: "HC",
#         2: "SENDERID",
#         3: "RECEIVERID",
#         4: "20250101",
#         5: "1200",
#         6: "1",
#         7: "X",
#         8: "005010X222A1",
#     },
#     "ST": {
#         1: "837",
#         2: "0001",
#         3: "005010X222A1",
#     },
# }

# AUTO_SEGMENTS = {"SE", "GE", "IEA"}


# class Command(BaseCommand):
#     help = "Populate EDIPayerRule for loops + envelope (X12-safe)"

#     def add_arguments(self, parser):
#         parser.add_argument("payer_name", type=str)
#         parser.add_argument("--json", type=str, required=True)

#     def handle(self, *args, **options):
#         payer_name = options["payer_name"]
#         json_path = options["json"]

#         # ----------------------------------
#         # Load Payer
#         # ----------------------------------
#         try:
#             payer = EDIPayer.objects.get(name=payer_name)
#         except EDIPayer.DoesNotExist:
#             self.stderr.write(f"❌ Payer '{payer_name}' not found")
#             return

#         # ----------------------------------
#         # Load JSON for loops
#         # ----------------------------------
#         with open(json_path) as f:
#             data = json.load(f)

#         # -------------------------------------------------------
#         # LOOP SEGMENTS (JSON-driven)
#         # -------------------------------------------------------
#         for loop_code, loop_data in data.get("loops", {}).items():

#             try:
#                 loop = EDILoop.objects.get(code=loop_code)
#             except EDILoop.DoesNotExist:
#                 self.stderr.write(f"❌ Loop {loop_code} not found")
#                 continue

#             for seg_code, seg_data in loop_data.get("segments", {}).items():

#                 try:
#                     segment = EDISegment.objects.get(loop=loop, name=seg_code)
#                 except EDISegment.DoesNotExist:
#                     self.stderr.write(
#                         f"❌ Segment {seg_code} not in loop {loop_code}"
#                     )
#                     continue

#                 for pos_str, el_data in seg_data.get("elements", {}).items():
#                     position = int(pos_str)

#                     element = EDIElement.objects.filter(
#                         segment=segment, position=position
#                     ).first()

#                     if not element:
#                         self.stderr.write(
#                             f"❌ Element {position} not in {loop_code}-{seg_code}"
#                         )
#                         continue

#                     EDIPayerRule.objects.get_or_create(
#                         payer=payer,
#                         element=element,
#                         target_type="ELEMENT",
#                         defaults={
#                             "rule_type": el_data.get("rule_type", "CONSTANT"),
#                             "constant_value": el_data.get("constant_value", ""),
#                             "required": el_data.get("required", element.required),
#                             "order": el_data.get("order", element.position),
#                             "min_length": el_data.get("min_length"),
#                             "max_length": el_data.get("max_length"),
#                             "pad_char": el_data.get("pad_char", " "),
#                             "pad_side": el_data.get("pad_side", "right"),
#                             "transformation": el_data.get("transformation"),
#                             "condition": el_data.get("condition"),
#                         },
#                     )

#         # -------------------------------------------------------
#         # ENVELOPE SEGMENTS (DEFAULT CONSTANTS)
#         # -------------------------------------------------------
#         for seg_name, values in ENVELOPE_DEFAULTS.items():

#             try:
#                 segment = EDISegment.objects.get(loop__isnull=True, name=seg_name)
#             except EDISegment.DoesNotExist:
#                 self.stderr.write(f"❌ Envelope segment {seg_name} missing")
#                 continue

#             for element in segment.elements.all():
#                 EDIPayerRule.objects.get_or_create(
#                     payer=payer,
#                     element=element,
#                     target_type="ELEMENT",
#                     defaults={
#                         "rule_type": "CONSTANT",
#                         "constant_value": values.get(element.position, ""),
#                         "required": True,
#                         "order": element.position,
#                         "max_length": element.length,
#                         "pad_char": " ",
#                         "pad_side": "right",
#                     },
#                 )

#         # -------------------------------------------------------
#         # AUTO SEGMENTS (SE, GE, IEA) — optional, no constants
#         # -------------------------------------------------------
#         for seg_name in AUTO_SEGMENTS:
#             try:
#                 segment = EDISegment.objects.get(loop__isnull=True, name=seg_name)
#             except EDISegment.DoesNotExist:
#                 self.stderr.write(f"❌ Auto segment {seg_name} missing")
#                 continue

#             for element in segment.elements.all():
#                 EDIPayerRule.objects.get_or_create(
#                     payer=payer,
#                     element=element,
#                     target_type="ELEMENT",
#                     defaults={
#                         "rule_type": "CONSTANT",
#                         "constant_value": "",
#                         "required": False,
#                         "order": element.position,
#                     },
#                 )

#         self.stdout.write(
#             self.style.SUCCESS("✅ EDIPayerRule populated (loops + envelope)")
#         )

import json
from datetime import datetime
from django.core.management.base import BaseCommand
from superbill.models import EDIPayer, EDILoop, EDISegment, EDIElement, EDIPayerRule

# Envelope defaults (type-safe)
ENVELOPE_DEFAULTS = {
    "ISA01": "00", "ISA02": "          ", "ISA03": "00", "ISA04": "          ",
    "ISA05": "ZZ", "ISA06": "SENDERID     ", "ISA07": "ZZ", "ISA08": "RECEIVERID   ",
    "ISA09": lambda: datetime.now().strftime("%y%m%d"),  # yyMMdd
    "ISA10": lambda: datetime.now().strftime("%H%M"),    # HHmm
    "ISA11": "U", "ISA12": "00501", "ISA13": 1, "ISA14": "0",
    "ISA15": "P", "ISA16": ">",

    "GS01": "HC", "GS02": "SENDERID", "GS03": "RECEIVERID",
    "GS04": lambda: datetime.now().strftime("%Y%m%d"),   # yyyyMMdd
    "GS05": lambda: datetime.now().strftime("%H%M"),     # HHmm
    "GS06": 1,
    "GS07": "X", "GS08": "005010X222A1",

    "ST01": "837", "ST02": 1,
    "SE01": 0, "SE02": 1,
    "GE01": 1, "GE02": 1,
    "IEA01": 1, "IEA02": 1,
}

# Auto segments that can be optional
AUTO_SEGMENTS = {"SE", "GE", "IEA"}
ENVELOPE_SEGMENTS = ["ISA", "GS", "ST", "SE", "GE", "IEA"]

# Placeholder values based on element type
PLACEHOLDER_BY_TYPE = {
    "AN": "DEFAULT",
    "ID": "ZZ",
    "N0": 1,
    "DT": lambda: datetime.now().strftime("%Y%m%d"),
    "TM": lambda: datetime.now().strftime("%H%M"),
    "R": 0.0,
}


class Command(BaseCommand):
    help = "Populate EDIPayerRule for all loops + envelope segments (X12-safe)"

    def add_arguments(self, parser):
        parser.add_argument("payer_name", type=str)
        parser.add_argument("--json", type=str, required=True)

    def handle(self, *args, **options):
        payer_name = options["payer_name"]
        json_path = options["json"]

        try:
            payer = EDIPayer.objects.get(name=payer_name)
        except EDIPayer.DoesNotExist:
            self.stderr.write(f"❌ Payer '{payer_name}' not found")
            return

        with open(json_path) as f:
            data = json.load(f)

        # -------------------------------
        # LOOP SEGMENTS (from JSON)
        # -------------------------------
        for loop_code, loop_data in data.get("loops", {}).items():
            try:
                loop = EDILoop.objects.get(code=loop_code)
            except EDILoop.DoesNotExist:
                self.stderr.write(f"❌ Loop {loop_code} not found")
                continue

            for seg_code, seg_data in loop_data.get("segments", {}).items():
                try:
                    segment = EDISegment.objects.get(loop=loop, name=seg_code)
                except EDISegment.DoesNotExist:
                    self.stderr.write(f"❌ Segment {seg_code} not in loop {loop_code}")
                    continue

                for pos_str, el_data in seg_data.get("elements", {}).items():
                    position = int(pos_str)
                    element = EDIElement.objects.filter(segment=segment, position=position).first()

                    if not element:
                        self.stderr.write(f"❌ Element {position} not in {loop_code}-{seg_code}")
                        continue

                    # Determine default value based on type
                    default_value = el_data.get("constant_value")
                    if default_value is None:
                        if element.data_type in PLACEHOLDER_BY_TYPE:
                            val = PLACEHOLDER_BY_TYPE[element.data_type]
                            default_value = val() if callable(val) else val
                        else:
                            default_value = "DEFAULT"

                    EDIPayerRule.objects.update_or_create(
                        payer=payer,
                        element=element,
                        target_type="ELEMENT",
                        defaults={
                            "rule_type": el_data.get("rule_type", "CONSTANT"),
                            "constant_value": default_value,
                            "required": el_data.get("required", element.required),
                            "order": el_data.get("order", element.position),
                            "min_length": el_data.get("min_length"),
                            "max_length": el_data.get("max_length"),
                            "pad_char": el_data.get("pad_char", " "),
                            "pad_side": el_data.get("pad_side", "right"),
                            "transformation": el_data.get("transformation"),
                            "condition": el_data.get("condition"),
                        }
                    )

        # -------------------------------
        # ENVELOPE SEGMENTS (ISA, GS, ST, SE, GE, IEA)
        # -------------------------------
        for seg_name in ENVELOPE_SEGMENTS:
            try:
                segment = EDISegment.objects.get(loop__isnull=True, name=seg_name)
            except EDISegment.DoesNotExist:
                self.stderr.write(f"❌ Envelope segment {seg_name} missing")
                continue

            for element in segment.elements.all():
                # Get default from ENVELOPE_DEFAULTS or by type
                if element.name in ENVELOPE_DEFAULTS:
                    val = ENVELOPE_DEFAULTS[element.name]
                    default_value = val() if callable(val) else val
                else:
                    val = PLACEHOLDER_BY_TYPE.get(element.data_type, "DEFAULT")
                    default_value = val() if callable(val) else val

                EDIPayerRule.objects.update_or_create(
                    payer=payer,
                    element=element,
                    target_type="ELEMENT",
                    defaults={
                        "rule_type": "CONSTANT",
                        "constant_value": default_value,
                        "required": False if seg_name in AUTO_SEGMENTS else element.required,
                        "order": element.position,
                        "min_length": element.length,
                        "max_length": element.length,
                        "pad_char": " ",
                        "pad_side": "right",
                    }
                )

        self.stdout.write(self.style.SUCCESS("✅ EDIPayerRule populated for all loops + envelope"))


# import json
# from datetime import datetime
# from decimal import Decimal
# from django.core.management.base import BaseCommand
# from superbill.models import EDIPayer, EDILoop, EDISegment, EDIElement, EDIPayerRule

# # Envelope segments and auto-handled segments
# ENVELOPE_SEGMENTS = ["ISA", "GS", "ST", "SE", "GE", "IEA"]
# AUTO_SEGMENTS = {"SE", "GE", "IEA"}

# # Default type-safe placeholders for EDI elements
# TYPE_SAFE_DEFAULTS = {
#     "AN": "ZZZZ",        # Alphanumeric
#     "ID": "00",          # Identifier
#     "DT": datetime.now().strftime("%y%m%d"),  # Date (yyMMdd)
#     "TM": datetime.now().strftime("%H%M"),    # Time (HHMM)
#     "N0": 1,             # Numeric integer
#     "R": Decimal("0.00"),# Decimal
# }

# # Loop-level placeholders (simplified for demo)
# LOOP_DEFAULTS = {
#     "1000A": {"NM1": ["ZZ", "DOE", "JOHN"], "N3": ["ADDR1"], "N4": ["CITY","ST","ZIP"]},
#     "1000B": {"NM1": ["ZZ", "INS", "CO"], "N3": ["ADDR2"], "N4": ["CITY","ST","ZIP"]},
#     "2000A": {"HL": ["1","0","20"]},
#     "2000B": {"HL": ["2","1","22"], "SBR": ["P","18","EMPID"]},
#     "2300": {"CLM": ["1","100.00","A","B"]},
#     # Add more loops/segments as needed
# }


# class Command(BaseCommand):
#     help = "Populate EDIPayerRule with X12-safe, type-compliant placeholders"

#     def add_arguments(self, parser):
#         parser.add_argument("payer_name", type=str)
#         parser.add_argument("--json", type=str, required=False, help="Optional loop JSON")

#     def handle(self, *args, **options):
#         payer_name = options["payer_name"]
#         json_path = options.get("json")

#         try:
#             payer = EDIPayer.objects.get(name=payer_name)
#         except EDIPayer.DoesNotExist:
#             self.stderr.write(f"❌ Payer '{payer_name}' not found")
#             return

#         # Load JSON if provided
#         json_data = {}
#         if json_path:
#             with open(json_path) as f:
#                 json_data = json.load(f)

#         # --------------------------
#         # ENVELOPE SEGMENTS
#         # --------------------------
#         for seg_name in ENVELOPE_SEGMENTS:
#             try:
#                 segment = EDISegment.objects.get(loop__isnull=True, name=seg_name)
#             except EDISegment.DoesNotExist:
#                 self.stderr.write(f"❌ Envelope segment {seg_name} missing")
#                 continue

#             for element in segment.elements.all():
#                 default_value = TYPE_SAFE_DEFAULTS.get(element.data_type, "ZZ")
#                 EDIPayerRule.objects.get_or_create(
#                     payer=payer,
#                     element=element,
#                     target_type="ELEMENT",
#                     defaults={
#                         "rule_type": "CONSTANT",
#                         "constant_value": default_value,
#                         "required": False if seg_name in AUTO_SEGMENTS else element.required,
#                         "order": element.position,
#                         "min_length": element.length,
#                         "max_length": element.length,
#                         "pad_char": " ",
#                         "pad_side": "right",
#                     }
#                 )

#         # --------------------------
#         # LOOP SEGMENTS
#         # --------------------------
#         loops_to_process = json_data.get("loops", LOOP_DEFAULTS)
#         for loop_code, loop_segments in loops_to_process.items():
#             try:
#                 loop = EDILoop.objects.get(code=loop_code)
#             except EDILoop.DoesNotExist:
#                 self.stderr.write(f"❌ Loop {loop_code} not found")
#                 continue

#             for seg_code, seg_values in loop_segments.items():
#                 try:
#                     segment = EDISegment.objects.get(loop=loop, name=seg_code)
#                 except EDISegment.DoesNotExist:
#                     self.stderr.write(f"❌ Segment {seg_code} not in loop {loop_code}")
#                     continue

#                 for element in segment.elements.all():
#                     # Determine placeholder value
#                     val_index = element.position - 1
#                     if isinstance(seg_values, list):
#                         default_value = str(seg_values[val_index]) if val_index < len(seg_values) else "ZZ"
#                     elif isinstance(seg_values, dict):
#                         default_value = str(seg_values.get(element.id, "ZZ"))
#                     else:
#                         default_value = "ZZ"

#                     # Type-safe fallback
#                     default_value = TYPE_SAFE_DEFAULTS.get(element.data_type, default_value)

#                     EDIPayerRule.objects.get_or_create(
#                         payer=payer,
#                         element=element,
#                         target_type="ELEMENT",
#                         defaults={
#                             "rule_type": "CONSTANT",
#                             "constant_value": default_value,
#                             "required": element.required,
#                             "order": element.position,
#                             "min_length": element.length,
#                             "max_length": element.length,
#                             "pad_char": " ",
#                             "pad_side": "right",
#                         }
#                     )

#         self.stdout.write(self.style.SUCCESS("✅ EDIPayerRule fully populated with X12-safe placeholders"))
