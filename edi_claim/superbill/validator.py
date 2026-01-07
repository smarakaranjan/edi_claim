class EDIValidationError(Exception):
    pass


class LoopContext:
    def __init__(self, loop_def):
        self.loop_def = loop_def
        self.segment_counts = {}


class EDIValidator:
    def __init__(self, root_loop):
        self.root = root_loop
        self.stack = [LoopContext(root_loop)]

    def validate_segment(self, seg_id, elements):
        ctx = self.stack[-1]

        if seg_id not in ctx.loop_def.segments:
            raise EDIValidationError(
                f"Unexpected segment {seg_id} in loop {ctx.loop_def.id}"
            )

        seg_def = ctx.loop_def.segments[seg_id]
        count = ctx.segment_counts.get(seg_id, 0) + 1

        if count > seg_def.max_repeat:
            raise EDIValidationError(
                f"Segment {seg_id} exceeds max repeat {seg_def.max_repeat}"
            )

        ctx.segment_counts[seg_id] = count

        # element validation
        for pos, el_def in seg_def.elements.items():
            if el_def.required and pos >= len(elements):
                raise EDIValidationError(
                    f"Missing required element {el_def.id} in {seg_id}"
                )

            if el_def.allowed and elements[pos] not in el_def.allowed:
                raise EDIValidationError(
                    f"Invalid value {elements[pos]} for {el_def.id}"
                )

    def enter_loop(self, loop_id):
        parent = self.stack[-1]
        if loop_id not in parent.loop_def.child_loops:
            raise EDIValidationError(f"Invalid loop {loop_id}")
        self.stack.append(LoopContext(parent.loop_def.child_loops[loop_id]))

    def exit_loop(self):
        self.stack.pop()
