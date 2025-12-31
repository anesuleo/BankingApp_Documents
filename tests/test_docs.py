from fastapi.testclient import TestClient
import httpx
import pytest

import app.main as documents_main

client = TestClient(documents_main.app)


@pytest.fixture
def sample_transactions():
    """Fake data shaped like the Account service response."""
    return [
        {
            "id": 1,
            "account_id": 1,
            "tx_type": "deposit",
            "amount": "1000.00",
            "description": "mari",
            "sender_name": "External",
            "sender_account_number": None,
            "receiver_name": "string",
            "receiver_account_number": "MX2721",
            "created_at": "2025-12-18T12:24:03.129125Z",
        }
    ]


def test_health_ok():
    """Checks the service is alive."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_statement_returns_pdf(monkeypatch, sample_transactions):
    """
    Pretend the Account service returns 200 OK + transactions.
    The Documents service should return a downloadable PDF.
    """

    class FakeAccountResponse:
        """Mimics what httpx returns from account-service."""
        status_code = 200

        def json(self):
            return sample_transactions

    class FakeHttpxClient:
        """
        This replaces 'httpx.Client' ONLY inside documents_main.
        It supports 'with httpx.Client() as client:'.
        """
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def get(self, url, *args, **kwargs):
            return FakeAccountResponse()

    # Patch the Client class only in your documents service module
    monkeypatch.setattr(documents_main.httpx, "Client", FakeHttpxClient)

    account_number = "PA5709"
    r = client.get(f"/documents/accounts/{account_number}/statement")

    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/pdf")
    assert f'statement_{account_number}.pdf' in r.headers.get("content-disposition", "")

    # PDF files always start with "%PDF"
    assert r.content[:4] == b"%PDF"
    assert len(r.content) > 100


def test_statement_account_service_unavailable(monkeypatch):
    """
    Pretend the Account service is down (connection error).
    The Documents service should return 503.
    """

    class FakeHttpxClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def get(self, url, *args, **kwargs):
            raise httpx.RequestError(
                "connection failed",
                request=httpx.Request("GET", url)
            )

    monkeypatch.setattr(documents_main.httpx, "Client", FakeHttpxClient)

    r = client.get("/documents/accounts/PA5709/statement")
    assert r.status_code == 503
    assert r.json()["detail"] == "Account service unavailable"


def test_statement_account_service_non_200(monkeypatch):
    """
    Pretend the Account service responds with an error code (e.g. 404).
    The Documents service should return the same status code message.
    """

    class FakeAccountResponse:
        status_code = 404

        def json(self):
            return {"detail": "not found"}

    class FakeHttpxClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def get(self, url, *args, **kwargs):
            return FakeAccountResponse()

    monkeypatch.setattr(documents_main.httpx, "Client", FakeHttpxClient)

    r = client.get("/documents/accounts/PA5709/statement")
    assert r.status_code == 404
    assert r.json()["detail"] == "Failed to fetch transactions"
