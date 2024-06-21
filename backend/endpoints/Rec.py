from .TreeNode import *
import sys
class RecursiveCalls:
    def __init__(self, llvm_code: str, AST: TreeNode) -> None:
        self.llvm_code = llvm_code
        self.AST = AST
        self.recursive_calls = None

    def _find_nr_function_calls(self, node: TreeNode, function_name: str) -> int:
        def _find_nr_function_calls_helper(node: TreeNode, function_name: str, nr_calls: int) -> int:
            if node.value == "FunctionCall":
                if node.children[0].value == function_name:
                    nr_calls += 1
            for child in node.children:
                nr_calls = _find_nr_function_calls_helper(child, function_name, nr_calls)
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
        assert self.recursive_calls is not None, "You cannot call _check_termination_function() directly"
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
        if_statements = []
        def find_if_statements(node: TreeNode, current_if = None) -> None:
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




    def check_termination(self) -> bool:
        assert self.recursive_calls is not None, "You must call get_recursive_calls() before calling check_termination()"

        for function in self.recursive_calls:
            terminates = self._check_termination_function(function[0], function[1])

