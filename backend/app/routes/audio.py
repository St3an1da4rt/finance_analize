from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session

from app import config
from app.database import get_db
from app.models import OperationSource
from app.routes.storage import save_upload
from app.schemas import OperationOut
from app.services.queue import extraction_queue

router = APIRouter()


@router.post(
    "/audio",
    response_model=OperationOut,
    status_code=201,
    summary="Upload a voice note",
    responses={
        413: {"description": "File larger than MAX_AUDIO_SIZE (25 MB by default)"},
        415: {"description": "Content type is not ogg, mp3, m4a or wav"},
    },
)
async def upload_audio(file: UploadFile, db: Session = Depends(get_db)):
    """Accept a voice note describing spending and queue it for extraction.

    The file is stored on disk and an operation with status `pending` is
    returned right away. A background worker then transcribes the note
    (Whisper) and reads the purchases from the transcript: the first one fills
    this operation, any further ones are created as separate operations over
    the same file. The status becomes `done`, or `failed` if extraction fails.

    Poll `GET /operations` for the result.
    """
    operation = await save_upload(
        db, file, config.ALLOWED_AUDIO_TYPES, config.MAX_AUDIO_SIZE, OperationSource.audio
    )
    extraction_queue.enqueue(operation.id)
    return operation
