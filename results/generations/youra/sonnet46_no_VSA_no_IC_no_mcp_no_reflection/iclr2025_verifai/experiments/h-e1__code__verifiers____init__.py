from dataclasses import dataclass


@dataclass
class VerifierResult:
    activated: bool
    signal: str
    latency_ms: float
