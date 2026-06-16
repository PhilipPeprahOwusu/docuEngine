"""Contract Finalization Workflow Service"""
import os
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.document import Document
from app.models.user import User
from app.models.policy_exception import PolicyException
from app.models.audit_log import AuditLog
from app.services.signature_service import SignatureService
from app.services.pdf_service import PDFService
from app.services.notification_service import NotificationService


class FinalizationService:
    """Handles the complete contract finalization workflow"""

    def __init__(self, db: Session):
        self.db = db
        self.signature_service = SignatureService()
        self.pdf_service = PDFService()
        self.notification_service = NotificationService(db_session=db)

    def finalize_contract(
        self,
        document_id: str,
        approver: User
    ) -> Dict[str, Any]:
        """
        Finalize a contract - orchestrates the complete finalization workflow.

        Steps:
        1. Verify all exceptions are approved
        2. Generate digital signature
        3. Create locked PDF
        4. Store PDF
        5. Update contract status to active
        6. Record finalization details
        7. Send notifications to Approver and Reviewer
        8. Write audit log entry

        Args:
            document_id: UUID of the document to finalize
            approver: User performing the finalization

        Returns:
            Dictionary with finalization results

        Raises:
            ValueError: If contract cannot be finalized
        """
        # Get the document
        document = self.db.query(Document).filter(
            Document.document_id == document_id
        ).first()

        if not document:
            raise ValueError(f"Document {document_id} not found")

        # Verify all exceptions are approved
        self._verify_exceptions_approved(document_id)

        # Get the original creator
        creator = self.db.query(User).filter(
            User.user_id == document.created_by
        ).first()

        # Step 1: Generate digital signature
        signature_data = self.signature_service.generate_signature(
            approver_id=str(approver.user_id),
            approver_name=approver.name,
            document_id=str(document_id),
            contract_title=document.filename
        )

        # Step 2: Generate locked PDF
        contract_data = {
            'document_id': str(document.document_id),
            'filename': document.filename,
            'content': document.content,
            'creator_name': creator.name if creator else 'Unknown',
            'finalizer_name': approver.name,
            'finalized_at': datetime.utcnow().isoformat()
        }

        # Calculate compliance score (mock for now - would come from policy engine)
        compliance_score = self._calculate_compliance_score(document_id)

        pdf_bytes = self.pdf_service.generate_locked_pdf(
            contract_data=contract_data,
            signature_data=signature_data,
            compliance_score=compliance_score
        )

        # Step 3: Store PDF (in production, upload to S3)
        pdf_url = self._store_pdf(document_id, pdf_bytes)

        # Step 4: Update document with finalization details
        document.status = "active"
        document.finalized_by = approver.user_id
        document.finalized_at = datetime.utcnow()
        document.signature_data = signature_data
        document.final_pdf_url = pdf_url

        self.db.commit()
        self.db.refresh(document)

        # Step 5: Send notifications to both Approver and Reviewer
        self._send_finalization_notifications(
            document=document,
            approver=approver,
            reviewer=creator,
            pdf_url=pdf_url,
            compliance_score=compliance_score
        )

        # Step 6: Write audit log
        self._write_audit_log(
            document_id=document_id,
            approver_id=str(approver.user_id),
            action="contract_finalized"
        )

        return {
            "document_id": str(document.document_id),
            "status": "active",
            "finalized_by": approver.name,
            "finalized_at": document.finalized_at.isoformat(),
            "signature_hash": signature_data.get("verification_hash"),
            "pdf_url": pdf_url,
            "compliance_score": compliance_score
        }

    def _verify_exceptions_approved(self, document_id: str):
        """Verify that all policy exceptions for this document are approved"""
        pending_exceptions = self.db.query(PolicyException).filter(
            PolicyException.document_id == document_id,
            PolicyException.status == "pending"
        ).count()

        if pending_exceptions > 0:
            raise ValueError(
                f"Cannot finalize: {pending_exceptions} policy exception(s) are still pending approval"
            )

        rejected_exceptions = self.db.query(PolicyException).filter(
            PolicyException.document_id == document_id,
            PolicyException.status == "rejected"
        ).count()

        if rejected_exceptions > 0:
            raise ValueError(
                f"Cannot finalize: {rejected_exceptions} policy exception(s) were rejected"
            )

    def _calculate_compliance_score(self, document_id: str) -> float:
        """Calculate the compliance score for the document"""
        # Mock implementation - in production, this would call the policy engine
        # For now, return a high score since all exceptions are approved
        return 9.2

    def _store_pdf(self, document_id: str, pdf_bytes: bytes) -> str:
        """
        Store the PDF file.

        In production, this would upload to S3.
        For now, store locally in a pdfs directory.
        """
        # Create pdfs directory if it doesn't exist
        pdf_dir = "pdfs"
        os.makedirs(pdf_dir, exist_ok=True)

        # Generate filename
        filename = f"contract_{document_id}_finalized.pdf"
        filepath = os.path.join(pdf_dir, filename)

        # Write PDF to file
        with open(filepath, 'wb') as f:
            f.write(pdf_bytes)

        # Return the URL/path
        # In production, this would be an S3 URL
        return f"/pdfs/{filename}"

    def _send_finalization_notifications(
        self,
        document: Document,
        approver: User,
        reviewer: Optional[User],
        pdf_url: str,
        compliance_score: float
    ):
        """Send finalization notifications to both Approver and Reviewer"""
        notification_data = {
            "contract_title": document.filename,
            "document_id": str(document.document_id),
            "approved_by": approver.name,
            "approval_date": document.finalized_at.strftime("%B %d, %Y"),
            "compliance_score": compliance_score,
            "status": "active",
            "pdf_url": pdf_url
        }

        # Send to Approver (primary recipient)
        self._send_notification_to_user(approver, notification_data, is_primary=True)

        # Send to Reviewer (copy)
        if reviewer and reviewer.user_id != approver.user_id:
            self._send_notification_to_user(reviewer, notification_data, is_primary=False)

    def _send_notification_to_user(
        self,
        user: User,
        notification_data: Dict[str, Any],
        is_primary: bool
    ):
        """Send notification to a specific user via their preferred channels"""
        # Get user notification preferences
        prefs = self.notification_service._get_notification_preferences(str(user.user_id))

        message_type = "primary" if is_primary else "copy"

        # Send via enabled channels
        if prefs.get("slack_enabled"):
            self._send_slack_finalization(user, notification_data, message_type)

        if prefs.get("email_enabled"):
            self._send_email_finalization(user, notification_data, message_type)

        if prefs.get("discord_enabled"):
            self._send_discord_finalization(user, notification_data, message_type)

    def _send_slack_finalization(
        self,
        user: User,
        notification_data: Dict[str, Any],
        message_type: str
    ):
        """Send Slack notification for finalization"""
        # Mock implementation - would use Slack SDK
        print(f"[SLACK] Sending finalization notice ({message_type}) to {user.name}")
        # Log the notification
        from app.models.notification_audit import NotificationAudit
        notification = NotificationAudit(
            notification_id=uuid.uuid4(),
            org_id=str(user.org_id),
            supervisor_id=str(user.user_id),
            event_type="contract_finalized",
            channel="slack",
            status="sent",
            exception_id=None,
            sent_at=datetime.utcnow()
        )
        self.db.add(notification)
        self.db.commit()

    def _send_email_finalization(
        self,
        user: User,
        notification_data: Dict[str, Any],
        message_type: str
    ):
        """Send email notification for finalization"""
        # Mock implementation - would use SMTP or AWS SES
        print(f"[EMAIL] Sending finalization notice ({message_type}) to {user.email}")
        # Log the notification
        from app.models.notification_audit import NotificationAudit
        notification = NotificationAudit(
            notification_id=uuid.uuid4(),
            org_id=str(user.org_id),
            supervisor_id=str(user.user_id),
            event_type="contract_finalized",
            channel="email",
            status="sent",
            exception_id=None,
            sent_at=datetime.utcnow()
        )
        self.db.add(notification)
        self.db.commit()

    def _send_discord_finalization(
        self,
        user: User,
        notification_data: Dict[str, Any],
        message_type: str
    ):
        """Send Discord notification for finalization"""
        # Mock implementation - would use Discord SDK
        print(f"[DISCORD] Sending finalization notice ({message_type}) to {user.name}")
        # Log the notification
        from app.models.notification_audit import NotificationAudit
        notification = NotificationAudit(
            notification_id=uuid.uuid4(),
            org_id=str(user.org_id),
            supervisor_id=str(user.user_id),
            event_type="contract_finalized",
            channel="discord",
            status="sent",
            exception_id=None,
            sent_at=datetime.utcnow()
        )
        self.db.add(notification)
        self.db.commit()

    def _write_audit_log(
        self,
        document_id: str,
        approver_id: str,
        action: str
    ):
        """Write an audit log entry for the finalization"""
        audit_log = AuditLog(
            log_id=uuid.uuid4(),
            org_id=self.db.query(Document).filter(
                Document.document_id == document_id
            ).first().org_id,
            user_id=approver_id,
            action=action,
            resource_type="document",
            resource_id=document_id,
            details={"action": action, "document_id": document_id},
            timestamp=datetime.utcnow()
        )

        self.db.add(audit_log)
        self.db.commit()
