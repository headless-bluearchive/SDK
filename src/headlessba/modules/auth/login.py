"""Convenience wrappers for login, proof-token, and queue-stage requests."""

from __future__ import annotations

from typing import Any, Mapping

from headlessba.core.client import BAReplayClient, BuiltRequest
from headlessba.core.crypto import generated_key_iv_fields


class LoginReplay:
    """Build login-chain requests with the same packet path as normal APIs.

    ProofToken solving is challenge/server-specific. This helper exposes the
    request/submit steps and lets callers plug in a solver result.
    """

    def __init__(self, client: BAReplayClient) -> None:
        self.client = client

    def proof_token_question(self) -> BuiltRequest:
        return self.client.build(
            "ProofTokenRequestQuestionRequest",
            {},
            inject_hash=True,
            include_base_defaults=True,
        )

    def proof_token_submit(self, answer: int) -> BuiltRequest:
        return self.client.build(
            "ProofTokenSubmitRequest",
            {"Answer": int(answer)},
            inject_hash=True,
            include_base_defaults=True,
        )

    def account_auth(self, fields: Mapping[str, Any], *, include_base_defaults: bool = False) -> BuiltRequest:
        return self.client.build(
            "AccountAuthRequest",
            fields,
            inject_hash=True,
            include_base_defaults=include_base_defaults,
        )

    def account_check_nexon(self, fields: Mapping[str, Any]) -> BuiltRequest:
        return self.client.build(
            "AccountCheckNexonRequest",
            fields,
            inject_hash=True,
            encrypt_request=False,
        )

    def account_login_sync(
        self,
        fields: Mapping[str, Any] | None = None,
        *,
        include_base_defaults: bool = False,
    ) -> BuiltRequest:
        return self.client.build(
            "AccountLoginSyncRequest",
            fields or {},
            inject_hash=True,
            include_base_defaults=include_base_defaults,
        )

    def native_relay_request(
        self,
        request_class: str,
        fields: Mapping[str, Any] | None = None,
        *,
        include_base_defaults: bool = True,
    ) -> BuiltRequest:
        return self.client.build(
            request_class,
            fields or {},
            inject_hash=True,
            include_base_defaults=include_base_defaults,
        )

    def queuing_get_ticket(self, fields: Mapping[str, Any] | None = None) -> BuiltRequest:
        return self.client.build("QueuingGetTicketRequest", fields or {}, inject_hash=True)

    def queuing_get_crypto_keys(self, fields: Mapping[str, Any]) -> BuiltRequest:
        return self.client.build("QueuingGetCryptoKeysRequest", fields, inject_hash=True)

    def queuing_get_crypto_keys_generated(self) -> tuple[BuiltRequest, bytes, bytes]:
        fields, key, iv = generated_key_iv_fields()
        return self.queuing_get_crypto_keys(fields), key, iv

    def queuing_get_auth_ticket(self, fields: Mapping[str, Any]) -> BuiltRequest:
        return self.client.build("QueuingGetAuthTicketRequest", fields, inject_hash=True)

    def queuing_process_waiting_queue(self, fields: Mapping[str, Any]) -> BuiltRequest:
        return self.client.build("QueuingProcessWaitingQueueRequest", fields, inject_hash=True)
