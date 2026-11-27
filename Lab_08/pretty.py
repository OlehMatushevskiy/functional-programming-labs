from model import Failure, Result, Success


def render(result: Result[object]) -> str:
    match result:
        case Success(value=value):
            return f"Success({value!r})"
        case Failure(message=message, code=code):
            return f"Failure[{code}]: {message}"
