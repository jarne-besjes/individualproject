class TreeNode:
    def __init__(self, value: str, line_nr: int = -1, children=None) -> None:
        self.value = value
        self.children = children if children is not None else []
        self.line_nr = line_nr


class ProgNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("Prog", children=children, line_nr=line_nr)


class ConvertNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1):
        super().__init__("Convert", children=children, line_nr=line_nr)


class EqualNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1):
        super().__init__("Equal", children=children, line_nr=line_nr)


class ReturnNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1):
        super().__init__("Return", children=children, line_nr=line_nr)


class MainNode(TreeNode):
    def __init__(self, children=None, line_nr: int = None):
        super().__init__("Main", children=children, line_nr=line_nr)


class MainNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("Main", children=children, line_nr=line_nr)


class StatNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("Stat", children=children, line_nr=line_nr)


class ExprNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("Expr", children=children, line_nr=line_nr)


class LiteralNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("Literal", children=children, line_nr=line_nr)


class VariableNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("Var", children=children, line_nr=line_nr)


class AssignNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("Assignment", children=children, line_nr=line_nr)
        self.converted = False


class NewVariableNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("NewVar", children=children, line_nr=line_nr)


class PlusNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("+", children=children, line_nr=line_nr)


class UnaryPlusNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("UnaryPlus", children=children, line_nr=line_nr)


class GtNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__(">", children=children, line_nr=line_nr)


class NeqNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("!=", children=children, line_nr=line_nr)


class LtNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("<", children=children, line_nr=line_nr)


class EqNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("=", children=children, line_nr=line_nr)


class GeqNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__(">=", children=children, line_nr=line_nr)


class LeqNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("<=", children=children, line_nr=line_nr)


class AndNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("&&", children=children, line_nr=line_nr)


class OrNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("||", children=children, line_nr=line_nr)


class ModNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("%", children=children, line_nr=line_nr)


class LShiftNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("<<", children=children, line_nr=line_nr)


class NotNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1):
        super().__init__("!", children=children, line_nr=line_nr)


class RShiftNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__(">>", children=children, line_nr=line_nr)


class BitAndNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("&", children=children, line_nr=line_nr)


class BitOrNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("|", children=children, line_nr=line_nr)


class BitXorNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("^", children=children, line_nr=line_nr)


class BitNotNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("~", children=children, line_nr=line_nr)


class MinusNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("-", children=children, line_nr=line_nr)


class UnaryMinusNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("UnaryMinus", children=children, line_nr=line_nr)


class MultNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("*", children=children, line_nr=line_nr)


class DivNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("/", children=children, line_nr=line_nr)


class IntNode(TreeNode):
    def __init__(self, value: str, children=None, line_nr: int = -1) -> None:
        super().__init__(value, children=children, line_nr=line_nr)


class FloatNode(TreeNode):
    def __init__(self, value: str, children=None, line_nr: int = -1) -> None:
        super().__init__(value, children=children, line_nr=line_nr)


class StringNode(TreeNode):
    def __init__(self, value: str, children=None, line_nr: int = -1) -> None:
        super().__init__(value, children=children, line_nr=line_nr)


class CommentNode(TreeNode):
    def __init__(self, value: str, children=None, line_nr: int = -1) -> None:
        super().__init__(value, children=children, line_nr=line_nr)


class IdNode(TreeNode):
    def __init__(self, value: str, children=None, line_nr: int = -1) -> None:
        super().__init__(value, children=children, line_nr=line_nr)


class AddressNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("Address", children=children, line_nr=line_nr)


class ConstNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("Const", children=children, line_nr=line_nr)


class PrintfNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("Printf", children=children, line_nr=line_nr)


class CharNode(TreeNode):
    def __init__(self, value: str, children=None, line_nr: int = -1) -> None:
        super().__init__(value, children=children, line_nr=line_nr)


class TypeNode(TreeNode):
    def __init__(self, value: str, children=None, line_nr: int = -1) -> None:
        super().__init__(value, children=children, line_nr=line_nr)


class BoolNode(TreeNode):
    def __init__(self, value: str, children=None, line_nr: int = -1) -> None:
        super().__init__(value, children=children, line_nr=line_nr)


class PointerNode(TreeNode):
    def __init__(self, depth: int, children=None, line_nr: int = -1) -> None:
        self.depth = depth
        super().__init__("Int pointer", children=children, line_nr=line_nr)


class IntPointerNode(TreeNode):
    def __init__(self, depth: int, children=None, line_nr: int = -1) -> None:
        self.depth = depth
        super().__init__("Int pointer", children=children, line_nr=line_nr)


class FloatPointerNode(TreeNode):
    def __init__(self, depth: int, children=None, line_nr: int = -1) -> None:
        self.depth = depth
        super().__init__("Float pointer", children=children, line_nr=line_nr)


class CharPointerNode(TreeNode):
    def __init__(self, depth: int, children=None, line_nr: int = -1) -> None:
        self.depth = depth
        super().__init__("Char pointer", children=children, line_nr=line_nr)


class BoolPointerNode(TreeNode):
    def __init__(self, depth: int, children=None, line_nr: int = -1) -> None:
        self.depth = depth
        super().__init__("Bool pointer", children=children, line_nr=line_nr)


class IfNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("If", children=children, line_nr=line_nr)


class ElifNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("Elif", children=children, line_nr=line_nr)


class ElseNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("Else", children=children, line_nr=line_nr)


class WhileNode(TreeNode):
    def __init__(
        self, children=None, line_nr: int = -1, origins_from_for: bool = False
    ) -> None:
        self.origins_from_for = origins_from_for
        super().__init__("While", children=children, line_nr=line_nr)


class ForNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("For", children=children, line_nr=line_nr)


class BreakNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("Break", children=children, line_nr=line_nr)


class ContinueNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("Continue", children=children, line_nr=line_nr)


class ScopeNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("Scope", children=children, line_nr=line_nr)


class SwitchNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("Switch", children=children, line_nr=line_nr)


class CaseNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("Case", children=children, line_nr=line_nr)


class DefaultNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("Default", children=children, line_nr=line_nr)


class EnumNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("Enum", children=children, line_nr=line_nr)


class EnumEntryNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("EnumEntry", children=children, line_nr=line_nr)


class EnumStatNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("EnumStat", children=children, line_nr=line_nr)


class FunctionNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("Function", children=children, line_nr=line_nr)


class FunctionDeclNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("FunctionDecl", children=children, line_nr=line_nr)


class FunctionCallNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("FunctionCall", children=children, line_nr=line_nr)


class DefineNode(TreeNode):
    def __init__(self, children=None, line_nr: int = -1) -> None:
        super().__init__("Define", children=children, line_nr=line_nr)


class IncludeNode(TreeNode):
    def __init__(self, children=None, line_nr=-1) -> None:
        super().__init__("Include", children=children, line_nr=line_nr)


class ArrayDeclarationNode(TreeNode):
    def __init__(self, children=None, line_nr=-1) -> None:
        super().__init__("ArrayDeclaration", children=children, line_nr=line_nr)


class ArrayDeclAssignNode(TreeNode):
    def __init__(self, children=None, line_nr=-1) -> None:
        super().__init__("ArrayDeclAssign", children=children, line_nr=line_nr)


class ArrayDeclElementsNode(TreeNode):
    def __init__(self, children=None, line_nr=-1) -> None:
        super().__init__("ArrayDeclElements", children=children, line_nr=line_nr)


class ArrayAccessNode(TreeNode):
    def __init__(self, children=None, line_nr=-1) -> None:
        super().__init__("ArrayAccess", children=children, line_nr=line_nr)


class ArrayAssignNode(TreeNode):
    def __init__(self, children=None, line_nr=-1) -> None:
        super().__init__("ArrayAssign", children=children, line_nr=-line_nr)


class ScanfNode(TreeNode):
    def __init__(self, children=None, line_nr=-1) -> None:
        super().__init__("Scanf", children=children, line_nr=line_nr)


class StructNode(TreeNode):
    def __init__(self, children=None, line_nr=-1) -> None:
        super().__init__("Struct", children=children, line_nr=line_nr)


class StructEntryNode(TreeNode):
    def __init__(self, children=None, line_nr=-1) -> None:
        super().__init__("StructEntry", children=children, line_nr=line_nr)


class StructDeclNode(TreeNode):
    def __init__(self, children=None, line_nr=-1) -> None:
        super().__init__("StructDecl", children=children, line_nr=line_nr)


class StructAccessNode(TreeNode):
    def __init__(self, children=None, line_nr=-1) -> None:
        super().__init__("StructAccess", children=children, line_nr=line_nr)
