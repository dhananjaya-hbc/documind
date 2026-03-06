# tests/test_documents.py

import pytest
from io import BytesIO


def create_simple_pdf() -> bytes:
    """Create a simple PDF for testing."""
    try:
        from fpdf import FPDF

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Test Document", ln=True)
        pdf.cell(200, 10, txt="This is a test document about artificial intelligence.", ln=True)
        pdf.cell(200, 10, txt="AI is a branch of computer science.", ln=True)
        pdf.cell(200, 10, txt="Machine learning is a subset of AI.", ln=True)
        pdf.cell(200, 10, txt="Deep learning uses neural networks.", ln=True)
        return pdf.output(dest="S").encode("latin-1")

    except ImportError:
        # If fpdf not installed, create minimal PDF
        return (
            b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
            b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R"
            b"/Contents 4 0 R>>endobj\n"
            b"4 0 obj<</Length 44>>stream\nBT /F1 12 Tf 100 700 Td "
            b"(Test Document) Tj ET\nendstream\nendobj\n"
            b"xref\n0 5\ntrailer<</Size 5/Root 1 0 R>>\nstartxref\n0\n%%EOF"
        )


# ============================================
# DOCUMENT UPLOAD TESTS
# ============================================

@pytest.mark.asyncio
async def test_upload_document(client, auth_headers):
    """Test successful PDF upload."""
    pdf_content = create_simple_pdf()

    response = await client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("test.pdf", BytesIO(pdf_content), "application/pdf")},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["status"] in ["ready", "processing"]
    assert "id" in data


@pytest.mark.asyncio
async def test_upload_non_pdf(client, auth_headers):
    """Test uploading non-PDF file fails."""
    response = await client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("test.txt", BytesIO(b"Hello world"), "text/plain")},
    )

    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_without_auth(client):
    """Test upload without authentication fails."""
    pdf_content = create_simple_pdf()

    response = await client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.pdf", BytesIO(pdf_content), "application/pdf")},
    )

    assert response.status_code == 403


# ============================================
# DOCUMENT LIST TESTS
# ============================================

@pytest.mark.asyncio
async def test_list_documents(client, auth_headers):
    """Test listing documents."""
    response = await client.get(
        "/api/v1/documents/",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert "total" in data
    assert isinstance(data["documents"], list)


@pytest.mark.asyncio
async def test_list_documents_without_auth(client):
    """Test listing documents without auth fails."""
    response = await client.get("/api/v1/documents/")

    assert response.status_code == 403