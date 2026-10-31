"""Conservative register liveness for the warped AST."""
from collections import deque

from ljd.ast import nodes, traverse


class _Reads(traverse.Visitor):
    def __init__(self):
        super().__init__()
        self.slots = set()

    def _visit(self, node):
        if not isinstance(node, nodes.FunctionDefinition):
            super()._visit(node)

    def visit_identifier(self, node):
        if node.type in (nodes.Identifier.T_SLOT, nodes.Identifier.T_LOCAL):
            self.slots.add(node.slot)


def reads(node):
    visitor = _Reads()
    visitor._visit(node)
    return visitor.slots


def effects(node):
    """RHS and table-address reads precede simultaneous register writes."""
    if isinstance(node, nodes.Assignment):
        used, defined = reads(node.expressions), set()
        for dst in node.destinations.contents:
            if isinstance(dst, nodes.Identifier) and dst.type in (dst.T_SLOT, dst.T_LOCAL):
                defined.add(dst.slot)
            else:
                used.update(reads(dst))
        return used, defined
    if isinstance(node, nodes.NumericLoopWarp):
        return reads(node.controls), {node.index.slot}
    if isinstance(node, nodes.IteratorWarp):
        return reads(node.controls), {v.slot for v in node.variables.contents}
    return reads(node), set()


def successors(warp):
    if isinstance(warp, nodes.UnconditionalWarp):
        return [warp.target]
    if isinstance(warp, nodes.ConditionalWarp):
        return [warp.true_target, warp.false_target]
    if isinstance(warp, (nodes.NumericLoopWarp, nodes.IteratorWarp)):
        return [warp.body, warp.way_out]
    return []


def _protect_function(function):
    blocks = function.statements.contents
    if not blocks or not all(isinstance(b, nodes.Block) for b in blocks):
        return
    block_set = set(blocks)
    edges = {b: [s for s in successors(b.warp) if s in block_set] for b in blocks}
    predecessors = {b: set() for b in blocks}
    uses, defs, last_writes = {}, {}, {}
    for block in blocks:
        used, defined, last = set(), set(), {}
        for node in [*block.contents, block.warp]:
            r, w = effects(node)
            used.update(r - defined)
            defined.update(w)
            last.update({slot: node for slot in w})
        uses[block], defs[block], last_writes[block] = used, defined, last
        for target in edges[block]:
            predecessors[target].add(block)

    # Solve to a fixed point: a backward edge is as significant as a forward one.
    live_in, live_out = {b: set() for b in blocks}, {b: set() for b in blocks}
    pending, queued = deque(reversed(blocks)), set(blocks)
    while pending:
        block = pending.popleft()
        queued.remove(block)
        out = set().union(*(live_in[s] for s in edges[block]))
        incoming = uses[block] | (out - defs[block])
        live_out[block] = out
        if incoming != live_in[block]:
            live_in[block] = incoming
            for previous in predecessors[block] - queued:
                pending.append(previous)
                queued.add(previous)

    # Trace the reaching writes needed at loop entries and exits. Do not mark
    # every use of the same physical register elsewhere in the function: a slot
    # can hold an unrelated temporary before or after its loop lifetime.
    # Numeric/iterator warps produce their index/results themselves; those reads
    # do not refer to a preceding assignment to the reused register.
    order = {b: i for i, b in enumerate(blocks)}
    needed_in, needed_out = {b: set() for b in blocks}, {b: set() for b in blocks}
    for block in blocks:
        produced = effects(block.warp)[1]
        for target in edges[block]:
            if order[target] <= order[block]:
                needed_in[target].update(live_in[target] - produced)
                needed_out[block].update(live_out[block] - produced)

    pending, queued = deque(blocks), set(blocks)
    while pending:
        block = pending.popleft()
        queued.remove(block)
        for slot in needed_out[block]:
            assignment = last_writes[block].get(slot)
            if isinstance(assignment, nodes.Assignment):
                assignment._preserve_live = True
        needed_in[block].update(needed_out[block] - defs[block])
        for previous in predecessors[block]:
            extra = needed_in[block] - needed_out[previous]
            if extra:
                needed_out[previous].update(extra)
                if previous not in queued:
                    pending.append(previous)
                    queued.add(previous)


def protect_live_writes(ast):
    """Keep cross-block state; the linear collector cannot prove it removable."""
    class Functions(traverse.Visitor):
        def visit_function_definition(self, node):
            _protect_function(node)
    traverse.traverse(Functions(), ast)
