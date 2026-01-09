from django.core.management.base import BaseCommand
from superbill.models import EDISegment, EDIElement

# Define exact positions for each segment per X12 837P spec
SEGMENT_ELEMENTS = {
    "ISA": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16],
    "GS":  [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16],
    "ST":  [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16],
    "SE":  [1,2],
    "GE":  [1,2],
    "IEA": [1,2],
    # Example loops
    "NM1": [1,2,3,4,5,6,7,8,9,10],
    "N3":  [1,2,3,4,5,6,7,8,9,10],
    "N4":  [1,2,3,4,5,6,7,8,9,10],
    "REF": [1,2,3,4,5,6,7,8,9,10],
    "HL":  [1,2,3,4,5,6,7,8,9,10],
    "PRV": [1,2,3,4,5,6,7,8,9,10],
    "SBR": [1,2,3,4,5,6,7,8,9,10],
    "CLM": [1,2,3,4,5,6,7,8,9,10],
    "DTP": [1,2,3,4,5,6,7,8,9,10],
    "LX":  [1,2,3,4,5,6,7,8,9,10],
    "SV1": [1,2,3,4,5,6,7,8,9,10],
    "HI":  [1,2,3,4,5,6,7,8,9,10],
    "PWK": [1,2,3,4,5,6,7,8,9,10],
}

# Default data_type for missing elements
DEFAULT_TYPE = "AN"

class Command(BaseCommand):
    help = "Populate missing EDI elements based on segment-specific positions"

    def handle(self, *args, **options):
        segments = EDISegment.objects.all()
        self.stdout.write(f"Checking {segments.count()} segments for missing elements...")

        for segment in segments:
            positions = SEGMENT_ELEMENTS.get(segment.name)
            if not positions:
                continue  # skip segments not in spec

            existing_positions = set(segment.elements.values_list("position", flat=True))

            for pos in positions:
                if pos not in existing_positions:
                    element = EDIElement.objects.create(
                        segment=segment,
                        position=pos,
                        x12_id=f"E{pos}",
                        name=f"{segment.name}-E{pos}",
                        data_type=DEFAULT_TYPE,
                        length=2,
                        required=True,
                    )
                    self.stdout.write(f"✅ Created missing element {element.x12_id} for segment {segment.name}")

        self.stdout.write(self.style.SUCCESS("All missing elements populated!"))
