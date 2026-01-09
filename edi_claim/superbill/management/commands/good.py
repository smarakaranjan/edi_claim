import json
from datetime import datetime
from django.core.management.base import BaseCommand
from superbill.models import EDIPayer, EDILoop, EDISegment, EDIElement, EDIPayerRule

# -------------------------------
# Envelope segments with strict X12 values
# -------------------------------
ENVELOPE_SEGMENTS = ["ISA", "GS", "ST", "SE", "GE", "IEA"]

ENVELOPE_VALUES = {
    "ISA": [
        "00", "          ", "00", "          ",
        "ZZ", "SENDERID      ", "ZZ", "RECEIVERID    ",
        datetime.now().strftime("%y%m%d"),
        datetime.now().strftime("%H%M"),
        "U", "00501", "000000001", "0", "P", ":"
    ],
    "GS": [
        "HC", "SENDERID", "RECEIVERID",
        datetime.now().strftime("%Y%m%d"),
        datetime.now().strftime("%H%M"),
        "1", "X", "005010X222A1"
    ],
    "ST": ["837", "0001", "005010X222A1"],
    "SE": ["1", "0001"],
    "GE": ["1", "1"],
    "IEA": ["1", "000000001"]
}

# -------------------------------
# Default loop data
# -------------------------------
LOOP_DEFAULTS = {
    "1000A": {"NM1": ["ZZ","DOE","JOHN"], "N3": ["ADDR1"], "N4": ["CITY","ST","ZIP"], "REF": ["AB","123456"]},
    "1000B": {"NM1": ["PR","INS","CO"], "N3": ["ADDR2"], "N4": ["CITY","ST","ZIP"], "REF": ["ZZ","999999"]},
    "2000A": {"HL": ["1","0","20"], "PRV": ["AD","ZZ","123"]},
    "2000B": {"HL": ["2","1","22"], "SBR": ["P","18","EMPID","",""]},
    "2010AA": {"NM1": ["IL","DOE","JANE"], "N3": ["ADDR1"], "N4": ["CITY","ST","ZIP"], "REF": ["SY","123456789"]},
    "2010BA": {"NM1": ["PR","INS","CO"], "N3": ["ADDR2"], "N4": ["CITY","ST","ZIP"], "DMG": ["D8","19600101","F"]},
    "2300": {"CLM": ["1","100.00","A","B"], "DTP": ["434","D8","20260101"], "HI": ["ABK:123"], "PWK": ["", "", ""], "REF": ["D9","111"]},
    "2400": {"LX": ["1"], "SV1": ["HC:123","100.00","UN"], "DTP": ["472","D8","20260101"], "REF": ["EA","0001"]},
}

class Command(BaseCommand):
    help = "Populate all EDI segments, elements, and EDIPayerRule constants for a payer"

    def add_arguments(self, parser):
        parser.add_argument("payer_name", type=str, help="Name of the payer")
        parser.add_argument("--json", type=str, required=False, help="Optional loop JSON path")

    def handle(self, *args, **options):
        payer_name = options["payer_name"]
        json_path = options.get("json")

        # Fetch payer
        try:
            payer = EDIPayer.objects.get(name=payer_name)
        except EDIPayer.DoesNotExist:
            self.stderr.write(f"❌ Payer '{payer_name}' not found")
            return

        # Load optional JSON loop data
        loop_data = LOOP_DEFAULTS
        if json_path:
            with open(json_path) as f:
                loop_data.update(json.load(f).get("loops", {}))

        self.stdout.write("🔄 Loading EDI structure and rules...")

        missing_segments = []

        # --------------------------
        # 1️⃣ Envelope segments
        # --------------------------
        for pos, seg_name in enumerate(ENVELOPE_SEGMENTS, start=1):
            segment, _ = EDISegment.objects.get_or_create(
                loop=None,
                name=seg_name,
                defaults={"position": pos}
            )
            self.stdout.write(f"✅ Envelope segment {seg_name} created/verified")

            for idx, val in enumerate(ENVELOPE_VALUES.get(seg_name, []), start=1):
                element = self.get_or_create_element(segment, idx, val)
                self.create_rule(payer, element, val)

        # --------------------------
        # 2️⃣ Loop segments
        # --------------------------
        for loop_code, segments in loop_data.items():
            loop, created = EDILoop.objects.get_or_create(
                code=loop_code,
                defaults={"name": loop_code}
            )
            if created:
                self.stdout.write(f"🌀 Loop {loop_code} created")
            seg_position = 1
            for seg_name, seg_values in segments.items():
                segment, _ = EDISegment.objects.get_or_create(
                    loop=loop,
                    name=seg_name,
                    defaults={"position": seg_position}
                )
                seg_position += 1

                if not isinstance(seg_values, list):
                    continue

                for idx, val in enumerate(seg_values, start=1):
                    element = self.get_or_create_element(segment, idx, val)
                    self.create_rule(payer, element, val)

                self.stdout.write(f"✅ Loop {loop_code} segment {seg_name} rules populated")

        # --------------------------
        # 3️⃣ Verify missing segments
        # --------------------------
        self.verify_segments(loop_data)

        self.stdout.write(self.style.SUCCESS("✅ EDI structure, rules, and verification completed"))

    # --------------------------
    # Helpers: create/get elements and rules
    # --------------------------
    def get_or_create_element(self, segment, position, val):
        """Create element if not exists, set default datatype and length"""
        data_type = self.detect_data_type(val)
        length = len(str(val))

        element, _ = EDIElement.objects.get_or_create(
            segment=segment,
            position=position,
            defaults={
                "x12_id": f"E{position}",
                "data_type": data_type,
                "length": length,
                "required": True,
            }
        )
        self.stdout.write(f"        ✅ Created rule for element {segment.name}{position} = {val}")
        return element

    def create_rule(self, payer, element, val):
        """Create or update EDIPayerRule"""
        length = len(str(val))
        EDIPayerRule.objects.update_or_create(
            payer=payer,
            element=element,
            target_type="ELEMENT",
            defaults={
                "rule_type": "CONSTANT",
                "constant_value": val,
                "required": True,
                "order": element.position,
                "min_length": length,
                "max_length": length,
                "pad_char": " ",
                "pad_side": "right",
            }
        )

    def detect_data_type(self, val):
        """Detect data type based on value"""
        if isinstance(val, int):
            return "N0"
        if isinstance(val, float):
            return "R"
        if isinstance(val, str):
            if val.isdigit():
                return "N0"
            elif len(val) == 6 and val.isdigit():
                return "DT"
            elif len(val) == 4 and val.isdigit():
                return "TM"
            else:
                return "AN"
        return "AN"

    # --------------------------
    # Verification function
    # --------------------------
    def verify_segments(self, data):
        missing_segments = []

        # Check envelope segments
        for seg_name in ENVELOPE_SEGMENTS:
            if not EDISegment.objects.filter(loop=None, name=seg_name).exists():
                missing_segments.append(f"{seg_name} (envelope)")

        # Check loops
        def check_loop_segments(loops):
            for loop_code, segments in loops.items():
                loop = EDILoop.objects.filter(code=loop_code).first()
                if not loop:
                    missing_segments.append(f"Loop {loop_code} missing entirely")
                    continue

                for seg_name in segments:
                    if not EDISegment.objects.filter(loop=loop, name=seg_name).exists():
                        missing_segments.append(f"{seg_name} in loop {loop_code}")

        check_loop_segments(data)

        if missing_segments:
            self.stdout.write(self.style.WARNING("⚠ Missing segments detected:"))
            for seg in missing_segments:
                self.stdout.write(f"   - {seg}")
        else:
            self.stdout.write(self.style.SUCCESS("✅ All segments verified in DB"))
