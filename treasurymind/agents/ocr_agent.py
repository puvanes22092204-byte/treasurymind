"""OCR + Document Extraction Agent - extracts payment data from receipts/PDFs."""
import re
from typing import Dict, Any, List
from PIL import Image
import io

try:
    import pytesseract
except ImportError:
    pytesseract = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None


class OCRAgent:
    """Extracts structured payment data from images and PDFs."""

    def extract_from_image(self, image_file) -> Dict[str, Any]:
        """Extract payment info from a receipt image."""
        if pytesseract is None:
            return self._mock_extraction("image")

        try:
            image = Image.open(image_file)
            text = pytesseract.image_to_string(image)
            return self._parse_text(text)
        except Exception as e:
            return {"error": str(e), "raw_text": ""}

    def extract_from_pdf(self, pdf_file) -> List[Dict[str, Any]]:
        """Extract payment info from a PDF invoice."""
        if pdfplumber is None:
            return [self._mock_extraction("pdf")]

        try:
            results = []
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    parsed = self._parse_text(text)
                    if parsed.get("amount"):
                        results.append(parsed)
            return results if results else [self._mock_extraction("pdf")]
        except Exception as e:
            return [{"error": str(e)}]

    def _parse_text(self, text: str) -> Dict[str, Any]:
        """Parse extracted text to find payment details."""
        result = {
            "raw_text": text,
            "amount": self._find_amount(text),
            "currency": self._find_currency(text),
            "date": self._find_date(text),
            "reference": self._find_reference(text),
            "payer": self._find_payer(text),
        }
        return result

    def _find_amount(self, text: str) -> float:
        patterns = [
            r"(?:RM|MYR|USD|EUR|GBP|SGD)\s*([\d,]+\.?\d*)",
            r"([\d,]+\.?\d*)\s*(?:RM|MYR|USD|EUR|GBP|SGD)",
            r"(?:Total|Amount|Sum|Grand Total)[:\s]*([\d,]+\.?\d*)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1).replace(",", ""))
        return 0.0

    def _find_currency(self, text: str) -> str:
        currencies = ["USD", "EUR", "GBP", "SGD", "AUD", "JPY", "CNY", "MYR", "RM"]
        for cur in currencies:
            if cur in text.upper():
                return "MYR" if cur == "RM" else cur
        return "MYR"

    def _find_date(self, text: str) -> str:
        patterns = [
            r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"(\d{4}[/-]\d{1,2}[/-]\d{1,2})",
            r"(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4})",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return ""

    def _find_reference(self, text: str) -> str:
        patterns = [
            r"(?:Ref|Reference|Invoice|INV)[:\s#-]*([A-Za-z0-9-]+)",
            r"(?:Transaction|TXN|Trans)[:\s#-]*([A-Za-z0-9-]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return ""

    def _find_payer(self, text: str) -> str:
        patterns = [
            r"(?:From|Sender|Payer|Remitter)[:\s]*(.+?)(?:\n|$)",
            r"(?:Company|Client)[:\s]*(.+?)(?:\n|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""

    def _mock_extraction(self, source: str) -> Dict[str, Any]:
        """Return mock data when OCR libraries unavailable."""
        return {
            "amount": 10.00,
            "currency": "USD",
            "date": "2025-05-15",
            "reference": "INV-001",
            "payer": "Sample Client",
            "raw_text": f"[Mock extraction from {source}]",
        }
