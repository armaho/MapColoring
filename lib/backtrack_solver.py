import copy

from lib.csp import CSP, Variable, InvalidValueError


class InconsistentCspError(Exception):
    def __init__(self):
        super().__init__("Inconsistent CSP")


class BacktrackSolver:
    def __init__(self, csp: CSP):
        self.csp = copy.deepcopy(csp)  # this property should not be changed after assignment

    def solve(self) -> None:
        if not self._backtrack_solving(self.csp.get_unassigned_variable()):
            raise InconsistentCspError()

    def _backtrack_solving(self, variable: Variable) -> bool:
        for possible_value in variable.domain:
            try:
                self.csp.assign(variable, possible_value)
            except InvalidValueError:
                continue

            next_variable = self.csp.get_unassigned_variable()

            if (next_variable is None) or self._backtrack_solving(next_variable):
                return True

        self.csp.assign(variable, None)
        return False
