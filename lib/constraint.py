from collections.abc import Callable

from lib.variable import Variable


class Constraint:
    def __init__(self, variables: list[Variable], constraint_func: Callable[..., bool]) -> None:
        """
        Initializes a constraint

        :param variables: a list on variables involved in the constraint
        :param constraint_func: a Callable that will be called with the value of variables if they all have a value,
        the number of parameters should be equal to the number of variables in the constraint
        """

        self.variables = variables
        self._constraint_func = constraint_func

    def check(self) -> bool:
        for variable in self.variables:
            if variable.value is None:
                return True

        return self._constraint_func(*[variable.value for variable in self.variables])

class BinaryConstraint(Constraint):
    def __init__(self, variables: list[Variable], constraint_func: Callable[[any, any], bool]) -> None:
        if len(variables) != 2:
            raise ValueError("A binary constraint should have exactly two variables.")

        super().__init__(variables, constraint_func)

    def revise(self, variable: Variable) -> bool:
        """
        Returns True if the variable domain is revised.
        """

        discarded_values = []

        other_variable = self.variables[0]
        if other_variable == variable:
            other_variable = self.variables[1]

        for first_variable_value in variable.domain:
            value_is_consistent = False

            for second_variable_value in other_variable.domain:
                if self._constraint_func(first_variable_value, second_variable_value):
                    value_is_consistent = True
                    break

            if not value_is_consistent:
                discarded_values.append(first_variable_value)

        for value in discarded_values:
            variable.domain.discard(value)

        return len(discarded_values) > 0
