from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session

from app import config
from app.database import get_db
from app.models import OperationSource
from app.routes.storage import save_upload
from app.schemas import OperationOut
from app.services.queue import extraction_queue

router = APIRouter()


@router.post("/images", response_model=OperationOut, status_code=201)
async def upload_image(file: UploadFile, db: Session = Depends(get_db)):
    operation = await save_upload(
        db, file, config.ALLOWED_IMAGE_TYPES, config.MAX_IMAGE_SIZE, OperationSource.image
    )
    extraction_queue.enqueue(operation.id)
    return operation
