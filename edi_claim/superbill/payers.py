import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edi_claim.settings")
django.setup()

from superbill.models import EDIClaim, EDIPayer, EDIPayerRule

# # ISA Segment
# # Envelope Segments: ISA / GS / ST / BHT / SE / GE / IEA
# EDIPayerRule.objects.create(segment_name="ISA", element_position=1, constant_value="00")  # Authorization Qualifier
# EDIPayerRule.objects.create(segment_name="ISA", element_position=2, constant_value="          ")  # Authorization Info
# EDIPayerRule.objects.create(segment_name="ISA", element_position=3, constant_value="00")  # Security Qualifier
# EDIPayerRule.objects.create(segment_name="ISA", element_position=4, constant_value="          ")  # Security Info
# EDIPayerRule.objects.create(segment_name="ISA", element_position=5, constant_value="ZZ")  # Sender Qualifier
# EDIPayerRule.objects.create(segment_name="ISA", element_position=6, constant_value="SUBMITTERID")  # Sender ID
# EDIPayerRule.objects.create(segment_name="ISA", element_position=7, constant_value="ZZ")  # Receiver Qualifier
# EDIPayerRule.objects.create(segment_name="ISA", element_position=8, constant_value="RECEIVERID")  # Receiver ID
# EDIPayerRule.objects.create(segment_name="ISA", element_position=9, constant_value="20260111")  # Interchange Date
# EDIPayerRule.objects.create(segment_name="ISA", element_position=10, constant_value="1200")  # Interchange Time
# EDIPayerRule.objects.create(segment_name="ISA", element_position=11, constant_value="U")  # Standards ID
# EDIPayerRule.objects.create(segment_name="ISA", element_position=12, constant_value="00501")  # Version
# EDIPayerRule.objects.create(segment_name="ISA", element_position=13, constant_value="000000905")  # Control #
# EDIPayerRule.objects.create(segment_name="ISA", element_position=14, constant_value="0")  # Acknowledgment
# EDIPayerRule.objects.create(segment_name="ISA", element_position=15, constant_value="T")  # Usage
# EDIPayerRule.objects.create(segment_name="ISA", element_position=16, constant_value=":")  # Component separator

# # GS Segment
# EDIPayerRule.objects.create(segment_name="GS", element_position=1, constant_value="HC")  # Functional ID
# EDIPayerRule.objects.create(segment_name="GS", element_position=2, constant_value="SUBMITTERID")  # Sender
# EDIPayerRule.objects.create(segment_name="GS", element_position=3, constant_value="RECEIVERID")  # Receiver
# EDIPayerRule.objects.create(segment_name="GS", element_position=4, constant_value="20260111")  # Date
# EDIPayerRule.objects.create(segment_name="GS", element_position=5, constant_value="1200")  # Time
# EDIPayerRule.objects.create(segment_name="GS", element_position=6, constant_value="1")  # Group Control #
# EDIPayerRule.objects.create(segment_name="GS", element_position=7, constant_value="X")  # Agency Code
# EDIPayerRule.objects.create(segment_name="GS", element_position=8, constant_value="005010X222A1")  # Version

# # ST Segment
# EDIPayerRule.objects.create(segment_name="ST", element_position=1, constant_value="837")  # Transaction Set ID
# EDIPayerRule.objects.create(segment_name="ST", element_position=2, constant_value="0001")  # Control #
# EDIPayerRule.objects.create(segment_name="ST", element_position=3, constant_value="005010X222A1")  # Implementation

# # BHT Segment
# EDIPayerRule.objects.create(segment_name="BHT", element_position=1, constant_value="0019")  # Hierarchical Structure
# EDIPayerRule.objects.create(segment_name="BHT", element_position=2, constant_value="00")  # Purpose Code
# EDIPayerRule.objects.create(segment_name="BHT", element_position=3, constant_value="01234")  # Reference
# EDIPayerRule.objects.create(segment_name="BHT", element_position=4, constant_value="20260111")  # Date
# EDIPayerRule.objects.create(segment_name="BHT", element_position=5, constant_value="1200")  # Time
# EDIPayerRule.objects.create(segment_name="BHT", element_position=6, constant_value="CH")  # Transaction Type


# # 2️⃣ Loop 1000A (Submitter)
# # NM1
# EDIPayerRule.objects.create(segment_name="NM1", element_position=1, constant_value="41")  # Entity ID
# EDIPayerRule.objects.create(segment_name="NM1", element_position=2, constant_value="2")   # Entity Type
# EDIPayerRule.objects.create(segment_name="NM1", element_position=3, constant_value="ACME BILLING")  # Name
# EDIPayerRule.objects.create(segment_name="NM1", element_position=9, constant_value="123456789")  # Submitter ID

# # N3
# EDIPayerRule.objects.create(segment_name="N3", element_position=1, constant_value="123 MAIN ST")  # Address
# EDIPayerRule.objects.create(segment_name="N3", element_position=2, constant_value="SUITE 100")  

# # N4
# EDIPayerRule.objects.create(segment_name="N4", element_position=1, constant_value="ANYTOWN")
# EDIPayerRule.objects.create(segment_name="N4", element_position=2, constant_value="CA")
# EDIPayerRule.objects.create(segment_name="N4", element_position=3, constant_value="90210")
# EDIPayerRule.objects.create(segment_name="N4", element_position=4, constant_value="US")

# # Loop 1000B (Receiver / Payer)
# # NM1
# EDIPayerRule.objects.create(segment_name="NM1", element_position=1, constant_value="40")  # Entity ID
# EDIPayerRule.objects.create(segment_name="NM1", element_position=2, constant_value="2")   # Entity Type
# EDIPayerRule.objects.create(segment_name="NM1", element_position=3, constant_value="INSURANCE CO")  # Name
# EDIPayerRule.objects.create(segment_name="NM1", element_position=9, constant_value="987654321")  # Receiver ID

# # N3
# EDIPayerRule.objects.create(segment_name="N3", element_position=1, constant_value="456 INSURANCE RD")
# EDIPayerRule.objects.create(segment_name="N3", element_position=2, constant_value="")  

# # N4
# EDIPayerRule.objects.create(segment_name="N4", element_position=1, constant_value="INSURECITY")
# EDIPayerRule.objects.create(segment_name="N4", element_position=2, constant_value="NY")
# EDIPayerRule.objects.create(segment_name="N4", element_position=3, constant_value="10001")
# EDIPayerRule.objects.create(segment_name="N4", element_position=4, constant_value="US")


# # Loop 2000A / 2010AA (Billing Provider)
# # HL
# EDIPayerRule.objects.create(segment_name="HL", element_position=1, constant_value="1")  # HL ID
# EDIPayerRule.objects.create(segment_name="HL", element_position=3, constant_value="20")  # Provider Level

# # PRV
# EDIPayerRule.objects.create(segment_name="PRV", element_position=1, constant_value="BI")  # Provider Code
# EDIPayerRule.objects.create(segment_name="PRV", element_position=3, constant_value="123456789")  # Provider NPI

# # NM1
# EDIPayerRule.objects.create(segment_name="NM1", element_position=1, constant_value="85")  # Entity ID
# EDIPayerRule.objects.create(segment_name="NM1", element_position=2, constant_value="2")   # Entity Type
# EDIPayerRule.objects.create(segment_name="NM1", element_position=3, constant_value="ACME CLINIC")  # Name
# EDIPayerRule.objects.create(segment_name="NM1", element_position=9, constant_value="123456789")  # NPI

# # N3 / N4 Address
# EDIPayerRule.objects.create(segment_name="N3", element_position=1, constant_value="123 MAIN ST")
# EDIPayerRule.objects.create(segment_name="N3", element_position=2, constant_value="SUITE 100")
# EDIPayerRule.objects.create(segment_name="N4", element_position=1, constant_value="ANYTOWN")
# EDIPayerRule.objects.create(segment_name="N4", element_position=2, constant_value="CA")
# EDIPayerRule.objects.create(segment_name="N4", element_position=3, constant_value="90210")
# EDIPayerRule.objects.create(segment_name="N4", element_position=4, constant_value="US")



# # Loop 2000B / 2010BA (Subscriber / Patient)

# # HL
# EDIPayerRule.objects.create(segment_name="HL", element_position=1, constant_value="2")  # HL ID
# EDIPayerRule.objects.create(segment_name="HL", element_position=3, constant_value="22")  # Subscriber Level

# # SBR
# EDIPayerRule.objects.create(segment_name="SBR", element_position=1, constant_value="P")  # Payer Responsibility
# EDIPayerRule.objects.create(segment_name="SBR", element_position=2, constant_value="18")  # Relationship Code

# # NM1
# EDIPayerRule.objects.create(segment_name="NM1", element_position=1, constant_value="IL")  # Entity ID
# EDIPayerRule.objects.create(segment_name="NM1", element_position=2, constant_value="1")   # Entity Type
# EDIPayerRule.objects.create(segment_name="NM1", element_position=3, constant_value="DOE")  # Last Name
# EDIPayerRule.objects.create(segment_name="NM1", element_position=4, constant_value="JOHN") # First Name
# EDIPayerRule.objects.create(segment_name="NM1", element_position=9, constant_value="123456789")  # Subscriber ID

# # N3 / N4 Address
# EDIPayerRule.objects.create(segment_name="N3", element_position=1, constant_value="789 PATIENT LN")
# EDIPayerRule.objects.create(segment_name="N3", element_position=2, constant_value="")
# EDIPayerRule.objects.create(segment_name="N4", element_position=1, constant_value="PATIENTCITY")
# EDIPayerRule.objects.create(segment_name="N4", element_position=2, constant_value="TX")
# EDIPayerRule.objects.create(segment_name="N4", element_position=3, constant_value="75001")
# EDIPayerRule.objects.create(segment_name="N4", element_position=4, constant_value="US")

# # DMG
# EDIPayerRule.objects.create(segment_name="DMG", element_position=1, constant_value="D8")  # Date Format
# EDIPayerRule.objects.create(segment_name="DMG", element_position=2, constant_value="19800101")  # DOB
# EDIPayerRule.objects.create(segment_name="DMG", element_position=3, constant_value="M")  # Gender


# # Loop 2300 / 2400 (Claim / Service Lines)

# # CLM
# EDIPayerRule.objects.create(segment_name="CLM", element_position=1, constant_value="CLM0001")  # Patient Control #
# EDIPayerRule.objects.create(segment_name="CLM", element_position=2, constant_value="150.00")  # Claim Amount
# EDIPayerRule.objects.create(segment_name="CLM", element_position=3, constant_value="Y")      # Filing Indicator

# # DTP (Claim Date)
# EDIPayerRule.objects.create(segment_name="DTP", element_position=1, constant_value="434")  # Claim Date Qualifier
# EDIPayerRule.objects.create(segment_name="DTP", element_position=2, constant_value="D8")
# EDIPayerRule.objects.create(segment_name="DTP", element_position=3, constant_value="20260101")

# # SV1 (Service Line)
# EDIPayerRule.objects.create(segment_name="SV1", element_position=1, constant_value="HC:99213:25")  # CPT
# EDIPayerRule.objects.create(segment_name="SV1", element_position=2, constant_value="100.00")      # Charge
# EDIPayerRule.objects.create(segment_name="SV1", element_position=3, constant_value="UN")           # Unit
# EDIPayerRule.objects.create(segment_name="SV1", element_position=4, constant_value="1")            # Units
# EDIPayerRule.objects.create(segment_name="SV1", element_position=5, constant_value="11")           # Place of Service

# # DTP (Service Date)
# EDIPayerRule.objects.create(segment_name="DTP", element_position=1, constant_value="472")  # Service Date
# EDIPayerRule.objects.create(segment_name="DTP", element_position=2, constant_value="D8")
# EDIPayerRule.objects.create(segment_name="DTP", element_position=3, constant_value="20260101")




import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edi_claim.settings")
django.setup()

from superbill.models import EDIPayer, EDILoop, EDIElement, EDIPayerRule

# --------------------------
# 1️⃣ Get the payer object
# --------------------------
payer = EDIPayer.objects.get(name="Your Test Payer")

print("🔥 RUNNING PAYER RULE POPULATION SCRIPT v2 🔥")

# --------------------------
# 2️⃣ Helper to get element
# --------------------------
def get_elem(loop_code, seg_name, pos):
    """Fetch EDIElement object by loop code, segment name, and element position"""
    if loop_code:
        return EDIElement.objects.get(
            segment__loop__code=loop_code,
            segment__name=seg_name,
            position=pos
        )
    else:  # envelope segments (ISA, GS, ST, BHT)
        return EDIElement.objects.get(
            segment__loop__isnull=True,
            segment__name=seg_name,
            position=pos
        )

# --------------------------
# 3️⃣ Function to create CONSTANT rules
# --------------------------
def create_rules(loop_code, rules):
    """rules = list of tuples (segment_name, element_position, constant_value)"""
    loop_obj = EDILoop.objects.get(code=loop_code) if loop_code else None
    for seg_name, pos, val in rules:
        elem = get_elem(loop_code, seg_name, pos)
        EDIPayerRule.objects.create(
            payer=payer,
            loop=loop_obj,
            element=elem,
            target_type="ELEMENT",
            rule_type="CONSTANT",
            constant_value=val,
            order=pos
        )

# --------------------------
# 4️⃣ Envelope Segments (ISA, GS, ST, BHT)
# --------------------------
create_rules(None, [
    ("ISA", 1, "00"), ("ISA", 2, "          "), ("ISA", 3, "00"), ("ISA", 4, "          "),
    ("ISA", 5, "ZZ"), ("ISA", 6, "SUBMITTERID"), ("ISA", 7, "ZZ"), ("ISA", 8, "RECEIVERID"),
    ("ISA", 9, "20260111"), ("ISA", 10, "1200"), ("ISA", 11, "U"), ("ISA", 12, "00501"),
    ("ISA", 13, "000000905"), ("ISA", 14, "0"), ("ISA", 15, "T"), ("ISA", 16, ":"),
    ("GS", 1, "HC"), ("GS", 2, "SUBMITTERID"), ("GS", 3, "RECEIVERID"), ("GS", 4, "20260111"),
    ("GS", 5, "1200"), ("GS", 6, "1"), ("GS", 7, "X"), ("GS", 8, "005010X222A1"),
    ("ST", 1, "837"), ("ST", 2, "0001"), ("ST", 3, "005010X222A1"),
    ("BHT", 1, "0019"), ("BHT", 2, "00"), ("BHT", 3, "01234"),
    ("BHT", 4, "20260111"), ("BHT", 5, "1200"), ("BHT", 6, "CH"),
])

# --------------------------
# 5️⃣ Loop 1000A (Submitter)
# --------------------------
create_rules("1000A", [
    ("NM1", 1, "41"), ("NM1", 2, "2"), ("NM1", 3, "ACME BILLING"), ("NM1", 9, "123456789"),
    ("N3", 1, "123 MAIN ST"), ("N3", 2, "SUITE 100"),
    ("N4", 1, "ANYTOWN"), ("N4", 2, "CA"), ("N4", 3, "90210"), ("N4", 4, "US"),
])

# --------------------------
# 6️⃣ Loop 1000B (Receiver / Payer)
# --------------------------
create_rules("1000B", [
    ("NM1", 1, "40"), ("NM1", 2, "2"), ("NM1", 3, "INSURANCE CO"), ("NM1", 9, "987654321"),
    ("N3", 1, "456 INSURANCE RD"), ("N3", 2, ""),
    ("N4", 1, "INSURECITY"), ("N4", 2, "NY"), ("N4", 3, "10001"), ("N4", 4, "US"),
])

# --------------------------
# 7️⃣ Loop 2000A / 2010AA (Billing Provider)
# --------------------------
create_rules("2000A", [
    ("HL", 1, "1"), ("HL", 3, "20"),
    ("PRV", 1, "BI"), ("PRV", 3, "123456789"),
    ("NM1", 1, "85"), ("NM1", 2, "2"), ("NM1", 3, "ACME CLINIC"), ("NM1", 9, "123456789"),
    ("N3", 1, "123 MAIN ST"), ("N3", 2, "SUITE 100"),
    ("N4", 1, "ANYTOWN"), ("N4", 2, "CA"), ("N4", 3, "90210"), ("N4", 4, "US"),
])

# --------------------------
# 8️⃣ Loop 2000B / 2010BA (Subscriber / Patient)
# --------------------------
create_rules("2000B", [
    ("HL", 1, "2"), ("HL", 3, "22"),
    ("SBR", 1, "P"), ("SBR", 2, "18"),
    ("NM1", 1, "IL"), ("NM1", 2, "1"), ("NM1", 3, "DOE"), ("NM1", 4, "JOHN"), ("NM1", 9, "123456789"),
    ("N3", 1, "789 PATIENT LN"), ("N3", 2, ""),
    ("N4", 1, "PATIENTCITY"), ("N4", 2, "TX"), ("N4", 3, "75001"), ("N4", 4, "US"),
    ("DMG", 1, "D8"), ("DMG", 2, "19800101"), ("DMG", 3, "M"),
])

# --------------------------
# 9️⃣ Loop 2300 / 2400 (Claim / Service Lines)
# --------------------------
create_rules("2300", [
    ("CLM", 1, "CLM0001"),
    ("CLM", 2, "150.00"), 
    ("CLM", 3, "Y"), 
    ("CLM", 4, "Y"), 
    ("CLM", 5, ["11", "B", "1"]), 
    ("CLM", 6, "Y"), 
    ("DTP", 1, "434"), 
    ("DTP", 2, "D8"), 
    ("DTP", 3, "20260101"),
    ("HI", 1, "AB123"),
    ("REF", 1, "1K"), 
    ("REF", 2, "12345"),
])


# --------------------------
# 10️⃣ Trailer segments (SE, GE, IEA)
# --------------------------
create_rules(None, [
    ("SE", 1, "23"), ("SE", 2, "0001"),
    ("GE", 1, "1"), ("GE", 2, "1"),
    ("IEA", 1, "1"), ("IEA", 2, "000000905"),
])

print("✅ EDIPayerRules populated successfully!")
