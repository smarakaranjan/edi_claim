import json
from django.core.management.base import BaseCommand
from superbill.models import EDILoop, EDISegment, EDIElement

# Simple validators for element data types
def validate_value(value, data_type, max_length=None):
    if not value:
        return True
    if max_length and len(str(value)) > max_length:
        return False
    if data_type == "ID" and not isinstance(value, str):
        return False
    if data_type == "AN" and not isinstance(value, str):
        return False
    if data_type == "DT":
        # expecting YYYYMMDD or similar
        if not isinstance(value, str) or not value.isdigit():
            return False
    if data_type == "TM":
        # expecting HHMM
        if not isinstance(value, str) or not value.isdigit():
            return False
    if data_type == "R":
        try:
            float(value)
        except:
            return False
    if data_type == "NO":
        if not str(value).isdigit():
            return False
    return True


class Command(BaseCommand):
    help = "Load EDI 837 JSON structure (loops, segments, elements)"

    def add_arguments(self, parser):
        parser.add_argument("json_file", type=str, help="Path to EDI JSON file")

    def handle(self, *args, **options):
        json_file = options["json_file"]
        with open(json_file) as f:
            data = json.load(f)

        self.stdout.write("🔄 Clearing existing EDI structure...")
        EDIElement.objects.all().delete()
        EDISegment.objects.all().delete()
        EDILoop.objects.all().delete()

        # Load envelopes
        self.load_envelopes(data.get("envelopes", {}))

        # Load loops recursively
        self.load_loops(data.get("loops", {}))

        self.stdout.write(self.style.SUCCESS("✅ EDI JSON loaded successfully."))

    def load_envelopes(self, envelopes):
        for seg_name, seg_data in envelopes.items():
            segment = EDISegment.objects.create(
                loop=None,  # Envelope segments have no loop
                name=seg_name,
                position=0
            )
            self.stdout.write(f"📦 Created envelope segment: {seg_name}")
            self.load_elements(segment, seg_data.get("elements", {}))

    def load_loops(self, loops, parent_loop=None):
        for loop_code, loop_data in loops.items():
            loop = EDILoop.objects.create(
                code=loop_code,
                name=loop_data.get("name"),
                parent=parent_loop
            )
            self.stdout.write(f"🌀 Created loop: {loop_code}")
            for seg_name, seg_data in loop_data.get("segments", {}).items():
                segment = EDISegment.objects.create(
                    loop=loop,
                    name=seg_name,
                    position=0
                )
                self.stdout.write(f"    ➡ Created segment: {seg_name}")
                self.load_elements(segment, seg_data.get("elements", {}))
            # Recursively handle subloops if present
            subloops = loop_data.get("loops")
            if subloops:
                self.load_loops(subloops, parent_loop=loop)

    def load_elements(self, segment, elements):
        for pos_str, el_data in elements.items():
            pos = int(pos_str)
            element = EDIElement.objects.create(
                segment=segment,
                position=pos,
                name=el_data.get("name"),
                x12_id=el_data.get("id"),
                data_type=el_data.get("data_type"),
                required=el_data.get("required", False),
                length=el_data.get("length")
            )
            self.stdout.write(f"        🔹 Created element: {el_data.get('id')} ({el_data.get('name')})")
            sub_elements = el_data.get("elements")
            if sub_elements:
                for sub_pos_str, sub_el_data in sub_elements.items():
                    sub_pos = int(sub_pos_str)
                    sub_element = EDIElement.objects.create(
                        segment=segment,
                        parent=element,           # link to composite parent
                        position=sub_pos,
                        name=sub_el_data.get("name"),
                        x12_id=sub_el_data.get("id"),
                        data_type=sub_el_data.get("data_type"),
                        required=sub_el_data.get("required", False),
                        length=sub_el_data.get("length")
                    )
                    self.stdout.write(f"            🔹 Created sub-element: {sub_el_data.get('id')} ({sub_el_data.get('name')})")



 


 