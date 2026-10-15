import logging
from pathlib import Path
import pymupdf


logger = logging.getLogger(__name__)


class PDFIngestion:

    def __init__(self, directory: str | Path):
        self.directory = Path(directory)

        if not self.directory.exists():
            raise FileNotFoundError(
                f"PDF directory does not exist: {self.directory}"
            )

        if not self.directory.is_dir():
            raise NotADirectoryError(
                f"Expected directory: {self.directory}"
            )

    def discover_files(self) -> list[Path]:

        files = sorted(
            path
            for path in self.directory.glob("*.pdf")
            if path.is_file()
        )

        logger.info(
            "Found %d PDF file(s)",
            len(files),
        )

        return files

    def extract_text(
        self,
        file_path: Path,
    ) -> list[dict]:

        pages: list[dict] = []

        try:
            with pymupdf.open(file_path) as document:

                for page_number, page in enumerate(
                    document,
                    start=1,
                ):

                    text = page.get_text().strip()

                    if not text:
                        continue

                    pages.append(
                        {
                            "filename": file_path.name,
                            "page_number": page_number,
                            "text": text,
                            "source": "pdf",
                        }
                    )

            return pages

        except Exception as exc:
            logger.exception(
                "Failed to process PDF: %s",
                file_path,
            )
     
            raise RuntimeError(
                f"Failed to process PDF '{file_path.name}'."
            ) from exc

    def ingest_all(self) -> list[dict]:

        documents: list[dict] = []

        for file_path in self.discover_files():

            try:
                pages = self.extract_text(file_path)
                documents.extend(pages)

                logger.info(
                    "Processed %s: %d pages",
                    file_path.name,
                    len(pages),
                )

            except Exception:
                logger.exception(
                    "Skipping failed PDF: %s",
                    file_path,
                )

        return documents