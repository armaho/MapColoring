from lib.error import InvalidValueError


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
