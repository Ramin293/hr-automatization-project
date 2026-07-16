from __future__ import annotations

import asyncio
import hashlib
import importlib
from collections.abc import AsyncIterator, Mapping
from tempfile import SpooledTemporaryFile
from typing import Any

from app.core.errors import ApplicationError
from app.core.errors.codes import ErrorCode
from app.modules.documents.application.ports import DocumentStoragePort, StoredObject


class S3DocumentStorage(DocumentStoragePort):
    """Private S3-compatible storage for MinIO/AWS without public object URLs."""

    def __init__(
        self,
        *,
        endpoint_url: str | None,
        bucket: str,
        access_key: str,
        secret_key: str,
        region: str,
    ) -> None:
        try:
            boto3: Any = importlib.import_module("boto3")
        except ImportError as exc:
            raise RuntimeError("boto3 is required for S3 document storage") from exc
        self._client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )
        self._bucket = bucket

    async def store(
        self,
        *,
        storage_key: str,
        content: AsyncIterator[bytes],
        content_type: str,
        metadata: Mapping[str, str],
    ) -> StoredObject:
        digest = hashlib.sha256()
        size = 0
        with SpooledTemporaryFile(max_size=8 * 1024 * 1024) as spool:
            try:
                async for chunk in content:
                    digest.update(chunk)
                    size += len(chunk)
                    spool.write(chunk)
                spool.seek(0)
                await asyncio.to_thread(
                    self._client.upload_fileobj,
                    spool,
                    self._bucket,
                    storage_key,
                    ExtraArgs={"ContentType": content_type, "Metadata": dict(metadata)},
                )
            except Exception as exc:
                raise ApplicationError(
                    code=ErrorCode.DOCUMENT_STORAGE_FAILED,
                    message="S3 document storage failed.",
                ) from exc
        return StoredObject(storage_key, size, digest.hexdigest())

    async def read(self, storage_key: str) -> AsyncIterator[bytes]:
        try:
            response = await asyncio.to_thread(
                self._client.get_object, Bucket=self._bucket, Key=storage_key
            )
            body = response["Body"]
            while chunk := await asyncio.to_thread(body.read, 64 * 1024):
                yield chunk
        except Exception as exc:
            raise ApplicationError(
                code=ErrorCode.DOCUMENT_STORAGE_FAILED, message="S3 document read failed."
            ) from exc

    async def delete_unreferenced(self, storage_key: str) -> None:
        try:
            await asyncio.to_thread(
                self._client.delete_object, Bucket=self._bucket, Key=storage_key
            )
        except Exception as exc:
            raise ApplicationError(
                code=ErrorCode.DOCUMENT_STORAGE_FAILED, message="S3 document delete failed."
            ) from exc
