import copy
from abc import ABC, abstractmethod

from lib.csp import BinaryCsp, Variable, InvalidValueError, Csp


class InconsistentCspError(Exception):
    def __init__(self):
        super().__init__("Inconsistent CSP")


class CspSolver(ABC):
    @abstractmethod
    def solve(self) -> None:
        pass


class BacktrackCspSolver(CspSolver):
    def __init__(self, csp: Csp):
        self.csp = copy.deepcopy(csp)  # this property should not be changed after assignment
        self._failure_depth_sum = 0
        self._failure_number = 0

    @property
    def average_failure_depth(self) -> float:
        return self._failure_depth_sum / self._failure_number

    def solve(self) -> None:
        initial_variable = self.csp.get_unassigned_variable()

        if initial_variable is None:
            return

        if not self._backtrack_solving(self.csp.get_unassigned_variable()):
            raise InconsistentCspError()

    def _backtrack_solving(self, variable: Variable, depth: int = 0) -> bool:
        for possible_value in variable.domain:
            try:
                self.csp.assign(variable, possible_value)
            except InvalidValueError:
                continue

            next_variable = self.csp.get_unassigned_variable()

            if (next_variable is None) or self._backtrack_solving(next_variable, depth + 1):
                return True

        self._failure_depth_sum += depth
        self._failure_number += 1

        self.csp.assign(variable, None)

        return False

class BacktrackBinaryCspSolver(CspSolver):
    def __init__(self, binary_csp: BinaryCsp, use_ac3=False) -> None:
        self.csp = copy.deepcopy(binary_csp)
        self._use_ac3 = use_ac3
        self._failure_depth_sum = 0
        self._failure_number = 0

    @property
    def average_failure_depth(self) -> float:
        return self._failure_depth_sum / self._failure_number if self._failure_number != 0 else 0

    @property
    def number_of_failures(self) -> int:
        return self._failure_number

    def solve(self) -> None:
        if self._use_ac3:
            self.csp.apply_ac3()

        initial_variable = self.csp.get_unassigned_variable()

        if initial_variable is None:
            return

        if not self._backtrack_solving(initial_variable):
            raise InconsistentCspError()

    def _backtrack_solving(self, variable: Variable, depth: int = 0) -> bool:
        for possible_value in self.csp.get_values_for_variable(variable):
            try:
                self.csp.assign(variable, possible_value)
            except InvalidValueError:
                continue

            next_variable = self.csp.get_unassigned_variable()

            if (next_variable is None) or self._backtrack_solving(next_variable, depth + 1):
                return True

        self._failure_depth_sum += depth
        self._failure_number += 1

        self.csp.assign(variable, None)
        return False
