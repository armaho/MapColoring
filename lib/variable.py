import copy

from lib.error import InvalidValueError


class Variable:
    number_of_created_instances: int = 0

    def __init__(self, domain: set) -> None:
        self.domain = domain
        self.original_domain = copy.deepcopy(self.domain)  # do not change
        self._value: any = None
        self.__id = Variable.number_of_created_instances

        Variable.number_of_created_instances += 1

    def __hash__(self) -> int:
        return hash(self.__id)

    def __eq__(self, other) -> bool:
        return self.__hash__() == other.__hash__()

    @property
    def value(self) -> any:
        return self._value

    @value.setter
    def value(self, new_value) -> None:
        if (new_value is not None) and (new_value not in self.domain):
            raise InvalidValueError(f"{new_value} is not in the domain.")

        self._value = new_value
