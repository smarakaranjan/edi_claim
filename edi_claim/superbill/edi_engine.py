# Default import's
from itertools import chain

# Module import's
from superbill.models import EDILoop, EDISegment

# class Dynamic837ClaimEngine:
    
#     """
#     Dynamic, memory-efficient 837 claim builder.
#     Only requires claim and payer objects.
#     """

#     def generate(self, claim, payer, context=None):
#         """
#         Yield the 837 claim line by line.
#         """
#         context = context or {}

#         # Automatically find root loop (loop with no parent)
#         root_loop = (
#             EDILoop.objects.prefetch_related(
#                 "segments__elements__rules__data_key",
#                 "subloops__segments__elements__rules__data_key",
#                 "subloops__subloops__segments__elements__rules__data_key",
#             )
#             .filter(parent__isnull=True)
#             .order_by("id")
#             .first()
#         )

#         if not root_loop:
#             raise ValueError("No root EDILoop defined in the database.")

#         yield from self._build_loop(root_loop, claim, payer, context)

#     def _build_loop(self, loop, obj, payer, context):
#         # Check if this loop should repeat over related objects dynamically
#         for field in obj._meta.get_fields():
#             if field.one_to_many:  # reverse FK
#                 related_name = field.get_accessor_name()
#                 if loop.code.lower() == related_name.lower():  # match loop to related name
#                     for item in getattr(obj, related_name).all():
#                         yield from self._build_loop(loop, item, payer, context)
#                     return

#         # Build segments for this object
#         segs = (
#             seg.name + "*" + "*".join(
#                 self._resolve_element_dynamic(e, obj, payer, context)
#                 for e in seg.elements.all().order_by("position")
#             ) + "~"
#             for seg in loop.segments.all().order_by("position")
#         )

#         # Child loops recursively
#         children = (
#             line
#             for child in loop.subloops.all().order_by("id")
#             for line in self._build_loop(child, obj, payer, context)
#         )

#         yield from chain(segs, children)


#     def _resolve_element_dynamic(self, element, claim, payer, context):
#         print(element, 'element56')
#         rule = next((r for r in element.rules.all() if r.payer_id == payer.id), None)
#         for r in element.rules.all():
#             print(r.payer_id, 'r.payer_id')
#             print(payer.id, 'payer.id') 
#         if not rule:
#             return ""

#         if rule.rule_type == "FIELD" and rule.data_key and rule.data_key.extractor:
#             data =  self._apply_transformation(
#                 self._extract_from_claim(claim, rule.data_key.extractor),
#                 rule.transformation,
#                 rule=rule,
#                 element=element
#             )
#             print(data)
#             return data

#         if rule.rule_type == "CONSTANT":
#             data = self._apply_transformation(
#                 rule.constant_value,
#                 rule.transformation,
#                 rule=rule,
#                 element=element
#             )
#             print(data)
#             return data

#         if rule.rule_type == "FUNC" and rule.data_key:
#             func = context.get(rule.data_key.key)
#             if callable(func):
#                 return self._apply_transformation(
#                     func(claim, payer, context),
#                     rule.transformation,
#                     rule=rule,
#                     element=element
#                 )

#         if rule.rule_type == "MAPPING" and rule.data_key:
#             mapping = rule.transformation or {}
#             value = self._extract_from_claim(claim, rule.data_key.extractor)
#             return self._apply_transformation(
#                 mapping.get(value, ""),
#                 rule.transformation,
#                 rule=rule,
#                 element=element
#             )

#         return ""


#     def _extract_from_claim(self, obj, path):
#         parts = path.split(".")
#         val = obj
#         try:
#             for p in parts:
#                 if p.isdigit():
#                     val = val[int(p)]
#                 else:
#                     val = getattr(val, p)
#             return val
#         except (AttributeError, IndexError, TypeError):
#             return None

#     def _apply_transformation(self, value, trans):
#         if value is None:
#             return ""
#         v = str(value)
#         if not trans:
#             return v
#         if trans.get("uppercase"):
#             v = v.upper()
#         if "truncate" in trans:
#             v = v[: int(trans["truncate"])]
#         if "date_format" in trans:
#             v = value.strftime(trans["date_format"])
#         return v

#     def _apply_transformation(self, value, trans, rule=None, element=None):
#         """
#         Apply transformations (semantic + syntactic) for EDI elements.
#         Handles uppercase, truncate, date_format, and EDI-specific length/padding.
#         """
#         if value is None:
#             value = ""
#         v = str(value)

#         # --- semantic transformations ---
#         if trans:
#             if trans.get("uppercase"):
#                 v = v.upper()
#             if "truncate" in trans:
#                 v = v[: int(trans["truncate"])]
#             if "date_format" in trans and hasattr(value, "strftime"):
#                 v = value.strftime(trans["date_format"])

#         # --- syntactic EDI formatting ---
#         # Priority: rule > element
#         min_len = getattr(rule, "min_length", None) if rule else None
#         max_len = getattr(rule, "max_length", None) if rule else None
#         pad_char = getattr(rule, "pad_char", " ") if rule else " "
#         pad_side = getattr(rule, "pad_side", "right") if rule else "right"

#         # Fallback: use element length if defined
#         if not max_len and element and hasattr(element, "length"):
#             max_len = element.length

#         # Enforce min length (pad with spaces or zeros)
#         if min_len and len(v) < min_len:
#             v = v.ljust(min_len, pad_char)

#         # Enforce max length (pad or truncate)
#         if max_len:
#             if len(v) < max_len:
#                 if pad_side == "left":
#                     v = v.rjust(max_len, pad_char)
#                 else:
#                     v = v.ljust(max_len, pad_char)
#             else:
#                 v = v[:max_len]

#         return v

#     def _apply_transformation(self, value, trans, rule=None, element=None):
#         """
#         Apply transformations (semantic + syntactic) for EDI elements.
#         Handles uppercase, truncate, date_format, and EDI-specific length/padding.
#         """
#         if value is None:
#             value = ""
#         v = str(value)

#         # --- semantic transformations ---
#         if trans:
#             if trans.get("uppercase"):
#                 v = v.upper()
#             if "truncate" in trans:
#                 v = v[: int(trans["truncate"])]
#             if "date_format" in trans and hasattr(value, "strftime"):
#                 v = value.strftime(trans["date_format"])

#         # --- syntactic EDI formatting ---
#         # Priority: rule > element
#         min_len = getattr(rule, "min_length", None) if rule else None
#         max_len = getattr(rule, "max_length", None) if rule else None
#         pad_char = getattr(rule, "pad_char", None) if rule else None
#         if not pad_char:  # Ensure we never pass None
#             pad_char = " "
#         pad_side = getattr(rule, "pad_side", "right") if rule else "right"

#         # Fallback: use element length if defined
#         if not max_len and element and hasattr(element, "length"):
#             max_len = element.length

#         # Enforce min length (pad with spaces or zeros)
#         if min_len and len(v) < min_len:
#             v = v.ljust(min_len, pad_char)

#         # Enforce max length (pad or truncate)
#         if max_len:
#             if len(v) < max_len:
#                 if pad_side == "left":
#                     v = v.rjust(max_len, pad_char)
#                 else:
#                     v = v.ljust(max_len, pad_char)
#             else:
#                 v = v[:max_len]

#         return v


# class Dynamic837ClaimEngine:
#     """
#     Correct 837 EDI claim builder.
#     Enforces hierarchy, element lengths, and proper padding.
#     """

#     def generate(self, claim, payer, context=None):
#         context = context or {}
#         isa_loop = EDILoop.objects.prefetch_related(
#             "segments__elements__rules__data_key",
#             "subloops__segments__elements__rules__data_key",
#             "subloops__subloops__segments__elements__rules__data_key"
#         ).filter(code="ISA_LOOP").first()
#         if not isa_loop:
#             raise ValueError("ISA_LOOP required.")

#         # ISA
#         isa_seg = isa_loop.segments.filter(name="ISA").first()
#         if isa_seg:
#             yield self._build_segment_line(isa_seg, claim, payer, context)

#         # GS
#         for gs_loop in isa_loop.subloops.filter(code="GS_LOOP").order_by("id"):
#             gs_seg = gs_loop.segments.filter(name="GS").first()
#             if gs_seg:
#                 yield self._build_segment_line(gs_seg, claim, payer, context)

#             # ST
#             for st_loop in gs_loop.subloops.filter(code="ST_LOOP").order_by("id"):
#                 st_seg = st_loop.segments.filter(name="ST").first()
#                 if st_seg:
#                     yield self._build_segment_line(st_seg, claim, payer, context)

#                 # Subloops like 1000A/B, 2000A/B, 2300, 2400
#                 for child_loop in st_loop.subloops.all().order_by("id"):
#                     yield from self._build_loop(child_loop, claim, payer, context)

#                 # SE
#                 se_seg = st_loop.segments.filter(name="SE").first()
#                 if se_seg:
#                     yield self._build_segment_line(se_seg, claim, payer, context)

#             # GE
#             ge_seg = gs_loop.segments.filter(name="GE").first()
#             if ge_seg:
#                 yield self._build_segment_line(ge_seg, claim, payer, context)

#         # IEA
#         iea_seg = isa_loop.segments.filter(name="IEA").first()
#         if iea_seg:
#             yield self._build_segment_line(iea_seg, claim, payer, context)

#     def _build_loop(self, loop, claim, payer, context):
#         for seg in loop.segments.all().order_by("position"):
#             yield self._build_segment_line(seg, claim, payer, context)
#         for child_loop in loop.subloops.all().order_by("id"):
#             yield from self._build_loop(child_loop, claim, payer, context)

#     def _build_segment_line(self, seg, claim, payer, context):
#         elements = []
#         for elem in seg.elements.all().order_by("position"):
#             val = self._resolve_element_dynamic(elem, claim, payer, context) or ""
#             # Fetch rule for padding/length
#             rule = elem.rules.filter(payer=payer).first()
#             if rule:
#                 max_len = getattr(rule, "max_length", elem.length)
#                 pad_char = getattr(rule, "pad_char", " ")
#                 pad_side = getattr(rule, "pad_side", "right")
#             else:
#                 max_len = elem.length
#                 pad_char = " "
#                 pad_side = "right"

#             # truncate
#             if max_len and len(val) > max_len:
#                 val = val[:max_len]
#             # pad
#             if max_len and len(val) < max_len:
#                 val = val.rjust(max_len, pad_char) if pad_side == "left" else val.ljust(max_len, pad_char)
#             elements.append(val)
#         return seg.name + "*" + "*".join(elements) + "~"

#     def _resolve_element_dynamic(self, element, claim, payer, context):
#         rule = element.rules.filter(payer=payer).first()
#         if not rule:
#             return ""
#         if rule.rule_type == "CONSTANT":
#             return str(rule.constant_value)
#         if rule.rule_type == "FIELD" and rule.data_key:
#             return str(self._extract_from_claim(claim, rule.data_key.key) or "")
#         return ""

#     def _extract_from_claim(self, obj, path):
#         val = obj
#         try:
#             for p in path.split("."):
#                 if p.isdigit():
#                     val = val[int(p)]
#                 else:
#                     val = getattr(val, p)
#             # Convert date/time fields if needed
#             if isinstance(val, (str, int, float)):
#                 return str(val)
#             return val
#         except (AttributeError, IndexError, TypeError):
#             return None



class Dynamic837ClaimEngine:
    """
    837P EDI claim builder.
    Handles hierarchy, repeating loops, element lengths, padding, and transformations.
    """

    def generate(self, claim, payer, context=None):
        context = context or {}
        isa_loop = EDILoop.objects.prefetch_related(
            "segments__elements__rules__data_key",
            "subloops__segments__elements__rules__data_key",
            "subloops__subloops__segments__elements__rules__data_key"
        ).filter(code="ISA_LOOP").first()
        if not isa_loop:
            raise ValueError("ISA_LOOP required.")

        # ISA
        isa_seg = isa_loop.segments.filter(name="ISA").first()
        if isa_seg:
            yield self._build_segment_line(isa_seg, claim, payer, context)

        # GS
        for gs_loop in isa_loop.subloops.filter(code="GS_LOOP").order_by("id"):
            gs_seg = gs_loop.segments.filter(name="GS").first()
            if gs_seg:
                yield self._build_segment_line(gs_seg, claim, payer, context)

            # ST
            for st_loop in gs_loop.subloops.filter(code="ST_LOOP").order_by("id"):
                st_seg = st_loop.segments.filter(name="ST").first()
                if st_seg:
                    yield self._build_segment_line(st_seg, claim, payer, context)

                # Dynamically generate repeating loops per claim
                for child_loop in st_loop.subloops.all().order_by("id"):
                    yield from self._build_loop_dynamic(child_loop, claim, payer, context)

                # SE
                se_seg = st_loop.segments.filter(name="SE").first()
                if se_seg:
                    # Count segments generated for this ST
                    segment_count = context.get("segment_count", 0)
                    context["segment_count"] = 0  # reset for next ST
                    # inject segment count into SE segment if SE01
                    context["ST_segment_count"] = segment_count
                    yield self._build_segment_line(se_seg, claim, payer, context)

            # GE
            ge_seg = gs_loop.segments.filter(name="GE").first()
            if ge_seg:
                yield self._build_segment_line(ge_seg, claim, payer, context)

        # IEA
        iea_seg = isa_loop.segments.filter(name="IEA").first()
        if iea_seg:
            yield self._build_segment_line(iea_seg, claim, payer, context)

    def _build_loop_dynamic(self, loop, claim, payer, context):
        """
        Handle repeating loops dynamically based on claim data.
        For example, 2000B → 2010BA → 2400 repeats per subscriber/service line.
        """
        # Check if loop has a rule or mapping to determine repeat count
        repeat_count = getattr(loop, "repeat_count", 1)  # can be set dynamically per loop
        if repeat_count < 1:
            repeat_count = 1

        for i in range(repeat_count):
            for seg in loop.segments.all().order_by("position"):
                line = self._build_segment_line(seg, claim, payer, context)
                # Update segment count for ST/SE
                context["segment_count"] = context.get("segment_count", 0) + 1
                yield line
            for child_loop in loop.subloops.all().order_by("id"):
                yield from self._build_loop_dynamic(child_loop, claim, payer, context)

    def _build_segment_line(self, seg, claim, payer, context):
        elements = []
        for elem in seg.elements.all().order_by("position"):
            val = self._resolve_element_dynamic(elem, claim, payer, context) or ""

            # Fetch rule for padding/length
            rule = elem.rules.filter(payer=payer).order_by("order").first()
            if rule:
                max_len = rule.max_length or elem.length
                pad_char = rule.pad_char or " "
                pad_side = rule.pad_side or "right"
            else:
                max_len = elem.length
                pad_char = " "
                pad_side = "right"

            # truncate
            if max_len and len(val) > max_len:
                val = val[:max_len]
            # pad
            if max_len and len(val) < max_len:
                val = val.rjust(max_len, pad_char) if pad_side == "left" else val.ljust(max_len, pad_char)

            elements.append(val)
        return seg.name + "*" + "*".join(elements) + "~"

    def _resolve_element_dynamic(self, element, claim, payer, context):
        """
        Resolve element value using rule:
        CONSTANT, FIELD, MAPPING, FUNC
        Apply transformations.
        """
        rule = element.rules.filter(payer=payer).order_by("order").first()
        if not rule:
            return ""

        val = ""
        if rule.rule_type == "CONSTANT":
            val = str(rule.constant_value)
        elif rule.rule_type == "FIELD" and rule.data_key:
            val = str(self._extract_from_claim(claim, rule.data_key.key) or "")
        elif rule.rule_type == "MAPPING" and rule.data_key:
            val = str(self._extract_from_claim(claim, rule.data_key.key) or "")
            # Apply mapping transformation if needed
        elif rule.rule_type == "FUNC" and callable(rule.transformation):
            val = str(rule.transformation(claim, element, payer, context))

        # Apply transformations
        if rule.transformation:
            if "uppercase" in rule.transformation and rule.transformation["uppercase"]:
                val = val.upper()
            if "date_format" in rule.transformation:
                from datetime import datetime
                try:
                    dt = datetime.strptime(val, rule.transformation.get("input_format", "%Y-%m-%d"))
                    val = dt.strftime(rule.transformation["date_format"])
                except Exception:
                    pass

        return val

    def _extract_from_claim(self, obj, path):
        val = obj
        try:
            for p in path.split("."):
                if p.isdigit():
                    val = val[int(p)]
                else:
                    val = getattr(val, p)
            if isinstance(val, (str, int, float)):
                return str(val)
            return val
        except (AttributeError, IndexError, TypeError):
            return None




from dataclasses import dataclass

@dataclass
class EDIError:
    segment_index: int        # Position within ST-SE
    loop_code: str
    segment_name: str
    element_position: int | None
    message: str

    def __str__(self):
        loc = f"SEG#{self.segment_index} {self.segment_name}"
        if self.element_position:
            loc += f"-E{self.element_position}"
        return f"{loc} [{self.loop_code}]: {self.message}"


class SegmentCounter:
    """
    Tracks ST-SE segment count per transaction set
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.in_transaction = False
        self.count = 0
        self.st_index = None

    def start_transaction(self):
        self.in_transaction = True
        self.count = 1  # ST counts as 1
        self.st_index = 1

    def add(self):
        if self.in_transaction:
            self.count += 1

    def end_transaction(self):
        self.add()  # SE
        self.in_transaction = False
        return self.count


# EDI TRANSFORM UTILITIES
class TransformUtils:

    @staticmethod
    def apply(value, *, transformations=None, max_length=None,
              pad_char=" ", pad_side="right"):

        if value is None:
            value = ""

        value = str(value)

        if transformations:
            if transformations.get("uppercase"):
                value = value.upper()
            if transformations.get("lowercase"):
                value = value.lower()
            if fmt := transformations.get("date_format"):
                try:
                    value = value.strftime(fmt)
                except Exception:
                    pass

        if max_length:
            value = value[:max_length]
            if len(value) < max_length:
                pad = pad_char * (max_length - len(value))
                value = value + pad if pad_side == "right" else pad + value

        return value

# EDI ELEMENTS RESOLVER
class ElementResolver:

    def __init__(self, claim, payer):
        self.claim = claim
        self.payer = payer

    def resolve(self, element):

        rule = element.rules.filter(
            payer=self.payer,
            target_type="ELEMENT"
        ).order_by("order").first()

        if not rule:
            return ""

        value = ""

        if rule.rule_type == "CONSTANT":
            value = rule.constant_value or ""

        elif rule.rule_type == "FIELD" and rule.data_key:
            value = self._extract(rule.data_key.extractor)

        elif rule.rule_type == "FUNC":
            fn = globals().get(rule.constant_value)
            if callable(fn):
                value = fn(self.claim)

        return TransformUtils.apply(
            value,
            transformations=rule.transformation,
            max_length=rule.max_length,
            pad_char=rule.pad_char,
            pad_side=rule.pad_side
        )

    def _extract(self, path):
        try:
            val = self.claim
            for part in path.split("."):
                if isinstance(val, list):
                    val = val[int(part)]
                elif isinstance(val, dict):
                    val = val.get(part)
                else:
                    val = getattr(val, part)
            return val
        except Exception:
            return ""


# EDI SEGMENT PROCESSOR
# class SegmentProcessor:

#     def __init__(self, claim, payer, counter, validator):
#         self.resolver = ElementResolver(claim, payer)
#         self.counter = counter
#         self.validator = validator

#     def build(self, segment, loop_code):
#         self.counter.add()
#         segment_index = self.counter.count

#         values = []
#         for el in segment.elements.order_by("position"):
#             val = self.resolver.resolve(el)
#             self.validator.validate_element(
#                 value=val,
#                 element=el,
#                 segment_index=segment_index,
#                 loop_code=loop_code,
#                 segment_name=segment.name
#             )
#             values.append(val)

#         return "*".join([segment.name] + values) + "~"

class SegmentProcessor:

    def __init__(self, payer, counter, validator):
        self.counter = counter
        self.validator = validator
        self.payer = payer

    def build(self, segment, loop_code, claim_ctx):
        resolver = ElementResolver(claim_ctx, self.payer)

        self.counter.add()
        segment_index = self.counter.count

        values = []
        for el in segment.elements.order_by("position"):
            val = resolver.resolve(el)
            self.validator.validate_element(
                value=val,
                element=el,
                segment_index=segment_index,
                loop_code=loop_code,
                segment_name=segment.name
            )
            values.append(val)

        return "*".join([segment.name] + values) + "~"


# EDI LOOP REPEAT RESOLVER
class LoopRepeatResolver:

    def __init__(self, claim, payer):
        self.claim = claim
        self.payer = payer

    def resolve(self, loop):

        rule = loop.rules.filter(
            payer=self.payer,
            target_type="LOOP"
        ).order_by("order").first()

        if not rule:
            return [self.claim]

        if rule.rule_type == "FIELD":
            items = self._extract(rule.data_key.extractor)
            return list(items)[:loop.max_repeat]

        return [self.claim]

    def _extract(self, path):
        try:
            val = self.claim
            for p in path.split("."):
                val = getattr(val, p)
            return val
        except Exception:
            return []

# EDI LOOP PROCESSOR
# class LoopProcessor:

#     def __init__(self, claim, payer, counter, validator):
#         self.claim = claim
#         self.payer = payer
#         self.counter = counter
#         self.validator = validator
#         self.segment_processor = SegmentProcessor(
#             claim, payer, counter, validator
#         )
#         self.repeat_resolver = LoopRepeatResolver(claim, payer)

#     def process(self, loop):
#         edi = ""

#         # Resolve all repetitions of this loop
#         for ctx in self.repeat_resolver.resolve(loop):
#             # Process each segment in order
#             for seg in loop.segments.order_by("position"):
#                 # Build the segment using rules + transformations
#                 # edi += self.segment_processor.build(seg, loop.code, claim_ctx=ctx)
#                 edi += self.segment_processor.build(seg, loop.code)

#             # Process subloops recursively
#             for sub in loop.subloops.all():
#                 edi += self.process(sub)

#         return edi

class LoopProcessor:

    def __init__(self, claim, payer, counter, validator):
        self.claim = claim
        self.payer = payer
        self.counter = counter
        self.validator = validator
        self.segment_processor = SegmentProcessor(
            payer, counter, validator
        )
        self.repeat_resolver = LoopRepeatResolver(claim, payer)

    def process(self, loop):
        edi = ""

        for ctx in self.repeat_resolver.resolve(loop):

            for seg in loop.segments.order_by("position"):
                edi += self.segment_processor.build(
                    seg, loop.code, ctx
                )

            for sub in loop.subloops.all():
                edi += self.process(sub)

        return edi

# class EnvelopeProcessor:

#     def __init__(self, claim, payer, counter, validator):
#         self.segment_processor = SegmentProcessor(
#             claim, payer, counter, validator
#         )
#         self.counter = counter
#         self.validator = validator

#     def open(self, name):
#         if name == "ST":
#             self.counter.start_transaction()

#         seg = EDISegment.objects.get(loop__isnull=True, name=name)
#         return self.segment_processor.build(seg, "ENVELOPE")

#     def close(self, name):
#         if name == "SE":
#             expected = self.counter.end_transaction()
#             actual = self.counter.count
#             self.validator.validate_segment_count(expected, actual)

#         seg = EDISegment.objects.get(loop__isnull=True, name=name)
#         return self.segment_processor.build(seg, "ENVELOPE")

class EnvelopeProcessor:

    def __init__(self, claim, payer, counter, validator):
        self.claim = claim
        self.payer = payer
        self.counter = counter
        self.validator = validator
        self.segment_processor = SegmentProcessor(
            payer, counter, validator
        )

    def open(self, name):
        if name == "ST":
            self.counter.start_transaction()

        seg = EDISegment.objects.get(loop__isnull=True, name=name)
        return self.segment_processor.build(
            seg, "ENVELOPE", self.claim
        )

    def close(self, name):
        if name == "SE":
            expected = self.counter.end_transaction()
            actual = self.counter.count
            self.validator.validate_segment_count(expected, actual)

        seg = EDISegment.objects.get(loop__isnull=True, name=name)
        return self.segment_processor.build(
            seg, "ENVELOPE", self.claim
        )


# EDI VALIDATOR
class EDIValidator:

    def __init__(self):
        self.errors: list[EDIError] = []

    def validate_element(
        self,
        *,
        value: str,
        element,
        segment_index: int,
        loop_code: str,
        segment_name: str
    ):
        if element.required and not value:
            self.errors.append(
                EDIError(
                    segment_index=segment_index,
                    loop_code=loop_code,
                    segment_name=segment_name,
                    element_position=element.position,
                    message="Required element missing"
                )
            )

    def validate_segment_count(self, expected, actual):
        if expected != actual:
            self.errors.append(
                EDIError(
                    segment_index=actual,
                    loop_code="ST-SE",
                    segment_name="SE",
                    element_position=1,
                    message=f"SE01 mismatch: expected {expected}, got {actual}"
                )
            )

    def raise_if_errors(self):
        if self.errors:
            raise ValueError(
                "\n".join(str(e) for e in self.errors)
            )


# EDI ENGINE ORCHESTRATOR
class EDIEngine:

    OPEN = ["ISA", "GS", "ST", "BHT"]
    CLOSE = ["SE", "GE", "IEA"]

    def __init__(self, claim, payer):
        self.counter = SegmentCounter()
        self.validator = EDIValidator()
        self.loop_processor = LoopProcessor(
            claim, payer, self.counter, self.validator
        )
        self.envelopes = EnvelopeProcessor(
            claim, payer, self.counter, self.validator
        )

    def generate(self):
        edi = ""

        for s in self.OPEN:
            edi += self.envelopes.open(s)

        for loop in EDILoop.objects.filter(parent__isnull=True):
            edi += self.loop_processor.process(loop)

        for s in self.CLOSE:
            edi += self.envelopes.close(s)

        self.validator.raise_if_errors()
        return edi
