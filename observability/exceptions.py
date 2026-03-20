class QuantumDxError(Exception):
    """Base application exception."""


class ValidationError(QuantumDxError):
    pass


class IngestionError(QuantumDxError):
    pass


class EncodingError(QuantumDxError):
    pass


class FeatureStoreError(QuantumDxError):
    pass


class TrainingError(QuantumDxError):
    pass


class RegistryError(QuantumDxError):
    pass


class SqlIntegrationError(QuantumDxError):
    pass


class VaultIntegrationError(QuantumDxError):
    pass