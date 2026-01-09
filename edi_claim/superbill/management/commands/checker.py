import json
from datetime import datetime
from django.core.management.base import BaseCommand
from superbill.models import EDILoop, EDISegment, EDIElement, EDIPayer, EDIPayerRule

# Type-safe defaults for elements
TYPE_SAFE_DEFAULTS = {
    "AN": "ZZ",
    "ID": "00",
    "DT": datetime.now().strftime("%y%m%d"),
    "TM": datetime.now().strftime("%H%M"),
    "N0": "1",
    "R": "0.00",
}


class Command(BaseCommand):
    help = "Populate missing EDI elements with type-safe defaults"

    def add_arguments(self, parser):
        parser.add_argument(
            "--payer", type=str, help="Optional payer name to populate EDIPayerRule"
        )

    def handle(self, *args, **options):
        payer_name = options.get("payer")
        payer = None

        if payer_name:
            try:
                payer = EDIPayer.objects.get(name=payer_name)
            except EDIPayer.DoesNotExist:
                self.stderr.write(f"❌ Payer '{payer_name}' not found. Skipping rules.")

        segments = EDISegment.objects.all()
        self.stdout.write(f"🔄 Checking {segments.count()} segments for missing elements...")

        for segment in segments:
            existing_positions = set(
                segment.elements.values_list("position", flat=True)
            )

            # Determine total positions expected for segment
            # We'll assume up to 16 for envelopes, 10 for loops (adjust if needed)
            if segment.loop is None:  # Envelope
                total_positions = 16
            else:
                total_positions = 10  # Default max elements for loop segments
                # Optional: dynamically read from segment.elements or JSON spec

            for pos in range(1, total_positions + 1):
                if pos not in existing_positions:
                    # Determine data_type
                    data_type = "AN" if pos <= 5 else "ID"  # simple heuristic
                    default_val = TYPE_SAFE_DEFAULTS.get(data_type, "ZZ")

                    element = EDIElement.objects.create(
                        segment=segment,
                        position=pos,
                        x12_id=f"E{pos}",
                        name=f"{segment.name}-E{pos}",
                        data_type=data_type,
                        length=len(default_val),
                        required=True,
                    )
                    self.stdout.write(f"🆕 Created missing element {element.x12_id} in {segment.name}")

                    # Populate payer rule if payer is given
                    if payer:
                        EDIPayerRule.objects.update_or_create(
                            payer=payer,
                            element=element,
                            target_type="ELEMENT",
                            defaults={
                                "rule_type": "CONSTANT",
                                "constant_value": default_val,
                                "required": True,
                                "order": pos,
                                "min_length": len(default_val),
                                "max_length": len(default_val),
                                "pad_char": " ",
                                "pad_side": "right",
                            },
                        )

        self.stdout.write(self.style.SUCCESS("✅ Missing elements populated successfully"))
