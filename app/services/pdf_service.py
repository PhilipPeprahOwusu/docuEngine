"""PDF Generation Service for Finalized Contracts"""
import io
from typing import Dict, Any, Optional
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from PyPDF2 import PdfReader, PdfWriter


class PDFService:
    """Handles generation of locked PDFs for approved contracts"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Header style
        self.styles.add(ParagraphStyle(
            name='CustomHeader',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0f172a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Subheader style
        self.styles.add(ParagraphStyle(
            name='CustomSubHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#475569'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))

        # Body style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            leading=16,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=12
        ))

        # Signature style
        self.styles.add(ParagraphStyle(
            name='SignatureBlock',
            parent=self.styles['Code'],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#334155'),
            fontName='Courier',
            leftIndent=20,
            rightIndent=20,
            spaceAfter=20
        ))

    def generate_locked_pdf(
        self,
        contract_data: Dict[str, Any],
        signature_data: Dict[str, Any],
        compliance_score: Optional[float] = None
    ) -> bytes:
        """
        Generate a locked PDF for an approved contract.

        Args:
            contract_data: Dictionary containing contract details
            signature_data: Digital signature data
            compliance_score: Optional compliance score

        Returns:
            PDF bytes that can be saved to file or S3
        """
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Build PDF content
        story = []

        # Header - Approved Contract Banner
        story.append(self._create_approval_banner())
        story.append(Spacer(1, 0.3 * inch))

        # Contract Details Table
        story.append(self._create_contract_details_table(contract_data, compliance_score))
        story.append(Spacer(1, 0.3 * inch))

        # Contract Content
        story.append(Paragraph("Contract Terms and Conditions", self.styles['CustomSubHeader']))
        contract_content = contract_data.get('content', 'No content available')
        # Split content into paragraphs
        for paragraph in contract_content.split('\n'):
            if paragraph.strip():
                story.append(Paragraph(paragraph, self.styles['CustomBody']))

        story.append(Spacer(1, 0.5 * inch))

        # Digital Signature Block
        story.append(self._create_signature_section(signature_data))

        # Build PDF
        doc.build(story)

        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()

        # Apply locking/encryption
        locked_pdf_bytes = self._apply_pdf_locking(pdf_bytes)

        return locked_pdf_bytes

    def _create_approval_banner(self):
        """Create the approval banner at the top of the PDF"""
        banner_style = ParagraphStyle(
            name='Banner',
            fontSize=18,
            textColor=colors.white,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=12
        )

        banner_table = Table(
            [[Paragraph("✓ APPROVED CONTRACT", banner_style)]],
            colWidths=[6.5 * inch]
        )

        banner_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#22c55e')),
            ('PADDING', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        return banner_table

    def _create_contract_details_table(
        self,
        contract_data: Dict[str, Any],
        compliance_score: Optional[float]
    ):
        """Create the contract details information table"""
        data = [
            ["Contract Title:", contract_data.get('filename', 'N/A')],
            ["Document ID:", contract_data.get('document_id', 'N/A')],
            ["Status:", "ACTIVE"],
            ["Uploaded By:", contract_data.get('creator_name', 'N/A')],
            ["Finalized By:", contract_data.get('finalizer_name', 'N/A')],
            ["Finalized On:", self._format_timestamp(contract_data.get('finalized_at'))],
        ]

        if compliance_score is not None:
            data.append(["Compliance Score:", f"{compliance_score:.1f}/10.0"])

        table = Table(data, colWidths=[2 * inch, 4.5 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#0f172a')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))

        return table

    def _create_signature_section(self, signature_data: Dict[str, Any]):
        """Create the digital signature section"""
        signature_text = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                   DIGITAL SIGNATURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Digitally Signed By: {signature_data.get('approver_name')}
Approver ID: {signature_data.get('approver_id')}
Signed On: {self._format_timestamp(signature_data.get('timestamp'))}

Verification Hash: {signature_data.get('verification_hash')}

This document has been digitally signed and approved.
Any modifications after signing will invalidate the signature.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return Paragraph(signature_text.replace('\n', '<br/>'), self.styles['SignatureBlock'])

    def _apply_pdf_locking(self, pdf_bytes: bytes) -> bytes:
        """
        Apply PDF permissions to lock the document against editing.
        Allows viewing and printing but prevents modification.
        """
        # Read the PDF
        input_pdf = PdfReader(io.BytesIO(pdf_bytes))
        output_pdf = PdfWriter()

        # Copy all pages
        for page in input_pdf.pages:
            output_pdf.add_page(page)

        # Apply encryption with permissions
        # Owner password allows full access, user password is empty (no password to open)
        # Permissions: allow printing but no modifications
        output_pdf.encrypt(
            user_password="",  # No password required to open
            owner_password="owner-password-change-in-production",  # Password for editing rights
            permissions_flag=0b0000_0100  # Allow printing only, no modifications
        )

        # Write to bytes
        output_buffer = io.BytesIO()
        output_pdf.write(output_buffer)
        locked_pdf_bytes = output_buffer.getvalue()
        output_buffer.close()

        return locked_pdf_bytes

    def _format_timestamp(self, timestamp) -> str:
        """Format timestamp for display"""
        if not timestamp:
            return "N/A"

        if isinstance(timestamp, str):
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except Exception:
                return timestamp
        else:
            dt = timestamp

        return dt.strftime("%B %d, %Y at %I:%M %p UTC")
