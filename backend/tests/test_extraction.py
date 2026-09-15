from io import BytesIO
from pathlib import Path
from unittest.mock import Mock

import pytest
from pydantic import ValidationError
from pypdf import PdfWriter

from app.extraction import service
from app.extraction.models import ExtractionResult, FieldId
from app.extraction.pdf import DocumentProcessingError

SAMPLE_DOCUMENTS = Path(__file__).resolve().parents[2] / "sample-documents"


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        (
            "complete-purchase-contract.pdf",
            {
                "purchaser_name": "Ana María Pérez Soto",
                "purchase_price": "UF 8.500",
                "contract_date": "1 de septiembre de 2026",
                "property_address": (
                    "Avenida Apoquindo 4500, departamento 1201, "
                    "comuna de Las Condes, Santiago"
                ),
            },
        ),
        (
            "missing-property-address.pdf",
            {
                "purchaser_name": "Diego Andrés Morales Vega",
                "purchase_price": "UF 6.250",
                "contract_date": "10 de septiembre de 2026",
                "property_address": None,
            },
        ),
        (
            "missing-price-and-date.pdf",
            {
                "purchaser_name": "Camila Fernanda Rojas Silva",
                "purchase_price": None,
                "contract_date": None,
                "property_address": (
                    "Pasaje Los Alerces 1840, comuna de Ñuñoa, Santiago"
                ),
            },
        ),
    ],
)
def test_supplied_contract_values(filename, expected):
    response = service.extract_fields(
        (SAMPLE_DOCUMENTS / filename).read_bytes(), list(FieldId)
    )

    assert response.model_dump(mode="json") == {
        "results": [
            {
                "field_id": field_id,
                "status": "missing" if value is None else "found",
                "value": value,
            }
            for field_id, value in expected.items()
        ]
    }


def test_only_selected_matcher_runs_and_pdf_is_read_once(monkeypatch):
    selected_matcher = Mock(wraps=service._EXTRACTORS[FieldId.PURCHASE_PRICE])
    reader = Mock(wraps=service.read_pdf_text)
    monkeypatch.setattr(service, "read_pdf_text", reader)
    for field_id in FieldId:
        matcher = (
            selected_matcher
            if field_id == FieldId.PURCHASE_PRICE
            else Mock(side_effect=AssertionError("Unselected matcher was called"))
        )
        monkeypatch.setitem(service._EXTRACTORS, field_id, matcher)

    response = service.extract_fields(
        (SAMPLE_DOCUMENTS / "complete-purchase-contract.pdf").read_bytes(),
        [FieldId.PURCHASE_PRICE],
    )

    assert response.model_dump(mode="json") == {
        "results": [
            {"field_id": "purchase_price", "status": "found", "value": "UF 8.500"}
        ]
    }
    reader.assert_called_once()
    selected_matcher.assert_called_once()


def test_mixed_subset_keeps_request_order_and_independent_results():
    document = (SAMPLE_DOCUMENTS / "missing-price-and-date.pdf").read_bytes()
    selection = [FieldId.CONTRACT_DATE, FieldId.PURCHASER_NAME]
    first = service.extract_fields(document, selection)
    selection.reverse()
    second = service.extract_fields(document, selection)

    assert first.model_dump(mode="json") == {
        "results": [
            {"field_id": "contract_date", "status": "missing", "value": None},
            {
                "field_id": "purchaser_name",
                "status": "found",
                "value": "Camila Fernanda Rojas Silva",
            },
        ]
    }
    assert [result.field_id for result in second.results] == selection


@pytest.mark.parametrize(
    ("price", "signing_label", "next_heading"),
    [
        ("CLP 125.000.000", "FIRMADO EL", "SEGUNDO - Precio"),
        ("USD 250,000.50", "Fecha de firma:", "SEGUNDO - Pago"),
    ],
)
def test_changed_values_and_explicit_currency_in_same_wording(
    monkeypatch, price, signing_label, next_heading
):
    text = f"""
        Documento preparado el 2 de enero de 2024.
        Comparecen: don Javier Ignacio Muñoz
        Díaz, como comprador, y Inmobiliaria del Valle, como vendedora.
        Domicilio de la vendedora: Calle Norte 900, Santiago.
        PRIMERO - Propiedad
        La vendedora promete vender la vivienda ubicada en Av. del Bosque 321,
        departamento 8, comuna de La Reina, Santiago.
        El inmueble incluye bodega.
        {next_heading}
        Anticipo: UF 100.
        El precio total prometido para la compraventa es de {price},
        que el comprador pagará según lo acordado.
        TERCERO - Acuerdo
        {signing_label} 14 de octubre de 2026.
    """
    monkeypatch.setattr(service, "read_pdf_text", lambda document: text)

    response = service.extract_fields(b"unused by the fake reader", list(FieldId))

    assert [result.status for result in response.results] == ["found"] * 4
    assert [result.value for result in response.results] == [
        "Javier Ignacio Muñoz Díaz",
        price,
        "14 de octubre de 2026",
        "Av. del Bosque 321, departamento 8, comuna de La Reina, Santiago",
    ]


def test_pending_signing_date_does_not_use_unrelated_date(monkeypatch):
    text = """
        En Santiago de Chile, a 3 de marzo de 2026, se prepara este borrador.
        Las partes firmarán el contrato definitivo cuando corresponda.
        Fecha de firma: pendiente.
    """
    monkeypatch.setattr(service, "read_pdf_text", lambda document: text)

    response = service.extract_fields(
        b"unused by the fake reader", [FieldId.CONTRACT_DATE]
    )

    assert response.model_dump(mode="json") == {
        "results": [{"field_id": "contract_date", "status": "missing", "value": None}]
    }


def test_textless_pdf_is_a_processing_error():
    with BytesIO() as stream, PdfWriter() as writer:
        writer.add_blank_page(width=612, height=792)
        writer.write(stream)
        document = stream.getvalue()

    with pytest.raises(DocumentProcessingError, match="extractable text"):
        service.extract_fields(document, list(FieldId))


def test_readable_text_without_selected_values_returns_missing(monkeypatch):
    monkeypatch.setattr(
        service, "read_pdf_text", lambda document: "Este documento es una nota general."
    )

    response = service.extract_fields(b"unused by the fake reader", list(FieldId))

    assert [result.field_id for result in response.results] == list(FieldId)
    assert all(result.status == "missing" for result in response.results)
    assert all(result.value is None for result in response.results)


@pytest.mark.parametrize(("status", "value"), [("found", "   "), ("missing", "UF 1")])
def test_result_rejects_inconsistent_status_and_value(status, value):
    with pytest.raises(ValidationError):
        ExtractionResult(field_id=FieldId.PURCHASE_PRICE, status=status, value=value)
