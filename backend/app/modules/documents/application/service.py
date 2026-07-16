from __future__ import annotations

import re
from collections.abc import AsyncIterator, Mapping
from pathlib import PurePath
from uuid import UUID, uuid4

from app.core.errors import ApplicationError, ValidationError
from app.core.errors.codes import ErrorCode
from app.core.security.identity import Principal
from app.core.security.ports import AuthorizationPort

from .ports import DocumentOperationsPort, DocumentStoragePort, DocumentView

_SAFE_FILENAME = re.compile(r"[^A-Za-z0-9._-]+")


class DocumentService:
    def __init__(
        self,
        operations: DocumentOperationsPort,
        storage: DocumentStoragePort,
        authorization: AuthorizationPort,
        *,
        maximum_size: int,
        allowed_mime_types: frozenset[str],
        development: bool,
    ) -> None:
        self._operations = operations
        self._storage = storage
        self._authorization = authorization
        self._maximum_size = maximum_size
        self._allowed_mime_types = allowed_mime_types
        self._development = development

    async def require(self, principal: Principal, permission: str, organization_id: UUID) -> None:
        await self._authorization.require(
            principal=principal, permission_code=permission, organization_id=organization_id
        )

    async def upload(
        self,
        principal: Principal,
        organization_id: UUID,
        document_id: UUID,
        *,
        filename: str,
        mime_type: str,
        chunks: AsyncIterator[bytes],
        source_type: str = "uploaded",
    ) -> DocumentView:
        await self.require(principal, "documents.upload", organization_id)
        await self._assert_organization(document_id, organization_id)
        if mime_type not in self._allowed_mime_types:
            raise ValidationError(
                "The document MIME type is not allowed.", details={"mimeType": mime_type}
            )
        safe_name = _safe_filename(filename)
        storage_key = f"{organization_id}/{document_id}/{uuid4()}-{safe_name}"
        size = 0

        async def bounded() -> AsyncIterator[bytes]:
            nonlocal size
            async for chunk in chunks:
                size += len(chunk)
                if size > self._maximum_size:
                    raise ValidationError(
                        "The document exceeds the maximum size.",
                        details={"maximumSize": self._maximum_size},
                    )
                yield chunk

        stored = await self._storage.store(
            storage_key=storage_key,
            content=bounded(),
            content_type=mime_type,
            metadata={"document-id": str(document_id)},
        )
        try:
            return await self._operations.add_version(
                document_id,
                principal.user_id,
                {
                    "storageKey": stored.storage_key,
                    "originalFilename": filename,
                    "safeFilename": safe_name,
                    "mimeType": mime_type,
                    "sizeBytes": stored.size,
                    "sha256": stored.sha256,
                    "sourceType": source_type,
                },
            )
        except Exception:
            await self._storage.delete_unreferenced(storage_key)
            raise

    async def download(
        self,
        principal: Principal,
        organization_id: UUID,
        document_id: UUID,
        version_id: UUID,
        *,
        sensitive: bool = False,
    ) -> tuple[DocumentView, AsyncIterator[bytes]]:
        await self.require(
            principal,
            "documents.read_sensitive" if sensitive else "documents.read",
            organization_id,
        )
        await self._assert_organization(document_id, organization_id)
        version = await self._operations.get_version(document_id, version_id)
        key = version.get("storageKey")
        if not isinstance(key, str):
            raise ApplicationError(
                code=ErrorCode.DOCUMENT_STORAGE_FAILED,
                message="Document storage reference is invalid.",
            )
        return version, self._storage.read(key)

    async def manual_signature(
        self,
        principal: Principal,
        organization_id: UUID,
        document_id: UUID,
        data: Mapping[str, object],
    ) -> DocumentView:
        await self.require(principal, "documents.sign_request", organization_id)
        await self._assert_organization(document_id, organization_id)
        if not self._development:
            raise ApplicationError(
                code=ErrorCode.PROCESS_ACTION_NOT_ALLOWED,
                message="Manual signature confirmation is development-only.",
            )
        payload = dict(data)
        payload["manualConfirmation"] = True
        return await self._operations.signature(document_id, principal.user_id, payload)

    async def generate(
        self,
        principal: Principal,
        organization_id: UUID,
        document_id: UUID,
        *,
        filename: str,
        mime_type: str,
        variables: Mapping[str, object],
    ) -> DocumentView:
        await self.require(principal, "documents.generate", organization_id)
        await self._assert_organization(document_id, organization_id)
        source = await self._operations.get_generation_source(document_id)
        key = source.get("storageKey")
        if not isinstance(key, str):
            raise ApplicationError(code=ErrorCode.DOCUMENT_STORAGE_FAILED)
        chunks: list[bytes] = []
        size = 0
        async for chunk in self._storage.read(key):
            size += len(chunk)
            if size > self._maximum_size:
                raise ValidationError("The template exceeds the maximum size.")
            chunks.append(chunk)
        try:
            rendered = b"".join(chunks).decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValidationError(
                "This template cannot be rendered by the local text adapter."
            ) from exc
        schema = source.get("variableSchema")
        allowed = set(schema) if isinstance(schema, Mapping) else set()
        if set(variables) - allowed:
            raise ValidationError("Template variables are not declared.")
        for name, value in variables.items():
            if not isinstance(value, str | int | float | bool):
                raise ValidationError("Template variables must be scalar values.")
            rendered = rendered.replace("{{" + name + "}}", str(value))

        async def generated_chunks() -> AsyncIterator[bytes]:
            yield rendered.encode("utf-8")

        return await self.upload(
            principal,
            organization_id,
            document_id,
            filename=filename,
            mime_type=mime_type,
            chunks=generated_chunks(),
            source_type="generated",
        )

    async def _assert_organization(self, document_id: UUID, organization_id: UUID) -> None:
        record = await self._operations.get_record(document_id)
        if record.get("organizationId") != organization_id:
            raise ApplicationError(
                code=ErrorCode.DOCUMENT_ACCESS_FORBIDDEN,
                message="Document access is forbidden.",
            )


def _safe_filename(value: str) -> str:
    leaf = PurePath(value.replace("\\", "/")).name
    safe = _SAFE_FILENAME.sub("_", leaf).strip("._")
    if not safe or safe in {".", ".."}:
        raise ValidationError("The filename is invalid.")
    return safe[:255]
