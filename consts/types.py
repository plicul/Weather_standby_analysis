from dataclasses import dataclass


@dataclass
class SeaData:
    year: int
    month: int
    day: int
    hour: int
    waveHeight: float
    waveDir: float
    wavePeriod: float


@dataclass
class LimitValue:
    wavePeriod: float
    waveDir: float
    waveHeight: float


@dataclass
class Limit:
    id: int
    values: list[LimitValue]


@dataclass
class Operation:
    id: int
    timeReq: int
    shipDir: int
    type: str
    limit: Limit


@dataclass
class OperationResult:
    operationId: int
    year: int
    month: int
    day: int
    hour: int
    success: bool


@dataclass
class Campaign:
    id: int
    operations: list[Operation]

