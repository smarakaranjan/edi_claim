# Default import's
from itertools import chain

# Module import's
from superbill.models import EDILoop

class Dynamic837ClaimEngine:
    
    """
    Dynamic, memory-efficient 837 claim builder.
    Only requires claim and payer objects.
    """

    def generate(self, claim, payer, context=None):
        """
        Yield the 837 claim line by line.
        """
        context = context or {}

        # Automatically find root loop (loop with no parent)
        root_loop = (
            EDILoop.objects.prefetch_related(
                "segments__elements__rules__data_key",
                "subloops__segments__elements__rules__data_key",
                "subloops__subloops__segments__elements__rules__data_key",
            )
            .filter(parent__isnull=True)
            .order_by("id")
            .first()
        )

        if not root_loop:
            raise ValueError("No root EDILoop defined in the database.")

        yield from self._build_loop(root_loop, claim, payer, context)

    def _build_loop(self, loop, obj, payer, context):
        # Check if this loop should repeat over related objects dynamically
        for field in obj._meta.get_fields():
            if field.one_to_many:  # reverse FK
                related_name = field.get_accessor_name()
                if loop.code.lower() == related_name.lower():  # match loop to related name
                    for item in getattr(obj, related_name).all():
                        yield from self._build_loop(loop, item, payer, context)
                    return

        # Build segments for this object
        segs = (
            seg.name + "*" + "*".join(
                self._resolve_element_dynamic(e, obj, payer, context)
                for e in seg.elements.all().order_by("position")
            ) + "~"
            for seg in loop.segments.all().order_by("position")
        )

        # Child loops recursively
        children = (
            line
            for child in loop.subloops.all().order_by("id")
            for line in self._build_loop(child, obj, payer, context)
        )

        yield from chain(segs, children)


    def _resolve_element_dynamic(self, element, claim, payer, context):
        rule = next((r for r in element.rules.all() if r.payer_id == payer.id), None)
        if not rule:
            return ""

        if rule.rule_type == "FIELD" and rule.data_key and rule.data_key.extractor:
            return self._apply_transformation(
                self._extract_from_claim(claim, rule.data_key.extractor),
                rule.transformation,
                rule=rule,
                element=element
            )

        if rule.rule_type == "CONSTANT":
            return self._apply_transformation(
                rule.constant_value,
                rule.transformation,
                rule=rule,
                element=element
            )

        if rule.rule_type == "FUNC" and rule.data_key:
            func = context.get(rule.data_key.key)
            if callable(func):
                return self._apply_transformation(
                    func(claim, payer, context),
                    rule.transformation,
                    rule=rule,
                    element=element
                )

        if rule.rule_type == "MAPPING" and rule.data_key:
            mapping = rule.transformation or {}
            value = self._extract_from_claim(claim, rule.data_key.extractor)
            return self._apply_transformation(
                mapping.get(value, ""),
                rule.transformation,
                rule=rule,
                element=element
            )

        return ""


    def _extract_from_claim(self, obj, path):
        parts = path.split(".")
        val = obj
        try:
            for p in parts:
                if p.isdigit():
                    val = val[int(p)]
                else:
                    val = getattr(val, p)
            return val
        except (AttributeError, IndexError, TypeError):
            return None

    # def _apply_transformation(self, value, trans):
    #     if value is None:
    #         return ""
    #     v = str(value)
    #     if not trans:
    #         return v
    #     if trans.get("uppercase"):
    #         v = v.upper()
    #     if "truncate" in trans:
    #         v = v[: int(trans["truncate"])]
    #     if "date_format" in trans:
    #         v = value.strftime(trans["date_format"])
    #     return v

    def _apply_transformation(self, value, trans, rule=None, element=None):
        """
        Apply transformations (semantic + syntactic) for EDI elements.
        Handles uppercase, truncate, date_format, and EDI-specific length/padding.
        """
        if value is None:
            value = ""
        v = str(value)

        # --- semantic transformations ---
        if trans:
            if trans.get("uppercase"):
                v = v.upper()
            if "truncate" in trans:
                v = v[: int(trans["truncate"])]
            if "date_format" in trans and hasattr(value, "strftime"):
                v = value.strftime(trans["date_format"])

        # --- syntactic EDI formatting ---
        # Priority: rule > element
        min_len = getattr(rule, "min_length", None) if rule else None
        max_len = getattr(rule, "max_length", None) if rule else None
        pad_char = getattr(rule, "pad_char", " ") if rule else " "
        pad_side = getattr(rule, "pad_side", "right") if rule else "right"

        # Fallback: use element length if defined
        if not max_len and element and hasattr(element, "length"):
            max_len = element.length

        # Enforce min length (pad with spaces or zeros)
        if min_len and len(v) < min_len:
            v = v.ljust(min_len, pad_char)

        # Enforce max length (pad or truncate)
        if max_len:
            if len(v) < max_len:
                if pad_side == "left":
                    v = v.rjust(max_len, pad_char)
                else:
                    v = v.ljust(max_len, pad_char)
            else:
                v = v[:max_len]

        return v
