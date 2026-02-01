import pytest
from app.services.document_gemini_service import document_service
from app.core.config import settings


def test_document_service_has_extract_method():
    assert hasattr(document_service, "extract_from_document")
    assert hasattr(document_service, "extract_document_to_csv")


def test_extract_document_to_csv_missing_file(tmp_path):
    out = tmp_path / "out.csv"
    with pytest.raises(FileNotFoundError):
        document_service.extract_document_to_csv(str(tmp_path / "nope.pdf"), str(out))


def test_default_model_setting():
    # The service should pick up the configured default model from settings
    assert document_service.model == settings.GOOGLE_GEMINI_MODEL
