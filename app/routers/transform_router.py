from fastapi import APIRouter, Form, UploadFile, File
from app.controllers.transform_controller import TransformController

router = APIRouter(prefix="/transforms", tags=["transforms"])


@router.post("", status_code=200)
async def create_transform(
    name: str = Form(..., description="File Name"),
    transformer: str = Form(..., description="Transform1 or Transform2"),
    file: UploadFile = File(..., description="Excel File"),
):
    return await TransformController.create(name, transformer, file)


@router.get("")
def list_transforms():
    return TransformController.list_all()


@router.get("/{job_id}")
def get_transform(job_id: str):
    return TransformController.get(job_id)


@router.delete("/{job_id}")
def delete_transform(job_id: str):
    return TransformController.delete(job_id)
