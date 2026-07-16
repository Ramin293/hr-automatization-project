from pathlib import Path

import pytest
from app.core.errors import ApplicationError
from app.modules.documents.infrastructure.local_storage import LocalDocumentStorage


async def _chunks(*values: bytes):
    for value in values:
        yield value


@pytest.mark.asyncio
async def test_local_storage_streams_and_hashes(tmp_path: Path) -> None:
    storage = LocalDocumentStorage(tmp_path)
    stored = await storage.store(
        storage_key="org/document/file.pdf",
        content=_chunks(b"abc", b"123"),
        content_type="application/pdf",
        metadata={},
    )
    assert stored.size == 6
    assert stored.sha256 == "6ca13d52ca70c883e0f0bb101e425a89e8624de51db2d2392593af6a84118090"
    assert b"".join([chunk async for chunk in storage.read(stored.storage_key)]) == b"abc123"


@pytest.mark.asyncio
@pytest.mark.parametrize("key", ["../secret", "a/../../secret", "C:/secret", "/absolute"])
async def test_local_storage_rejects_path_traversal(tmp_path: Path, key: str) -> None:
    storage = LocalDocumentStorage(tmp_path)
    with pytest.raises(ApplicationError):
        await storage.store(
            storage_key=key, content=_chunks(b"x"), content_type="text/plain", metadata={}
        )
