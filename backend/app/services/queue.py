import asyncio
import logging
from decimal import Decimal

from fastapi.concurrency import run_in_threadpool
from sqlalchemy import select

from app import config, database
from app.models import Operation, OperationSource, OperationStatus
from app.services.extraction import extract_operation

logger = logging.getLogger(__name__)


def process_operation(operation_id: int) -> None:
    """Run extraction for one pending image operation and store the result."""
    with database.SessionLocal() as db:
        operation = db.get(Operation, operation_id)
        if (
            operation is None
            or operation.source != OperationSource.image
            or operation.status != OperationStatus.pending
        ):
            return
        try:
            extracted = extract_operation(config.UPLOAD_DIR / operation.file_path)
        except Exception:
            logger.exception("Extraction failed for operation %s", operation_id)
            operation.status = OperationStatus.failed
        else:
            operation.category = extracted.category
            operation.description = extracted.description
            if extracted.amount is not None:
                operation.amount = Decimal(str(extracted.amount))
            operation.status = OperationStatus.done
        db.commit()


class ExtractionQueue:
    """In-process FIFO queue of operation ids, drained by a single worker task.

    Jobs are not persisted: on startup every image operation still `pending`
    is enqueued again.
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
                .where(
                    Operation.source == OperationSource.image,
                    Operation.status == OperationStatus.pending,
                )
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
