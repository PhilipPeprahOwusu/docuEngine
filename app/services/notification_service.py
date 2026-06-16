"""Multi-Channel Notification Service (Slack, Email, Discord)"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


class NotificationService:
    """Handles multi-channel notifications for supervisor approvals"""

    def __init__(self, db_session=None):
        self.db = db_session

    def send_exception_approval(
        self,
        exception_id: str,
        violations: List[Dict[str, Any]],
        custom_context: str,
        org_id: str
    ):
        """
        Send approval notification across all configured channels.
        """
        # Get supervisor preferences
        supervisors = self._get_supervisors(org_id)

        for supervisor in supervisors:
            prefs = self._get_notification_preferences(supervisor["user_id"])

            if prefs.get("slack_enabled"):
                self._send_slack_notification(
                    supervisor,
                    exception_id,
                    violations,
                    custom_context
                )

            if prefs.get("email_enabled"):
                self._send_email_notification(
                    supervisor,
                    exception_id,
                    violations,
                    custom_context
                )

            if prefs.get("discord_enabled"):
                self._send_discord_notification(
                    supervisor,
                    exception_id,
                    violations,
                    custom_context
                )

    def _send_slack_notification(
        self,
        supervisor: Dict[str, Any],
        exception_id: str,
        violations: List[Dict[str, Any]],
        custom_context: str
    ):
        """Send Slack notification with interactive buttons"""
        # Mock implementation - would use Slack SDK
        print(f"[SLACK] Sending to {supervisor['name']}")

        message = self._build_slack_message(
            exception_id,
            violations,
            custom_context,
            supervisor
        )

        # Would call Slack API here
        # client.chat_postMessage(channel=channel_id, blocks=message["blocks"])

        # Log notification
        self._log_notification(
            supervisor["user_id"],
            "slack",
            exception_id,
            "sent"
        )

    def _build_slack_message(
        self,
        exception_id: str,
        violations: List[Dict[str, Any]],
        custom_context: str,
        supervisor: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build Slack message with blocks"""
        violation = violations[0] if violations else {}

        return {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚨 Policy Exception Approval Needed"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Contract*\n{violation.get('contract_name', 'Unknown')}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Issue*\n{violation.get('violation_type', 'N/A')}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Severity*\n{violation.get('severity', 'MEDIUM')}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Policy Requirement:*\n\"{violation.get('policy_quote', '')}\"\n\n*Contract States:*\n\"{violation.get('violation_text', '')}\"\n\n*Reason:*\n{custom_context}"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "✅ Approve"},
                            "value": f"approve_{exception_id}",
                            "action_id": "approve_exception",
                            "style": "primary"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "❌ Reject"},
                            "value": f"reject_{exception_id}",
                            "action_id": "reject_exception",
                            "style": "danger"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "👀 Full Details"},
                            "value": f"review_{exception_id}",
                            "action_id": "review_exception"
                        }
                    ]
                }
            ]
        }

    def _send_email_notification(
        self,
        supervisor: Dict[str, Any],
        exception_id: str,
        violations: List[Dict[str, Any]],
        custom_context: str
    ):
        """Send email notification"""
        print(f"[EMAIL] Sending to {supervisor['email']}")

        html_body = self._build_email_html(
            exception_id,
            violations,
            custom_context,
            supervisor
        )

        # Would use SMTP or AWS SES here
        # send_email(to=supervisor['email'], subject="...", html=html_body)

        self._log_notification(
            supervisor["user_id"],
            "email",
            exception_id,
            "sent"
        )

    def _build_email_html(
        self,
        exception_id: str,
        violations: List[Dict[str, Any]],
        custom_context: str,
        supervisor: Dict[str, Any]
    ) -> str:
        """Build HTML email template"""
        violation = violations[0] if violations else {}

        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #d32f2f;">🚨 Policy Exception Approval Needed</h2>
                <p>Hi <strong>{supervisor.get('name', 'there')}</strong>,</p>
                <p>A contract exception needs your approval.</p>

                <div style="background: #f5f5f5; padding: 15px; border-left: 4px solid #d32f2f; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Contract: {violation.get('contract_name', 'Unknown')}</h3>
                    <p><strong>Issue:</strong> {violation.get('violation_type', 'N/A')}</p>
                    <p><strong>Severity:</strong> {violation.get('severity', 'MEDIUM')}</p>
                </div>

                <div style="background: #fff9c4; padding: 15px; border-left: 4px solid #fbc02d; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Policy Citation</h3>
                    <p><strong>Policy:</strong> {violation.get('policy_name', 'N/A')}</p>
                    <p><strong>Section:</strong> {violation.get('policy_section', 'N/A')}</p>
                    <p><em>"{violation.get('policy_quote', '')}"</em></p>
                </div>

                <div style="background: #e3f2fd; padding: 15px; border-left: 4px solid #1976d2; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Contract Violation</h3>
                    <p><strong>Section:</strong> {violation.get('contract_section', 'N/A')}</p>
                    <p><em>"{violation.get('violation_text', '')}"</em></p>
                </div>

                <div style="margin: 20px 0;">
                    <p><strong>Reason for Exception:</strong> {custom_context}</p>
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:8000/exceptions/{exception_id}/approve"
                       style="background: #28a745; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 0 10px;">
                        ✅ Approve Exception
                    </a>
                    <a href="http://localhost:8000/exceptions/{exception_id}/reject"
                       style="background: #dc3545; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 0 10px;">
                        ❌ Reject
                    </a>
                </div>

                <hr style="margin: 30px 0;">
                <p style="font-size: 12px; color: #999;">
                    Request ID: {exception_id}
                </p>
            </div>
        </body>
        </html>
        """

    def _send_discord_notification(
        self,
        supervisor: Dict[str, Any],
        exception_id: str,
        violations: List[Dict[str, Any]],
        custom_context: str
    ):
        """Send Discord notification with embed"""
        print(f"[DISCORD] Sending to {supervisor['name']}")

        embed = self._build_discord_embed(
            exception_id,
            violations,
            custom_context
        )

        # Would use Discord SDK here
        # webhook.send(embed=embed)

        self._log_notification(
            supervisor["user_id"],
            "discord",
            exception_id,
            "sent"
        )

    def _build_discord_embed(
        self,
        exception_id: str,
        violations: List[Dict[str, Any]],
        custom_context: str
    ) -> Dict[str, Any]:
        """Build Discord embed message"""
        violation = violations[0] if violations else {}

        return {
            "title": "🚨 Policy Exception Approval Needed",
            "color": 0xd32f2f,
            "fields": [
                {
                    "name": "Contract",
                    "value": violation.get("contract_name", "Unknown"),
                    "inline": True
                },
                {
                    "name": "Severity",
                    "value": violation.get("severity", "MEDIUM"),
                    "inline": True
                },
                {
                    "name": "Policy Requirement",
                    "value": f"\"{violation.get('policy_quote', '')}\"",
                    "inline": False
                },
                {
                    "name": "Contract States",
                    "value": f"\"{violation.get('violation_text', '')}\"",
                    "inline": False
                },
                {
                    "name": "Reason for Exception",
                    "value": custom_context,
                    "inline": False
                }
            ],
            "footer": {
                "text": f"Exception ID: {exception_id}"
            }
        }

    def _get_supervisors(self, org_id: str) -> List[Dict[str, Any]]:
        """Get list of supervisors for an organization"""
        if not self.db:
            return [{
                "user_id": "user_123",
                "name": "John Supervisor",
                "email": "john@example.com"
            }]

        from app.models.user import User

        supervisors = self.db.query(User).filter(
            User.org_id == org_id,
            User.role.in_(["approver", "admin"]),
            User.is_active == True
        ).all()

        return [
            {
                "user_id": str(s.user_id),
                "name": s.name,
                "email": s.email
            }
            for s in supervisors
        ]

    def _get_notification_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user's notification preferences"""
        if not self.db:
            return {
                "slack_enabled": True,
                "email_enabled": True,
                "discord_enabled": False
            }

        from app.models.notification_preference import NotificationPreference

        prefs = self.db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id
        ).first()

        if not prefs:
            return {
                "slack_enabled": True,
                "email_enabled": True,
                "discord_enabled": False
            }

        return {
            "slack_enabled": prefs.slack_enabled,
            "email_enabled": prefs.email_enabled,
            "discord_enabled": prefs.discord_enabled
        }

    def _log_notification(
        self,
        supervisor_id: str,
        channel: str,
        exception_id: str,
        status: str
    ):
        """Log notification to audit table"""
        if not self.db:
            return

        from app.models.notification_audit import NotificationAudit

        notification = NotificationAudit(
            notification_id=uuid.uuid4(),
            org_id="org_id",  # Would get from exception
            supervisor_id=supervisor_id,
            event_type="exception_approval",
            channel=channel,
            status=status,
            exception_id=exception_id,
            sent_at=datetime.utcnow()
        )

        self.db.add(notification)
        self.db.commit()
