from collections.abc import AsyncIterator, Mapping
from uuid import UUID, uuid4

import pytest
from app.core.errors import ApplicationError, ForbiddenError, ValidationError
from app.core.errors.codes import ErrorCode
from app.core.security.identity import Principal
from app.modules.documents.application.ports import StoredObject
from app.modules.documents.application.service import DocumentService


async def _chunks(*values: bytes) -> AsyncIterator[bytes]:
    for value in values:
        yield value


class Authorization:
    def __init__(self, *, deny: bool = False) -> None:
        self.deny = deny
        self.permissions: list[str] = []

    async def require(self, **values: object) -> None:
        self.permissions.append(str(values["permission_code"]))
        if self.deny:
            raise ForbiddenError()


class Storage:
    def __init__(self) -> None:
        self.store_calls = 0
        self.deleted: list[str] = []

    async def store(
        self,
        *,
        storage_key: str,
        content: AsyncIterator[bytes],
        content_type: str,
        metadata: Mapping[str, str],
    ) -> StoredObject:
        self.store_calls += 1
        payload = b"".join([chunk async for chunk in content])
        return StoredObject(storage_key, len(payload), "a" * 64)

    async def delete_unreferenced(self, storage_key: str) -> None:
        self.deleted.append(storage_key)

    async def read(self, storage_key: str) -> AsyncIterator[bytes]:
        yield b"document"


class Operations:
    def __init__(self, organization_id: UUID) -> None:
        self.organization_id = organization_id
        self.signature_payload: Mapping[str, object] | None = None

    async def get_record(self, document_id: UUID) -> Mapping[str, object]:
        return {"id": document_id, "organizationId": self.organization_id}

    async def add_version(
        self, document_id: UUID, actor_id: UUID, data: Mapping[str, object]
    ) -> Mapping[str, object]:
        return {"id": uuid4(), "documentId": document_id, **data}

    async def get_version(self, document_id: UUID, version_id: UUID) -> Mapping[str, object]:
        return {"id": version_id, "documentId": document_id, "storageKey": "safe/key"}

    async def signature(
        self, document_id: UUID, actor_id: UUID, data: Mapping[str, object]
    ) -> Mapping[str, object]:
        self.signature_payload = data
        return {"id": uuid4(), "documentId": document_id, **data}


def _service(
    *,
    organization_id: UUID,
    authorization: Authorization | None = None,
    storage: Storage | None = None,
    development: bool = True,
) -> tuple[DocumentService, Storage, Operations]:
    actual_storage = storage or Storage()
    operations = Operations(organization_id)
    return (
        DocumentService(
            operations,
            actual_storage,
            authorization or Authorization(),
            maximum_size=5,
            allowed_mime_types=frozenset({"application/pdf"}),
            development=development,
        ),
        actual_storage,
        operations,
    )


def _principal() -> Principal:
    return Principal(user_id=uuid4(), subject="documents-test")


@pytest.mark.asyncio
async def test_upload_rejects_mime_before_writing_storage() -> None:
    organization_id, document_id = uuid4(), uuid4()
    service, storage, _ = _service(organization_id=organization_id)
    with pytest.raises(ValidationError):
        await service.upload(
            _principal(),
            organization_id,
            document_id,
            filename="payload.exe",
            mime_type="application/octet-stream",
            chunks=_chunks(b"bad"),
        )
    assert storage.store_calls == 0


@pytest.mark.asyncio
async def test_upload_stops_when_stream_exceeds_limit() -> None:
    organization_id, document_id = uuid4(), uuid4()
    service, storage, _ = _service(organization_id=organization_id)
    with pytest.raises(ValidationError):
        await service.upload(
            _principal(),
            organization_id,
            document_id,
            filename="large.pdf",
            mime_type="application/pdf",
            chunks=_chunks(b"123", b"456"),
        )
    assert storage.store_calls == 1


@pytest.mark.asyncio
async def test_download_requires_authorization_before_resource_access() -> None:
    organization_id = uuid4()
    service, _, _ = _service(
        organization_id=organization_id, authorization=Authorization(deny=True)
    )
    with pytest.raises(ForbiddenError):
        await service.download(_principal(), organization_id, uuid4(), uuid4())


@pytest.mark.asyncio
async def test_document_organization_mismatch_is_stable_access_error() -> None:
    service, _, _ = _service(organization_id=uuid4())
    with pytest.raises(ApplicationError) as error:
        await service.download(_principal(), uuid4(), uuid4(), uuid4())
    assert error.value.code is ErrorCode.DOCUMENT_ACCESS_FORBIDDEN


@pytest.mark.asyncio
async def test_manual_signature_is_explicitly_marked_and_development_only() -> None:
    organization_id, document_id = uuid4(), uuid4()
    service, _, operations = _service(organization_id=organization_id)
    result = await service.manual_signature(
        _principal(), organization_id, document_id, {"status": "signed"}
    )
    assert result["manualConfirmation"] is True
    assert operations.signature_payload == {"status": "signed", "manualConfirmation": True}

    production, _, _ = _service(organization_id=organization_id, development=False)
    with pytest.raises(ApplicationError) as error:
        await production.manual_signature(
            _principal(), organization_id, document_id, {"status": "signed"}
        )
    assert error.value.code is ErrorCode.PROCESS_ACTION_NOT_ALLOWED
