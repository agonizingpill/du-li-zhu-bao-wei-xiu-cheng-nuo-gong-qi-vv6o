from typing import Annotated

from pydantic import BaseModel, ConfigDict, FiniteFloat, StringConstraints

class Receive(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    description: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    mass_g: FiniteFloat
    stone_count: int
    seal: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    arrived: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
