"""File service — wraps uploaded file bytes with validation."""
from io import BytesIO

import pandas as pd


class File:
    EXCEL_EXTENSIONS = {".xlsx", ".xls"}
    EXCEL_CONTENT_TYPES = {
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
    }

    def __init__(self, data: bytes, filename: str, content_type: str) -> None:
        self.data = data
        self.filename = filename
        self.content_type = content_type

    def read_excel(self) -> pd.DataFrame:
        return pd.read_excel(BytesIO(self.data), header=None, engine="openpyxl")

    def validate_excel(self) -> None:
        file_ext = any(self.filename.lower().endswith(ext) for ext in self.EXCEL_EXTENSIONS)
        file_type = self.content_type in self.EXCEL_CONTENT_TYPES
        if not (file_ext or file_type):
            raise ValueError(
                f"Unsupported file type '{self.filename}'. Please upload an Excel file (.xlsx or .xls)."
            )
