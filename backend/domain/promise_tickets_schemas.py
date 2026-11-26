from typing import Annotated

from pydantic import BaseModel, ConfigDict, FiniteFloat, StringConstraints

class IssueTicket(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    estimate: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    bench: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    start_day: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]


class ReviseTicket(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    estimate: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    bench: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    start_day: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    previous: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    reason: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
