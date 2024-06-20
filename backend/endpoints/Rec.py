from .TreeNode import *
import sys
class RecursiveCalls:
    def __init__(self, llvm_code: str, AST: TreeNode) -> None:
        self.llvm_code = llvm_code
        self.AST = AST

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
        return recursive_calls