from fastapi import FastAPI
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import os

app = FastAPI(title="Document Service")

# Dummy transactions that match TransactionRead schema
DUMMY_TRANSACTIONS = [
    {
        "id": 1,
        "account_id": 123,
        "tx_type": "deposit",
        "amount": "1000.00",
        "description": "Initial deposit",
        "sender_name": None,
        "sender_account_number": None,
        "receiver_name": "John Doe",
        "receiver_account_number": "TA1234",
        "created_at": "2025-10-01"
    },
    {
        "id": 2,
        "account_id": 123,
        "tx_type": "withdrawal",
        "amount": "-200.00",
        "description": "ATM withdrawal",
        "sender_name": "John Doe",
        "sender_account_number": "TA1234",
        "receiver_name": None,
        "receiver_account_number": None,
        "created_at": "2025-10-05"
    },
    {
        "id": 3,
        "account_id": 123,
        "tx_type": "transfer_out",
        "amount": "-150.00",
        "description": "Sent to Mary",
        "sender_name": "John Doe",
        "sender_account_number": "TA1234",
        "receiver_name": "Mary",
        "receiver_account_number": "AB9876",
        "created_at": "2025-10-12"
    },
]


@app.get("/generate-pdf/{account_id}")
def generate_pdf(account_id: int):

    # Ensure docs folder exists
    docs_dir = "docs"
    os.makedirs(docs_dir, exist_ok=True)

    filename = f"statement_{account_id}.pdf"
    filepath = os.path.join(docs_dir, filename)

    # PDF creation
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(180, height - 50, "Account Statement")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Account ID: {account_id}")
    c.drawString(50, height - 100, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Table header
    y = height - 150
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y, "Date")
    c.drawString(130, y, "Type")
    c.drawString(220, y, "Amount (€)")
    c.drawString(320, y, "From")
    c.drawString(400, y, "To")
    c.drawString(480, y, "Description")
    c.line(40, y - 5, 560, y - 5)

    # Table rows
    y -= 25
    c.setFont("Helvetica", 10)

    for txn in DUMMY_TRANSACTIONS:

        c.drawString(40, y, txn["created_at"])
        c.drawString(130, y, txn["tx_type"])
        c.drawString(220, y, str(txn["amount"]))

        from_acc = txn["sender_account_number"] or "-"
        to_acc = txn["receiver_account_number"] or "-"

        c.drawString(320, y, from_acc)
        c.drawString(400, y, to_acc)

        description = txn["description"] or "-"
        c.drawString(480, y, description[:20])  # Trim text so it fits

        y -= 20

    # Footer
    c.save()

    return FileResponse(
        path=filepath,
        media_type="application/pdf",
        filename=filename
    )
