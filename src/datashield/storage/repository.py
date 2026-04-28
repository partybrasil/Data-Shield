"""Repository for database operations."""

from typing import Optional, List
from sqlalchemy.orm import Session
from ..core.models import Finding as FindingModel
from .database import Finding, ScanSession, VaultEntry


class FindingRepository:
    """Repository for finding operations."""

    def __init__(self, session: Session):
        """Initialize with database session."""
        self.session = session

    def create(self, finding: Finding) -> Finding:
        """Create a new finding."""
        self.session.add(finding)
        self.session.commit()
        return finding

    def get_by_id(self, finding_id: str) -> Optional[Finding]:
        """Get finding by ID."""
        return self.session.query(Finding).filter_by(id=finding_id).first()

    def get_by_session(self, session_id: str) -> List[Finding]:
        """Get all findings for a session."""
        return self.session.query(Finding).filter_by(session_id=session_id).all()

    def update(self, finding_id: str, **kwargs) -> Optional[Finding]:
        """Update finding."""
        finding = self.get_by_id(finding_id)
        if finding:
            for key, value in kwargs.items():
                if hasattr(finding, key):
                    setattr(finding, key, value)
            self.session.commit()
        return finding

    def delete(self, finding_id: str) -> bool:
        """Delete finding."""
        finding = self.get_by_id(finding_id)
        if finding:
            self.session.delete(finding)
            self.session.commit()
            return True
        return False


class ScanSessionRepository:
    """Repository for scan session operations."""

    def __init__(self, session: Session):
        """Initialize with database session."""
        self.session = session

    def create(self, session: ScanSession) -> ScanSession:
        """Create a new scan session."""
        self.session.add(session)
        self.session.commit()
        return session

    def get_by_id(self, session_id: str) -> Optional[ScanSession]:
        """Get session by ID."""
        return self.session.query(ScanSession).filter_by(id=session_id).first()

    def update(self, session_id: str, **kwargs) -> Optional[ScanSession]:
        """Update scan session."""
        session = self.get_by_id(session_id)
        if session:
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            self.session.commit()
        return session
