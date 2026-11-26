from typing import Annotated

from pydantic import BaseModel, ConfigDict, FiniteFloat, StringConstraints

class AddOperation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    piece: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    operation: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    minutes: int


class WitnessStone(BaseModel):
    model_config = ConfigDict(extra="forbid")
    task: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    seal: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
