import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app import config
from app.models import Operation, OperationSource

CHUNK_SIZE = 1024 * 1024


async def save_upload(
    db: Session,
    file: UploadFile,
    allowed_types: dict[str, str],
    max_size: int,
    source: OperationSource,
) -> Operation:
    ext = allowed_types.get(file.content_type or "")
    if ext is None:
        raise HTTPException(415, f"Unsupported media type: {file.content_type}")

    config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    name = f"{uuid.uuid4().hex}{ext}"
    path = config.UPLOAD_DIR / name

    try:
        size = 0
        with path.open("wb") as out:
            while chunk := await file.read(CHUNK_SIZE):
                size += len(chunk)
                if size > max_size:
                    raise HTTPException(413, "File too large")
                out.write(chunk)

        operation = Operation(source=source, file_path=name)
        db.add(operation)
        db.commit()
    except BaseException:
        db.rollback()
        path.unlink(missing_ok=True)
        raise

    db.refresh(operation)
    return operation
