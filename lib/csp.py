from collections import deque
from collections.abc import Callable

from sortedcontainers import SortedSet

from lib.constraint import Constraint, BinaryConstraint
from lib.error import InvalidValueError, InvalidConstraintError
from lib.variable import Variable


class Csp:
    def __init__(self, use_degree_heuristic=False):
        self._variables: set[Variable] = set()
        self._constraints: set[Constraint] = set()
        self._variable_constraints: dict[Variable, set[Constraint]] = {}
        self._unassigned_variables: set[Variable] = set()
        self._use_degree_heuristic = use_degree_heuristic

        if use_degree_heuristic:
            self._variables_sorted_by_degree_heuristic: list[Variable] = []
            self._degree_heuristic_idx = 0

    @property
    def assignments_number(self):
        return len(self._variables) - len(self._unassigned_variables)

    def add_variable(self, variable: Variable) -> None:
        self._variables.add(variable)
        self._unassigned_variables.add(variable)
        self._variable_constraints[variable] = set()

        if self._use_degree_heuristic:
            self._variables_sorted_by_degree_heuristic.append(variable)

    def add_constraint(self, constraint: Constraint) -> None:
        self._constraints.add(constraint)
        for variable in constraint.variables:
            self._variable_constraints[variable].add(constraint)

    def adding_completed(self) -> None:
        if (self._use_degree_heuristic):
            self._variables_sorted_by_degree_heuristic = sorted(self._variables_sorted_by_degree_heuristic, reverse=True
                                                                , key=lambda v: len(self._variable_constraints[v]))

    def assign(self, variable: Variable, value: any) -> None:
        """
        Tries to assign a value to a variable.
        If the assignment is inconsistent, an exception of type InvalidValueError is raised.
        """

        last_value = variable.value

        try:
            variable.value = value

            for constraint in self._variable_constraints[variable]:
                if not constraint.check():
                    raise InvalidValueError(f"Violation of constraint")

            if value is None:
                self._unassigned_variables.add(variable)

                if self._use_degree_heuristic:
                    self._degree_heuristic_idx -= 1
            else:
                self._unassigned_variables.discard(variable)
        except InvalidValueError as ive:
            variable.value = last_value
            raise ive

    def get_unassigned_variable(self) -> Variable | None:
        """
        Returns an unassigned variable
        """

        if (len(self._unassigned_variables) == 0):
            return None

        if not self._use_degree_heuristic:
            return next(iter(self._unassigned_variables))

        if self._degree_heuristic_idx == len(self._variables_sorted_by_degree_heuristic):
            return None

        variable = self._variables_sorted_by_degree_heuristic[self._degree_heuristic_idx]
        self._degree_heuristic_idx += 1
        return variable

    def is_solved(self) -> bool:
        return len(self._unassigned_variables) == 0

    def get_variable_used_in_csp(self, original_variable: Variable) -> Variable | None:
        for variable in self._variables:
            if variable == original_variable:
                return variable

        return None


class BinaryCsp(Csp):
    def __init__(self, use_mrv=False, use_lcv=False, use_degree_heuristic=False) -> None:
        super().__init__(use_degree_heuristic)

        self._constraints: set[BinaryConstraint] = set()
        self._variable_constraints: dict[Variable, set[BinaryConstraint]] = {}
        self._use_mrv = use_mrv
        self._use_lcv = use_lcv

        if use_mrv:
            self._unassigned_variables_sorted_by_mrv: SortedSet[Variable] = SortedSet(key=lambda v: len(v.domain))
            self._removed_values: dict[Variable, dict[Variable, set[any]]] = dict()

    def add_variable(self, variable: Variable) -> None:
        super().add_variable(variable)

        if self._use_mrv:
            self._unassigned_variables_sorted_by_mrv.add(variable)

    def add_constraint(self, constraint: BinaryConstraint) -> None:
        super().add_constraint(constraint)

    def adding_completed(self) -> None:
        super().adding_completed()

        if self._use_mrv:
            for variable in self._variables:
                self._removed_values[variable] = dict()

                for constraint in self._variable_constraints[variable]:
                    other_variable = constraint.get_other_variable(variable)
                    self._removed_values[variable][other_variable] = set()

    def get_unassigned_variable(self) -> Variable | None:
        if not self._use_mrv:
            return super().get_unassigned_variable()

        if len(self._unassigned_variables_sorted_by_mrv) == 0:
            return None

        return next(iter(self._unassigned_variables_sorted_by_mrv))

    def get_values_for_variable(self, variable: Variable) -> list | set:
        """
        Returns a list of values assignable to the given variable
        """

        def value_key(value: any) -> int:
            removed_values_cnt = 0

            for constraint in self._variable_constraints[variable]:
                other_variable = constraint.get_other_variable(variable)

                if other_variable not in self._unassigned_variables:
                    continue

                for other_value in other_variable.domain:
                    if not constraint.check(overriding_values={variable: value, other_variable: other_value}):
                        removed_values_cnt += 1

            return removed_values_cnt

        if not self._use_lcv:
            return variable.domain

        return sorted(list(variable.domain), key=value_key)

    def assign(self, variable: Variable, value: any) -> None:
        super().assign(variable, value)

        if self._use_mrv:
            if value is not None:
                self._unassigned_variables_sorted_by_mrv.discard(variable)
            else:
                self._unassigned_variables_sorted_by_mrv.add(variable)

            for constraint in self._variable_constraints[variable]:
                other_variable = constraint.get_other_variable(variable)

                if (other_variable in self._unassigned_variables_sorted_by_mrv):
                    self._unassigned_variables_sorted_by_mrv.discard(other_variable)

                    for value in self._removed_values[variable][other_variable]:
                        other_variable.domain.add(value)

                    self._removed_values[variable][other_variable] = set()

                    removed_values = []

                    for value in other_variable.domain:
                        if not constraint.check(overriding_values={other_variable: value}):
                            removed_values.append(value)
                            self._removed_values[variable][other_variable].add(value)

                    for value in removed_values:
                        other_variable.domain.discard(value)

                    self._unassigned_variables_sorted_by_mrv.add(other_variable)

    def apply_ac3(self) -> None:
        """
        Applies the AC3 algorithm to the CSP.
        """

        constraint_queue: deque[tuple[Variable, BinaryConstraint]] = deque()

        for constraint in self._constraints:
            constraint_queue.append((constraint.variables[0], constraint))
            constraint_queue.append((constraint.variables[1], constraint))

        while len(constraint_queue) > 0:
            variable, constraint = constraint_queue.popleft()

            if constraint.revise(variable):
                for other_constraint in self._variable_constraints[variable]:
                    other_variable = other_constraint.variables[0]
                    if other_variable == variable:
                        other_variable = other_constraint.variables[1]

                    constraint_queue.append((other_variable, other_constraint))
