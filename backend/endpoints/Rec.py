from enum import Enum

from .TreeNode import *
import sys


class OperationType(Enum):
    addition = "+"
    subtraction = "-"
    multiplication = "*"
    division = "/"
    gt = ">"
    lt = "<"
    gte = ">="
    lte = "<="
    eq = "=="
    neq = "!="
    and_op = "&&"
    ass = "="


class Operation:
    def __init__(self, a: str, type: OperationType, b: str) -> None:
        self.a = a
        self.type = type
        self.b = b

    def __str__(self) -> str:
        return f"{self.a} {self.type.value} {self.b}"

    def __repr__(self) -> str:
        return "(" + self.__str__() + ")"


class RecursiveFunction:
    def __init__(
        self,
        name: str,
        args: list,
        base_cases: list,
        recursive_calls: list[TreeNode],
        calls: list[TreeNode],
    ) -> None:
        self.function_name = name
        self.args = args
        self.recursive_calls = recursive_calls
        self.base_cases = base_cases
        self.base_case_operations = []
        self.check_base_cases()

        print("Base case operations: ", self.base_case_operations, file=sys.stderr)

        self.calls = calls
        self.function_call_values = []
        self.check_call_values()
        self.recursive_operations = []
        self.check_recursive_calls_operations()

        print("Recursive operations: ", self.recursive_operations, file=sys.stderr)

    def check_call_values(self) -> None:
        """
        Check initial values of function calls
        :return: None
        """
        for call in self.calls:
            for i in range(1, len(call.children)):
                self.function_call_values.append(
                    Operation(
                        self.args[i - 1], OperationType.ass, call.children[i].value
                    )
                )

        print("Function call values: ", self.function_call_values, file=sys.stderr)

    def check_base_cases(self) -> None:
        """
        Check the comparison operations in the base cases
        :return: None
        """
        for case in self.base_cases:
            current_operations = []
            for node in case:
                if isinstance(node, IfNode):
                    if isinstance(node.children[0], GtNode):
                        current_operations.append(
                            Operation(
                                node.children[0].children[0].value,
                                OperationType.gt,
                                node.children[0].children[1].value,
                            )
                        )
                    elif isinstance(node.children[0], LtNode):
                        current_operations.append(
                            Operation(
                                node.children[0].children[0].value,
                                OperationType.lt,
                                node.children[0].children[1].value,
                            )
                        )
                    elif isinstance(node.children[0], GeqNode):
                        current_operations.append(
                            Operation(
                                node.children[0].children[0].value,
                                OperationType.gte,
                                node.children[0].children[1].value,
                            )
                        )
                    elif isinstance(node.children[0], LeqNode):
                        current_operations.append(
                            Operation(
                                node.children[0].children[0].value,
                                OperationType.lte,
                                node.children[0].children[1].value,
                            )
                        )
                    elif isinstance(node.children[0], EqualNode):
                        current_operations.append(
                            Operation(
                                node.children[0].children[0].value,
                                OperationType.eq,
                                node.children[0].children[1].value,
                            )
                        )
                    elif isinstance(node.children[0], NeqNode):
                        current_operations.append(
                            Operation(
                                node.children[0].children[0].value,
                                OperationType.neq,
                                node.children[0].children[1].value,
                            )
                        )
            if len(current_operations) == 0:
                continue
            if len(current_operations) == 1:
                self.base_case_operations.append(current_operations[0])
            else:
                # Merge into and operations
                for i in range(1, len(current_operations)):
                    self.base_case_operations.append(
                        Operation(
                            current_operations[i - 1],
                            OperationType.and_op,
                            current_operations[i],
                        )
                    )

    def check_recursive_calls_operations(self) -> None:
        """
        Check which operations are performed on the recursive calls
        :return: None
        """
        for call in self.recursive_calls:
            match call.children[1]:
                case PlusNode():
                    self.recursive_operations.append(
                        Operation(
                            call.children[1].children[0].value,
                            OperationType.addition,
                            call.children[1].children[1].value,
                        )
                    )
                case MinusNode():
                    self.recursive_operations.append(
                        Operation(
                            call.children[1].children[0].value,
                            OperationType.subtraction,
                            call.children[1].children[1].value,
                        )
                    )
                case MultNode():
                    self.recursive_operations.append(
                        Operation(
                            call.children[1].children[0].value,
                            OperationType.multiplication,
                            call.children[1].children[1].value,
                        )
                    )
                case DivNode():
                    self.recursive_operations.append(
                        Operation(
                            call.children[1].children[0].value,
                            OperationType.division,
                            call.children[1].children[1].value,
                        )
                    )

    def _check_termination(self, arg: int) -> bool:
        """
        Find valid arguments for which the function terminates
            using the base case operations and recursive operations
        :return: list of valid arguments for which the function terminates
        """
        pass


class RecursiveCalls:
    def __init__(self, llvm_code: str, AST: TreeNode) -> None:
        self.llvm_code = llvm_code
        self.AST = AST
        self.recursive_calls = None

    def _find_nr_function_calls(self, node: TreeNode, function_name: str) -> int:
        def _find_nr_function_calls_helper(
            node: TreeNode, function_name: str, nr_calls: int
        ) -> int:
            if node.value == "FunctionCall":
                if node.children[0].value == function_name:
                    nr_calls += 1
            for child in node.children:
                nr_calls = _find_nr_function_calls_helper(
                    child, function_name, nr_calls
                )
            return nr_calls

        nr_calls = 0
        for child in node.children:
            nr_calls = _find_nr_function_calls_helper(child, function_name, nr_calls)
        return nr_calls

    def get_recursive_calls(self) -> list:
        recursive_calls = []
        for function in self.AST.children:
            if function.value == "Function":
                function_name = function.children[1].value
                nr_calls = self._find_nr_function_calls(function, function_name)
                if nr_calls > 0:
                    recursive_calls.append((function_name, nr_calls))
        self.recursive_calls = recursive_calls
        return recursive_calls

    def _check_termination_function(self, function_name: str, nr_of_calls: int) -> bool:
        assert (
            self.recursive_calls is not None
        ), "You cannot call _check_termination_function() directly"
        # Find function node
        function_node: TreeNode | None = None

        def find_function_node(node: TreeNode) -> TreeNode | None:
            if node.value == "Function" and node.children[1].value == function_name:
                return node
            for child in node.children:
                return find_function_node(child)
            return None

        for child in self.AST.children:
            function_node = find_function_node(child)
            if function_node is not None:
                break

        assert function_node is not None, "Function node not found"

        # Find if statements
        # Check for nested if statements, we should use AND there
        if_statements = []

        def find_if_statements(node: TreeNode, current_if=None) -> None:
            is_if_node: bool = False
            if isinstance(node, IfNode):
                is_if_node = True
                if current_if is not None:
                    last_if = if_statements[-1]
                    if_statements.remove(last_if)
                    if_statements.append((*last_if, node))
                    current_if = node
                else:
                    if_statements.append((node,))
                    current_if = node
            if not is_if_node:
                for child in node.children:
                    find_if_statements(child, current_if)
            else:
                for child in node.children[-1].children:
                    find_if_statements(child, current_if)
            return

        for child in function_node.children[-1].children:
            find_if_statements(child)

        print("If statements: ", if_statements, file=sys.stderr)

        # find base cases
        base_cases = []
        for if_statement in if_statements:
            if_stat = if_statement[-1]

            def is_base_case(node: TreeNode) -> bool:
                if isinstance(node, ReturnNode):
                    if isinstance(node.children[0], FunctionCallNode):
                        if node.children[0].children[0].value != function_name:
                            return True
                    else:
                        return True

                for child in node.children:
                    if is_base_case(child):
                        return True

            for child in if_stat.children[-1].children:
                if is_base_case(child):
                    base_cases.append(if_statement)
                    break

        print("Base cases: ", base_cases, file=sys.stderr)

        # Find recursive calls
        recursive_calls = []

        def find_rec_calls(node: TreeNode) -> None:
            if isinstance(node, FunctionCallNode):
                if node.children[0].value == function_name:
                    recursive_calls.append(node)

            for child in node.children:
                find_rec_calls(child)

        for child in function_node.children[-1].children:
            find_rec_calls(child)

        # Find function calls
        function_calls = []

        def find_calls(node: TreeNode) -> None:
            if isinstance(node, FunctionNode):
                if node.children[1].value == function_name:
                    return  # Skip function calls inside of the current function
            if isinstance(node, FunctionCallNode):
                if node.children[0].value == function_name:
                    function_calls.append(node)
            for child in node.children:
                find_calls(child)

        for child in self.AST.children:
            find_calls(child)

        print("Recursive calls: ", recursive_calls, file=sys.stderr)

        print("Function calls: ", function_calls, file=sys.stderr)

        args = []
        for arg in function_node.children[2:-1]:
            if isinstance(arg, IdNode):
                args.append(arg.value)

        rec_func = RecursiveFunction(
            function_name, args, base_cases, recursive_calls, function_calls
        )

    def check_termination(self) -> bool:
        assert (
            self.recursive_calls is not None
        ), "You must call get_recursive_calls() before calling check_termination()"

        for function in self.recursive_calls:
            terminates = self._check_termination_function(function[0], function[1])
