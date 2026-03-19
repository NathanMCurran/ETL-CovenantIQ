from pydantic import BaseModel


class TransformRecord(BaseModel):
    account: str
    last_day_of_month: str
    amount: float


class TransformError(BaseModel):
    level: str  # "basic" | "intermediate" | "detail"
    message: str
    row_number: int | None = None
    detail: str | None = None


class TransformResult(BaseModel):
    success: bool
    records: list[TransformRecord] = []
    errors: list[TransformError] = []


class TransformJobSummary(BaseModel):
    id: str
    name: str
    created_at: str


class TransformJobDetail(BaseModel):
    id: str
    name: str
    created_at: str
    records: list[TransformRecord]
