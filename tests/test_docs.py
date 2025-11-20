import os
from fastapi.testclient import TestClient
from app.main import app   # adjust import to your project structure

client = TestClient(app)


def test_generate_pdf():
    account_id = 123
    filename = f"statement_{account_id}.pdf"
    filepath = os.path.join("docs", filename)

    # Ensure docs folder is clean before test
    if os.path.exists(filepath):
        os.remove(filepath)

    # Call the PDF endpoint
    response = client.get(f"/generate-pdf/{account_id}")
    # Correct HTTP response
    assert response.status_code == 200
    # Check content type
    assert response.headers["content-type"] == "application/pdf"
    # File should now exist inside docs/
    assert os.path.exists(filepath)
    # Cleanup
    os.remove(filepath)
    #Ensure delete worked
    assert not os.path.exists(filepath)