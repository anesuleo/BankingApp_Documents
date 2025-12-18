from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import httpx
import os

app = FastAPI(title="Document Service")

# Base URL for Account microservice
ACCOUNT_SERVICE_BASE_URL = os.getenv(
    "ACCOUNT_SERVICE_BASE_URL",
    "http://localhost:8000"
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/documents/accounts/{account_number}/statement")
def generate_account_statement(account_number: str):
    """
    Fetch transactions from Account microservice
    and generate a PDF account statement.
    """

    # -------- Call Account microservice --------
    url = f"{ACCOUNT_SERVICE_BASE_URL}/accounts/by-number/{account_number}/transactions"

    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(url)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Account service unavailable")

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Failed to fetch transactions"
        )

    transactions = response.json()

    # -------- Prepare PDF storage --------
    os.makedirs("docs", exist_ok=True)
    filename = f"statement_{account_number}.pdf"
    filepath = os.path.join("docs", filename)

    # -------- Generate PDF --------
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(170, height - 50, "Account Statement")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Account Number: {account_number}")
    c.drawString(
        50,
        height - 100,
        f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
    )

    # Table header
    y = height - 150
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y, "Date")
    c.drawString(130, y, "Type")
    c.drawString(220, y, "Amount (€)")
    c.drawString(320, y, "From")
    c.drawString(410, y, "To")
    c.drawString(490, y, "Description")
    c.line(40, y - 5, 560, y - 5)

    # Table rows
    y -= 25
    c.setFont("Helvetica", 10)

    for tx in transactions:
        # Handle ISO datetime with Z suffix
        created_at = datetime.fromisoformat(
            tx["created_at"].replace("Z", "+00:00")
        ).strftime("%Y-%m-%d %H:%M")

        tx_type = tx["tx_type"]
        amount = str(tx["amount"])

        from_acc = tx.get("sender_account_number") or "-"
        to_acc = tx.get("receiver_account_number") or "-"
        description = tx.get("description") or "-"

        c.drawString(40, y, created_at)
        c.drawString(130, y, tx_type)
        c.drawString(220, y, amount)
        c.drawString(320, y, from_acc)
        c.drawString(410, y, to_acc)
        c.drawString(490, y, description[:20])

        y -= 20

        # Page break
        if y < 80:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - 80

    # Footer
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, 50, "This is a system-generated statement.")
    c.save()

    # -------- Return PDF --------
    return FileResponse(
        path=filepath,
        media_type="application/pdf",
        filename=filename
    )
