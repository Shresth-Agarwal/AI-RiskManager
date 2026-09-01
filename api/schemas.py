from pydantic import BaseModel, Field


class RiskRequest(BaseModel):
    description: str = Field(
        ...,
        min_length=10,
        description="Natural-language description of the transaction dispute",
    )