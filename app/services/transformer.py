"""Core ETL transform logic for Transform1 (v1 xlsx) and Transform2 (v2 xlsx)."""
import calendar
import re
from abc import ABC
from datetime import datetime

import numpy as np
import pandas as pd

from app.models.transform_job import TransformError, TransformRecord, TransformResult
from app.services.file import File


class BaseTransformer(ABC):

    ACCOUNT_RE = re.compile(r"^\d+[\s\-]")

    def _is_account(self, account_name: object) -> bool:
        if not isinstance(account_name, str):
            return False
        return bool(self.ACCOUNT_RE.match(account_name.strip()))

    def _find_date_row(self, df: pd.DataFrame) -> tuple[int, list[tuple[int, str]]] | None:
        for i in range(min(5, len(df))):
            result = self._parse_date_columns(df.iloc[i])
            if not isinstance(result, TransformResult):
                return i, result
        return None

    def extract_data(self, file: File) -> TransformResult:
        try:
            df = file.read_excel()
        except Exception as exc:
            return TransformResult(
                success=False,
                errors=[TransformError(level="basic", message=f"Transform failed: could not open file ({exc})")],
            )

        date_range_row = self._find_date_row(df)
        if date_range_row is None:
            return TransformResult(
                success=False,
                errors=[TransformError(level="intermediate", message="Transform failed", detail="Date ranges are not in the expected format")],
            )

        date_row_idx, date_cols = date_range_row

        records, detail_errors = self._parse_account_rows(df.iloc[date_row_idx + 1:], date_cols)
        records.sort(key=lambda r: (r.account, r.last_day_of_month))

        if detail_errors:
            return TransformResult(success=False, records=records, errors=detail_errors)
        return TransformResult(success=True, records=records)

    def _parse_account_rows(
        self,
        data_df: pd.DataFrame,
        date_cols: list[tuple[int, str]],
    ) -> tuple[list[TransformRecord], list[TransformError]]:
        records: list[TransformRecord] = []
        detail_errors: list[TransformError] = []

        for _, row in data_df.iterrows():
            
            excel_row_num = row.name + 1

            account_val = self._get_account(row)

            if account_val is None or self._skip_row(row, date_cols):
                continue

            account_name = str(account_val).strip()

            for col_index, date in date_cols:
                amount = row.iloc[col_index] if col_index < len(row) else None

                if pd.isna(amount):
                    amount = 0.0

                if isinstance(amount, (int, float, np.integer, np.floating)):
                    records.append(TransformRecord(
                        account=account_name,
                        last_day_of_month=date,
                        amount=round(float(amount), 2),
                    ))
                else:
                    detail_errors.append(TransformError(
                        level="detail",
                        message="Non-numeric amount in account row",
                        row_number=excel_row_num,
                        detail=f"Column {col_index + 1}: expected number, got {type(amount).__name__!r} ({amount!r})",
                    ))

        return records, detail_errors

    def _skip_row(self, row: pd.Series, date_cols: list[tuple[int, str]]) -> bool:
        data_start = min(col_idx for col_idx, _ in date_cols)
        return row.iloc[data_start:].isna().all()


class TransformerOneService(BaseTransformer):
    
    def _last_day_str(self, year: int, month: int) -> str:
        last = calendar.monthrange(year, month)[1]
        return f"{month:02d}/{last:02d}/{year}"

    def _parse_date_columns(self, period_row: pd.Series) -> list[tuple[int, str]] | TransformResult:
        date_cols: list[tuple[int, str]] = []
        for col_idx, cell_val in enumerate(period_row):
            if isinstance(cell_val, datetime):
                try:
                    date_str = self._last_day_str(cell_val.year, cell_val.month)
                    date_cols.append((col_idx, date_str))
                except Exception:
                    return TransformResult(
                        success=False,
                        errors=[TransformError(
                            level="intermediate",
                            message="Transform failed",
                            detail=f" Could not parse date at column {col_idx + 1}",
                        )],
                    )

        if not date_cols:
            return TransformResult(
                success=False,
                errors=[TransformError(level="intermediate", message="Transform failed", detail="No date columns found")],
            )
        return date_cols

    def _get_account(self, row: pd.Series) -> str | None:
        for col_idx in range(min(5, len(row))):
            val = row.iloc[col_idx]
            if pd.notna(val) and self._is_account(val):
                return val
        return None


class TransformerTwoService(BaseTransformer):

    def _parse_date(self, date_str: str) -> str:
        dt = datetime.strptime(date_str.strip(), "%b %d, %Y")
        return f"{dt.month:02d}/{dt.day:02d}/{dt.year}"

    def _parse_date_columns(self, period_row: pd.Series) -> list[tuple[int, str]] | TransformResult:
        date_cols: list[tuple[int, str]] = []
        for col_index, value in enumerate(period_row):
            if not isinstance(value, str) or not value.strip():
                continue
            try:
                date_str = self._parse_date(value)
                date_cols.append((col_index, date_str))
            except ValueError:
                continue

        if not date_cols:
            return TransformResult(
                success=False,
                errors=[TransformError(level="intermediate", message="Transform failed at dates", detail="no date columns found in row 5")],
            )
        return date_cols

    def _get_account(self, row: pd.Series) -> str | None:
        if len(row) <= 2:
            return None
        account_val = row.iloc[2]
        if pd.isna(account_val) or not self._is_account(account_val):
            return None
        return account_val


TRANSFORMERS: dict[str, BaseTransformer] = {
    "Transform1": TransformerOneService(),
    "Transform2": TransformerTwoService(),
}


