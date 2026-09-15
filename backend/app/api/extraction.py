"""Single-document extraction requests and HTTP error mapping."""

import logging
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.extraction.models import ExtractionResponse, FieldId
from app.extraction.pdf import DocumentProcessingError
from app.extraction.service import extract_fields

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/api/extractions",
    response_model=ExtractionResponse,
    tags=["extraction"],
    responses={500: {"description": "Unexpected extraction or reader failure."}},
)
def extract_contract(
    file: Annotated[
        UploadFile, File(description="One text-based purchase-contract PDF")
    ],
    selected_fields: Annotated[
        list[FieldId],
        Form(min_length=1, max_length=4, description="One to four distinct field IDs"),
    ],
) -> ExtractionResponse:
    """Extract only the fields submitted with this PDF, in their submitted order."""
    if len(set(selected_fields)) != len(selected_fields):
        raise HTTPException(status_code=422, detail="Select each field only once.")

    # A synchronous route runs file reading and PDF extraction in FastAPI's thread pool.
    try:
        document = file.file.read()
        if not document:
            raise HTTPException(status_code=422, detail="Please upload a nonempty PDF.")

        return extract_fields(document, tuple(selected_fields))
    except HTTPException:
        raise
    except DocumentProcessingError:
        raise HTTPException(
            status_code=422,
            detail=(
                "The PDF contains no extractable text. Please upload a text-based PDF."
            ),
        ) from None
    except Exception as exc:
        # Do not expose document contents, parser diagnostics, or internal paths.
        logger.error("Extraction failed: %s", type(exc).__name__)
        raise HTTPException(
            status_code=500, detail="Extraction failed. Please try again."
        ) from None
