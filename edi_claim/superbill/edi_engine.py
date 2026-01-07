# Default import's
from itertools import chain

# Module import's
from superbill.models import EDILoop

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


class Dynamic837ClaimEngine:
    """
    Correct 837 EDI claim builder.
    Enforces hierarchy, element lengths, and proper padding.
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

                # Subloops like 1000A/B, 2000A/B, 2300, 2400
                for child_loop in st_loop.subloops.all().order_by("id"):
                    yield from self._build_loop(child_loop, claim, payer, context)

                # SE
                se_seg = st_loop.segments.filter(name="SE").first()
                if se_seg:
                    yield self._build_segment_line(se_seg, claim, payer, context)

            # GE
            ge_seg = gs_loop.segments.filter(name="GE").first()
            if ge_seg:
                yield self._build_segment_line(ge_seg, claim, payer, context)

        # IEA
        iea_seg = isa_loop.segments.filter(name="IEA").first()
        if iea_seg:
            yield self._build_segment_line(iea_seg, claim, payer, context)

    def _build_loop(self, loop, claim, payer, context):
        for seg in loop.segments.all().order_by("position"):
            yield self._build_segment_line(seg, claim, payer, context)
        for child_loop in loop.subloops.all().order_by("id"):
            yield from self._build_loop(child_loop, claim, payer, context)

    def _build_segment_line(self, seg, claim, payer, context):
        elements = []
        for elem in seg.elements.all().order_by("position"):
            val = self._resolve_element_dynamic(elem, claim, payer, context) or ""
            # Fetch rule for padding/length
            rule = elem.rules.filter(payer=payer).first()
            if rule:
                max_len = getattr(rule, "max_length", elem.length)
                pad_char = getattr(rule, "pad_char", " ")
                pad_side = getattr(rule, "pad_side", "right")
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
        rule = element.rules.filter(payer=payer).first()
        if not rule:
            return ""
        if rule.rule_type == "CONSTANT":
            return str(rule.constant_value)
        if rule.rule_type == "FIELD" and rule.data_key:
            return str(self._extract_from_claim(claim, rule.data_key.key) or "")
        return ""

    def _extract_from_claim(self, obj, path):
        val = obj
        try:
            for p in path.split("."):
                if p.isdigit():
                    val = val[int(p)]
                else:
                    val = getattr(val, p)
            # Convert date/time fields if needed
            if isinstance(val, (str, int, float)):
                return str(val)
            return val
        except (AttributeError, IndexError, TypeError):
            return None
