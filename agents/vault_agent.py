from __future__ import annotations

import os
from typing import Any

import hvac

from .base import AgentResult
from observability import get_logger, monitored, VaultIntegrationError


class VaultAgent:
    def __init__(
        self,
        vault_addr: str | None = None,
        vault_token: str | None = None,
        db_secret_path: str = "secret/data/quantumdx/database",
        user_secret_prefix: str = "secret/data/quantumdx/users",
    ) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.vault_addr = vault_addr or os.getenv("VAULT_ADDR")
        self.vault_token = vault_token or os.getenv("VAULT_TOKEN")
        self.db_secret_path = db_secret_path
        self.user_secret_prefix = user_secret_prefix

        if not self.vault_addr:
            raise VaultIntegrationError("VAULT_ADDR is not set")
        if not self.vault_token:
            raise VaultIntegrationError("VAULT_TOKEN is not set")

        self.client = hvac.Client(url=self.vault_addr, token=self.vault_token)
        if not self.client.is_authenticated():
            raise VaultIntegrationError("Vault authentication failed")

    @staticmethod
    def _kv2_path(path: str) -> str:
        return path.replace("secret/data/", "")

    @staticmethod
    def _extract_kv2_secret(response: dict[str, Any]) -> dict[str, Any]:
        return response["data"]["data"]

    @monitored("VaultAgent", "get_database_config")
    def get_database_config(self, trace_id: str | None = None) -> AgentResult:
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=self._kv2_path(self.db_secret_path)
            )
            secret = self._extract_kv2_secret(response)

            required = ["server", "database", "username", "password"]
            missing = [k for k in required if not secret.get(k)]
            if missing:
                return AgentResult(False, f"Missing DB config fields in Vault: {missing}")

            return AgentResult(True, "Database config retrieved from Vault", secret)
        except Exception as exc:
            raise VaultIntegrationError(f"Failed to read DB config from Vault: {exc}") from exc

    @monitored("VaultAgent", "get_user_info")
    def get_user_info(self, user_id: str, trace_id: str | None = None) -> AgentResult:
        try:
            path = self._kv2_path(f"{self.user_secret_prefix}/{user_id}")
            response = self.client.secrets.kv.v2.read_secret_version(path=path)
            secret = self._extract_kv2_secret(response)
            return AgentResult(True, "User info retrieved from Vault", secret)
        except Exception as exc:
            raise VaultIntegrationError(f"Failed to read user info from Vault: {exc}") from exc