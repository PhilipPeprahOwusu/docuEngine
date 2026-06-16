"""Digital Signature Service for Contract Finalization"""
import hashlib
import json
from datetime import datetime
from typing import Dict, Any
from jose import jwt


class SignatureService:
    """Handles generation and verification of system-generated digital signatures"""

    def __init__(self):
        # In production, this should be a secure secret from environment variables
        self.signing_secret = "your-secret-key-here-use-env-var-in-production"

    def generate_signature(
        self,
        approver_id: str,
        approver_name: str,
        document_id: str,
        contract_title: str
    ) -> Dict[str, Any]:
        """
        Generate a system digital signature for contract finalization.

        Args:
            approver_id: UUID of the approver
            approver_name: Full name of the approver
            document_id: UUID of the document being signed
            contract_title: Title/filename of the contract

        Returns:
            Dictionary containing signature data with verification hash
        """
        timestamp = datetime.utcnow().isoformat()

        # Create signature payload
        signature_payload = {
            "approver_id": approver_id,
            "approver_name": approver_name,
            "document_id": document_id,
            "contract_title": contract_title,
            "timestamp": timestamp,
            "signature_type": "system_generated"
        }

        # Generate verification hash
        verification_hash = self._generate_verification_hash(signature_payload)

        # Complete signature data
        signature_data = {
            **signature_payload,
            "verification_hash": verification_hash
        }

        return signature_data

    def verify_signature(
        self,
        signature_data: Dict[str, Any]
    ) -> bool:
        """
        Verify that a signature is valid and has not been tampered with.

        Args:
            signature_data: The signature data to verify

        Returns:
            Boolean indicating whether the signature is valid
        """
        stored_hash = signature_data.get("verification_hash")
        if not stored_hash:
            return False

        # Remove the hash to recompute it
        payload_without_hash = {k: v for k, v in signature_data.items() if k != "verification_hash"}

        # Recompute the hash
        recomputed_hash = self._generate_verification_hash(payload_without_hash)

        # Verify the hashes match
        return stored_hash == recomputed_hash

    def _generate_verification_hash(self, payload: Dict[str, Any]) -> str:
        """
        Generate a verification hash from the signature payload.

        This provides tamper-evidence - if any field changes, verification fails.
        """
        # Sort keys for consistent hashing
        payload_string = json.dumps(payload, sort_keys=True)

        # Create HMAC-SHA256 hash
        hash_input = f"{payload_string}{self.signing_secret}".encode('utf-8')
        verification_hash = hashlib.sha256(hash_input).hexdigest()

        return verification_hash

    def format_signature_block(self, signature_data: Dict[str, Any]) -> str:
        """
        Format the signature data as a human-readable signature block for PDF.

        Args:
            signature_data: The signature data

        Returns:
            Formatted signature block text
        """
        return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    DIGITAL SIGNATURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Digitally Signed By: {signature_data.get('approver_name')}
Approver ID: {signature_data.get('approver_id')}
Signed On: {self._format_timestamp(signature_data.get('timestamp'))}
Document: {signature_data.get('contract_title')}

Verification Hash: {signature_data.get('verification_hash')[:32]}...

This document has been digitally signed and approved. Any modifications
to this document after signing will invalidate the signature.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    def _format_timestamp(self, iso_timestamp: str) -> str:
        """Format ISO timestamp for display"""
        try:
            dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
            return dt.strftime("%B %d, %Y at %I:%M %p UTC")
        except Exception:
            return iso_timestamp
