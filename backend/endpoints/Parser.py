import copy

from antlr4 import *
from .TreeNode import *
from antlr4.error.ErrorListener import ConsoleErrorListener, ErrorListener

from .antlr.compilerLexer import compilerLexer as CLexer
from .antlr.compilerParser import compilerParser, compilerParser as CParser
from .antlr.compilerVisitor import compilerVisitor as CVisitor


class MyErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e) -> None:
        raise Exception(
            "Syntax error at line {0} column {1}: {2}".format(line, column, msg)
        )


class Parser:
    def __init__(self) -> None:
        pass

    @staticmethod
    def parse(input_file: str) -> TreeNode:
        """
        Parse the input file and return the CST
        :arg input_file: str
        :return tree: CParser.ProgContext
        """
        error_listener = MyErrorListener()
        lexer = CLexer(FileStream(input_file))
        lexer.removeErrorListener(ConsoleErrorListener.INSTANCE)
        lexer.addErrorListener(error_listener)

        stream: CommonTokenStream = CommonTokenStream(lexer)
        parser: CParser = CParser(stream)
        parser.removeErrorListener(ConsoleErrorListener.INSTANCE)
        parser.addErrorListener(error_listener)

        tree: CParser.ProgContext = parser.prog()
        ast = ASTVisitor().visit(tree)
        ast = Parser.transform_loops(ast)
        ast = Parser.convert_to_ast(ast)
        return ast

    @staticmethod
    def transform_loops(ast: TreeNode) -> TreeNode:
        # Transform for loops into while loops
        for child in ast.children:
            if isinstance(child, ForNode):
                idx = ast.children.index(child)
                first = child.children[0]
                condition = child.children[1]
                third = child.children[2]

                scope = child.children[-1]
                scope.children.append(third)

                while_children = [copy.deepcopy(condition)] + [scope]
                while_node = WhileNode(
                    children=while_children,
                    line_nr=child.line_nr,
                    origins_from_for=True,
                )
                first_node = copy.deepcopy(first)

                ast.children[idx] = while_node
                ast.children.insert(idx - 1, first_node)

        for child in ast.children:
            Parser.transform_loops(child)

        return ast

    @staticmethod
    def convert_to_ast(cst: TreeNode) -> TreeNode | None:
        if not cst.children:
            return

        for child in cst.children:
            Parser.convert_to_ast(child)

        for child in cst.children:
            # Remove all statements that have only one child except for some specific ones
            if len(child.children) == 1:
                new_child = child.children[0]
                if not isinstance(
                        child,
                        (
                                ProgNode,
                                AddressNode,
                                ReturnNode,
                                NotNode,
                                PointerNode,
                                IntPointerNode,
                                FloatPointerNode,
                                CharPointerNode,
                                BoolPointerNode,
                                PrintfNode,
                                ElseNode,
                                IfNode,
                                ScopeNode,
                                DefaultNode,
                                CaseNode,
                                EnumNode,
                                EnumEntryNode,
                                IncludeNode,
                                BitNotNode,
                                ArrayDeclElementsNode,
                        ),
                ):
                    idx = cst.children.index(child)
                    cst.children[idx] = new_child

            # C-string
            if (
                    isinstance(child, ArrayDeclAssignNode)
                    and child.children[0].value == "char"
                    and isinstance(child.children[-1], StringNode)
            ):
                char_array = []
                for c in child.children[-1].value:
                    char_array.append(CharNode(f"'{c}'", line_nr=child.line_nr))
                char_array.pop(0)
                char_array.pop(-1)
                char_array.append(CharNode("'\\0'", line_nr=child.line_nr))
                child.children[-1] = ArrayDeclElementsNode(
                    line_nr=child.line_nr, children=char_array
                )
                child.children[2].value = str(len(char_array))

        return cst

    @staticmethod
    def check_const_loops(ast: TreeNode, root: TreeNode) -> bool | str:
        for child in ast.children:
            # Ignore non-while nodes
            if not isinstance(child, WhileNode):
                result = Parser.check_const_loops(child, root)
                if result is not None:
                    return result

            else:
                # Get all variables in the condition
                condition_variables = []

                def find_condition_variables(node: TreeNode) -> None:
                    if isinstance(node, IdNode):
                        condition_variables.append(node.value)
                    for child in node.children:
                        find_condition_variables(child)

                condition = child.children[0]
                scope = child.children[1]
                find_condition_variables(condition)

                # Check if any of the variables in the condition are changed in the loop
                def find_variable_in_loop(node: TreeNode) -> bool:
                    if isinstance(node, AssignNode):
                        if node.children[0].value in condition_variables:
                            return True
                    for child in node.children:
                        if find_variable_in_loop(child):
                            return True
                    return False

                condition_changes = find_variable_in_loop(child.children[1])

                # At least one of the condition variables changes in the loop
                if condition_changes:
                    # TODO: find original values, determine if they need to go up or down, determine if they go up or down respectively
                    # Find all original values of the variables in the condition
                    def find_condition_variable_value(node: str, root: TreeNode) -> TreeNode | None:
                        if isinstance(root, NewVariableNode):
                            if root.children[1].value == node:
                                return root.children[-1].value
                        for c in root.children:
                            temp = find_condition_variable_value(node, c)
                            if temp is not None:
                                return temp
                        return None

                    condition_variables_values = {}
                    for var in condition_variables:
                        condition_variables_values[var] = find_condition_variable_value(var, root)

                    # Determine the terminal values of the condition variables
                    terminal_values = {}
                    for var in condition_variables:
                        def find_comparisons(node: TreeNode):
                            if isinstance(node, (LtNode, LeqNode, GtNode, GeqNode, NeqNode)):
                                if node.children[0].value == var or node.children[1].value == var:
                                    return node
                            for child in node.children:
                                res = find_comparisons(child)
                                if res is not None:
                                    return res

                        comparison = find_comparisons(condition)
                        terminal_value = None
                        if isinstance(comparison, (LtNode, GtNode, NeqNode)):
                            if comparison.children[0].value == var:
                                terminal_value = int(comparison.children[1].value)
                            else:
                                terminal_value = int(comparison.children[0].value)
                        elif isinstance(comparison, (LeqNode, GeqNode)):
                            if comparison.children[0].value == var:
                                terminal_value = int(comparison.children[1].value) + 1
                            else:
                                terminal_value = int(comparison.children[0].value) + 1

                        terminal_values[var] = terminal_value

                    # Determine if the condition goes up or down
                    variable_terminates = {}
                    for var in condition_variables:
                        def find_condition_direction(node: TreeNode):
                            if isinstance(node, PlusNode) and (node.children[0].value == var or node.children[1].value == var):
                                return True
                            if isinstance(node, MinusNode) and (node.children[0].value == var or node.children[1].value == var):
                                return False
                            for c in node.children:
                                res = find_condition_direction(c)
                                if res is not None:
                                    return res
                            return None

                        goes_up = find_condition_direction(scope)
                        if goes_up is None:
                            variable_terminates[var] = False
                            continue

                        print(var)
                        print(goes_up)
                        print(terminal_values[var], condition_variables_values[var])
                        if terminal_values[var] >= int(condition_variables_values[var]) and goes_up:
                            variable_terminates[var] = True
                        elif terminal_values[var] <= int(condition_variables_values[var]) and not goes_up:
                            variable_terminates[var] = True
                        else:
                            variable_terminates[var] = False

                    if all(variable_terminates.values()):
                        return True
                    else:
                        return False

                else:
                    return Parser.evaluate_condition(root, condition)

    @staticmethod
    def evaluate_condition(ast: TreeNode, condition: TreeNode) -> bool:
        # Find all id's in condition
        condition_ids = []
        if not isinstance(condition, (IntNode, BoolNode)):
            for child in condition.children:
                if isinstance(child, IdNode):
                    condition_ids.append(child.value)

            # Find all variable values in the condition
            condition_var_values = {}

            def find_variable_value(node: TreeNode):
                if isinstance(node, NewVariableNode):
                    if node.children[1].value in condition_ids:
                        condition_var_values[node.children[1].value] = node.children[-1]
                for child in node.children:
                    find_variable_value(child)
                return None

            find_variable_value(ast)

            # Replace all id's in the condition with their values
            for i, child in enumerate(condition.children):
                if isinstance(child, IdNode) and child.value in condition_var_values:
                    condition.children[i] = copy.copy(condition_var_values[child.value])

            match condition:
                case PlusNode():
                    return bool(int(condition.children[0].value) + int(condition.children[1].value))
                case MinusNode():
                    return bool(int(condition.children[0].value) - int(condition.children[1].value))
                case MultNode():
                    return bool(int(condition.children[0].value) * int(condition.children[1].value))
                case DivNode():
                    return bool(int(condition.children[0].value) / int(condition.children[1].value))
                case ModNode():
                    return bool(int(condition.children[0].value) % int(condition.children[1].value))
                case GtNode():
                    return bool(int(condition.children[0].value) > int(condition.children[1].value))
                case LtNode():
                    return bool(int(condition.children[0].value) < int(condition.children[1].value))
                case GeqNode():
                    return bool(int(condition.children[0].value) >= int(condition.children[1].value))
                case LeqNode():
                    return bool(int(condition.children[0].value) <= int(condition.children[1].value))
                case EqualNode():
                    return bool(int(condition.children[0].value) == int(condition.children[1].value))
                case NeqNode():
                    return bool(int(condition.children[0].value) != int(condition.children[1].value))


operator_signs = {
    "+",
    "-",
    "*",
    "/",
    "<",
    ">",
    "==",
    "&&",
    "||",
    ">=",
    "<=",
    "!=",
    "%",
    ">>",
    "<<",
    "!",
}


class ASTVisitor(CVisitor):
    def __init__(self) -> None:
        self.typedefs = {}
        self.visited_main = False

    def visitArray_declaration(self, ctx: compilerParser.Array_declarationContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)
        return ArrayDeclarationNode(line_nr=ctx.start.line, children=children)

    def visitArray_decl_assignment(
            self, ctx: compilerParser.Array_decl_assignmentContext
    ):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)
        return ArrayDeclAssignNode(line_nr=ctx.start.line, children=children)

    def visitStruct(self, ctx: compilerParser.StructContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)
        return StructNode(line_nr=ctx.start.line, children=children)

    def visitStruct_decl(self, ctx: compilerParser.Struct_declContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)
        return StructDeclNode(line_nr=ctx.start.line, children=children)

    def visitStruct_entry(self, ctx: compilerParser.Struct_entryContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)
        return StructEntryNode(line_nr=ctx.start.line, children=children)

    def visitStruct_access(self, ctx: compilerParser.Struct_accessContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)
        return StructAccessNode(line_nr=ctx.start.line, children=children)

    def visitScanf(self, ctx: compilerParser.ScanfContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)
        return ScanfNode(line_nr=ctx.start.line, children=children)

    def visitArray_decl_elements(self, ctx: compilerParser.Array_decl_elementsContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)
        return ArrayDeclElementsNode(line_nr=ctx.start.line, children=children)

    def visitArray_access(self, ctx: compilerParser.Array_accessContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)
        return ArrayAccessNode(line_nr=ctx.start.line, children=children)

    def visitDefine(self, ctx: compilerParser.DefineContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)
        return DefineNode(line_nr=ctx.start.line, children=children)

    def visitInclude(self, ctx: compilerParser.IncludeContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)
        return IncludeNode(line_nr=ctx.start.line, children=children)

    def visitProg(self, ctx: CParser.ProgContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        return ProgNode(line_nr=ctx.start.line, children=children)

    def visitTypedef(self, ctx: compilerParser.TypedefContext):
        c_type = ctx.children[1].getText()
        new_type = ctx.children[2].getText()
        if new_type in ["int", "float", "char"]:
            raise Exception(
                f"Type {new_type} is a reserved keyword and cannot be used as a typedef."
            )
        self.typedefs[new_type] = c_type

    def visitMain(self, ctx: compilerParser.MainContext):
        children = []
        self.visited_main = True
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        return MainNode(line_nr=ctx.start.line, children=children)

    def visitFunction(self, ctx: compilerParser.FunctionContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)
        return FunctionNode(line_nr=ctx.start.line, children=children)

    def visitFunction_decl(self, ctx: compilerParser.Function_declContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)
        return FunctionDeclNode(line_nr=ctx.start.line, children=children)

    def visitFunctioncall(self, ctx: compilerParser.FunctioncallContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)
        return FunctionCallNode(line_nr=ctx.start.line, children=children)

    def visitStat(self, ctx: CParser.StatContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        return StatNode(line_nr=ctx.start.line, children=children)

    def visitPrintf(self, ctx: compilerParser.PrintfContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        return PrintfNode(line_nr=ctx.start.line, children=children)

    def visitEnum(self, ctx: compilerParser.EnumContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        return EnumNode(line_nr=ctx.start.line, children=children)

    def visitEnumentry(self, ctx: compilerParser.EnumentryContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)
        return EnumEntryNode(line_nr=ctx.start.line, children=children)

    def visitEnumstat(self, ctx: compilerParser.EnumstatContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)
        return EnumStatNode(line_nr=ctx.start.line, children=children)

    def visitExpr(self, ctx: CParser.ExprContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        # Check which expression
        if len(children) == 3:
            middle = children[1]
            if isinstance(middle, PlusNode):
                return PlusNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, MinusNode):
                return MinusNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, MultNode):
                return MultNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, DivNode):
                return DivNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, ModNode):
                return ModNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, LShiftNode):
                return LShiftNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, RShiftNode):
                return RShiftNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, AddressNode):
                return BitAndNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, BitOrNode):
                return BitOrNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, BitXorNode):
                return BitXorNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, EqualNode):
                return EqualNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, NeqNode):
                return NeqNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, LtNode):
                return LtNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, GtNode):
                return GtNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, LeqNode):
                return LeqNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, GeqNode):
                return GeqNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, AndNode):
                return AndNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
            elif isinstance(middle, OrNode):
                return OrNode(
                    line_nr=ctx.start.line, children=[children[0], children[2]]
                )
        if len(children) == 2:
            if isinstance(children[0], ReturnNode):
                return ReturnNode(line_nr=ctx.start.line, children=[children[1]])
            if isinstance(children[0], NotNode):
                return NotNode(line_nr=ctx.start.line, children=[children[1]])
            if isinstance(children[0], PlusNode):
                return children[1]
            if isinstance(children[0], MinusNode) and children[0].children == []:
                try:
                    if isinstance(children[1].children[0].children[0], IntNode):
                        return IntNode(
                            "-" + children[1].children[0].children[0].value,
                            line_nr=children[1].line_nr,
                        )
                    if isinstance(children[1].children[0].children[0], FloatNode):
                        return FloatNode(
                            "-" + children[1].children[0].children[0].value,
                            line_nr=children[1].line_nr,
                        )
                except:
                    pass
            if isinstance(children[0], BitNotNode):
                return BitNotNode(line_nr=ctx.start.line, children=[children[1]])

        return ExprNode(line_nr=ctx.start.line, children=children)

    def visitSwitch(self, ctx: compilerParser.SwitchContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)
        return SwitchNode(line_nr=ctx.start.line, children=children)

    def visitCase_stat(self, ctx: compilerParser.Case_statContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)
        return CaseNode(line_nr=ctx.start.line, children=children)

    def visitDefault_stat(self, ctx: compilerParser.Default_statContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)
        return DefaultNode(line_nr=ctx.start.line, children=children)

    def visitVariable(self, ctx: CParser.VariableContext) -> VariableNode:
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        return VariableNode(line_nr=ctx.start.line, children=children)

    def visitUnaryplusplus(self, ctx: CParser.UnaryplusplusContext) -> AssignNode:
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        value_node = None
        if isinstance(children[0], (LiteralNode, VariableNode)):
            value_node = children[0]
        elif isinstance(children[1], (LiteralNode, VariableNode)):
            value_node = children[1]

        assign_node = AssignNode(
            children=[
                value_node,
                PlusNode(
                    children=[value_node, IntNode("1", line_nr=ctx.start.line)],
                    line_nr=ctx.start.line,
                ),
            ],
            line_nr=ctx.start.line,
        )
        return assign_node

    def visitUnaryminusminus(self, ctx: CParser.UnaryminusminusContext) -> AssignNode:
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        value_node = None
        if isinstance(children[0], (LiteralNode, VariableNode)):
            value_node = children[0]
        elif isinstance(children[1], (LiteralNode, VariableNode)):
            value_node = children[1]

        assign_node = AssignNode(
            children=[
                value_node,
                MinusNode(
                    children=[value_node, IntNode("1", line_nr=ctx.start.line)],
                    line_nr=ctx.start.line,
                ),
            ],
            line_nr=ctx.start.line,
        )

        return assign_node

    def visitIf(self, ctx: CParser.IfContext) -> IfNode:
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        return IfNode(line_nr=ctx.start.line, children=children)

    def visitScope(self, ctx: CParser.ScopeContext) -> ScopeNode:
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        return ScopeNode(line_nr=ctx.start.line, children=children)

    def visitElif(self, ctx: CParser.ElifContext) -> ElseNode:
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        if_child = IfNode(children=copy.deepcopy(children), line_nr=children[0].line_nr)

        return ElseNode(line_nr=ctx.start.line, children=[if_child])

    def visitWhile(self, ctx: compilerParser.WhileContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)
        return WhileNode(line_nr=ctx.start.line, children=children)

    def visitFor(self, ctx: compilerParser.ForContext):
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        return ForNode(line_nr=ctx.start.line, children=children)

    def visitElse(self, ctx: CParser.ElseContext) -> ElseNode:
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        return ElseNode(line_nr=ctx.start.line, children=children)

    def visitNewVariable(self, ctx: CParser.NewVariableContext) -> NewVariableNode:
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        # Process children
        is_const_node = isinstance(children[0], ConstNode)
        type_node = children[0 + is_const_node]
        pointer_node = children[1 + is_const_node]
        pointer_idx = 1 + is_const_node

        if len(children) == 2 + is_const_node:
            if children[0 + is_const_node].value == "int":
                children.append(IntNode("0", line_nr=ctx.start.line))
            elif children[0 + is_const_node].value == "float":
                children.append(FloatNode("0.0", line_nr=ctx.start.line))
            elif children[0 + is_const_node].value == "char":
                children.append(CharNode("'\0'", line_nr=ctx.start.line))

        is_explicit_conversion = isinstance(children[2 + is_const_node], TypeNode)
        if self.typedefs.get(type_node.value):
            node_type = self.typedefs.get(type_node.value)
            children[0 + is_const_node] = TypeNode(node_type, line_nr=type_node.line_nr)

        # Variable is a pointer
        if isinstance(pointer_node, PointerNode):
            match type_node.value:
                case "int":
                    children[pointer_idx] = IntPointerNode(
                        pointer_node.depth, pointer_node.children, pointer_node.line_nr
                    )
                    type_node.value = "int*"
                case "float":
                    children[pointer_idx] = FloatPointerNode(
                        pointer_node.depth, pointer_node.children, pointer_node.line_nr
                    )
                    type_node.value = "float*"
                case "char":
                    children[pointer_idx] = CharPointerNode(
                        pointer_node.depth, pointer_node.children, pointer_node.line_nr
                    )
                    type_node.value = "char*"
                case "bool":
                    children[pointer_idx] = BoolPointerNode(
                        pointer_node.depth, pointer_node.children, pointer_node.line_nr
                    )
                    type_node.value = "bool*"

        # Explicit conversion
        if is_explicit_conversion:
            node_type = children[2 + is_const_node]
            children.pop(2 + is_const_node)
            children[2 + is_const_node] = ConvertNode(
                children=[node_type, children[2 + is_const_node]],
                line_nr=node_type.line_nr,
            )

        return NewVariableNode(line_nr=ctx.start.line, children=children)

    def visitPointer(self, ctx: CParser.PointerContext) -> PointerNode:
        children = []
        pointer_depth = 0
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            if isinstance(cstChild, MultNode):
                pointer_depth += 1
                continue
            children.append(cstChild)

        return PointerNode(pointer_depth, line_nr=ctx.start.line, children=children)

    def visitAddress(self, ctx: CParser.AddressContext) -> AddressNode:
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None or isinstance(cstChild, AddressNode):
                continue
            children.append(cstChild)

        return AddressNode(line_nr=ctx.start.line, children=children)

    def visitAssignment(self, ctx: CParser.AssignmentContext) -> AssignNode:
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        # check for explicit conversion
        if isinstance(children[1], TypeNode):
            type = children[1]
            children.pop(1)
            children[1] = ConvertNode(
                children=[type, children[1]], line_nr=type.line_nr
            )
        return AssignNode(line_nr=ctx.start.line, children=children)

    def visitLiteral(self, ctx: CParser.LiteralContext) -> LiteralNode:
        children = []
        for child in ctx.children:
            cstChild = self.visit(child)
            if cstChild is None:
                continue
            children.append(cstChild)

        return LiteralNode(line_nr=ctx.start.line, children=children)

    def visitBreak(self, ctx: compilerParser.BreakContext):
        return BreakNode(line_nr=ctx.start.line)

    def visitContinue(self, ctx: compilerParser.ContinueContext):
        return ContinueNode(line_nr=ctx.start.line)

    def visitTerminal(self, node: TerminalNode) -> TreeNode:
        text = node.getText()

        if text in operator_signs:
            match text:
                case "+":
                    return PlusNode(line_nr=node.symbol.line)
                case "-":
                    return MinusNode(line_nr=node.symbol.line)
                case "*":
                    return MultNode(line_nr=node.symbol.line)
                case "/":
                    return DivNode(line_nr=node.symbol.line)
                case "%":
                    return ModNode(line_nr=node.symbol.line)
                case ">>":
                    return RShiftNode(line_nr=node.symbol.line)
                case "<<":
                    return LShiftNode(line_nr=node.symbol.line)
                case "==":
                    return EqualNode(line_nr=node.symbol.line)
                case "!=":
                    return NeqNode(line_nr=node.symbol.line)
                case "<":
                    return LtNode(line_nr=node.symbol.line)
                case ">":
                    return GtNode(line_nr=node.symbol.line)
                case "<=":
                    return LeqNode(line_nr=node.symbol.line)
                case ">=":
                    return GeqNode(line_nr=node.symbol.line)
                case "&&":
                    return AndNode(line_nr=node.symbol.line)
                case "||":
                    return OrNode(line_nr=node.symbol.line)
                case "!":
                    return NotNode(line_nr=node.symbol.line)
                case "&":
                    return AddressNode(line_nr=node.symbol.line)
                case _:
                    raise Exception(f"Unknown operator: {text}")
                # TODO: Add more cases
        match node.symbol.type:
            case CParser.INT:
                return IntNode(text, line_nr=node.symbol.line)
            case CParser.POINTER:
                return PointerNode(text, line_nr=node.symbol.line)
            case CParser.FLOAT:
                return FloatNode(text, line_nr=node.symbol.line)
            case CParser.STRING:
                return StringNode(text, line_nr=node.symbol.line)
            case CParser.ID:
                if text in ("true", "false"):
                    return BoolNode(text, line_nr=node.symbol.line)
                return IdNode(text, line_nr=node.symbol.line)
            case CParser.POINTER:
                return PointerNode(text, line_nr=node.symbol.line)
            case CParser.AMPERSAND:
                return AddressNode(text, line_nr=node.symbol.line)
            case CParser.BITOR:
                return BitOrNode(text, line_nr=node.symbol.line)
            case CParser.BITXOR:
                return BitXorNode(text, line_nr=node.symbol.line)
            case CParser.BITNOT:
                return BitNotNode(text, line_nr=node.symbol.line)
            case CParser.RETURN:
                return ReturnNode(text, line_nr=node.symbol.line)
            case CParser.CONST:
                return ConstNode(line_nr=node.symbol.line)
            case CParser.CHAR:
                return CharNode(text, line_nr=node.symbol.line)
            case CParser.TYPE:
                return TypeNode(text, line_nr=node.symbol.line)
            case CParser.BOOL:
                return BoolNode(text, line_nr=node.symbol.line)
            case CParser.LINE_COMMENT:
                return CommentNode(text, line_nr=node.symbol.line)
            case CParser.COMMENT:
                return CommentNode(text, line_nr=node.symbol.line)
            case CParser.PLUSPLUS:
                return UnaryPlusNode(text, line_nr=node.symbol.line)
            case CParser.MINUSMINUS:
                return UnaryMinusNode(text, line_nr=node.symbol.line)
