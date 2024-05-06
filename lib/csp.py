from collections.abc import Callable


class InvalidValueError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Variable:
    def __init__(self, domain: set = None) -> None:
        if domain is None:
            domain = set()

        self.domain = domain
        self._value: any = None

    @property
    def value(self) -> any:
        return self._value

    @value.setter
    def value(self, new_value) -> None:
        if (new_value is not None) and (new_value not in self.domain):
            raise InvalidValueError(f"{new_value} is not in the domain.")

        self._value = new_value


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

    def __call__(self) -> bool:
        for variable in self.variables:
            if variable.value is None:
                return True

        return self._constraint_func(*[variable.value for variable in self.variables])

class CSP:
    def __init__(self):
        self._variables: set[Variable] = set()
        self._constraints: set[Constraint] = set()
        self._variable_constraints: dict[Variable, set[Constraint]] = {}
        self._unassigned_variables: set[Variable] = set()

    def add_variable(self, variable: Variable) -> None:
        self._variables.add(variable)
        self._unassigned_variables.add(variable)
        self._variable_constraints[variable] = set()

    def add_constraint(self, constraint: Constraint) -> None:
        self._constraints.add(constraint)

        for variable in constraint.variables:
            self._variable_constraints[variable].add(constraint)

    def assign(self, variable: Variable, value: any) -> None:
        """
        Tries to assign a value to a variable.
        If the assignment is inconsistent, an exception of type InvalidValueError is raised.
        """

        last_value = variable.value

        try:
            variable.value = value

            for constraint in self._variable_constraints[variable]:
                if not constraint():
                    raise InvalidValueError(f"Violation of constraint")

            if value is None:
                self._unassigned_variables.add(variable)
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

        return next(iter(self._unassigned_variables))

    def is_solved(self) -> bool:
        return len(self._unassigned_variables) == 0
