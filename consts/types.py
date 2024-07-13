from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class SeaDataDate:
    year: int
    month: int
    day: int
    hour: int

    def __lt__(self, other):
        if not isinstance(other, SeaDataDate):
            return NotImplemented
        if self.year != other.year:
            return self.year < other.year
        if self.month != other.month:
            return self.month < other.month
        if self.day != other.day:
            return self.day < other.day
        return self.hour < other.hour

    def __le__(self, other):
        if not isinstance(other, SeaDataDate):
            return NotImplemented
        return self < other or self == other

    def __eq__(self, other):
        if not isinstance(other, SeaDataDate):
            return NotImplemented
        return (self.year == other.year and
                self.month == other.month and
                self.day == other.day and
                self.hour == other.hour)

    def __add__(self, delta: timedelta):
        date_time = datetime(self.year, self.month, self.day, self.hour) + delta
        return SeaDataDate(date_time.year, date_time.month, date_time.day, date_time.hour)

    def __radd__(self, delta: timedelta):
        return self.__add__(delta)


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
class CampaignOperation:
    #operation: Operation
    id: int
    operationId: int
    order: int
    relation: str


@dataclass
class Campaign:
    id: int
    operations: list[CampaignOperation]


@dataclass
class CampaignResultValue:
    campaignResultId: int
    year: int
    month: int
    day: int
    hour: int
    operation_id: int
    status: str
    campaignOperationId: int
    relationship: Optional[str]


@dataclass
class CampaignResult:
    id: int | None
    campaign_id: int
    year: int
    month: int
    day: int
    hour: int
    total_wait: float
    total_work: float
    success: bool
    resultValues: list[CampaignResultValue] | None
