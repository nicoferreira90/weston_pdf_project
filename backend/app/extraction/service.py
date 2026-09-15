"""Deterministic extraction scoped to the supplied Spanish contract wording."""

import re
from collections.abc import Callable, Sequence

from app.extraction.models import ExtractionResponse, ExtractionResult, FieldId
from app.extraction.pdf import read_pdf_text


def _match_value(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(1).strip() if match else None


def _purchaser_name(text: str) -> str | None:
    return _match_value(
        r"\bcomparecen\s*:?\s*(?:(?:don|doña)\s+)?"
        r"([^,]+),\s*como\s+comprador(?:a)?\b",
        text,
    )


def _purchase_price(text: str) -> str | None:
    return _match_value(
        r"\bel precio total prometido para la compraventa es de\s+"
        r"((?:UF|CLP|USD)\s+\d+(?:[.,]\d+)*)\b",
        text,
    )


def _contract_date(text: str) -> str | None:
    return _match_value(
        r"\b(?:firmado el|fecha de firma:)\s+(\d{1,2} de [a-z]+ de \d{4})\b",
        text,
    )


def _property_address(text: str) -> str | None:
    # Stop at the sentence boundary, preserving common address abbreviations.
    return _match_value(
        r"\bla vendedora promete vender\s+[^.]*?\bubicad[oa] en\s+"
        r"((?:\b(?:Av|Avda|Depto|Dpto)\.|[^.])+)\.",
        text,
    )


_EXTRACTORS: dict[FieldId, Callable[[str], str | None]] = {
    FieldId.PURCHASER_NAME: _purchaser_name,
    FieldId.PURCHASE_PRICE: _purchase_price,
    FieldId.CONTRACT_DATE: _contract_date,
    FieldId.PROPERTY_ADDRESS: _property_address,
}


def extract_fields(
    document: bytes, selected_fields: Sequence[FieldId]
) -> ExtractionResponse:
    """Extract a validated selection in order; PDF/processing errors propagate."""
    text = " ".join(read_pdf_text(document).split())
    results = []
    for field_id in selected_fields:
        value = _EXTRACTORS[field_id](text)
        results.append(
            ExtractionResult(
                field_id=field_id,
                status="missing" if value is None else "found",
                value=value,
            )
        )
    return ExtractionResponse(results=results)
