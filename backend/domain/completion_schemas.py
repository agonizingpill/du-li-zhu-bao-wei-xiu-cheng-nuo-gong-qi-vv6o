from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator

class RecordCompletion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)] | None = None
    piece: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    ticket: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)] | None = None
    completed_day: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]

    @field_validator('code', 'ticket', mode='before')
    @classmethod
    def blank_is_absent(cls, value):
        # 表单里的空字符串按“未填写”处理：编号自动生成，承诺票取最后一张。
        if isinstance(value, str) and not value.strip():
            return None
        return value
