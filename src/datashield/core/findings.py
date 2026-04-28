"""Finding management and queries."""

from typing import List, Optional
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session
from ..storage.database import Finding as FindingDB
from ..storage.repository import FindingRepository


class FindingService:
    """Service for managing findings."""

    def __init__(self, session: Session):
        """Initialize with database session."""
        self.repository = FindingRepository(session)
        self.session = session

    def create_finding(
        self,
        file_path: str,
        pattern_name: str,
        match_text: str,
        risk_score: float,
        confidence: float,
        session_id: str,
    ) -> FindingDB:
        """Create and store a finding.

        Args:
            file_path: Path to file where credential was found
            pattern_name: Name of pattern that matched
            match_text: The matched credential text
            risk_score: Risk score (0-1)
            confidence: Confidence level (0-1)
            session_id: Associated scan session ID

        Returns:
            Created finding object.
        """
        finding = FindingDB(
            id=str(uuid4()),
            session_id=session_id,
            file_path=file_path,
            pattern_name=pattern_name,
            match_text=match_text,
            risk_score=risk_score,
            confidence=confidence,
            found_at=datetime.utcnow(),
        )
        return self.repository.create(finding)

    def get_session_findings(self, session_id: str) -> List[FindingDB]:
        """Get all findings for a session.

        Args:
            session_id: Scan session ID

        Returns:
            List of findings.
        """
        return self.repository.get_by_session(session_id)

    def mark_as_false_positive(self, finding_id: str) -> Optional[FindingDB]:
        """Mark a finding as false positive.

        Args:
            finding_id: Finding ID

        Returns:
            Updated finding or None if not found.
        """
        return self.repository.update(finding_id, is_false_positive=True)

    def mark_as_encrypted(self, finding_id: str) -> Optional[FindingDB]:
        """Mark a finding as encrypted.

        Args:
            finding_id: Finding ID

        Returns:
            Updated finding or None if not found.
        """
        return self.repository.update(finding_id, encrypted=True)

    def get_high_risk_findings(self, session_id: str, threshold: float = 0.7) -> List[FindingDB]:
        """Get findings above risk threshold.

        Args:
            session_id: Scan session ID
            threshold: Risk score threshold

        Returns:
            List of high-risk findings.
        """
        all_findings = self.get_session_findings(session_id)
        return [f for f in all_findings if f.risk_score >= threshold]
