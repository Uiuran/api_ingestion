import warnings

# %%


class DateDataIngestionNotFoundException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__()

    def __str__(self):
        return self.message


class StartDateNotProvidedException(Exception):
    def __init__(self, message) -> None:
        super().__init__()
        self.message = message

    def __str__(self) -> str:
        return self.message


# %%


class WarningWrongDataTypeNotWritable(Warning):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    def warns(self, message: str) -> None:
        warnings.warn(message=message)


class WarningDateProvidedLowerThanCheckpoint(Warning):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    def warns(self, message: str) -> None:
        warnings.warn(message=message)
