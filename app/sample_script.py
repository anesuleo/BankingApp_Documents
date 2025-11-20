from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

def generate_statement_pdf(account_id):
    filename = f"statement_{account_id}.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, height - 50, "Account Statement")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Account ID: {account_id}")
    c.drawString(50, height - 100, f"Date Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Sample transaction data
    transactions = [
        {"date": "2025-10-01", "type": "Deposit", "amount": 1000.00},
        {"date": "2025-10-05", "type": "Withdrawal", "amount": -200.00},
        {"date": "2025-10-12", "type": "Transfer", "amount": -150.00},
        {"date": "2025-10-18", "type": "Deposit", "amount": 500.00},
    ]

    # Table header
    y = height - 150
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Date")
    c.drawString(200, y, "Type")
    c.drawString(350, y, "Amount (€)")
    c.line(50, y - 5, 500, y - 5)

    # Table content
    c.setFont("Helvetica", 12)
    y -= 25
    for txn in transactions:
        c.drawString(50, y, txn["date"])
        c.drawString(200, y, txn["type"])
        c.drawString(350, y, f"{txn['amount']:.2f}")
        y -= 20

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 50, "This is a system-generated statement.")
    c.save()

    print(f"PDF generated: {filename}")

# Example usage
if __name__ == "__main__":
    generate_statement_pdf(account_id=12345)