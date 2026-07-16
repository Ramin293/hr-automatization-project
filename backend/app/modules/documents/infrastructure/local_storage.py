from __future__ import annotations

import hashlib
from collections.abc import AsyncIterator, Mapping
from pathlib import Path, PurePosixPath

from app.core.errors import ApplicationError
from app.core.errors.codes import ErrorCode
from app.modules.documents.application.ports import DocumentStoragePort, StoredObject


class LocalDocumentStorage(DocumentStoragePort):
    """Development/test storage with traversal protection and streamed hashing."""

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        normalized = PurePosixPath(key)
        if normalized.is_absolute() or ".." in normalized.parts or ":" in normalized.parts[0]:
            raise ApplicationError(
                code=ErrorCode.DOCUMENT_STORAGE_FAILED, message="Unsafe storage key."
            )
        target = self._root.joinpath(*normalized.parts).resolve()
        if self._root != target and self._root not in target.parents:
            raise ApplicationError(
                code=ErrorCode.DOCUMENT_STORAGE_FAILED, message="Unsafe storage key."
            )
        return target

    async def store(
        self,
        *,
        storage_key: str,
        content: AsyncIterator[bytes],
        content_type: str,
        metadata: Mapping[str, str],
    ) -> StoredObject:
        del content_type, metadata
        target = self._path(storage_key)
        target.parent.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256()
        size = 0
        try:
            with target.open("xb") as handle:
                async for chunk in content:
                    size += len(chunk)
                    digest.update(chunk)
                    handle.write(chunk)
        except OSError as exc:
            raise ApplicationError(
                code=ErrorCode.DOCUMENT_STORAGE_FAILED, message="Document storage failed."
            ) from exc
        return StoredObject(storage_key, size, digest.hexdigest())

    async def read(self, storage_key: str) -> AsyncIterator[bytes]:
        target = self._path(storage_key)
        try:
            with target.open("rb") as handle:
                while chunk := handle.read(64 * 1024):
                    yield chunk
        except OSError as exc:
            raise ApplicationError(
                code=ErrorCode.DOCUMENT_STORAGE_FAILED, message="Document read failed."
            ) from exc

    async def delete_unreferenced(self, storage_key: str) -> None:
        target = self._path(storage_key)
        if target.exists():
            target.unlink()
