from enum import Enum


class LotStatus(str, Enum):
    CREATED = "created"
    SEARCHING = "searching"
    CANDIDATES_FOUND = "candidates_found"
    NO_CANDIDATES = "no_candidates"
    SELECTED = "selected"
    DEAL_INITIATED = "deal_initiated"
    EXPORTED = "exported"
    FAILED = "failed"


class DealStatus(str, Enum):
    INITIATED = "initiated"
    PENDING_RESPONSE = "pending_response"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    CANCELLED = "cancelled"


class ExportFormat(str, Enum):
    JSON = "json"
    CSV = "csv"


class IntegrationJobStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    FAILED = "failed"