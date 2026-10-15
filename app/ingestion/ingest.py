from pathlib import Path
from app.ingestion.pdf_ingestion import PDFIngestion
from app.ingestion.csv_ingestion import CSVIngestion


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PDF_DIRECTORY = PROJECT_ROOT / "app" / "data"
CSV_DIRECTORY = PROJECT_ROOT / "app" / "csv"


def ingest_documents() -> list[dict]:
    pdf_ingestion = PDFIngestion(PDF_DIRECTORY)
    csv_ingestion = CSVIngestion(CSV_DIRECTORY)

    pdf_documents = pdf_ingestion.ingest_all()
    csv_documents = csv_ingestion.ingest_all()

    return pdf_documents + csv_documents










