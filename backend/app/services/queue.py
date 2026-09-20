import asyncio
import logging
from decimal import Decimal
from pathlib import Path

from fastapi.concurrency import run_in_threadpool
from sqlalchemy import select

from app import config, database
from app.models import Operation, OperationSource, OperationStatus
from app.services.extraction import ExtractedOperation, extract_operation
from app.services.voice_expenses import extract_audio_operations

logger = logging.getLogger(__name__)


def _extract(source: OperationSource, path: Path) -> list[ExtractedOperation]:
    """Read the operation records an uploaded file describes.

    An image is one document, so it yields at most one record; a voice note may
    describe several purchases.
    """
    if source == OperationSource.image:
        return [extract_operation(path)]
    return extract_audio_operations(path)


def _fill(operation: Operation, extracted: ExtractedOperation) -> None:
    operation.category = extracted.category
    operation.description = extracted.description
    if extracted.amount is not None:
        operation.amount = Decimal(str(extracted.amount))


def process_operation(operation_id: int) -> None:
    """Run extraction for one pending operation and store the result.

    The first record fills the operation itself; any further records from the
    same voice note become extra operations over the same file.
    """
    with database.SessionLocal() as db:
        operation = db.get(Operation, operation_id)
        if operation is None or operation.status != OperationStatus.pending:
            return
        try:
            extracted = _extract(operation.source, config.UPLOAD_DIR / operation.file_path)
        except Exception:
            logger.exception("Extraction failed for operation %s", operation_id)
            operation.status = OperationStatus.failed
        else:
            operation.status = OperationStatus.done
            if extracted:
                _fill(operation, extracted[0])
            for extra in extracted[1:]:
                sibling = Operation(
                    source=operation.source,
                    file_path=operation.file_path,
                    status=OperationStatus.done,
                )
                _fill(sibling, extra)
                db.add(sibling)
        db.commit()


class ExtractionQueue:
    """In-process FIFO queue of operation ids, drained by a single worker task.

    Jobs are not persisted: on startup every operation still `pending` is
    enqueued again.
    """

    def __init__(self) -> None:
        self._queue: asyncio.Queue[int] = asyncio.Queue()
        self._worker: asyncio.Task | None = None

    def enqueue(self, operation_id: int) -> None:
        self._queue.put_nowait(operation_id)

    async def start(self) -> None:
        with database.SessionLocal() as db:
            pending = db.scalars(
                select(Operation.id)
                .where(Operation.status == OperationStatus.pending)
                .order_by(Operation.id)
            ).all()
        for operation_id in pending:
            self.enqueue(operation_id)
        self._worker = asyncio.create_task(self._run())

    async def join(self) -> None:
        await self._queue.join()

    async def stop(self) -> None:
        if self._worker is not None:
            self._worker.cancel()
            await asyncio.gather(self._worker, return_exceptions=True)
            self._worker = None

    async def _run(self) -> None:
        while True:
            operation_id = await self._queue.get()
            try:
                await run_in_threadpool(process_operation, operation_id)
            except Exception:
                logger.exception("Queue job %s crashed", operation_id)
            finally:
                self._queue.task_done()


extraction_queue = ExtractionQueue()
