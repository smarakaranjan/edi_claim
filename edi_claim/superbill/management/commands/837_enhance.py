# import json
# from django.core.management.base import BaseCommand
# from superbill.models import EDILoop, EDISegment, EDIElement

# # Simple validators for element data types
# def validate_value(value, data_type, max_length=None):
#     if not value:
#         return True
#     if max_length and len(str(value)) > max_length:
#         return False
#     if data_type == "ID" and not isinstance(value, str):
#         return False
#     if data_type == "AN" and not isinstance(value, str):
#         return False
#     if data_type == "DT":
#         # expecting YYYYMMDD or similar
#         if not isinstance(value, str) or not value.isdigit():
#             return False
#     if data_type == "TM":
#         # expecting HHMM
#         if not isinstance(value, str) or not value.isdigit():
#             return False
#     if data_type == "R":
#         try:
#             float(value)
#         except:
#             return False
#     if data_type == "NO":
#         if not str(value).isdigit():
#             return False
#     return True


# class Command(BaseCommand):
#     help = "Load EDI 837 JSON structure (loops, segments, elements)"

#     def add_arguments(self, parser):
#         parser.add_argument("json_file", type=str, help="Path to EDI JSON file")

#     def handle(self, *args, **options):
#         json_file = options["json_file"]
#         with open(json_file) as f:
#             data = json.load(f)

#         self.stdout.write("🔄 Clearing existing EDI structure...")
#         EDIElement.objects.all().delete()
#         EDISegment.objects.all().delete()
#         EDILoop.objects.all().delete()

#         # Load envelopes
#         self.load_envelopes(data.get("envelopes", {}))

#         # Load loops recursively
#         self.load_loops(data.get("loops", {}))

#         self.stdout.write(self.style.SUCCESS("✅ EDI JSON loaded successfully."))

#     def load_envelopes(self, envelopes):
#         for seg_name, seg_data in envelopes.items():
#             segment = EDISegment.objects.create(
#                 loop=None,  # Envelope segments have no loop
#                 name=seg_name,
#                 position=0
#             )
#             self.stdout.write(f"📦 Created envelope segment: {seg_name}")
#             self.load_elements(segment, seg_data.get("elements", {}))

#     def load_loops(self, loops, parent_loop=None):
#         for loop_code, loop_data in loops.items():
#             loop = EDILoop.objects.create(
#                 code=loop_code,
#                 name=loop_data.get("name"),
#                 parent=parent_loop
#             )
#             self.stdout.write(f"🌀 Created loop: {loop_code}")
#             for seg_name, seg_data in loop_data.get("segments", {}).items():
#                 segment = EDISegment.objects.create(
#                     loop=loop,
#                     name=seg_name,
#                     position=0
#                 )
#                 self.stdout.write(f"    ➡ Created segment: {seg_name}")
#                 self.load_elements(segment, seg_data.get("elements", {}))
#             # Recursively handle subloops if present
#             subloops = loop_data.get("loops")
#             if subloops:
#                 self.load_loops(subloops, parent_loop=loop)

#     def load_elements(self, segment, elements):
#         for pos_str, el_data in elements.items():
#             pos = int(pos_str)
#             element = EDIElement.objects.create(
#                 segment=segment,
#                 position=pos,
#                 name=el_data.get("name"),
#                 x12_id=el_data.get("id"),
#                 data_type=el_data.get("data_type"),
#                 required=el_data.get("required", False),
#                 length=el_data.get("length")
#             )
#             self.stdout.write(f"        🔹 Created element: {el_data.get('id')} ({el_data.get('name')})")


# # ------------------------------
# # Example EDI validation usage:
# # ------------------------------
# # element = EDIElement.objects.first()
# # is_valid = validate_value("12345", element.data_type, element.max_length)
# # print(is_valid)



# import json
# from django.core.management.base import BaseCommand
# from superbill.models import EDILoop, EDISegment, EDIElement


# class Command(BaseCommand):
#     help = "Load EDI 837 JSON structure (loops, segments, elements) – FIXED"

#     def add_arguments(self, parser):
#         parser.add_argument("json_file", type=str, help="Path to EDI JSON file")

#     def handle(self, *args, **options):
#         json_file = options["json_file"]

#         with open(json_file) as f:
#             data = json.load(f)

#         self.stdout.write("🔄 Loading EDI structure (idempotent)...")

#         # ------------------------------------------------------------------
#         # Create virtual ENVELOPE loop
#         # ------------------------------------------------------------------
#         envelope_loop, _ = EDILoop.objects.get_or_create(
#             code="ENVELOPE",
#             parent=None,
#             defaults={"name": "X12 Envelope"}
#         )

#         # ------------------------------------------------------------------
#         # Load envelope segments (ISA, GS, ST, etc.)
#         # ------------------------------------------------------------------
#         self.load_envelopes(envelope_loop, data.get("envelopes", {}))

#         # ------------------------------------------------------------------
#         # Load loops recursively
#         # ------------------------------------------------------------------
#         self.load_loops(data.get("loops", {}), parent_loop=None)

#         self.stdout.write(self.style.SUCCESS("✅ EDI JSON loaded successfully"))

#     # ----------------------------------------------------------------------
#     # ENVELOPE SEGMENTS
#     # ----------------------------------------------------------------------
#     def load_envelopes(self, envelope_loop, envelopes):
#         position = 1
#         for seg_name, seg_data in envelopes.items():
#             segment, _ = EDISegment.objects.get_or_create(
#                 loop=envelope_loop,
#                 name=seg_name,
#                 defaults={"position": position}
#             )
#             self.stdout.write(f"📦 Envelope segment: {seg_name}")
#             self.load_elements(segment, seg_data.get("elements", {}))
#             position += 1

#     # ----------------------------------------------------------------------
#     # LOOPS (RECURSIVE)
#     # ----------------------------------------------------------------------
#     def load_loops(self, loops, parent_loop=None):
#         for loop_code, loop_data in loops.items():
#             loop, _ = EDILoop.objects.get_or_create(
#                 code=loop_code,
#                 parent=parent_loop,
#                 defaults={"name": loop_data.get("name")}
#             )
#             self.stdout.write(f"🌀 Loop: {loop_code}")

#             segment_position = 1
#             for seg_name, seg_data in loop_data.get("segments", {}).items():
#                 segment, _ = EDISegment.objects.get_or_create(
#                     loop=loop,
#                     name=seg_name,
#                     defaults={"position": segment_position}
#                 )
#                 self.stdout.write(f"    ➡ Segment: {seg_name}")
#                 self.load_elements(segment, seg_data.get("elements", {}))
#                 segment_position += 1

#             # Subloops
#             if loop_data.get("loops"):
#                 self.load_loops(loop_data["loops"], parent_loop=loop)

#     # ----------------------------------------------------------------------
#     # ELEMENTS
#     # ----------------------------------------------------------------------
#     def load_elements(self, segment, elements):
#         for pos_str, el_data in elements.items():
#             position = int(pos_str)

#             EDIElement.objects.get_or_create(
#                 segment=segment,
#                 position=position,
#                 x12_id=el_data["id"],
#                 defaults={
#                     "name": el_data.get("name"),
#                     "data_type": el_data.get("data_type"),
#                     "required": el_data.get("required", False),
#                     "length": el_data.get("length"),
#                 }
#             )

#             self.stdout.write(
#                 f"        🔹 Element {el_data['id']} (pos {position})"
#             )


# import json
# from datetime import datetime
# from django.core.management.base import BaseCommand
# from superbill.models import EDILoop, EDISegment, EDIElement


# class Command(BaseCommand):
#     help = "Load EDI 837 JSON structure (loops, segments, elements) – FIXED + constants"

#     def add_arguments(self, parser):
#         parser.add_argument("json_file", type=str, help="Path to EDI JSON file")

#     def handle(self, *args, **options):
#         json_file = options["json_file"]

#         with open(json_file) as f:
#             data = json.load(f)

#         self.stdout.write("🔄 Loading EDI structure (idempotent)...")

#         # ------------------------------------------------------------------
#         # Load envelope segments (ISA, GS, ST, etc.) with loop=None
#         # ------------------------------------------------------------------
#         self.load_envelopes(data.get("envelopes", {}))

#         # ------------------------------------------------------------------
#         # Load loops recursively
#         # ------------------------------------------------------------------
#         self.load_loops(data.get("loops", {}), parent_loop=None)

#         self.stdout.write(self.style.SUCCESS("✅ EDI JSON loaded successfully"))

#     # ----------------------------------------------------------------------
#     # ENVELOPE SEGMENTS (loop=None)
#     # ----------------------------------------------------------------------
#     def load_envelopes(self, envelopes):
#         position = 1
#         for seg_name, seg_data in envelopes.items():
#             segment, _ = EDISegment.objects.get_or_create(
#                 loop=None,  # envelope segments have no loop
#                 name=seg_name,
#                 defaults={"position": position}
#             )
#             self.stdout.write(f"📦 Envelope segment: {seg_name}")
#             self.load_elements(segment, seg_data.get("elements", {}))
#             position += 1

#     # ----------------------------------------------------------------------
#     # LOOPS (RECURSIVE)
#     # ----------------------------------------------------------------------
#     def load_loops(self, loops, parent_loop=None):
#         for loop_code, loop_data in loops.items():
#             loop, _ = EDILoop.objects.get_or_create(
#                 code=loop_code,
#                 parent=parent_loop,
#                 defaults={"name": loop_data.get("name")}
#             )
#             self.stdout.write(f"🌀 Loop: {loop_code}")

#             segment_position = 1
#             for seg_name, seg_data in loop_data.get("segments", {}).items():
#                 segment, _ = EDISegment.objects.get_or_create(
#                     loop=loop,
#                     name=seg_name,
#                     defaults={"position": segment_position}
#                 )
#                 self.stdout.write(f"    ➡ Segment: {seg_name}")
#                 self.load_elements(segment, seg_data.get("elements", {}))
#                 segment_position += 1

#             # Subloops
#             if loop_data.get("loops"):
#                 self.load_loops(loop_data["loops"], parent_loop=loop)

#     # ----------------------------------------------------------------------
#     # ELEMENTS (populate default constant values)
#     # ----------------------------------------------------------------------
#     def load_elements(self, segment, elements):
#         for pos_str, el_data in elements.items():
#             position = int(pos_str)

#             # Default constant value based on data_type (for logging only)
#             data_type = el_data.get("data_type")
#             default_value = self.get_constant_value(data_type)

#             element, _ = EDIElement.objects.get_or_create(
#                 segment=segment,
#                 position=position,
#                 x12_id=el_data["id"],
#                 defaults={
#                     "name": el_data.get("name"),
#                     "data_type": data_type,
#                     "required": el_data.get("required", False),
#                     "length": el_data.get("length"),
#                 }
#             )

#             self.stdout.write(
#                 f"        🔹 Element {el_data['id']} (pos {position}) = {default_value}"
#             )

#     # ----------------------------------------------------------------------
#     # DEFAULT CONSTANTS FOR ELEMENTS
#     # ----------------------------------------------------------------------
#     def get_constant_value(self, data_type):
#         """Return a default value based on X12 data type."""
#         now = datetime.now()
#         if data_type in ["AN", "ID"]:
#             return "X" * 5  # arbitrary alphanumeric
#         elif data_type == "NO":
#             return "1"  # numeric
#         elif data_type == "R":
#             return "123.45"  # decimal
#         elif data_type == "DT":
#             return now.strftime("%y%m%d")  # YYMMDD
#         elif data_type == "TM":
#             return now.strftime("%H%M")  # HHMM
#         else:
#             return "X"





import json
from datetime import datetime
from django.core.management.base import BaseCommand
from superbill.models import EDILoop, EDISegment, EDIElement


class Command(BaseCommand):
    help = "Load EDI 837 JSON structure (loops, segments, elements) – FIXED + constants + verification"

    def add_arguments(self, parser):
        parser.add_argument("json_file", type=str, help="Path to EDI JSON file")

    def handle(self, *args, **options):
        json_file = options["json_file"]

        with open(json_file) as f:
            data = json.load(f)

        self.stdout.write("🔄 Loading EDI structure (idempotent)...")

        # ------------------------------------------------------------------
        # Load envelope segments (ISA, GS, ST, etc.) with loop=None
        # ------------------------------------------------------------------
        self.load_envelopes(data.get("envelopes", {}))

        # ------------------------------------------------------------------
        # Load loops recursively
        # ------------------------------------------------------------------
        self.load_loops(data.get("loops", {}), parent_loop=None)

        self.stdout.write(self.style.SUCCESS("✅ EDI JSON loaded successfully"))

        # ------------------------------------------------------------------
        # Verification: check missing segments
        # ------------------------------------------------------------------
        self.verify_segments(data)

    # ----------------------------------------------------------------------
    # ENVELOPE SEGMENTS (loop=None)
    # ----------------------------------------------------------------------
    def load_envelopes(self, envelopes):
        position = 1
        for seg_name, seg_data in envelopes.items():
            segment, _ = EDISegment.objects.get_or_create(
                loop=None,  # envelope segments have no loop
                name=seg_name,
                defaults={"position": position}
            )
            self.stdout.write(f"📦 Envelope segment: {seg_name}")
            self.load_elements(segment, seg_data.get("elements", {}))
            position += 1

    # ----------------------------------------------------------------------
    # LOOPS (RECURSIVE)
    # ----------------------------------------------------------------------
    def load_loops(self, loops, parent_loop=None):
        for loop_code, loop_data in loops.items():
            loop, _ = EDILoop.objects.get_or_create(
                code=loop_code,
                parent=parent_loop,
                defaults={"name": loop_data.get("name")}
            )
            self.stdout.write(f"🌀 Loop: {loop_code}")

            segment_position = 1
            for seg_name, seg_data in loop_data.get("segments", {}).items():
                segment, _ = EDISegment.objects.get_or_create(
                    loop=loop,
                    name=seg_name,
                    defaults={"position": segment_position}
                )
                self.stdout.write(f"    ➡ Segment: {seg_name}")
                self.load_elements(segment, seg_data.get("elements", {}))
                segment_position += 1

            # Subloops
            if loop_data.get("loops"):
                self.load_loops(loop_data["loops"], parent_loop=loop)

    # ----------------------------------------------------------------------
    # ELEMENTS (populate default constant values)
    # ----------------------------------------------------------------------
    def load_elements(self, segment, elements):
        for pos_str, el_data in elements.items():
            position = int(pos_str)

            # Default constant value based on data_type (for logging only)
            data_type = el_data.get("data_type")
            default_value = self.get_constant_value(data_type)

            element, _ = EDIElement.objects.get_or_create(
                segment=segment,
                position=position,
                x12_id=el_data["id"],
                defaults={
                    "name": el_data.get("name"),
                    "data_type": data_type,
                    "required": el_data.get("required", False),
                    "length": el_data.get("length"),
                }
            )

            self.stdout.write(
                f"        🔹 Element {el_data['id']} (pos {position}) = {default_value}"
            )

    # ----------------------------------------------------------------------
    # DEFAULT CONSTANTS FOR ELEMENTS
    # ----------------------------------------------------------------------
    def get_constant_value(self, data_type):
        """Return a default value based on X12 data type."""
        now = datetime.now()
        if data_type in ["AN", "ID"]:
            return "X" * 5  # arbitrary alphanumeric
        elif data_type == "NO":
            return "1"  # numeric
        elif data_type == "R":
            return "123.45"  # decimal
        elif data_type == "DT":
            return now.strftime("%y%m%d")  # YYMMDD
        elif data_type == "TM":
            return now.strftime("%H%M")  # HHMM
        else:
            return "X"

    # ----------------------------------------------------------------------
    # VERIFICATION
    # ----------------------------------------------------------------------
    def verify_segments(self, data):
        missing_segments = []

        # Check envelope segments
        for seg_name in data.get("envelopes", {}):
            if not EDISegment.objects.filter(loop=None, name=seg_name).exists():
                missing_segments.append(f"{seg_name} (envelope)")

        # Check loops recursively
        def check_loop_segments(loops):
            for loop_code, loop_data in loops.items():
                loop = EDILoop.objects.filter(code=loop_code).first()
                if not loop:
                    missing_segments.append(f"Loop {loop_code} missing entirely")
                    continue

                for seg_name in loop_data.get("segments", {}):
                    if not EDISegment.objects.filter(loop=loop, name=seg_name).exists():
                        missing_segments.append(f"{seg_name} in loop {loop_code}")

                if loop_data.get("loops"):
                    check_loop_segments(loop_data["loops"])

        check_loop_segments(data.get("loops", {}))

        if missing_segments:
            self.stdout.write(self.style.WARNING("⚠ Missing segments detected:"))
            for seg in missing_segments:
                self.stdout.write(f"   - {seg}")
        else:
            self.stdout.write(self.style.SUCCESS("✅ All segments verified in DB"))
