from __future__ import annotations

from collections.abc import AsyncIterator, Mapping, Sequence
from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class StoredObject:
    storage_key: str
    size: int
    sha256: str


class DocumentStoragePort(Protocol):
    async def store(
        self,
        *,
        storage_key: str,
        content: AsyncIterator[bytes],
        content_type: str,
        metadata: Mapping[str, str],
    ) -> StoredObject: ...

    def read(self, storage_key: str) -> AsyncIterator[bytes]: ...

    async def delete_unreferenced(self, storage_key: str) -> None: ...


DocumentView = Mapping[str, object]


class DocumentOperationsPort(Protocol):
    async def require_organization(
        self, resource: str, resource_id: UUID, organization_id: UUID
    ) -> None: ...
    async def list_types(self, organization_id: UUID) -> Sequence[DocumentView]: ...
    async def create_type(
        self, organization_id: UUID, actor_id: UUID, data: Mapping[str, object]
    ) -> DocumentView: ...
    async def create_template(
        self, organization_id: UUID, actor_id: UUID, data: Mapping[str, object]
    ) -> DocumentView: ...
    async def add_template_version(
        self, template_id: UUID, actor_id: UUID, data: Mapping[str, object]
    ) -> DocumentView: ...
    async def publish_template_version(
        self, version_id: UUID, actor_id: UUID, revision: int, reason: str
    ) -> DocumentView: ...
    async def create_record(
        self, organization_id: UUID, actor_id: UUID, data: Mapping[str, object]
    ) -> DocumentView: ...
    async def add_version(
        self, document_id: UUID, actor_id: UUID, data: Mapping[str, object]
    ) -> DocumentView: ...
    async def get_record(self, document_id: UUID) -> DocumentView: ...
    async def get_version(self, document_id: UUID, version_id: UUID) -> DocumentView: ...
    async def get_generation_source(self, document_id: UUID) -> DocumentView: ...
    async def register(
        self, document_id: UUID, actor_id: UUID, revision: int, number: str, registration_date: str
    ) -> DocumentView: ...
    async def signature(
        self, document_id: UUID, actor_id: UUID, data: Mapping[str, object]
    ) -> DocumentView: ...
    async def acknowledge(
        self,
        acknowledgement_id: UUID,
        actor_id: UUID,
        organization_id: UUID,
        revision: int,
        evidence: Mapping[str, object],
    ) -> DocumentView: ...
    async def create_acknowledgement(
        self, document_id: UUID, actor_id: UUID, assigned_employee_id: UUID
    ) -> DocumentView: ...
    async def signature_status(self, document_id: UUID) -> Sequence[DocumentView]: ...
    async def create_checklist_item(
        self, organization_id: UUID, actor_id: UUID, data: Mapping[str, object]
    ) -> DocumentView: ...
    async def validate_checklist(
        self, business_type: str, business_id: UUID, organization_id: UUID
    ) -> Sequence[DocumentView]: ...
