"""PDF parsing and text extraction using pypdf."""

import re
from typing import Dict, List

from pypdf import PdfReader


class PDFParser:
    """Extract text and metadata from PDF contracts."""

    def __init__(self):
        """Initialize PDF parser."""
        pass

    def parse_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Parse PDF and extract text with page information.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            List of dicts with {page_num, text, bbox}
        """
        results = []

        try:
            reader = PdfReader(pdf_path)
            total_pages = len(reader.pages)

            for page_num, page in enumerate(reader.pages, start=1):
                # Extract text from page
                text = page.extract_text()

                # Clean up text: remove extra whitespace and normalize
                text = self._clean_text(text)

                # Get page dimensions for bbox
                mediabox = page.mediabox
                bbox = {
                    "x0": float(mediabox.left),
                    "y0": float(mediabox.bottom),
                    "x1": float(mediabox.right),
                    "y1": float(mediabox.top),
                }

                results.append(
                    {
                        "page_num": page_num,
                        "text": text,
                        "bbox": bbox,
                        "total_pages": total_pages,
                    }
                )

        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")

        return results

    def extract_clauses_text(self, pdf_path: str) -> str:
        """
        Extract all text from PDF as single string.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Combined text from all pages
        """
        pages = self.parse_pdf(pdf_path)
        return "\n\n".join([page["text"] for page in pages])

    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Clean extracted text by removing artifacts and normalizing whitespace.

        Args:
            text: Raw text from PDF

        Returns:
            Cleaned text
        """
        # Remove form feed characters
        text = text.replace("\f", "")

        # Remove multiple consecutive newlines (normalize to max 2)
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Remove leading/trailing whitespace on each line
        lines = [line.rstrip() for line in text.split("\n")]
        text = "\n".join(lines)

        # Remove excessive spaces
        text = re.sub(r" {2,}", " ", text)

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    @staticmethod
    def strip_header_footer(text: str) -> str:
        """
        Attempt to remove header and footer content.

        Args:
            text: Text to process

        Returns:
            Text with headers/footers removed
        """
        lines = text.split("\n")

        # Simple heuristic: remove first 2 and last 2 lines if they're short
        if len(lines) > 4:
            # Check if first lines are headers (usually short)
            first_lines = lines[:2]
            if all(len(line) < 100 for line in first_lines):
                lines = lines[2:]

            # Check if last lines are footers (usually short)
            last_lines = lines[-2:]
            if all(len(line) < 100 for line in last_lines):
                lines = lines[:-2]

        return "\n".join(lines)
