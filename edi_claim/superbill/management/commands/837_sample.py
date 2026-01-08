from django.core.management.base import BaseCommand
from superbill.models import (
    EDILoop,
    EDISegment,
    EDIElement,
    EDIPayerRule,
    EDIPayer,
)

class Command(BaseCommand):
    help = "Build FULL parser-safe 837P (005010X222A1) master data"

    def handle(self, *args, **options):
        self.stdout.write("🔧 Rebuilding FULL 837P master data...")

        # ---------------------------------------------------------------------
        # RESET
        # ---------------------------------------------------------------------
        EDIPayerRule.objects.all().delete()
        EDIElement.objects.all().delete()
        EDISegment.objects.all().delete()
        EDILoop.objects.all().delete()

        payer, _ = EDIPayer.objects.get_or_create(name="DEFAULT")

        # ---------------------------------------------------------------------
        # LOOP TREE (STRICT X12)
        # ---------------------------------------------------------------------
        def loop(code, name, parent=None):
            return EDILoop.objects.create(code=code, name=name, parent=parent)

        ISA  = loop("ISA", "Interchange")
        GS   = loop("GS", "Group", ISA)
        ST   = loop("ST", "Transaction", GS)

        L1000A = loop("1000A", "Submitter", ST)
        L1000B = loop("1000B", "Receiver", ST)

        L2000A = loop("2000A", "Billing Provider HL", ST)
        L2010AA = loop("2010AA", "Billing Provider Name", L2000A)
        L2010AB = loop("2010AB", "Pay-To Provider", L2000A)
        L2010AC = loop("2010AC", "Pay-To Plan", L2000A)

        L2000B = loop("2000B", "Subscriber HL", ST)
        L2010BA = loop("2010BA", "Subscriber Name", L2000B)
        L2010BB = loop("2010BB", "Payer Name", L2000B)

        L2000C = loop("2000C", "Patient HL", L2000B)
        L2010CA = loop("2010CA", "Patient Name", L2000C)

        L2300 = loop("2300", "Claim Information", L2000C)

        L2310A = loop("2310A", "Referring Provider", L2300)
        L2310B = loop("2310B", "Rendering Provider", L2300)
        L2310C = loop("2310C", "Service Facility", L2300)

        L2400 = loop("2400", "Service Line", L2300)

        # ---------------------------------------------------------------------
        # SEGMENT HELPER
        # ---------------------------------------------------------------------
        def seg(loop, name, pos):
            return EDISegment.objects.create(loop=loop, name=name, position=pos)

        # ---------------------------------------------------------------------
        # ENVELOPE
        # ---------------------------------------------------------------------
        seg(ISA, "ISA", 1)
        seg(ISA, "IEA", 2)

        seg(GS, "GS", 1)
        seg(GS, "GE", 2)

        seg(ST, "ST", 1)
        seg(ST, "BHT", 2)
        seg(ST, "SE", 3)

        # ---------------------------------------------------------------------
        # 1000A / 1000B
        # ---------------------------------------------------------------------
        seg(L1000A, "NM1", 1)
        seg(L1000A, "PER", 2)

        seg(L1000B, "NM1", 1)

        # ---------------------------------------------------------------------
        # 2000A
        # ---------------------------------------------------------------------
        seg(L2000A, "HL", 1)
        seg(L2000A, "PRV", 2)

        seg(L2010AA, "NM1", 1)
        seg(L2010AA, "N3", 2)
        seg(L2010AA, "N4", 3)
        seg(L2010AA, "REF", 4)
        seg(L2010AA, "PER", 5)

        seg(L2010AB, "NM1", 1)
        seg(L2010AB, "N3", 2)
        seg(L2010AB, "N4", 3)

        seg(L2010AC, "NM1", 1)
        seg(L2010AC, "N3", 2)
        seg(L2010AC, "N4", 3)
        seg(L2010AC, "REF", 4)

        # ---------------------------------------------------------------------
        # 2000B
        # ---------------------------------------------------------------------
        seg(L2000B, "HL", 1)
        seg(L2000B, "SBR", 2)
        seg(L2000B, "PAT", 3)

        seg(L2010BA, "NM1", 1)
        seg(L2010BA, "N3", 2)
        seg(L2010BA, "N4", 3)
        seg(L2010BA, "DMG", 4)
        seg(L2010BA, "REF", 5)

        seg(L2010BB, "NM1", 1)
        seg(L2010BB, "N3", 2)
        seg(L2010BB, "N4", 3)
        seg(L2010BB, "REF", 4)

        # ---------------------------------------------------------------------
        # 2000C
        # ---------------------------------------------------------------------
        seg(L2000C, "HL", 1)
        seg(L2000C, "PAT", 2)

        seg(L2010CA, "NM1", 1)
        seg(L2010CA, "N3", 2)
        seg(L2010CA, "N4", 3)
        seg(L2010CA, "DMG", 4)

        # ---------------------------------------------------------------------
        # 2300
        # ---------------------------------------------------------------------
        seg(L2300, "CLM", 1)
        seg(L2300, "DTP", 2)
        seg(L2300, "PWK", 3)
        seg(L2300, "AMT", 4)
        seg(L2300, "REF", 5)
        seg(L2300, "NTE", 6)
        seg(L2300, "HI", 7)

        seg(L2310A, "NM1", 1)
        seg(L2310A, "REF", 2)

        seg(L2310B, "NM1", 1)
        seg(L2310B, "PRV", 2)
        seg(L2310B, "REF", 3)

        seg(L2310C, "NM1", 1)
        seg(L2310C, "N3", 2)
        seg(L2310C, "N4", 3)
        seg(L2310C, "REF", 4)

        # ---------------------------------------------------------------------
        # 2400
        # ---------------------------------------------------------------------
        seg(L2400, "LX", 1)
        seg(L2400, "SV1", 2)
        seg(L2400, "PWK", 3)
        seg(L2400, "DTP", 4)
        seg(L2400, "QTY", 5)
        seg(L2400, "MEA", 6)
        seg(L2400, "REF", 7)
        seg(L2400, "NTE", 8)

        self.stdout.write(self.style.SUCCESS("✅ FULL 837P MASTER DATA BUILT SUCCESSFULLY"))




