from django.core.management.base import BaseCommand
from superbill.models import EDILoop, EDISegment, EDIElement, EDIPayerRule, EDIPayer


# class Command(BaseCommand):
#     help = "Populate master data for dynamic 837 claim generation (loops, segments, elements, rules)."

#     def handle(self, *args, **options):
#         self.stdout.write("Starting full 837 master data population...")

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

#         # --- Elements per segment ---
#         elements = {
#             # ISA Loop
#             "ISA_LOOP_ISA": [
#                 ("Authorization Information Qualifier", "AN", 2),
#                 ("Authorization Information", "AN", 10),
#                 ("Security Info Qualifier", "AN", 2),
#                 ("Security Info", "AN", 10),
#                 ("Interchange ID Qualifier (Sender)", "AN", 2),
#                 ("Interchange Sender ID", "AN", 15),
#                 ("Interchange ID Qualifier (Receiver)", "AN", 2),
#                 ("Interchange Receiver ID", "AN", 15),
#                 ("Interchange Date", "DT", 6),  # yyMMdd
#                 ("Interchange Time", "TM", 4),  # HHMM
#                 ("Control Standards ID", "AN", 1),
#                 ("Version Number", "AN", 5),
#                 ("Interchange Control Number", "N0", 9),
#                 ("Acknowledgment Requested", "AN", 1),
#                 ("Usage Indicator", "AN", 1),
#                 ("Component Element Separator", "AN", 1)
#             ],
#             "ISA_LOOP_IEA": [
#                 ("Number of Included Functional Groups", "N0", 5),
#                 ("Interchange Control Number", "N0", 9)
#             ],

#             # GS Loop
#             "GS_LOOP_GS": [
#                 ("Functional ID Code", "AN", 2),
#                 ("Application Sender Code", "AN", 15),
#                 ("Application Receiver Code", "AN", 15),
#                 ("Date", "DT", 8),  # CCYYMMDD
#                 ("Time", "TM", 4),  # HHMM
#                 ("Group Control Number", "N0", 9),
#                 ("Responsible Agency Code", "AN", 2),
#                 ("Version/Release/Industry ID Code", "AN", 12)
#             ],
#             "GS_LOOP_GE": [
#                 ("Number of Transaction Sets Included", "N0", 5),
#                 ("Group Control Number", "N0", 9)
#             ],

#             # ST Loop
#             "ST_LOOP_ST": [
#                 ("Transaction Set Identifier Code", "AN", 3),  # Must be 837
#                 ("Transaction Set Control Number", "AN", 9)
#             ],
#             "ST_LOOP_SE": [
#                 ("Number of Included Segments", "N0", 10),
#                 ("Transaction Set Control Number", "AN", 9)
#             ],

#             # 1000A Submitter
#             "1000A_NM1": [
#                 ("Entity Identifier Code", "AN", 2),
#                 ("Entity Type Qualifier", "AN", 1),
#                 ("Submitter Name", "AN", 60),
#                 ("Submitter First Name", "AN", 35),
#                 ("Submitter Middle Name", "AN", 25),
#                 ("Name Prefix", "AN", 10),
#                 ("Name Suffix", "AN", 10),
#                 ("Identification Code Qualifier", "AN", 2),
#                 ("Submitter Identifier", "AN", 80)
#             ],

#             # 1000B Receiver
#             "1000B_NM1": [
#                 ("Entity Identifier Code", "AN", 2),
#                 ("Entity Type Qualifier", "AN", 1),
#                 ("Receiver Name", "AN", 60),
#                 ("Receiver First Name", "AN", 35),
#                 ("Receiver Middle Name", "AN", 25),
#                 ("Name Prefix", "AN", 10),
#                 ("Name Suffix", "AN", 10),
#                 ("Identification Code Qualifier", "AN", 2),
#                 ("Receiver Identifier", "AN", 80)
#             ],

#             # 2000B HL
#             "2000B_HL": [
#                 ("Hierarchical ID Number", "N0", 12),
#                 ("Hierarchical Parent ID", "N0", 12),
#                 ("Hierarchical Level Code", "AN", 2),
#                 ("Hierarchical Child Code", "AN", 1)
#             ],

#             # 2300 Claim
#             "2300_CLM": [
#                 ("Claim Submitter Identifier", "AN", 38),
#                 ("Monetary Amount", "R2", 18),
#                 ("Claim Filing Indicator Code", "AN", 2)
#             ],

#             # 2400 Service Line
#             "2400_SV1": [
#                 ("Composite Procedure Code", "AN", 48),
#                 ("Line Item Charge Amount", "R2", 18),
#                 ("Unit or Basis for Measurement Code", "AN", 2),
#                 ("Service Unit Count", "R2", 10),
#                 ("Place of Service Code", "AN", 2)
#             ]
#         }

#         # --- Create elements with CONSTANT payer rules enforcing length/padding ---
#         EDI_PAYER, _ = EDIPayer.objects.get_or_create(name="Default Payer")

#         for seg_key, elems in elements.items():
#             seg = segment_objs.get(seg_key)
#             if not seg:
#                 continue
#             for i, (name, dtype, length) in enumerate(elems, start=1):
#                 elem = EDIElement.objects.create(
#                     segment=seg,
#                     position=i,
#                     name=name,
#                     data_type=dtype,
#                     length=length
#                 )

#                 # Determine dummy value for type
#                 if "DATE" in name.upper():
#                     value = "260107"  # yyMMdd for ISA09 or CCYYMMDD for GS
#                     if "GS" in seg_key:
#                         value = "20260107"  # CCYYMMDD
#                 elif "TIME" in name.upper():
#                     value = "1030"
#                 elif "Monetary" in name or "Amount" in name:
#                     value = "100.00"
#                 elif "Identifier" in name:
#                     value = "ZZ"
#                 else:
#                     value = f"TEST{str(i).zfill(2)}"

#                 # Enforce padding/length
#                 padded_value = (value[:length] if len(value) > length else value.ljust(length))

#                 EDIPayerRule.objects.create(
#                     element=elem,
#                     rule_type="CONSTANT",
#                     constant_value=padded_value,
#                     payer=EDI_PAYER,
#                     min_length=length,
#                     max_length=length,
#                     pad_char=" " if dtype == "AN" else "0",
#                     pad_side="right" if dtype == "AN" else "left"
#                 )

#         self.stdout.write(self.style.SUCCESS(
#             "Full 837 master data (loops, segments, elements, payer rules) populated successfully."
#         ))




from django.core.management.base import BaseCommand
from superbill.models import EDILoop, EDISegment, EDIElement, EDIPayerRule, EDIPayer

# class Command(BaseCommand):
#     help = "Populate master data for dynamic 837 claim generation (loops, segments, elements, rules)."

#     def handle(self, *args, **options):
#         self.stdout.write("Starting full 837 master data population...")

#         # --- Clear existing data ---
#         EDIPayerRule.objects.all().delete()
#         EDIElement.objects.all().delete()
#         EDISegment.objects.all().delete()
#         EDILoop.objects.all().delete()

#         # --- Payer ---
#         payer, _ = EDIPayer.objects.get_or_create(name="Default Payer")

#         # --- Loops ---
#         loops = [
#             ("ISA_LOOP", "Interchange Control Header", None),
#             ("GS_LOOP", "Functional Group Header", "ISA_LOOP"),
#             ("ST_LOOP", "Transaction Set Header", "GS_LOOP"),
#             ("1000A", "Submitter", "ST_LOOP"),
#             ("1000B", "Receiver", "ST_LOOP"),
#             ("2000A", "Billing Provider", "ST_LOOP"),
#             ("2000B", "Subscriber", "ST_LOOP"),
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

#         # --- Elements per segment (type, length) ---
#         elements = {
#             "ISA_LOOP_ISA": [
#                 ("Authorization Info Qualifier", "AN", 2, "CONSTANT", "00"),
#                 ("Authorization Info", "AN", 10, "CONSTANT", ""),
#                 ("Security Info Qualifier", "AN", 2, "CONSTANT", "00"),
#                 ("Security Info", "AN", 10, "CONSTANT", ""),
#                 ("Interchange ID Qualifier 1", "AN", 2, "CONSTANT", "ZZ"),
#                 ("Interchange Sender ID", "AN", 15, "FIELD", "sender_id"),
#                 ("Interchange ID Qualifier 2", "AN", 2, "CONSTANT", "ZZ"),
#                 ("Interchange Receiver ID", "AN", 15, "FIELD", "receiver_id"),
#                 ("Interchange Date", "DT", 6, "FIELD", "date"),
#                 ("Interchange Time", "TM", 4, "FIELD", "time"),
#                 ("Control Standards ID", "AN", 1, "CONSTANT", "U"),
#                 ("Version Number", "AN", 5, "CONSTANT", "00501"),
#                 ("Control Number", "N0", 9, "FIELD", "control_number"),
#                 ("Acknowledgment Requested", "AN", 1, "CONSTANT", "0"),
#                 ("Usage Indicator", "AN", 1, "CONSTANT", "T"),
#                 ("Component Element Separator", "AN", 1, "CONSTANT", ":"),
#             ],
#             "ISA_LOOP_IEA": [
#                 ("Number of Functional Groups", "N0", 5, "FIELD", "num_groups"),
#                 ("Control Number", "N0", 9, "FIELD", "control_number"),
#             ],
#             "GS_LOOP_GS": [
#                 ("Functional ID Code", "AN", 2, "CONSTANT", "HC"),
#                 ("Sender Code", "AN", 15, "FIELD", "sender_id"),
#                 ("Receiver Code", "AN", 15, "FIELD", "receiver_id"),
#                 ("Date", "DT", 8, "FIELD", "date"),
#                 ("Time", "TM", 4, "FIELD", "time"),
#                 ("Group Control Number", "N0", 9, "FIELD", "group_number"),
#                 ("Responsible Agency Code", "AN", 2, "CONSTANT", "X"),
#                 ("Version/Industry ID", "AN", 12, "CONSTANT", "005010X222A1"),
#             ],
#             "GS_LOOP_GE": [
#                 ("Number of Transaction Sets", "N0", 5, "FIELD", "num_trans"),
#                 ("Group Control Number", "N0", 9, "FIELD", "group_number"),
#             ],
#             # Add more segments like ST/SE, 1000A/B, 2000A/B, 2300, 2400 here...
#         }

#         # --- Create elements and payer rules ---
#         for seg_key, elems in elements.items():
#             seg = segment_objs.get(seg_key)
#             if not seg:
#                 continue
#             for i, (name, dtype, length, rule_type, value_or_field) in enumerate(elems, start=1):
#                 elem = EDIElement.objects.create(
#                     segment=seg,
#                     position=i,
#                     name=name,
#                     data_type=dtype,
#                     length=length
#                 )

#                 # Create Payer Rule
#                 kwargs = {
#                     "element": elem,
#                     "payer": payer,
#                     "rule_type": rule_type,
#                     "min_length": length,
#                     "max_length": length,
#                     "pad_char": " " if dtype == "AN" else "0",
#                     "pad_side": "right" if dtype == "AN" else "left"
#                 }

#                 if rule_type == "CONSTANT":
#                     kwargs["constant_value"] = value_or_field
#                 else:  # FIELD
#                     from superbill.models import EDIDataKey
#                     key_obj, _ = EDIDataKey.objects.get_or_create(key=value_or_field)
#                     kwargs["data_key"] = key_obj

#                 EDIPayerRule.objects.create(**kwargs)

#         self.stdout.write(self.style.SUCCESS("837 master data populated with loops, segments, elements, and payer rules."))


from django.core.management.base import BaseCommand
from superbill.models import EDILoop, EDISegment, EDIElement, EDIPayerRule, EDIPayer

class Command(BaseCommand):
    help = "Populate parser-compatible 837P master data with constant test values."

    def handle(self, *args, **options):
        self.stdout.write("Starting parser-compatible 837P master data population...")

        # --- Clear existing data ---
        EDIPayerRule.objects.all().delete()
        EDIElement.objects.all().delete()
        EDISegment.objects.all().delete()
        EDILoop.objects.all().delete()

        # --- Create default payer ---
        EDI_PAYER, _ = EDIPayer.objects.get_or_create(name="Default Payer")

        # --- Loops ---
        loops = [
            ("ISA_LOOP", "Interchange Header", None),
            ("GS_LOOP", "Functional Group Header", "ISA_LOOP"),
            ("ST_LOOP", "Transaction Set Header", "GS_LOOP"),
            ("1000A", "Submitter", "ST_LOOP"),
            ("1000B", "Receiver", "ST_LOOP"),
            ("2000A", "Billing Provider HL", "ST_LOOP"),
            ("2000B", "Subscriber HL", "ST_LOOP"),
            ("2300", "Claim Info", "2000B"),
            ("2400", "Service Line", "2300"),
        ]

        loop_objs = {}
        for code, name, parent_code in loops:
            parent = loop_objs.get(parent_code)
            loop_objs[code] = EDILoop.objects.create(code=code, name=name, parent=parent)

        # --- Segments per loop ---
        segments = {
            "ISA_LOOP": ["ISA", "IEA"],
            "GS_LOOP": ["GS", "GE"],
            "ST_LOOP": ["ST", "SE"],
            "1000A": ["NM1", "N3", "N4"],
            "1000B": ["NM1", "N3", "N4", "REF"],
            "2000B": ["HL", "SBR", "NM1", "N3", "N4"],
            "2300": ["CLM", "DTP", "HI", "REF"],
            "2400": ["LX", "SV1", "DTP"],
            "2000A": ["HL", "PRV", "NM1", "N3", "N4", "REF", "PER"],
        }

        segment_objs = {}
        for loop_code, seg_names in segments.items():
            loop = loop_objs[loop_code]
            for pos, seg_name in enumerate(seg_names, start=1):
                seg = EDISegment.objects.create(loop=loop, name=seg_name, position=pos)
                segment_objs[f"{loop_code}_{seg_name}"] = seg

        # --- Elements with CONSTANT values ---
        elements = {
            "ISA_LOOP_ISA": [
                ("Authorization Info Qualifier", "AN", 2, "00"),
                ("Authorization Info", "AN", 10, "          "),
                ("Security Info Qualifier", "AN", 2, "00"),
                ("Security Info", "AN", 10, "          "),
                ("Sender Qualifier", "AN", 2, "ZZ"),
                ("Sender ID", "AN", 15, "TEST02         "),
                ("Receiver Qualifier", "AN", 2, "ZZ"),
                ("Receiver ID", "AN", 15, "TEST03         "),
                ("Date", "DT", 6, "260107"),
                ("Time", "TM", 4, "1030"),
                ("Control Standards ID", "AN", 1, "U"),
                ("Version", "AN", 5, "00501"),
                ("Control Number", "N0", 9, "000000001"),
                ("Ack Requested", "AN", 1, "0"),
                ("Usage Indicator", "AN", 1, "T"),
                ("Component Separator", "AN", 1, ":")
            ],
            "ISA_LOOP_IEA": [
                ("Number of Groups", "N0", 5, "00001"),
                ("Control Number", "N0", 9, "000000001")
            ],
            "GS_LOOP_GS": [
                ("Functional ID Code", "AN", 2, "HC"),
                ("Sender Code", "AN", 15, "TEST02         "),
                ("Receiver Code", "AN", 15, "TEST03         "),
                ("Date", "DT", 8, "20260107"),
                ("Time", "TM", 4, "1030"),
                ("Group Control #", "N0", 9, "000000001"),
                ("Agency Code", "AN", 2, "X "),
                ("Version", "AN", 12, "005010X222A1")
            ],
            "GS_LOOP_GE": [
                ("Number of STs", "N0", 5, "00001"),
                ("Group Control #", "N0", 9, "000000001")
            ],
            "ST_LOOP_ST": [
                ("Transaction Set ID", "AN", 3, "837"),
                ("Control #", "AN", 9, "0001")
            ],
            "ST_LOOP_SE": [
                ("Control #", "AN", 9, "0001")
            ],
            "1000A_NM1": [
                ("Entity ID Code", "AN", 2, "41"),
                ("Entity Type", "AN", 1, "2"),
                ("Name", "AN", 60, "TEST SUBMITTER                                         "),
                ("ID Code Qualifier", "AN", 2, "46"),
                ("ID Code", "AN", 80, "1234567890                                        ")
            ],
            "1000A_N3": [
                ("Address Line 1", "AN", 55, "123 MAIN ST                              ")
            ],
            "1000A_N4": [
                ("City", "AN", 30, "SEATTLE                       "),
                ("State", "AN", 2, "WA"),
                ("ZIP", "AN", 9, "98101    ")
            ],
            "1000B_NM1": [
                ("Entity ID Code", "AN", 2, "40"),
                ("Entity Type", "AN", 1, "2"),
                ("Name", "AN", 60, "TEST RECEIVER                                          "),
                ("ID Code Qualifier", "AN", 2, "46"),
                ("ID Code", "AN", 80, "9876543210                                        ")
            ],
            "1000B_N3": [
                ("Address Line 1", "AN", 55, "456 BROADWAY AVE                         ")
            ],
            "1000B_N4": [
                ("City", "AN", 30, "SEATTLE                       "),
                ("State", "AN", 2, "WA"),
                ("ZIP", "AN", 9, "98102    ")
            ],
            "2000B_HL": [
                ("HL ID", "N0", 12, "1"),
                ("Parent HL", "N0", 12, "0"),
                ("Level Code", "AN", 2, "22"),
                ("Child Code", "AN", 1, "0")
            ],
            "2300_CLM": [
                ("Claim ID", "AN", 38, "1001"),
                ("Claim Amt", "R2", 18, "100.00"),
                ("Filing Indicator", "AN", 2, "TC")
            ],
            "2400_LX": [
                ("Service Line #", "N0", 6, "1")
            ],
            "2400_SV1": [
                ("Procedure Code", "AN", 48, "99213"),
                ("Line Amt", "R2", 18, "100.00"),
                ("Unit Code", "AN", 2, "UN"),
                ("Quantity", "R2", 10, "1")
            ],
            "2000A_HL": [
                ("HL ID", "N0", 12, "1"),
                ("Parent HL", "N0", 12, ""),
                ("Level Code", "AN", 2, "20"),
                ("Child Code", "AN", 1, "1")
            ],
            "2000B_HL": [
                ("HL ID", "N0", 12, "2"),
                ("Parent HL", "N0", 12, "1"),
                ("Level Code", "AN", 2, "22"),
                ("Child Code", "AN", 1, "0")
            ],
            "2000B_NM1": [
                ("Entity ID Code", "AN", 2, "IL"),
                ("Entity Type", "AN", 1, "1"),
                ("Last Name", "AN", 35, "DOE"),
                ("First Name", "AN", 25, "JOHN"),
                ("ID Code Qualifier", "AN", 2, "MI"),
                ("ID Code", "AN", 80, "SUBSCRIBER123")
            ],

            "2000A_PRV": [
                ("Provider Code", "AN", 2, "BI"),
                ("Reference Qualifier", "AN", 3, "PXC"),
                ("Taxonomy Code", "AN", 50, "207Q00000X")
            ],
            "2000A_NM1": [
                ("Entity ID Code", "AN", 2, "85"),   # Billing Provider
                ("Entity Type", "AN", 1, "2"),
                ("Name", "AN", 60, "BILLING PROVIDER INC                         "),
                ("ID Code Qualifier", "AN", 2, "XX"),
                ("ID Code", "AN", 80, "1234567893")
            ],
        }

        # --- Create elements and CONSTANT rules ---
        for seg_key, elems in elements.items():
            seg = segment_objs.get(seg_key)
            if not seg:
                continue
            for pos, (name, dtype, length, const_val) in enumerate(elems, start=1):
                elem = EDIElement.objects.create(
                    segment=seg,
                    position=pos,
                    name=name,
                    data_type=dtype,
                    length=length
                )
                EDIPayerRule.objects.create(
                    element=elem,
                    rule_type="CONSTANT",
                    constant_value=const_val,
                    payer=EDI_PAYER,
                    min_length=length,
                    max_length=length,
                    pad_char=" " if dtype != "N0" else "0",
                    pad_side="right" if dtype != "N0" else "left"
                )

        self.stdout.write(self.style.SUCCESS("837P master data populated successfully."))
