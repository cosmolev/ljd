"""Bind prototype upvalues and retain their storage across UCLO/register reuse.

Descriptors name either a parent's register (0x8000, optional immutable 0x4000)
or a parent's upvalue index. Debug names are not binding identities. Captured
registers use private one-element cells; a closure factory captures the current
cell, and UCLO replaces it while retaining the register's value. This expresses
the VM's open/closed lifetime without guessing lexical scopes from stripped code.
"""
import copy

from ljd.ast import liveness, nodes, traverse
from ljd.ast.helpers import insert_table_record


def _children(node):
    """AST edges only, excluding metadata and control-flow backreferences."""
    for name, value in vars(node).items():
        if not name.startswith('_') and name not in ('target', 'true_target', 'false_target', 'body', 'way_out'):
            if isinstance(value, list):
                for child in value:
                    if hasattr(child, '_accept'):
                        yield child
            elif hasattr(value, '_accept'):
                yield value


def _own_nodes(function):
    pending = [function.statements]
    seen = set()
    while pending:
        node = pending.pop()
        if id(node) in seen:
            continue
        seen.add(id(node))
        yield node
        if not isinstance(node, nodes.FunctionDefinition):
            pending.extend(_children(node))


def _identifier(name):
    node = nodes.Identifier()
    node.type, node.name = node.T_UPVALUE, name
    # Synthetic identities lie outside the VM's register/upvalue indices.
    node.slot = 256 + int(name[2:].rstrip('_'))
    # This identifier denotes the cell itself, not its stored value.
    node._cell_pointer = True
    return node


def _value(name):
    node = nodes.TableElement()
    node.table = _identifier(name)
    node.key = nodes.Constant()
    node.key.type, node.key.value = nodes.Constant.T_INTEGER, 1
    return node


def _cell(value=None):
    node = nodes.TableConstructor()
    if value is not None:
        key = nodes.Constant()
        key.type, key.value = nodes.Constant.T_INTEGER, 1
        insert_table_record(node, key, value, False)
    return node


def _assignment(destinations, expressions, local=False):
    node = nodes.Assignment()
    node.type = node.T_LOCAL_DEFINITION if local else node.T_NORMAL
    node.destinations.contents = destinations
    node.expressions.contents = expressions
    return node


def _calls(node):
    if isinstance(node, nodes.FunctionDefinition):
        return False
    return isinstance(node, nodes.FunctionCall) or any(_calls(c) for c in _children(node))


def _protect(function):
    """Trace FNEW's reaching writes and writes while a capture is open.

    A physical register can be an ordinary temporary outside that lifetime. In
    particular, retaining a reused condition temporary can prevent the unwarper
    from substituting its constant before extracting a while condition.
    """
    blocks = function.statements.contents
    edges = {b: liveness.successors(b.warp) for b in blocks}
    closes = dict(function._upvalue_closes)
    actions = {}
    for block in blocks:
        actions[block] = sorted([*block.contents, block.warp], key=lambda n: getattr(n, '_addr', block.last_address))
        for addr, first in closes.items():
            if block.first_address <= addr <= block.last_address:
                actions[block].append((addr, first))
        actions[block].sort(key=lambda n: n[0] if isinstance(n, tuple) else getattr(n, '_addr', block.last_address))

    def captures(node):
        if isinstance(node, nodes.FunctionDefinition):
            return {d & 0xff for d in node._upvalues or [] if d & 0x8000}
        return set().union(*(captures(c) for c in _children(node)))

    facts = {action: (*liveness.effects(action), captures(action))
             for block in blocks for action in actions[block] if not isinstance(action, tuple)}

    opened = {b: set() for b in blocks}
    changed = True
    while changed:
        changed = False
        for block in blocks:
            active = set(opened[block])
            for action in actions[block]:
                if isinstance(action, tuple):
                    active = {s for s in active if s < action[1]}
                    continue
                used, defined, newly_captured = facts[action]
                if isinstance(action, nodes.Assignment) and active & (used | defined):
                    action._preserve_live = True
                    action._capture_access = True
                active.update(newly_captured)
            for target in edges[block]:
                if not active <= opened[target]:
                    opened[target].update(active)
                    changed = True

    needed = {b: set() for b in blocks}
    changed = True
    while changed:
        changed = False
        for block in reversed(blocks):
            demand = set().union(*(needed[s] for s in edges[block]))
            for action in reversed(actions[block]):
                if isinstance(action, tuple):
                    continue
                _, defined, newly_captured = facts[action]
                if isinstance(action, nodes.Assignment) and demand & defined:
                    action._preserve_live = True
                demand.difference_update(defined)
                demand.update(newly_captured)
            if not demand <= needed[block]:
                needed[block].update(demand)
                changed = True


def prepare(ast):
    """Resolve identities and protect reads/writes before temporary elimination."""
    class Names(traverse.Visitor):
        def __init__(self):
            self.used = set()

        def visit_identifier(self, node):
            if node.name:
                self.used.add(node.name)

        def visit_constant(self, node):
            if node.type == node.T_STRING:
                self.used.add(node.value)

        def visit_function_definition(self, node):
            if node._debuginfo is not None:
                self.used.update(v.name for v in node._debuginfo.variable_info)

    names = Names()
    traverse.traverse(names, ast)
    next_cell = 0
    immutable = set()

    def bind(function, inherited):
        nonlocal next_cell
        own = list(_own_nodes(function))
        children = [n for n in own if isinstance(n, nodes.FunctionDefinition) and n.error is None]
        captured = sorted({d & 0xff for child in children for d in child._upvalues
                           if d & 0x8000})
        cells = {}
        for slot in captured:
            name = 'uv%d' % next_cell
            next_cell += 1
            while name in names.used:
                name += '_'
            names.used.add(name)
            cells[slot] = name
            descriptors = [d for child in children for d in child._upvalues
                           if d & 0x8000 and d & 0xff == slot]
            if all(d & 0x4000 for d in descriptors):
                immutable.add(name)
        function._capture_cells = cells
        function._capture_bindings = inherited

        for child in children:
            bindings = []
            for descriptor in child._upvalues:
                if descriptor & 0x8000:
                    bindings.append(cells[descriptor & 0xff])
                else:
                    if descriptor >= len(inherited):
                        raise ValueError('Upvalue descriptor outside lexical parent')
                    bindings.append(inherited[descriptor])
            bind(child, bindings)

        if cells:
            _protect(function)

        def touches(node):
            if isinstance(node, nodes.FunctionDefinition):
                return bool(node._upvalues)
            if isinstance(node, nodes.Identifier):
                return (node.type == node.T_UPVALUE and
                        inherited[node.slot] not in immutable)
            return any(touches(child) for child in _children(node))

        for node in own:
            if (cells or inherited) and isinstance(node, (nodes.Assignment, nodes.FunctionCall)) and _calls(node):
                # Calls can mutate captured state even without a UGET/USET in
                # this function. Keep their order relative to other calls too.
                node._capture_access = True
            if isinstance(node, nodes.Assignment) and (cells or inherited):
                node._capture_context = True
            if isinstance(node, nodes.Assignment) and touches(node):
                # A read is a snapshot, even if an intervening call writes the
                # captured variable. FNEW must capture before a later UCLO.
                node._preserve_live = True
                node._capture_access = True
            elif isinstance(node, nodes.NumericLoopWarp) and node.index.slot in cells:
                node._preserve_live = True
            elif isinstance(node, nodes.IteratorWarp) and any(v.slot in cells for v in node.variables.contents):
                node._preserve_live = True
        if any(getattr(arg, 'slot', -1) in cells for arg in function.arguments.contents):
            function._preserve_live = True

        # Keep closing on the original CFG edge, including conditional break/
        # return edges. A cell copied here is never shared with old closures.
        for addr, first_slot in function._upvalue_closes:
            closing = [s for s in captured if s >= first_slot]
            if not closing:
                continue
            block = next(b for b in function.statements.contents
                         if b.first_address <= addr <= b.last_address)
            for slot in closing:
                statement = _assignment([_identifier(cells[slot])], [_cell(_value(cells[slot]))])
                statement._addr = addr
                statement._preserve_live = True
                index = next((i for i, n in enumerate(block.contents)
                              if getattr(n, '_addr', addr) > addr), len(block.contents))
                block.contents.insert(index, statement)

    if ast._upvalues:
        raise ValueError('Root prototype requires external upvalue bindings')
    bind(ast, [])


def preserve_call(info, ref, src):
    """A call cannot move past a snapshot of storage it may mutate.

    Calls used immediately in a condition can still form short-circuit
    expressions. Blanket call retention prevents that structural reconstruction.
    """
    if not getattr(info.assignment, '_capture_context', False):
        return False

    if not _calls(src):
        return False
    block = next((n for n in reversed(info.references[0].path) if isinstance(n, nodes.Block)), None)
    if block is None or block not in ref.path or info.assignment not in block.contents:
        return True
    use = next((n for n in ref.path[ref.path.index(block) + 1:] if n in block.contents), None)
    last = len(block.contents) if use is None else block.contents.index(use)
    first = block.contents.index(info.assignment)
    if last <= first:
        # Constructor folding may otherwise run a call before the retained
        # assignment that loads its captured callee or argument.
        return True
    return any(getattr(n, '_capture_access', False) and not getattr(n, '_invalidated', False)
               for n in block.contents[first + 1:last])


def preserve_table_field(info, ref):
    """Do not fold a field before a retained captured-value snapshot or call."""
    if not getattr(info.assignment, '_capture_context', False):
        return False
    block = next((n for n in reversed(info.references[0].path) if isinstance(n, nodes.Block)), None)
    if block is None or block not in ref.path or info.assignment not in block.contents:
        return True
    assignment = next((n for n in ref.path[ref.path.index(block) + 1:] if n in block.contents), None)
    if assignment is None:
        return True
    first, last = block.contents.index(info.assignment), block.contents.index(assignment)
    return any(getattr(n, '_capture_access', False) and not getattr(n, '_invalidated', False)
               for n in block.contents[first + 1:last])


def mark_temporaries(ast):
    """Do not attach retained snapshots to a later variable's debug lifetime.

    The regular locals pass has already resolved actual debug locals. The late
    heuristic otherwise renames the temporary function in `local x = f()` to x,
    leaving the call's earlier reference unbound when that snapshot is retained.
    """
    class Functions(traverse.Visitor):
        def visit_function_definition(self, function):
            if function.error is not None:
                return
            if function._capture_cells or function._capture_bindings:
                for node in _own_nodes(function):
                    if isinstance(node, nodes.Identifier) and node.type == node.T_SLOT:
                        node._capture_temporary = True
    traverse.traverse(Functions(), ast)


def lower(ast):
    """Emit cells and factories after the normal control-flow/slot passes."""
    def function_body(function):
        cells = function._capture_cells
        bindings = function._capture_bindings

        def cell_name(identifier):
            if getattr(identifier, '_cell_pointer', False):
                return None
            if identifier.type == identifier.T_UPVALUE:
                if identifier.slot >= len(bindings) or identifier.slot < 0:
                    raise ValueError('Unresolved upvalue reference')
                return bindings[identifier.slot]
            if identifier.type in (identifier.T_SLOT, identifier.T_LOCAL):
                return cells.get(identifier.slot)
            return None

        def rewrite(node):
            if isinstance(node, nodes.Identifier):
                name = cell_name(node)
                return _value(name) if name is not None else node
            if isinstance(node, nodes.FunctionDefinition):
                if node.error is not None:
                    return node
                function_body(node)
                if not node._capture_bindings:
                    return node
                # Each factory parameter freezes this FNEW's cell identity.
                # Siblings still share the same cell, so writes remain visible.
                names = list(dict.fromkeys(node._capture_bindings))
                factory = nodes.FunctionDefinition()
                for name in names:
                    arg = _identifier(name)
                    arg.type = arg.T_LOCAL
                    factory.arguments.contents.append(arg)
                result = nodes.Return()
                result.returns.contents.append(node)
                factory.statements.contents.append(result)
                call = nodes.FunctionCall()
                call.function = factory
                call.arguments.contents = [_identifier(name) for name in names]
                return call
            if isinstance(node, (nodes.NumericFor, nodes.IteratorFor)):
                variables = ([node.variable] if isinstance(node, nodes.NumericFor)
                             else node.identifiers.contents)
                copies = [_assignment([_value(cells[v.slot])], [copy.copy(v)])
                          for v in variables if v.slot in cells]
                # Loop indices have native lexical declarations. Copy their
                # value into the current cell at the start of each iteration.
                for name, value in list(vars(node).items()):
                    if name not in ('variable', 'identifiers') and not name.startswith('_'):
                        if hasattr(value, '_accept'):
                            setattr(node, name, rewrite(value))
                node.statements.contents[0:0] = copies
                return node
            if isinstance(node, nodes.StatementsList):
                contents = []
                for statement in node.contents:
                    if isinstance(statement, nodes.Assignment) and statement.type == statement.T_LOCAL_DEFINITION:
                        destinations = statement.destinations.contents
                        if any(isinstance(d, nodes.Identifier) and cell_name(d) for d in destinations):
                            # Keep simultaneous/multiple-result assignment intact.
                            ordinary = [copy.copy(d) for d in destinations
                                        if isinstance(d, nodes.Identifier) and cell_name(d) is None]
                            if ordinary:
                                nil = nodes.Primitive()
                                nil.type = nil.T_NIL
                                contents.append(_assignment(ordinary, [nil], local=True))
                            statement.type = statement.T_NORMAL
                    contents.append(rewrite(statement))
                node.contents = contents
                return node
            for name, value in list(vars(node).items()):
                if name.startswith('_'):
                    continue
                if isinstance(value, list):
                    setattr(node, name, [rewrite(v) if hasattr(v, '_accept') else v for v in value])
                elif hasattr(value, '_accept'):
                    setattr(node, name, rewrite(value))
            return node

        rewrite(function.statements)
        parameters = {a.slot: a for a in function.arguments.contents if isinstance(a, nodes.Identifier)}
        declarations = []
        for slot, name in cells.items():
            identifier = _identifier(name)
            identifier.type = identifier.T_LOCAL
            parameter = parameters.get(slot)
            declarations.append(_assignment([identifier], [_cell(parameter)], local=True))
        function.statements.contents[0:0] = declarations

    function_body(ast)
