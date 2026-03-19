"""Transform controller — orchestrates ETL + persistence."""
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, UploadFile

from app.models.transform_job import TransformError, TransformJobDetail, TransformJobSummary, TransformRecord
from app.services import database as db
from app.services.file import File
from app.services.transformer import TRANSFORMERS


class TransformController:

    @staticmethod
    async def create(name: str, transformer: str, file: UploadFile) -> dict:
        
        
        if not transformer or transformer not in TRANSFORMERS:
            raise HTTPException(status_code=400, detail=f"Unknown transformer '{transformer}'. Use {list(TRANSFORMERS.keys())}")

        file_obj = File(await file.read(), file.filename, file.content_type)
        
        try:
            file_obj.validate_excel()
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Transformer failed",
                    "errors": "Please upload a valid Excel File in .xlsx or .xls format.",
                },
            )

        trans_service = TRANSFORMERS.get(transformer)
        result = trans_service.extract_data(file_obj)

        if not result.success:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Transformer failed",
                    "errors": [e.model_dump(exclude_none=True) for e in result.errors],
                },
            )

        job_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        records_dicts = [r.model_dump() for r in result.records]

        db.insert_job(job_id, name, transformer, created_at, records_dicts)
        return {"id": job_id}

    @staticmethod
    def list_all() -> list[TransformJobSummary]:
        rows = db.list_jobs()
        return [TransformJobSummary(**r) for r in rows]

    @staticmethod
    def get(job_id: str) -> list[TransformRecord]:
        row = db.get_job(job_id)
        if row is None:
            raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
        return TransformJobDetail(**row).records

    @staticmethod
    def delete(job_id: str) -> dict:
        deleted = db.delete_job(job_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
        return {"deleted": True, "id": job_id}
