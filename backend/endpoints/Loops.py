import copy
import sys

from .TreeNode import *


class LoopAnalyzer:
    def __init__(self, ast) -> None:
        self.ast = ast
        self.loop_infinity: dict = {}
        self.loop_max_iterations: dict = {}

    def analyze(self, node: TreeNode):
        for child in node.children:
            # Ignore non-while nodes
            if not isinstance(child, WhileNode):
                result = self.analyze(child)
                if result is not None:
                    return result

            else:
                # Get all variables in the condition
                condition_variables = []

                if isinstance(child.children[0], IntNode) and bool(
                        int(child.children[0].value) >= 1
                ):
                    self.loop_infinity[id(child)] = True
                    self.loop_max_iterations[id(child)] = float("inf")
                    return

                def find_condition_variables(node: TreeNode) -> None:
                    if isinstance(node, IdNode):
                        condition_variables.append(node.value)
                    for c in node.children:
                        find_condition_variables(c)

                condition = child.children[0]
                loop_inside = child.children[1]
                find_condition_variables(condition)

                # Check if any of the variables in the condition are changed in the loop
                def find_variable_in_loop(node: TreeNode) -> bool:
                    if isinstance(node, AssignNode):
                        if node.children[0].value in condition_variables:
                            return True
                    for c in node.children:
                        if find_variable_in_loop(c):
                            return True
                    return False

                condition_changes = find_variable_in_loop(loop_inside)

                # At least one of the condition variables changes in the loop
                if condition_changes:
                    # Find all original values of the variables in the condition
                    def find_condition_variable_value(
                            variable: str,
                            m: TreeNode
                    ) -> TreeNode | None:
                        if isinstance(m, NewVariableNode):
                            if m.children[1].value == variable:
                                return m.children[-1].value
                        for c in m.children:
                            temp = find_condition_variable_value(variable, c)
                            if temp is not None:
                                return temp
                        return None

                    condition_variables_values = {}
                    for var in condition_variables:
                        condition_variables_values[var] = find_condition_variable_value(
                            var,
                            self.ast
                        )

                    # Determine the terminal values of the condition variables
                    terminal_values = {}
                    variable_conditions = {}
                    for var in condition_variables:
                        def find_comparisons(n: TreeNode):
                            if isinstance(
                                    n, (LtNode, LeqNode, GtNode, GeqNode, NeqNode)
                            ):
                                if (
                                        n.children[0].value == var
                                        or n.children[1].value == var
                                ):
                                    return n
                            for child in n.children:
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
                        variable_conditions[var] = comparison

                    # Determine if the condition goes up or down
                    variable_terminates = {}
                    for var in condition_variables:

                        def find_condition_direction(n: TreeNode):
                            if isinstance(n, PlusNode) and (
                                    n.children[0].value == var
                                    or n.children[1].value == var
                            ):
                                return True
                            if isinstance(n, MinusNode) and (
                                    n.children[0].value == var
                                    or n.children[1].value == var
                            ):
                                return False
                            for c in n.children:
                                res = find_condition_direction(c)
                                if res is not None:
                                    return res
                            return None

                        goes_up = find_condition_direction(loop_inside)
                        if goes_up is None:
                            variable_terminates[var] = False
                            continue

                        if (
                                terminal_values[var] >= int(condition_variables_values[var])
                                and goes_up
                        ):
                            variable_terminates[var] = True
                        elif (
                                terminal_values[var] <= int(condition_variables_values[var])
                                and not goes_up
                        ):
                            variable_terminates[var] = True
                        elif (
                            terminal_values[var] >= int(condition_variables_values[var]) and not goes_up and isinstance(variable_conditions[var], LtNode)
                        ):
                            variable_terminates[var] = True
                        elif (
                            terminal_values[var] <= int(condition_variables_values[var]) and goes_up and isinstance(variable_conditions[var], GtNode)
                        ):
                            variable_terminates[var] = False
                        elif (
                            terminal_values[var] <= int(condition_variables_values[var]) and isinstance(variable_conditions[var], (LtNode, LeqNode))
                        ):
                            variable_terminates[var] = True
                        else:
                            variable_terminates[var] = False

                    # Determine iterations
                    iterations = float("inf")
                    for var in condition_variables:
                        temp = abs(terminal_values[var] - int(condition_variables_values[var]))
                        if temp < iterations:
                            iterations = temp

                    if isinstance(condition, AndNode):
                        for i in variable_terminates.values():
                            if i is False:
                                self.loop_max_iterations[id(child)] = iterations
                    elif isinstance(condition, OrNode):
                        if all(variable_terminates.values()):
                            self.loop_infinity[id(child)] = False
                            self.loop_max_iterations[id(child)] = iterations
                    else:
                        if all(list(variable_terminates.values())):
                            self.loop_infinity[id(child)] = False
                            self.loop_max_iterations[id(child)] = iterations
                        else:
                            self.loop_infinity[id(child)] = True
                            self.loop_max_iterations[id(child)] = float("inf")

                else:
                    evaluation = self._evaluate_condition(condition)
                    self.loop_infinity[id(child)] = evaluation
                    if evaluation:
                        self.loop_max_iterations[id(child)] = float("inf")
                    else:
                        self.loop_max_iterations[id(child)] = 0

    def _evaluate_condition(self, condition: TreeNode) -> bool:
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

            find_variable_value(self.ast)

            # Replace all id's in the condition with their values
            for i, child in enumerate(condition.children):
                if isinstance(child, IdNode) and child.value in condition_var_values:
                    condition.children[i] = copy.copy(condition_var_values[child.value])

            match condition:
                case PlusNode():
                    return bool(
                        int(condition.children[0].value)
                        + int(condition.children[1].value)
                    )
                case MinusNode():
                    return bool(
                        int(condition.children[0].value)
                        - int(condition.children[1].value)
                    )
                case MultNode():
                    return bool(
                        int(condition.children[0].value)
                        * int(condition.children[1].value)
                    )
                case DivNode():
                    return bool(
                        int(condition.children[0].value)
                        / int(condition.children[1].value)
                    )
                case ModNode():
                    return bool(
                        int(condition.children[0].value)
                        % int(condition.children[1].value)
                    )
                case GtNode():
                    return bool(
                        int(condition.children[0].value)
                        > int(condition.children[1].value)
                    )
                case LtNode():
                    return bool(
                        int(condition.children[0].value)
                        < int(condition.children[1].value)
                    )
                case GeqNode():
                    return bool(
                        int(condition.children[0].value)
                        >= int(condition.children[1].value)
                    )
                case LeqNode():
                    return bool(
                        int(condition.children[0].value)
                        <= int(condition.children[1].value)
                    )
                case EqualNode():
                    return bool(
                        int(condition.children[0].value)
                        == int(condition.children[1].value)
                    )
                case NeqNode():
                    return bool(
                        int(condition.children[0].value)
                        != int(condition.children[1].value)
                    )
                case IntNode():
                    return bool(
                        int(condition.children[0].value) >= 1
                    )
