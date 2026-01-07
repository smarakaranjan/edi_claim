# from django.core.management.base import BaseCommand
# from datetime import datetime
# from superbill.models import EDILoop, EDISegment, EDIElement, EDIPayerRule, EDIPayer

# class Command(BaseCommand):
#     help = "Populate production-grade 837 master data with loops, segments, elements, and payer rules."

#     def handle(self, *args, **options):
#         self.stdout.write("Starting production-grade 837 master data population...")

#         # --- Clear existing data ---
#         EDIPayerRule.objects.all().delete()
#         EDIElement.objects.all().delete()
#         EDISegment.objects.all().delete()
#         EDILoop.objects.all().delete()

#         # --- Loops ---
#         loops = [
#             ("ISA_LOOP", "Interchange Control Header", None),
#             ("GS_LOOP", "Functional Group Header", "ISA_LOOP"),
#             ("ST_LOOP", "Transaction Set Header", "GS_LOOP"),
#             ("1000A", "Submitter", "ST_LOOP"),
#             ("1000B", "Receiver", "ST_LOOP"),
#             ("2000A", "Billing Provider Hierarchical Loop", "ST_LOOP"),
#             ("2000B", "Subscriber Hierarchical Loop", "ST_LOOP"),
#             ("2300", "Claim Information", "2000B"),
#             ("2400", "Service Line", "2300"),
#         ]

#         loop_objs = {}
#         for code, name, parent_code in loops:
#             parent = loop_objs.get(parent_code)
#             loop_objs[code] = EDILoop.objects.create(code=code, name=name, parent=parent)

#         # --- Segments per loop ---
#         segments = {
#             "ISA_LOOP": ["ISA", "IEA"],
#             "GS_LOOP": ["GS", "GE"],
#             "ST_LOOP": ["ST", "SE"],
#             "1000A": ["NM1", "N3", "N4", "REF"],
#             "1000B": ["NM1", "N3", "N4", "REF"],
#             "2000A": ["HL", "PRV", "NM1", "N3", "N4", "REF", "PER"],
#             "2000B": ["HL", "SBR", "NM1", "N3", "N4", "DMG", "REF"],
#             "2300": ["CLM", "DTP", "HI", "REF"],
#             "2400": ["LX", "SV1", "DTP", "PWK", "REF", "MEA", "CN1"],
#         }

#         segment_objs = {}
#         for loop_code, seg_names in segments.items():
#             loop = loop_objs[loop_code]
#             for i, seg_name in enumerate(seg_names, start=1):
#                 seg = EDISegment.objects.create(loop=loop, name=seg_name, position=i)
#                 segment_objs[f"{loop_code}_{seg_name}"] = seg

#         # --- Elements per segment with proper production values ---
#         elements = {
#             # ISA Loop
#             "ISA_LOOP_ISA": [
#                 ("Authorization Information Qualifier", "AN", 2, "00"),
#                 ("Authorization Information", "AN", 10, "          "),
#                 ("Security Info Qualifier", "AN", 2, "00"),
#                 ("Security Info", "AN", 10, "          "),
#                 ("Interchange ID Qualifier Sender", "AN", 2, "ZZ"),
#                 ("Interchange Sender ID", "AN", 15, "SENDERID      "),
#                 ("Interchange ID Qualifier Receiver", "AN", 2, "ZZ"),
#                 ("Interchange Receiver ID", "AN", 15, "RECEIVERID    "),
#                 ("Interchange Date", "DT", 6, datetime.now().strftime("%y%m%d")),
#                 ("Interchange Time", "TM", 4, datetime.now().strftime("%H%M")),
#                 ("Interchange Control Standards ID", "AN", 1, "U"),
#                 ("Interchange Control Version Number", "AN", 5, "00501"),
#                 ("Interchange Control Number", "N0", 9, 1),
#                 ("Acknowledgment Requested", "AN", 1, "0"),
#                 ("Usage Indicator", "AN", 1, "P"),
#                 ("Component Element Separator", "AN", 1, ":"),
#             ],
#             "ISA_LOOP_IEA": [
#                 ("Number of Included Functional Groups", "N0", 5, 1),
#                 ("Interchange Control Number", "N0", 9, 1),
#             ],
#             # GS Loop
#             "GS_LOOP_GS": [
#                 ("Functional ID Code", "AN", 2, "HC"),
#                 ("Application Sender Code", "AN", 15, "SENDERID"),
#                 ("Application Receiver Code", "AN", 15, "RECEIVERID"),
#                 ("Date", "DT", 8, datetime.now().strftime("%Y%m%d")),
#                 ("Time", "TM", 4, datetime.now().strftime("%H%M")),
#                 ("Group Control Number", "N0", 9, 1),
#                 ("Responsible Agency Code", "AN", 2, "X"),
#                 ("Version/Release/Industry ID Code", "AN", 12, "005010X222A1"),
#             ],
#             "GS_LOOP_GE": [
#                 ("Number of Transaction Sets Included", "N0", 5, 1),
#                 ("Group Control Number", "N0", 9, 1),
#             ],
#             # ST Loop
#             "ST_LOOP_ST": [
#                 ("Transaction Set Identifier Code", "AN", 3, "837"),
#                 ("Transaction Set Control Number", "AN", 9, "0001"),
#             ],
#             "ST_LOOP_SE": [
#                 ("Number of Included Segments", "N0", 10, 10),
#                 ("Transaction Set Control Number", "AN", 9, "0001"),
#             ],
#             # 1000A Submitter
#             "1000A_NM1": [
#                 ("Entity Identifier Code", "AN", 2, "41"),
#                 ("Entity Type Qualifier", "AN", 1, "2"),
#                 ("Submitter Name", "AN", 60, "SUBMITTER NAME"),
#                 ("Identification Code Qualifier", "AN", 2, "46"),
#                 ("Submitter Identifier", "AN", 80, "123456789"),
#             ],
#             # 1000B Receiver
#             "1000B_NM1": [
#                 ("Entity Identifier Code", "AN", 2, "40"),
#                 ("Entity Type Qualifier", "AN", 1, "2"),
#                 ("Receiver Name", "AN", 60, "RECEIVER NAME"),
#                 ("Identification Code Qualifier", "AN", 2, "46"),
#                 ("Receiver Identifier", "AN", 80, "987654321"),
#             ],
#             # 2000B Subscriber HL
#             "2000B_HL": [
#                 ("Hierarchical ID Number", "N0", 12, 2),
#                 ("Hierarchical Parent ID", "N0", 12, 1),
#                 ("Hierarchical Level Code", "AN", 2, "22"),
#                 ("Hierarchical Child Code", "AN", 1, "0"),
#             ],
#             # 2300 Claim
#             "2300_CLM": [
#                 ("Claim Submitter Identifier", "AN", 38, "CLAIM12345"),
#                 ("Total Claim Charge Amount", "R2", 18, 100.00),
#                 ("Claim Filing Indicator Code", "AN", 2, "CI"),
#             ],
#             # 2400 Service Line
#             "2400_SV1": [
#                 ("Procedure Code", "AN", 48, "99213"),
#                 ("Line Item Charge Amount", "R2", 18, 75.00),
#                 ("Unit or Basis for Measurement Code", "AN", 2, "UN"),
#                 ("Service Unit Count", "R2", 10, 1),
#                 ("Place of Service Code", "AN", 2, "11"),
#             ],
#         }

#         # --- Create elements and payer rules ---
#         EDI_PAYER, _ = EDIPayer.objects.get_or_create(name="Default Payer")
#         element_objs = {}

#         for seg_key, elems in elements.items():
#             seg = segment_objs.get(seg_key)
#             if not seg:
#                 continue
#             for i, (name, dtype, length, val) in enumerate(elems, start=1):
#                 elem = EDIElement.objects.create(
#                     segment=seg,
#                     position=i,
#                     name=name,
#                     data_type=dtype,
#                     length=length
#                 )
#                 element_objs[f"{seg_key}_{i}"] = elem

#                 # Create proper production-grade payer rule
#                 EDIPayerRule.objects.create(
#                     element=elem,
#                     payer=EDI_PAYER,
#                     rule_type="CONSTANT",
#                     constant_value=val
#                 )

#         self.stdout.write(self.style.SUCCESS(
#             "✅ Production-grade 837 master data populated successfully!"
#         ))




# from django.core.management.base import BaseCommand
# from superbill.models import EDILoop, EDISegment, EDIElement, EDIPayerRule, EDIPayer

# class Command(BaseCommand):
#     help = "Populate production-ready 837 master data (loops, segments, elements, rules)."

#     def handle(self, *args, **options):
#         self.stdout.write("Starting production-ready 837 master data population...")

#         # --- Clear existing data ---
#         EDIPayerRule.objects.all().delete()
#         EDIElement.objects.all().delete()
#         EDISegment.objects.all().delete()
#         EDILoop.objects.all().delete()

#         # --- Loops ---
#         loops = [
#             ("ISA_LOOP", "Interchange Control Header", None),
#             ("GS_LOOP", "Functional Group Header", "ISA_LOOP"),
#             ("ST_LOOP", "Transaction Set Header", "GS_LOOP"),
#             ("1000A", "Submitter", "ST_LOOP"),
#             ("1000B", "Receiver", "ST_LOOP"),
#             ("2000A", "Billing Provider HL", "ST_LOOP"),
#             ("2000B", "Subscriber HL", "ST_LOOP"),
#             ("2300", "Claim Information", "2000B"),
#             ("2400", "Service Line", "2300"),
#         ]

#         loop_objs = {}
#         for code, name, parent_code in loops:
#             parent = loop_objs.get(parent_code)
#             loop_objs[code] = EDILoop.objects.create(code=code, name=name, parent=parent)

#         # --- Segments per loop ---
#         segments = {
#             "ISA_LOOP": ["ISA", "IEA"],
#             "GS_LOOP": ["GS", "GE"],
#             "ST_LOOP": ["ST", "SE"],
#             "1000A": ["NM1", "N3", "N4", "REF"],
#             "1000B": ["NM1", "N3", "N4", "REF"],
#             "2000A": ["HL", "PRV", "NM1", "N3", "N4", "REF", "PER"],
#             "2000B": ["HL", "SBR", "NM1", "N3", "N4", "DMG", "REF"],
#             "2300": ["CLM", "DTP", "HI", "REF"],
#             "2400": ["LX", "SV1", "DTP", "PWK", "REF", "MEA", "CN1"],
#         }

#         segment_objs = {}
#         for loop_code, seg_names in segments.items():
#             loop = loop_objs[loop_code]
#             for i, seg_name in enumerate(seg_names, start=1):
#                 seg = EDISegment.objects.create(loop=loop, name=seg_name, position=i)
#                 segment_objs[f"{loop_code}_{seg_name}"] = seg

#         # --- Elements per segment (production-ready sample values) ---
#         elements = {
#             # ISA Loop
#             "ISA_LOOP_ISA": [
#                 ("Authorization Info Qualifier", "AN", 2, "00"),
#                 ("Authorization Info", "AN", 10, "          "),
#                 ("Security Info Qualifier", "AN", 2, "00"),
#                 ("Security Info", "AN", 10, "          "),
#                 ("Interchange ID Qualifier", "AN", 2, "ZZ"),
#                 ("Interchange Sender ID", "AN", 15, "SENDERID      "),
#                 ("Interchange ID Qualifier", "AN", 2, "ZZ"),
#                 ("Interchange Receiver ID", "AN", 15, "RECEIVERID    "),
#                 ("Interchange Date", "DT", 6, "260105"),  # YYMMDD
#                 ("Interchange Time", "TM", 4, "1133"),    # HHMM
#                 ("Control Standards ID", "AN", 1, "U"),
#                 ("Interchange Version Number", "AN", 5, "00501"),
#                 ("Interchange Control Number", "N0", 9, "000000001"),
#                 ("Acknowledgment Requested", "AN", 1, "0"),
#                 ("Usage Indicator", "AN", 1, "P"),
#                 ("Component Element Separator", "AN", 1, ":")
#             ],
#             "ISA_LOOP_IEA": [
#                 ("Number of Included Functional Groups", "N0", 5, "1"),
#                 ("Interchange Control Number", "N0", 9, "000000001")
#             ],

#             # GS Loop
#             "GS_LOOP_GS": [
#                 ("Functional ID Code", "AN", 2, "HC"),
#                 ("Application Sender Code", "AN", 15, "SENDERID"),
#                 ("Application Receiver Code", "AN", 15, "RECEIVERID"),
#                 ("Date", "DT", 8, "20260105"),
#                 ("Time", "TM", 4, "1133"),
#                 ("Group Control Number", "N0", 9, "1"),
#                 ("Responsible Agency Code", "AN", 2, "X"),
#                 ("Version/Release/Industry ID Code", "AN", 12, "005010X222A1")
#             ],
#             "GS_LOOP_GE": [
#                 ("Number of Transaction Sets Included", "N0", 5, "1"),
#                 ("Group Control Number", "N0", 9, "1")
#             ],

#             # ST Loop
#             "ST_LOOP_ST": [
#                 ("Transaction Set Identifier Code", "AN", 3, "837"),
#                 ("Transaction Set Control Number", "AN", 9, "0001")
#             ],
#             "ST_LOOP_SE": [
#                 ("Number of Included Segments", "N0", 10, "10"),
#                 ("Transaction Set Control Number", "AN", 9, "0001")
#             ],

#             # 1000A Submitter
#             "1000A_NM1": [
#                 ("Entity Identifier Code", "AN", 2, "41"),
#                 ("Entity Type Qualifier", "AN", 1, "2"),
#                 ("Submitter Name", "AN", 60, "SUBMITTER NAME"),
#                 ("Identification Code Qualifier", "AN", 2, "46"),
#                 ("Submitter ID", "AN", 80, "123456789")
#             ],

#             # 1000B Receiver
#             "1000B_NM1": [
#                 ("Entity Identifier Code", "AN", 2, "40"),
#                 ("Entity Type Qualifier", "AN", 1, "2"),
#                 ("Receiver Name", "AN", 60, "RECEIVER NAME"),
#                 ("Identification Code Qualifier", "AN", 2, "46"),
#                 ("Receiver ID", "AN", 80, "987654321")
#             ],

#             # 2000A Billing HL
#             "2000A_HL": [
#                 ("Hierarchical ID Number", "N0", 12, "1"),
#                 ("Hierarchical Parent ID", "N0", 12, ""),
#                 ("Hierarchical Level Code", "AN", 2, "20"),
#                 ("Hierarchical Child Code", "AN", 1, "1")
#             ],
#             "2000A_PRV": [
#                 ("Provider Code", "AN", 2, "BI"),
#                 ("Reference ID", "AN", 10, "PXC"),
#                 ("Provider Specialty", "AN", 5, "207Q0")
#             ],

#             # 2000B Subscriber HL
#             "2000B_HL": [
#                 ("Hierarchical ID Number", "N0", 12, "2"),
#                 ("Hierarchical Parent ID", "N0", 12, "1"),
#                 ("Hierarchical Level Code", "AN", 2, "22"),
#                 ("Hierarchical Child Code", "AN", 1, "0")
#             ],
#             "2000B_SBR": [
#                 ("Payer Responsibility Sequence", "AN", 1, "P"),
#                 ("Individual Relationship Code", "AN", 2, "18")
#             ],

#             # 2300 Claim
#             "2300_CLM": [
#                 ("Claim Submitter Identifier", "AN", 38, "CLAIM12345"),
#                 ("Total Claim Charge Amount", "R2", 18, "100.00"),
#                 ("Claim Filing Indicator Code", "AN", 2, "CI")
#             ],

#             # 2400 Service Line
#             "2400_SV1": [
#                 ("Procedure Code", "AN", 48, "99213"),
#                 ("Line Item Charge Amount", "R2", 18, "75.00"),
#                 ("Unit or Basis for Measurement Code", "AN", 2, "UN"),
#                 ("Service Unit Count", "R2", 10, "1"),
#                 ("Place of Service Code", "AN", 2, "11")
#             ],
#         }

#         # --- Create elements with production-ready payer rules ---
#         EDI_PAYER, _ = EDIPayer.objects.get_or_create(name="Default Payer")
#         element_objs = {}

#         for seg_key, elems in elements.items():
#             seg = segment_objs.get(seg_key)
#             if not seg:
#                 continue
#             for i, (name, dtype, length, value) in enumerate(elems, start=1):
#                 elem = EDIElement.objects.create(
#                     segment=seg,
#                     position=i,
#                     name=name,
#                     data_type=dtype,
#                     length=length
#                 )
#                 element_objs[f"{seg_key}_{i}"] = elem

#                 # --- Use proper value for payer rule ---
#                 EDIPayerRule.objects.create(
#                     element=elem,
#                     payer=EDI_PAYER,
#                     rule_type="CONSTANT",
#                     constant_value=value
#                 )

#         self.stdout.write(self.style.SUCCESS("Production-ready 837 master data populated successfully."))


# from django.core.management.base import BaseCommand
# from superbill.models import EDILoop, EDISegment, EDIElement, EDIPayerRule, EDIPayer

# class Command(BaseCommand):
#     help = "Populate master data for dynamic 837 claim generation (production-ready loops, segments, elements, rules)."

#     def handle(self, *args, **options):
#         self.stdout.write("Starting production-ready 837 master data population...")

#         # --- Clear existing data ---
#         EDIPayerRule.objects.all().delete()
#         EDIElement.objects.all().delete()
#         EDISegment.objects.all().delete()
#         EDILoop.objects.all().delete()

#         # --- Loops ---
#         loops = [
#             ("ISA_LOOP", "Interchange Control Header", None),
#             ("GS_LOOP", "Functional Group Header", "ISA_LOOP"),
#             ("ST_LOOP", "Transaction Set Header", "GS_LOOP"),
#             ("1000A", "Submitter", "ST_LOOP"),
#             ("1000B", "Receiver", "ST_LOOP"),
#             ("2000A", "Billing Provider Hierarchical Loop", "ST_LOOP"),
#             ("2000B", "Subscriber Hierarchical Loop", "ST_LOOP"),
#             ("2300", "Claim Information", "2000B"),
#             ("2400", "Service Line", "2300"),
#         ]

#         loop_objs = {}
#         for code, name, parent_code in loops:
#             parent = loop_objs.get(parent_code)
#             loop_objs[code] = EDILoop.objects.create(code=code, name=name, parent=parent)

#         # --- Segments per loop ---
#         segments = {
#             "ISA_LOOP": ["ISA", "IEA"],
#             "GS_LOOP": ["GS", "GE"],
#             "ST_LOOP": ["ST", "SE"],
#             "1000A": ["NM1", "N3", "N4", "REF"],
#             "1000B": ["NM1", "N3", "N4", "REF"],
#             "2000A": ["HL", "PRV", "NM1", "N3", "N4", "REF", "PER"],
#             "2000B": ["HL", "SBR", "NM1", "N3", "N4", "DMG", "REF"],
#             "2300": ["CLM", "DTP", "HI", "REF"],
#             "2400": ["LX", "SV1", "DTP", "PWK", "REF", "MEA", "CN1"],
#         }

#         segment_objs = {}
#         for loop_code, seg_names in segments.items():
#             loop = loop_objs[loop_code]
#             for i, seg_name in enumerate(seg_names, start=1):
#                 seg = EDISegment.objects.create(loop=loop, name=seg_name, position=i)
#                 segment_objs[f"{loop_code}_{seg_name}"] = seg

#         # --- Elements per segment with production-ready values ---
#         elements = {
#             # ISA Loop
#             "ISA_LOOP_ISA": [
#                 ("Authorization Information Qualifier", "AN", 2, "00"),
#                 ("Authorization Information", "AN", 10, "AUTHO_VAL"),
#                 ("Security Info Qualifier", "AN", 2, "00"),
#                 ("Security Info", "AN", 10, "SECUR_VAL"),
#                 ("Interchange ID Qualifier (Sender)", "AN", 2, "ZZ"),
#                 ("Interchange Sender ID", "AN", 15, "SENDERID"),
#                 ("Interchange ID Qualifier (Receiver)", "AN", 2, "ZZ"),
#                 ("Interchange Receiver ID", "AN", 15, "RECEIVERID"),
#                 ("Interchange Date", "DT", 6, "260105"),
#                 ("Interchange Time", "TM", 4, "1133"),
#                 ("Interchange Control Standards ID", "AN", 1, "U"),
#                 ("Interchange Control Version Number", "AN", 5, "00501"),
#                 ("Interchange Control Number", "N0", 9, "1"),
#                 ("Acknowledgment Requested", "AN", 1, "0"),
#                 ("Usage Indicator", "AN", 1, "P"),
#                 ("Component Element Separator", "AN", 1, ":")
#             ],
#             "ISA_LOOP_IEA": [
#                 ("Number of Included Functional Groups", "N0", 5, "1"),
#                 ("Interchange Control Number", "N0", 9, "1")
#             ],
#             # GS Loop
#             "GS_LOOP_GS": [
#                 ("Functional ID Code", "AN", 2, "HC"),
#                 ("Application Sender Code", "AN", 15, "SENDERID"),
#                 ("Application Receiver Code", "AN", 15, "RECEIVERID"),
#                 ("Date", "DT", 8, "20260105"),
#                 ("Time", "TM", 4, "1133"),
#                 ("Group Control Number", "N0", 9, "1"),
#                 ("Responsible Agency Code", "AN", 2, "X"),
#                 ("Version/Release/Industry ID Code", "AN", 12, "005010X222A1")
#             ],
#             "GS_LOOP_GE": [
#                 ("Number of Transaction Sets Included", "N0", 5, "1"),
#                 ("Group Control Number", "N0", 9, "1")
#             ],
#             # ST Loop
#             "ST_LOOP_ST": [
#                 ("Transaction Set Identifier Code", "AN", 3, "837"),
#                 ("Transaction Set Control Number", "AN", 9, "0001")
#             ],
#             "ST_LOOP_SE": [
#                 ("Number of Included Segments", "N0", 10, "10"),
#                 ("Transaction Set Control Number", "AN", 9, "0001")
#             ],
#             # 1000A Submitter
#             "1000A_NM1": [
#                 ("Entity Identifier Code", "AN", 2, "41"),
#                 ("Entity Type Qualifier", "AN", 1, "2"),
#                 ("Submitter Name", "AN", 60, "SUBMITTER NAME"),
#                 ("Identification Code Qualifier", "AN", 2, "46"),
#                 ("Submitter Identifier", "AN", 80, "123456789")
#             ],
#             # 1000B Receiver
#             "1000B_NM1": [
#                 ("Entity Identifier Code", "AN", 2, "40"),
#                 ("Entity Type Qualifier", "AN", 1, "2"),
#                 ("Receiver Name", "AN", 60, "RECEIVER NAME"),
#                 ("Identification Code Qualifier", "AN", 2, "46"),
#                 ("Receiver Identifier", "AN", 80, "987654321")
#             ],
#             # 2000A Billing Provider HL & PRV & NM1
#             "2000A_HL": [
#                 ("Hierarchical ID Number", "N0", 12, "1"),
#                 ("Hierarchical Parent ID Number", "N0", 12, ""),
#                 ("Hierarchical Level Code", "AN", 2, "20"),
#                 ("Hierarchical Child Code", "AN", 1, "1")
#             ],
#             "2000A_PRV": [
#                 ("Provider Code", "AN", 2, "BI"),
#                 ("Reference Identification Code", "AN", 3, "PXC"),
#                 ("Provider Taxonomy Code", "AN", 5, "207Q0")
#             ],
#             "2000A_NM1": [
#                 ("Entity Identifier Code", "AN", 2, "85"),
#                 ("Entity Type Qualifier", "AN", 1, "2"),
#                 ("Billing Provider Name", "AN", 60, "BILLING PROVIDER"),
#                 ("Identification Code Qualifier", "AN", 2, "XX"),
#                 ("Billing Provider NPI", "AN", 80, "1234567893")
#             ],
#             # 2000B Subscriber HL & SBR & NM1
#             "2000B_HL": [
#                 ("Hierarchical ID Number", "N0", 12, "2"),
#                 ("Hierarchical Parent ID Number", "N0", 12, "1"),
#                 ("Hierarchical Level Code", "AN", 2, "22"),
#                 ("Hierarchical Child Code", "AN", 1, "0")
#             ],
#             "2000B_SBR": [
#                 ("Payer Responsibility Sequence", "AN", 1, "P"),
#                 ("Individual Relationship Code", "AN", 2, "18")
#             ],
#             "2000B_NM1": [
#                 ("Entity Identifier Code", "AN", 2, "IL"),
#                 ("Entity Type Qualifier", "AN", 1, "1"),
#                 ("Subscriber Last Name", "AN", 35, "DOE"),
#                 ("Subscriber First Name", "AN", 25, "JOHN"),
#                 ("Identification Code Qualifier", "AN", 2, "MI"),
#                 ("Subscriber Identifier", "AN", 80, "123456789")
#             ],
#             # 2300 Claim
#             "2300_CLM": [
#                 ("Claim Submitter Identifier", "AN", 38, "CLAIM12345"),
#                 ("Total Claim Charge Amount", "R2", 18, "100.00"),
#                 ("Claim Filing Indicator Code", "AN", 2, "CI")
#             ],
#             # 2400 Service Line
#             "2400_SV1": [
#                 ("Composite Procedure Code", "AN", 48, "99213"),
#                 ("Line Item Charge Amount", "R2", 18, "75.00"),
#                 ("Unit or Basis for Measurement Code", "AN", 2, "UN"),
#                 ("Service Unit Count", "R2", 10, "1"),
#                 ("Place of Service Code", "AN", 2, "11")
#             ]
#         }

#         # --- Create elements & payer rules ---
#         EDI_PAYER, _ = EDIPayer.objects.get_or_create(name="Default Payer")
#         for seg_key, elems in elements.items():
#             seg = segment_objs.get(seg_key)
#             if not seg:
#                 continue
#             for i, (name, dtype, length, const_value) in enumerate(elems, start=1):
#                 elem = EDIElement.objects.create(
#                     segment=seg,
#                     position=i,
#                     name=name,
#                     data_type=dtype,
#                     length=length
#                 )
#                 # Production-ready constant rule
#                 EDIPayerRule.objects.create(
#                     element=elem,
#                     payer=EDI_PAYER,
#                     rule_type="CONSTANT",
#                     constant_value=const_value
#                 )

#         self.stdout.write(self.style.SUCCESS(
#             "Full production-ready 837 master data (loops, segments, elements, rules) populated successfully."
#         ))




# superbill/management/commands/populate_full_837p.py

from django.core.management.base import BaseCommand
from superbill.models import EDILoop, EDISegment, EDIElement

class Command(BaseCommand):
    help = "Populate EDILoop, EDISegment, and EDIElement tables with full 837P example"

    def handle(self, *args, **options):
        # 1️⃣ Loops
        loops_data = [
            {"code": "1000A", "name": "Submitter Loop", "parent": None},
            {"code": "1000B", "name": "Receiver Loop", "parent": None},
            {"code": "2000A", "name": "Billing Provider Loop", "parent": None},
            {"code": "2010AA", "name": "Billing Provider Details", "parent": "2000A"},
            {"code": "2010AB", "name": "Pay-To Provider", "parent": "2000A"},
            {"code": "2000B", "name": "Subscriber Loop", "parent": None},
            {"code": "2010BA", "name": "Subscriber Details", "parent": "2000B"},
            {"code": "2000C", "name": "Patient Loop", "parent": "2000B"},
            {"code": "2010CA", "name": "Patient Details", "parent": "2000C"},
            {"code": "2300", "name": "Claim Info", "parent": "2000C"},
            {"code": "2310A", "name": "Rendering Provider", "parent": "2300"},
            {"code": "2310B", "name": "Referring Provider", "parent": "2300"},
            {"code": "2310C", "name": "Supervising Provider", "parent": "2300"},
            {"code": "2400", "name": "Service Line", "parent": "2300"},
        ]

        loops = {}
        for loop in loops_data:
            parent_instance = loops.get(loop["parent"])
            loops[loop["code"]] = EDILoop.objects.create(
                code=loop["code"],
                name=loop["name"],
                parent=parent_instance
            )

        
        segments_data = [

            # =========================
            # 1000A – Submitter
            # =========================
            {"loop": "1000A", "position": 1, "name": "NM1"},
            {"loop": "1000A", "position": 2, "name": "PER"},

            # =========================
            # 1000B – Receiver
            # =========================
            {"loop": "1000B", "position": 1, "name": "NM1"},

            # =========================
            # 2000A – Billing Provider HL
            # =========================
            {"loop": "2000A", "position": 1, "name": "HL"},
            {"loop": "2000A", "position": 2, "name": "PRV"},

            # =========================
            # 2010AA – Billing Provider Details
            # =========================
            {"loop": "2010AA", "position": 1, "name": "NM1"},
            {"loop": "2010AA", "position": 2, "name": "N3"},
            {"loop": "2010AA", "position": 3, "name": "N4"},
            {"loop": "2010AA", "position": 4, "name": "REF"},
            {"loop": "2010AA", "position": 5, "name": "PER"},

            # =========================
            # 2010AB – Pay-To Provider
            # =========================
            {"loop": "2010AB", "position": 1, "name": "NM1"},
            {"loop": "2010AB", "position": 2, "name": "N3"},
            {"loop": "2010AB", "position": 3, "name": "N4"},
            {"loop": "2010AB", "position": 4, "name": "REF"},

            # =========================
            # 2000B – Subscriber HL
            # =========================
            {"loop": "2000B", "position": 1, "name": "HL"},
            {"loop": "2000B", "position": 2, "name": "SBR"},

            # =========================
            # 2010BA – Subscriber Details
            # =========================
            {"loop": "2010BA", "position": 1, "name": "NM1"},
            {"loop": "2010BA", "position": 2, "name": "N3"},
            {"loop": "2010BA", "position": 3, "name": "N4"},
            {"loop": "2010BA", "position": 4, "name": "DMG"},
            {"loop": "2010BA", "position": 5, "name": "REF"},

            # =========================
            # 2000C – Patient HL
            # =========================
            {"loop": "2000C", "position": 1, "name": "HL"},
            {"loop": "2000C", "position": 2, "name": "PAT"},

            # =========================
            # 2010CA – Patient Details
            # =========================
            {"loop": "2010CA", "position": 1, "name": "NM1"},
            {"loop": "2010CA", "position": 2, "name": "N3"},
            {"loop": "2010CA", "position": 3, "name": "N4"},
            {"loop": "2010CA", "position": 4, "name": "DMG"},
            {"loop": "2010CA", "position": 5, "name": "REF"},

            # =========================
            # 2300 – Claim Information
            # =========================
            {"loop": "2300", "position": 1, "name": "CLM"},
            {"loop": "2300", "position": 2, "name": "DTP"},
            {"loop": "2300", "position": 3, "name": "PWK"},
            {"loop": "2300", "position": 4, "name": "AMT"},
            {"loop": "2300", "position": 5, "name": "REF"},
            {"loop": "2300", "position": 6, "name": "NTE"},
            {"loop": "2300", "position": 7, "name": "HI"},

            # =========================
            # 2310A – Rendering Provider
            # =========================
            {"loop": "2310A", "position": 1, "name": "NM1"},
            {"loop": "2310A", "position": 2, "name": "N3"},
            {"loop": "2310A", "position": 3, "name": "N4"},
            {"loop": "2310A", "position": 4, "name": "REF"},
            {"loop": "2310A", "position": 5, "name": "PRV"},

            # =========================
            # 2310B – Referring Provider
            # =========================
            {"loop": "2310B", "position": 1, "name": "NM1"},
            {"loop": "2310B", "position": 2, "name": "N3"},
            {"loop": "2310B", "position": 3, "name": "N4"},
            {"loop": "2310B", "position": 4, "name": "REF"},

            # =========================
            # 2310C – Supervising Provider
            # =========================
            {"loop": "2310C", "position": 1, "name": "NM1"},
            {"loop": "2310C", "position": 2, "name": "N3"},
            {"loop": "2310C", "position": 3, "name": "N4"},
            {"loop": "2310C", "position": 4, "name": "REF"},
            {"loop": "2310C", "position": 5, "name": "PRV"},

            # =========================
            # 2400 – Service Line
            # =========================
            {"loop": "2400", "position": 1, "name": "LX"},
            {"loop": "2400", "position": 2, "name": "SV1"},
            {"loop": "2400", "position": 3, "name": "PWK"},
            {"loop": "2400", "position": 4, "name": "DTP"},
            {"loop": "2400", "position": 5, "name": "REF"},
            {"loop": "2400", "position": 6, "name": "HI"},
            {"loop": "2400", "position": 7, "name": "CN1"},
            {"loop": "2400", "position": 8, "name": "SVD"},
            {"loop": "2400", "position": 9, "name": "CAS"},
        ]


        segments = {}
        for seg in segments_data:
            loop_instance = loops[seg["loop"]]
            key = f"{seg['loop']}_{seg['name']}_{seg['position']}"
            segments[key] = EDISegment.objects.create(
                loop=loop_instance,
                name=seg["name"],
                position=seg["position"]
            )

        # 3️⃣ Elements
        # This is an example for NM1 segments; you would expand for all segments in your example
        elements_data = [
        # -----------------------------
        # 1000A - Submitter
        # -----------------------------
        {"segment": "1000A_NM1_1", "position": 1, "name": "Entity Identifier Code", "data_type": "AN", "length": 2},
        {"segment": "1000A_NM1_1", "position": 2, "name": "Entity Type Qualifier", "data_type": "ID", "length": 1},
        {"segment": "1000A_NM1_1", "position": 3, "name": "Name Last/Organization Name", "data_type": "AN", "length": 60},
        {"segment": "1000A_NM1_1", "position": 4, "name": "Name First", "data_type": "AN", "length": 35},
        {"segment": "1000A_NM1_1", "position": 5, "name": "Name Middle", "data_type": "AN", "length": 25},
        {"segment": "1000A_NM1_1", "position": 6, "name": "Name Prefix", "data_type": "AN", "length": 10},
        {"segment": "1000A_NM1_1", "position": 7, "name": "Name Suffix", "data_type": "AN", "length": 10},
        {"segment": "1000A_NM1_1", "position": 8, "name": "Identification Code Qualifier", "data_type": "ID", "length": 2},
        {"segment": "1000A_NM1_1", "position": 9, "name": "Identification Code", "data_type": "AN", "length": 80},

        {"segment": "1000A_PER_2", "position": 1, "name": "Contact Function Code", "data_type": "ID", "length": 2},
        {"segment": "1000A_PER_2", "position": 2, "name": "Name", "data_type": "AN", "length": 60},
        {"segment": "1000A_PER_2", "position": 3, "name": "Communication Number Qualifier", "data_type": "ID", "length": 2},
        {"segment": "1000A_PER_2", "position": 4, "name": "Communication Number", "data_type": "AN", "length": 80},
        {"segment": "1000A_PER_2", "position": 5, "name": "Extra Communication Qualifier", "data_type": "ID", "length": 2},
        {"segment": "1000A_PER_2", "position": 6, "name": "Extra Communication Number", "data_type": "AN", "length": 80},

        # -----------------------------
        # 1000B - Receiver
        # -----------------------------
        {"segment": "1000B_NM1_1", "position": 1, "name": "Entity Identifier Code", "data_type": "AN", "length": 2},
        {"segment": "1000B_NM1_1", "position": 2, "name": "Entity Type Qualifier", "data_type": "ID", "length": 1},
        {"segment": "1000B_NM1_1", "position": 3, "name": "Name Last/Organization Name", "data_type": "AN", "length": 60},
        {"segment": "1000B_NM1_1", "position": 8, "name": "Identification Code Qualifier", "data_type": "ID", "length": 2},
        {"segment": "1000B_NM1_1", "position": 9, "name": "Identification Code", "data_type": "AN", "length": 80},

        # -----------------------------
        # 2010AA - Billing Provider Details
        # -----------------------------
        {"segment": "2010AA_NM1_1", "position": 1, "name": "Entity Identifier Code", "data_type": "AN", "length": 2},
        {"segment": "2010AA_NM1_1", "position": 2, "name": "Entity Type Qualifier", "data_type": "ID", "length": 1},
        {"segment": "2010AA_NM1_1", "position": 3, "name": "Last Name", "data_type": "AN", "length": 35},
        {"segment": "2010AA_NM1_1", "position": 4, "name": "First Name", "data_type": "AN", "length": 25},
        {"segment": "2010AA_NM1_1", "position": 8, "name": "Identification Code Qualifier", "data_type": "ID", "length": 2},
        {"segment": "2010AA_NM1_1", "position": 9, "name": "Identification Code", "data_type": "AN", "length": 80},

        {"segment": "2010AA_N3_2", "position": 1, "name": "Address Line 1", "data_type": "AN", "length": 55},
        {"segment": "2010AA_N3_2", "position": 2, "name": "Address Line 2", "data_type": "AN", "length": 55},

        {"segment": "2010AA_N4_3", "position": 1, "name": "City Name", "data_type": "AN", "length": 30},
        {"segment": "2010AA_N4_3", "position": 2, "name": "State Code", "data_type": "ID", "length": 2},
        {"segment": "2010AA_N4_3", "position": 3, "name": "Postal Code", "data_type": "ID", "length": 15},

        {"segment": "2010AA_REF_4", "position": 1, "name": "Reference Identification Qualifier", "data_type": "ID", "length": 2},
        {"segment": "2010AA_REF_4", "position": 2, "name": "Reference Identification", "data_type": "AN", "length": 50},

        {"segment": "2010AA_PER_5", "position": 1, "name": "Contact Function Code", "data_type": "ID", "length": 2},
        {"segment": "2010AA_PER_5", "position": 2, "name": "Name", "data_type": "AN", "length": 60},
        {"segment": "2010AA_PER_5", "position": 3, "name": "Communication Number Qualifier", "data_type": "ID", "length": 2},
        {"segment": "2010AA_PER_5", "position": 4, "name": "Communication Number", "data_type": "AN", "length": 80},
        {"segment": "2010AA_PER_5", "position": 5, "name": "Extra Communication Qualifier", "data_type": "ID", "length": 2},
        {"segment": "2010AA_PER_5", "position": 6, "name": "Extra Communication Number", "data_type": "AN", "length": 80},

        # -----------------------------
        # 2010AB - Pay-To Provider
        # -----------------------------
        {"segment": "2010AB_NM1_1", "position": 1, "name": "Entity Identifier Code", "data_type": "AN", "length": 2},
        {"segment": "2010AB_NM1_1", "position": 2, "name": "Entity Type Qualifier", "data_type": "ID", "length": 1},
        {"segment": "2010AB_NM1_1", "position": 3, "name": "Last Name", "data_type": "AN", "length": 35},
        {"segment": "2010AB_NM1_1", "position": 4, "name": "First Name", "data_type": "AN", "length": 25},
        {"segment": "2010AB_NM1_1", "position": 8, "name": "Identification Code Qualifier", "data_type": "ID", "length": 2},
        {"segment": "2010AB_NM1_1", "position": 9, "name": "Identification Code", "data_type": "AN", "length": 80},

        {"segment": "2010AB_N3_2", "position": 1, "name": "Address Line 1", "data_type": "AN", "length": 55},
        {"segment": "2010AB_N3_2", "position": 2, "name": "Address Line 2", "data_type": "AN", "length": 55},

        {"segment": "2010AB_N4_3", "position": 1, "name": "City Name", "data_type": "AN", "length": 30},
        {"segment": "2010AB_N4_3", "position": 2, "name": "State Code", "data_type": "ID", "length": 2},
        {"segment": "2010AB_N4_3", "position": 3, "name": "Postal Code", "data_type": "ID", "length": 15},

        {"segment": "2010AB_REF_4", "position": 1, "name": "Reference Identification Qualifier", "data_type": "ID", "length": 2},
        {"segment": "2010AB_REF_4", "position": 2, "name": "Reference Identification", "data_type": "AN", "length": 50},

        # -----------------------------
        # 2310A/B/C - Providers
        # -----------------------------
        {"segment": "2310A_NM1_1", "position": 1, "name": "Entity Identifier Code", "data_type": "AN", "length": 2},
        {"segment": "2310A_NM1_1", "position": 2, "name": "Entity Type Qualifier", "data_type": "ID", "length": 1},
        {"segment": "2310A_NM1_1", "position": 3, "name": "Last Name", "data_type": "AN", "length": 35},
        {"segment": "2310A_NM1_1", "position": 4, "name": "First Name", "data_type": "AN", "length": 25},
        {"segment": "2310A_NM1_1", "position": 8, "name": "Identification Code Qualifier", "data_type": "ID", "length": 2},
        {"segment": "2310A_NM1_1", "position": 9, "name": "Identification Code", "data_type": "AN", "length": 80},

        {"segment": "2310B_NM1_1", "position": 1, "name": "Entity Identifier Code", "data_type": "AN", "length": 2},
        {"segment": "2310B_NM1_1", "position": 2, "name": "Entity Type Qualifier", "data_type": "ID", "length": 1},
        {"segment": "2310B_NM1_1", "position": 3, "name": "Last Name", "data_type": "AN", "length": 35},
        {"segment": "2310B_NM1_1", "position": 4, "name": "First Name", "data_type": "AN", "length": 25},
        {"segment": "2310B_NM1_1", "position": 8, "name": "Identification Code Qualifier", "data_type": "ID", "length": 2},
        {"segment": "2310B_NM1_1", "position": 9, "name": "Identification Code", "data_type": "AN", "length": 80},

        {"segment": "2310C_NM1_1", "position": 1, "name": "Entity Identifier Code", "data_type": "AN", "length": 2},
        {"segment": "2310C_NM1_1", "position": 2, "name": "Entity Type Qualifier", "data_type": "ID", "length": 1},
        {"segment": "2310C_NM1_1", "position": 3, "name": "Last Name", "data_type": "AN", "length": 35},
        {"segment": "2310C_NM1_1", "position": 4, "name": "First Name", "data_type": "AN", "length": 25},
        {"segment": "2310C_NM1_1", "position": 8, "name": "Identification Code Qualifier", "data_type": "ID", "length": 2},
        {"segment": "2310C_NM1_1", "position": 9, "name": "Identification Code", "data_type": "AN", "length": 80},

        # Continue this pattern for N3, N4, REF segments of 2310A/B/C
        # -----------------------------
# 2310A - Rendering/Attending Provider Address and References
# -----------------------------
{"segment": "2310A_N3_2", "position": 1, "name": "Address Line 1", "data_type": "AN", "length": 55},
{"segment": "2310A_N3_2", "position": 2, "name": "Address Line 2", "data_type": "AN", "length": 55},

{"segment": "2310A_N4_3", "position": 1, "name": "City Name", "data_type": "AN", "length": 30},
{"segment": "2310A_N4_3", "position": 2, "name": "State Code", "data_type": "ID", "length": 2},
{"segment": "2310A_N4_3", "position": 3, "name": "Postal Code", "data_type": "ID", "length": 15},

{"segment": "2310A_REF_4", "position": 1, "name": "Reference Identification Qualifier", "data_type": "ID", "length": 2},
{"segment": "2310A_REF_4", "position": 2, "name": "Reference Identification", "data_type": "AN", "length": 50},

# -----------------------------
# 2310B - Rendering/Attending Provider Address and References
# -----------------------------
{"segment": "2310B_N3_2", "position": 1, "name": "Address Line 1", "data_type": "AN", "length": 55},
{"segment": "2310B_N3_2", "position": 2, "name": "Address Line 2", "data_type": "AN", "length": 55},

{"segment": "2310B_N4_3", "position": 1, "name": "City Name", "data_type": "AN", "length": 30},
{"segment": "2310B_N4_3", "position": 2, "name": "State Code", "data_type": "ID", "length": 2},
{"segment": "2310B_N4_3", "position": 3, "name": "Postal Code", "data_type": "ID", "length": 15},

{"segment": "2310B_REF_4", "position": 1, "name": "Reference Identification Qualifier", "data_type": "ID", "length": 2},
{"segment": "2310B_REF_4", "position": 2, "name": "Reference Identification", "data_type": "AN", "length": 50},

# -----------------------------
# 2310C - Rendering/Attending Provider Address and References
# -----------------------------
{"segment": "2310C_N3_2", "position": 1, "name": "Address Line 1", "data_type": "AN", "length": 55},
{"segment": "2310C_N3_2", "position": 2, "name": "Address Line 2", "data_type": "AN", "length": 55},

{"segment": "2310C_N4_3", "position": 1, "name": "City Name", "data_type": "AN", "length": 30},
{"segment": "2310C_N4_3", "position": 2, "name": "State Code", "data_type": "ID", "length": 2},
{"segment": "2310C_N4_3", "position": 3, "name": "Postal Code", "data_type": "ID", "length": 15},

{"segment": "2310C_REF_4", "position": 1, "name": "Reference Identification Qualifier", "data_type": "ID", "length": 2},
{"segment": "2310C_REF_4", "position": 2, "name": "Reference Identification", "data_type": "AN", "length": 50},
# -----------------------------
# 2400 - Service Line Loop
# -----------------------------

# LX Segment (Service Line Number)
{"segment": "2400_LX_1", "position": 1, "name": "Assigned Number", "data_type": "NO", "length": 6},

# SV1 Segment (Professional Service)
{"segment": "2400_SV1_2", "position": 1, "name": "Product/Service ID Qualifier", "data_type": "ID", "length": 2},
{"segment": "2400_SV1_2", "position": 2, "name": "Procedure Code", "data_type": "AN", "length": 48},
{"segment": "2400_SV1_2", "position": 3, "name": "Line Item Charge Amount", "data_type": "R", "length": 18},
{"segment": "2400_SV1_2", "position": 4, "name": "Unit or Basis for Measurement Code", "data_type": "ID", "length": 2},
{"segment": "2400_SV1_2", "position": 5, "name": "Service Unit Count", "data_type": "R", "length": 10},
{"segment": "2400_SV1_2", "position": 6, "name": "Diagnosis Code Pointer", "data_type": "ID", "length": 2},
{"segment": "2400_SV1_2", "position": 7, "name": "Revenue Code", "data_type": "ID", "length": 4},
{"segment": "2400_SV1_2", "position": 8, "name": "National Drug Code", "data_type": "AN", "length": 11},

# REF Segment (Service Line Identifiers)
{"segment": "2400_REF_5", "position": 1, "name": "Reference Identification Qualifier", "data_type": "ID", "length": 2},
{"segment": "2400_REF_5", "position": 2, "name": "Reference Identification", "data_type": "AN", "length": 50},

# DTP Segment (Service Date)
{"segment": "2400_DTP_4", "position": 1, "name": "Date/Time Qualifier", "data_type": "ID", "length": 3},
{"segment": "2400_DTP_4", "position": 2, "name": "Date Time Period Format Qualifier", "data_type": "ID", "length": 2},
{"segment": "2400_DTP_4", "position": 3, "name": "Service Date", "data_type": "DT", "length": 8},

# HI Segment (Diagnosis Codes for Service Line)
{"segment": "2400_HI_6", "position": 1, "name": "Code List Qualifier Code", "data_type": "ID", "length": 2},
{"segment": "2400_HI_6", "position": 2, "name": "Diagnosis Code", "data_type": "AN", "length": 10},
{"segment": "2400_HI_6", "position": 3, "name": "Diagnosis Code 2", "data_type": "AN", "length": 10},
{"segment": "2400_HI_6", "position": 4, "name": "Diagnosis Code 3", "data_type": "AN", "length": 10},
{"segment": "2400_HI_6", "position": 5, "name": "Diagnosis Code 4", "data_type": "AN", "length": 10},
# -----------------------------
# 2400 - Optional/Additional Segments
# -----------------------------

# PWK Segment (Paperwork / Attachments)
{"segment": "2400_PWK_3", "position": 1, "name": "Report Type Code", "data_type": "ID", "length": 2},
{"segment": "2400_PWK_3", "position": 2, "name": "Attachment Transmission Code", "data_type": "ID", "length": 1},
{"segment": "2400_PWK_3", "position": 3, "name": "Attachment Control Number", "data_type": "AN", "length": 50},
{"segment": "2400_PWK_3", "position": 4, "name": "Attachment Description", "data_type": "AN", "length": 80},

# CN1 Segment (Contract Information)
{"segment": "2400_CN1_7", "position": 1, "name": "Contract Type Code", "data_type": "ID", "length": 2},
{"segment": "2400_CN1_7", "position": 2, "name": "Monetary Amount", "data_type": "R", "length": 18},
{"segment": "2400_CN1_7", "position": 3, "name": "Percentage", "data_type": "R", "length": 6},
{"segment": "2400_CN1_7", "position": 4, "name": "Reference Identification", "data_type": "AN", "length": 50},

# SVD Segment (Service Line Adjudication / Payer Amounts)
{"segment": "2400_SVD_8", "position": 1, "name": "Payer Identifier", "data_type": "ID", "length": 2},
{"segment": "2400_SVD_8", "position": 2, "name": "Monetary Amount Paid", "data_type": "R", "length": 18},
{"segment": "2400_SVD_8", "position": 3, "name": "Unit or Basis for Measurement Code", "data_type": "ID", "length": 2},
{"segment": "2400_SVD_8", "position": 4, "name": "Service Unit Count", "data_type": "R", "length": 10},
{"segment": "2400_SVD_8", "position": 5, "name": "Revenue Code", "data_type": "ID", "length": 4},
{"segment": "2400_SVD_8", "position": 6, "name": "Service Identification Code", "data_type": "AN", "length": 48},

# Additional Optional Segments can include
# CAS (Claim Adjustment), AMT (Amount), QTY (Quantity), LQ (Industry Code), if required
# Example for CAS:
{"segment": "2400_CAS_9", "position": 1, "name": "Claim Adjustment Group Code", "data_type": "ID", "length": 2},
{"segment": "2400_CAS_9", "position": 2, "name": "Adjustment Reason Code", "data_type": "ID", "length": 3},
{"segment": "2400_CAS_9", "position": 3, "name": "Adjustment Amount", "data_type": "R", "length": 18},
{"segment": "2400_CAS_9", "position": 4, "name": "Adjustment Quantity", "data_type": "R", "length": 10},



]



        for el in elements_data:
            segment_instance = segments[el["segment"]]
            EDIElement.objects.create(
                segment=segment_instance,
                position=el["position"],
                name=el["name"],
                data_type=el["data_type"],
                length=el["length"]
            )

        self.stdout.write(self.style.SUCCESS("Successfully populated full 837P loops, segments, and elements"))
