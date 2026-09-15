from pathlib import Path
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.api import extraction
from app.extraction.models import ExtractionResponse, ExtractionResult, FieldId
from app.extraction.pdf import DocumentProcessingError
from app.main import app

SAMPLE_DOCUMENTS = Path(__file__).resolve().parents[2] / "sample-documents"


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def document():
    return (SAMPLE_DOCUMENTS / "complete-purchase-contract.pdf").read_bytes()


def test_upload_extracts_only_selected_fields_from_renamed_pdf(client):
    document = (SAMPLE_DOCUMENTS / "missing-property-address.pdf").read_bytes()

    response = client.post(
        "/api/extractions",
        files={"file": ("renamed-contract.pdf", document, "application/pdf")},
        data={"selected_fields": ["property_address", "purchaser_name"]},
    )

    assert response.status_code == 200
    assert response.json() == {
        "results": [
            {"field_id": "property_address", "status": "missing", "value": None},
            {
                "field_id": "purchaser_name",
                "status": "found",
                "value": "Diego Andrés Morales Vega",
            },
        ]
    }


@pytest.mark.parametrize(
    "selection",
    [
        [],
        ["unknown_field"],
        ["purchase_price", "purchase_price"],
        [field.value for field in FieldId] + ["purchase_price"],
    ],
    ids=["empty", "unknown", "duplicate", "too-many"],
)
def test_invalid_selection_fails_before_extraction(
    client, document, monkeypatch, selection
):
    extract = Mock()
    monkeypatch.setattr(extraction, "extract_fields", extract)

    response = client.post(
        "/api/extractions",
        files={"file": ("contract.pdf", document, "application/pdf")},
        data={"selected_fields": selection},
    )

    assert response.status_code == 422
    assert "detail" in response.json()
    assert "results" not in response.json()
    extract.assert_not_called()


@pytest.mark.parametrize("include_file", [False, True], ids=["missing", "empty"])
def test_missing_or_empty_file_fails_before_extraction(
    client, monkeypatch, include_file
):
    extract = Mock()
    monkeypatch.setattr(extraction, "extract_fields", extract)

    response = client.post(
        "/api/extractions",
        files={"file": ("contract.pdf", b"", "application/pdf")}
        if include_file
        else None,
        data={"selected_fields": ["purchase_price"]},
    )

    assert response.status_code == 422
    assert "detail" in response.json()
    assert "results" not in response.json()
    extract.assert_not_called()


def test_successfully_processed_document_can_have_all_fields_missing(
    client, document, monkeypatch
):
    extract = Mock(
        return_value=ExtractionResponse(
            results=[
                ExtractionResult(
                    field_id=FieldId.PURCHASE_PRICE, status="missing", value=None
                )
            ]
        )
    )
    monkeypatch.setattr(extraction, "extract_fields", extract)

    response = client.post(
        "/api/extractions",
        files={"file": ("contract.pdf", document, "application/pdf")},
        data={"selected_fields": ["purchase_price"]},
    )

    assert response.status_code == 200
    assert response.json() == {
        "results": [{"field_id": "purchase_price", "status": "missing", "value": None}]
    }
    extract.assert_called_once_with(document, (FieldId.PURCHASE_PRICE,))


@pytest.mark.parametrize(
    ("error", "status", "detail"),
    [
        (
            DocumentProcessingError("Private document diagnostics"),
            422,
            "The PDF contains no extractable text. Please upload a text-based PDF.",
        ),
        (
            RuntimeError("Private document contents and internal path"),
            500,
            "Extraction failed. Please try again.",
        ),
    ],
    ids=["textless-document", "unexpected-failure"],
)
def test_processing_errors_are_separate_from_missing_results(
    client, document, monkeypatch, caplog, error, status, detail
):
    monkeypatch.setattr(extraction, "extract_fields", Mock(side_effect=error))

    response = client.post(
        "/api/extractions",
        files={"file": ("contract.pdf", document, "application/pdf")},
        data={"selected_fields": ["purchase_price"]},
    )

    assert response.status_code == status
    assert response.json() == {"detail": detail}
    records = [
        record for record in caplog.records if record.name == extraction.__name__
    ]
    if status == 500:
        assert len(records) == 1
        assert records[0].getMessage() == "Extraction failed: RuntimeError"
        assert records[0].exc_info is None
    else:
        assert not records
    assert str(error) not in caplog.text


def test_successive_requests_keep_their_own_document_and_selection(
    client, document, monkeypatch
):
    def fake_extract(document, selected_fields):
        return ExtractionResponse(
            results=[
                ExtractionResult(field_id=field, status="missing", value=None)
                for field in selected_fields
            ]
        )

    extract = Mock(side_effect=fake_extract)
    monkeypatch.setattr(extraction, "extract_fields", extract)
    second_document = (SAMPLE_DOCUMENTS / "missing-price-and-date.pdf").read_bytes()

    first = client.post(
        "/api/extractions",
        files={"file": ("first.pdf", document, "application/pdf")},
        data={"selected_fields": ["contract_date", "purchase_price"]},
    )
    second = client.post(
        "/api/extractions",
        files={"file": ("second.pdf", second_document, "application/pdf")},
        data={"selected_fields": ["purchaser_name"]},
    )

    assert first.status_code == second.status_code == 200
    assert [result["field_id"] for result in first.json()["results"]] == [
        "contract_date",
        "purchase_price",
    ]
    assert [result["field_id"] for result in second.json()["results"]] == [
        "purchaser_name"
    ]
    assert extract.call_args_list[0].args == (
        document,
        (FieldId.CONTRACT_DATE, FieldId.PURCHASE_PRICE),
    )
    assert extract.call_args_list[1].args == (
        second_document,
        (FieldId.PURCHASER_NAME,),
    )
