"""Constants and helpers for record closure_type values."""

CLOSURE_TYPE_OPEN = "Open"
CLOSURE_TYPE_CLOSED = "Closed"
CLOSURE_TYPE_RETAINED_FOR_SECURITY = "Retained for security"

# closure_type values (as stored) that should match when a user
# filters by record_status "closed".
CLOSED_CLOSURE_TYPES = [CLOSURE_TYPE_CLOSED, CLOSURE_TYPE_RETAINED_FOR_SECURITY]


def closure_types_for_record_status(record_status):
    """Map a record_status filter value ('open'/'closed') to the
    closure_type values (as stored) that should match it."""
    if (record_status or "").strip().lower() == CLOSURE_TYPE_CLOSED.lower():
        return CLOSED_CLOSURE_TYPES
    return [CLOSURE_TYPE_OPEN]
