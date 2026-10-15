import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

class CSVIngestion:

    def __init__(self, directory: str | Path):
        self.directory = Path(directory)

        if not self.directory.exists():
            raise FileNotFoundError(
                f"CSV directory does not exist: {self.directory}"
            )

        if not self.directory.is_dir():
            raise NotADirectoryError(
                f"Expected directory: {self.directory}"
            )

    def discover_files(self) -> list[Path]:
        files = sorted(
            path
            for path in self.directory.glob("*.csv")
            if path.is_file()
        )

        logger.info(
            "Found %d CSV file(s)",
            len(files),
        )

        return files

    def extract_data(
        self,
        file_path: Path,
    ) -> list[dict]:

        if not file_path.is_file():
            raise FileNotFoundError(file_path)
        
        try:
            df = pd.read_csv(
                file_path,
                keep_default_na=False,
            )
            
            if df.empty:
                logger.warning(
                    "CSV file is empty: %s",
                    file_path,
                )
                return []

            documents: list[dict] = []
        
            columns = list(df.columns)

            for row_number, row in enumerate(
                df.itertuples(index=False, name=None),
                start=1,
            ):
                values = dict(zip(columns, row))
                 
                text = ", ".join(
                    f"{column}: {value}"
                    for column, value in values.items()
                    if str(value).strip()
                )
                
                if not text.strip():
                    continue
                
            
                documents.append(
                    {
                        "filename": file_path.name,
                        "row_number": row_number,
                        "text": text,
                        "source": "csv",
                    }
                )
            
            return documents

        except Exception as exc:
            logger.exception(
                "Failed to process CSV: %s",
                file_path,
            )
            raise RuntimeError(
                f"Failed to process CSV '{file_path.name}'."
            ) from exc

    def ingest_all(self) -> list[dict]:

        documents: list[dict] = []

        for file_path in self.discover_files():

            try:
                rows = self.extract_data(file_path)
                documents.extend(rows)

                logger.info(
                    "Processed %s: %d rows",
                    file_path.name,
                    len(rows),
                )

            except Exception:
                logger.exception(
                    "Skipping failed CSV: %s",
                    file_path,
                )

        return documents