"""PDF annotation and report generation using ReportLab."""

import io
from typing import Dict, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.pdfgen import canvas

from contract_risk_scorer.scoring.risk_engine import RiskScore


class PDFAnnotator:
    """Generate annotated PDF reports with risk scores."""

    RISK_COLORS = {
        "LOW": colors.HexColor("#00B050"),  # Green
        "MEDIUM": colors.HexColor("#FFC000"),  # Yellow
        "HIGH": colors.HexColor("#FF6B00"),  # Orange
        "CRITICAL": colors.HexColor("#C00000"),  # Red
    }

    def __init__(self):
        """Initialize PDF annotator."""
        pass

    def generate_report(
        self,
        contract_id: str,
        risk_scores: List[RiskScore],
        overall_score: int,
        risk_distribution: Dict,
    ) -> bytes:
        """
        Generate annotated PDF report.

        Args:
            contract_id: Contract identifier
            risk_scores: List of RiskScore objects
            overall_score: Overall contract risk score (0-100)
            risk_distribution: Dict with count of each risk level

        Returns:
            PDF bytes
        """
        # Create PDF in memory
        pdf_buffer = io.BytesIO()

        # Create document
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            rightMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
        )

        # Build story (content)
        story = []

        # Add executive summary
        story.extend(self._build_executive_summary(risk_scores, overall_score, risk_distribution))

        story.append(PageBreak())

        # Add detailed clause analysis
        story.extend(self._build_clause_analysis(risk_scores))

        # Add footer
        story.append(Spacer(1, 0.5 * inch))
        story.append(self._build_footer())

        # Build PDF
        doc.build(story)

        # Get PDF bytes
        pdf_bytes = pdf_buffer.getvalue()
        pdf_buffer.close()

        return pdf_bytes

    def _build_executive_summary(
        self, risk_scores: List[RiskScore], overall_score: int, risk_distribution: Dict
    ) -> List:
        """
        Build executive summary section.

        Args:
            risk_scores: List of risk scores
            overall_score: Overall score
            risk_distribution: Risk distribution

        Returns:
            List of Platypus elements
        """
        story = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#1F4E78"),
            spaceAfter=12,
            alignment=1,  # Center
        )
        story.append(Paragraph("CONTRACT RISK ASSESSMENT REPORT", title_style))
        story.append(Spacer(1, 0.2 * inch))

        # Overall Risk Score
        risk_level = self._get_risk_level_from_score(overall_score)
        risk_color = self.RISK_COLORS.get(risk_level, colors.black)

        score_style = ParagraphStyle(
            "ScoreStyle",
            parent=styles["Heading2"],
            fontSize=18,
            textColor=risk_color,
            spaceAfter=6,
        )
        story.append(
            Paragraph(f"Overall Risk Score: {overall_score}/100 ({risk_level})", score_style)
        )
        story.append(Spacer(1, 0.2 * inch))

        # Risk Distribution Table
        distribution_data = [
            ["Risk Level", "Count", "Percentage"],
            ["LOW", str(risk_distribution.get("LOW", 0)), self._get_percentage(risk_distribution, "LOW", risk_scores)],
            ["MEDIUM", str(risk_distribution.get("MEDIUM", 0)), self._get_percentage(risk_distribution, "MEDIUM", risk_scores)],
            ["HIGH", str(risk_distribution.get("HIGH", 0)), self._get_percentage(risk_distribution, "HIGH", risk_scores)],
            ["CRITICAL", str(risk_distribution.get("CRITICAL", 0)), self._get_percentage(risk_distribution, "CRITICAL", risk_scores)],
        ]

        dist_table = Table(distribution_data, colWidths=[1.5 * inch, 1 * inch, 1.5 * inch])
        dist_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(dist_table)
        story.append(Spacer(1, 0.3 * inch))

        # Critical Clauses Summary
        critical_clauses = [rs for rs in risk_scores if rs.risk_level == "CRITICAL"]

        if critical_clauses:
            heading_style = ParagraphStyle(
                "CriticalHeading",
                parent=styles["Heading3"],
                fontSize=14,
                textColor=self.RISK_COLORS["CRITICAL"],
                spaceAfter=6,
            )
            story.append(Paragraph(f"Critical Risk Clauses ({len(critical_clauses)})", heading_style))

            for clause in critical_clauses[:3]:  # Show top 3
                clause_text = f"• {clause.clause_type}: {clause.risk_reason[:100]}..."
                story.append(Paragraph(clause_text, styles["Normal"]))

            story.append(Spacer(1, 0.1 * inch))

        return story

    def _build_clause_analysis(self, risk_scores: List[RiskScore]) -> List:
        """
        Build detailed clause analysis.

        Args:
            risk_scores: List of risk scores

        Returns:
            List of Platypus elements
        """
        story = []
        styles = getSampleStyleSheet()

        heading_style = ParagraphStyle(
            "DetailHeading",
            parent=styles["Heading2"],
            fontSize=16,
            textColor=colors.HexColor("#1F4E78"),
            spaceAfter=12,
        )

        story.append(Paragraph("DETAILED CLAUSE ANALYSIS", heading_style))
        story.append(Spacer(1, 0.1 * inch))

        # Sort by risk level (CRITICAL first)
        risk_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        sorted_scores = sorted(risk_scores, key=lambda x: risk_order.get(x.risk_level, 4))

        for idx, risk_score in enumerate(sorted_scores, 1):
            # Clause header with color bar
            risk_color = self.RISK_COLORS.get(risk_score.risk_level, colors.black)

            clause_heading = f"{idx}. {risk_score.clause_type} - Page {risk_score.page_num}"
            clause_style = ParagraphStyle(
                f"ClauseStyle{idx}",
                parent=styles["Heading3"],
                fontSize=12,
                textColor=risk_color,
                spaceAfter=6,
                leftIndent=10,
            )
            story.append(Paragraph(clause_heading, clause_style))

            # Risk level badge
            risk_text = f"Risk Level: {risk_score.risk_level} | Confidence: {risk_score.confidence_score:.1%}"
            story.append(Paragraph(risk_text, styles["Normal"]))

            # Risk reason
            story.append(Paragraph("<b>Analysis:</b>", styles["Normal"]))
            story.append(Paragraph(risk_score.risk_reason[:300], styles["BodyText"]))

            # Benchmark position
            benchmark_text = f"<b>Market Position:</b> {risk_score.benchmark_position}"
            story.append(Paragraph(benchmark_text, styles["Normal"]))

            # Dispute flag
            if risk_score.dispute_prone:
                story.append(
                    Paragraph(
                        "<b style='color: red;'>⚠ This clause has been subject to litigation</b>",
                        styles["Normal"],
                    )
                )

            # Suggested revision
            story.append(Paragraph("<b>Suggested Revision:</b>", styles["Normal"]))
            story.append(Paragraph(risk_score.suggested_revision[:300], styles["BodyText"]))

            story.append(Spacer(1, 0.2 * inch))

            # Add page break every 4 clauses
            if (idx % 4) == 0 and idx < len(sorted_scores):
                story.append(PageBreak())

        return story

    def _build_footer(self) -> Paragraph:
        """
        Build footer.

        Returns:
            Footer paragraph
        """
        styles = getSampleStyleSheet()
        footer_style = ParagraphStyle(
            "FooterStyle",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.grey,
            alignment=1,  # Center
        )
        return Paragraph("Generated by Contract Risk Scorer | Confidential", footer_style)

    @staticmethod
    def _get_risk_level_from_score(score: int) -> str:
        """Get risk level from numeric score."""
        if score >= 80:
            return "CRITICAL"
        elif score >= 60:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        else:
            return "LOW"

    @staticmethod
    def _get_percentage(distribution: Dict, level: str, risk_scores: List[RiskScore]) -> str:
        """Calculate percentage for distribution."""
        if not risk_scores:
            return "0%"
        count = distribution.get(level, 0)
        percentage = (count / len(risk_scores)) * 100
        return f"{percentage:.1f}%"
