"""Event system for Data-Shield."""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


class EventType(str, Enum):
    """Types of events in Data-Shield."""

    SCAN_STARTED = "scan_started"
    SCAN_PROGRESS = "scan_progress"
    SCAN_COMPLETED = "scan_completed"
    SCAN_PAUSED = "scan_paused"
    SCAN_RESUMED = "scan_resumed"
    SCAN_FAILED = "scan_failed"

    FINDING_DETECTED = "finding_detected"
    FINDING_VERIFIED = "finding_verified"
    FINDING_ENCRYPTED = "finding_encrypted"

    MONITOR_STARTED = "monitor_started"
    MONITOR_STOPPED = "monitor_stopped"
    FILE_CHANGED = "file_changed"

    VAULT_LOCKED = "vault_locked"
    VAULT_UNLOCKED = "vault_unlocked"
    VAULT_ENTRY_ADDED = "vault_entry_added"

    ERROR_OCCURRED = "error_occurred"


@dataclass
class Event:
    """Base event class."""

    type: EventType
    timestamp: datetime
    data: Optional[dict[str, Any]] = None
    error: Optional[str] = None


class EventBus:
    """Simple event bus for decoupled communication."""

    def __init__(self):
        """Initialize event bus."""
        self.listeners: dict[EventType, list] = {}

    def subscribe(self, event_type: EventType, handler):
        """Subscribe to an event type.

        Args:
            event_type: Type of event to listen for
            handler: Callable to handle events
        """
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(handler)

    def emit(self, event: Event):
        """Emit an event to all listeners.

        Args:
            event: Event to emit
        """
        if event.type in self.listeners:
            for handler in self.listeners[event.type]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"Error in event handler: {e}")
