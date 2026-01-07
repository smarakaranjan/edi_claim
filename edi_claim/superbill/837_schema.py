from .schema import ElementDef, SegmentDef, LoopDef

# ------------------------
# 1000A SUBMITTER
# ------------------------
LOOP_1000A = LoopDef(
    id="1000A",
    segments={
        "NM1": SegmentDef(
            "NM1",
            elements={
                1: ElementDef("NM101", required=True, allowed=["41"]),
                2: ElementDef("NM102", required=True, allowed=["1", "2"]),
            }
        ),
        "PER": SegmentDef("PER", max_repeat=2),
    }
)

# ------------------------
# 1000B RECEIVER
# ------------------------
LOOP_1000B = LoopDef(
    id="1000B",
    segments={
        "NM1": SegmentDef(
            "NM1",
            elements={
                1: ElementDef("NM101", required=True, allowed=["40"]),
            }
        )
    }
)

# ------------------------
# 2000A BILLING PROVIDER HL
# ------------------------
LOOP_2000A = LoopDef(
    id="2000A",
    segments={
        "HL": SegmentDef(
            "HL",
            elements={
                3: ElementDef("HL03", required=True, allowed=["20"]),
            }
        ),
        "PRV": SegmentDef("PRV"),
    },
    child_loops={
        "2010AA": LoopDef(
            id="2010AA",
            segments={
                "NM1": SegmentDef(
                    "NM1",
                    elements={
                        1: ElementDef("NM101", allowed=["85"]),
                    }
                ),
                "N3": SegmentDef("N3"),
                "N4": SegmentDef("N4"),
            }
        )
    }
)

# ------------------------
# 2300 CLAIM
# ------------------------
LOOP_2300 = LoopDef(
    id="2300",
    segments={
        "CLM": SegmentDef("CLM"),
        "DTP": SegmentDef("DTP", max_repeat=2),
        "HI": SegmentDef("HI"),
    },
    child_loops={
        "2400": LoopDef(
            id="2400",
            segments={
                "LX": SegmentDef("LX", max_repeat=99),
                "SV1": SegmentDef("SV1"),
                "DTP": SegmentDef("DTP", max_repeat=2),
            }
        )
    }
)

# ROOT
ROOT_LOOP = LoopDef(
    id="ROOT",
    segments={
        "ST": SegmentDef("ST"),
        "SE": SegmentDef("SE"),
    },
    child_loops={
        "1000A": LOOP_1000A,
        "1000B": LOOP_1000B,
        "2000A": LOOP_2000A,
        "2300": LOOP_2300,
    }
)
