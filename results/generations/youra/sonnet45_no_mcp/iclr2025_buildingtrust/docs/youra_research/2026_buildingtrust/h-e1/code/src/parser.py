"""Report Parsing Module

This module extracts category-level benchmark data from technical reports.
Supports both PDF and HTML formats with robust table detection.
"""

import re
import logging
from typing import List, Optional, Union, Dict
from pathlib import Path
import pandas as pd

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


logger = logging.getLogger(__name__)


class PDFTableParser:
    """Extract tables from PDF technical reports."""

    def __init__(self, pdf_path: str):
        """
        Initialize parser.

        Args:
            pdf_path: Path to PDF file
        """
        if PyPDF2 is None:
            raise ImportError("PyPDF2 not installed. Install with: pip install PyPDF2")

        self.pdf_path = Path(pdf_path)
        self.reader: Optional[PyPDF2.PdfReader] = None
        self._load_pdf()

    def _load_pdf(self):
        """Load PDF file."""
        try:
            # Keep file handle open by reading into memory
            self.reader = PyPDF2.PdfReader(str(self.pdf_path))
        except Exception as e:
            logger.error(f"Failed to load PDF {self.pdf_path}: {e}")
            raise

    def extract_tables(self) -> List[pd.DataFrame]:
        """
        Extract all tables from PDF.

        Returns:
            List of DataFrames, one per table found
        """
        # Note: PyPDF2 doesn't directly support table extraction
        # This is a simplified implementation that extracts text
        # For production, use libraries like tabula-py or camelot
        logger.warning("PDF table extraction is limited. Consider using tabula-py for better results.")

        tables = []
        if self.reader is None:
            return tables

        # Extract text from all pages
        for page_num, page in enumerate(self.reader.pages):
            text = page.extract_text()
            # Look for table-like structures
            # This is a basic heuristic - real implementation would use proper table detection
            lines = text.split('\n')
            current_table = []
            in_table = False

            for line in lines:
                # Detect table headers (multiple whitespace-separated items)
                if re.search(r'\w+\s{2,}\w+\s{2,}\w+', line):
                    if not in_table:
                        current_table = []
                        in_table = True
                    current_table.append(line)
                elif in_table and len(current_table) > 2:
                    # End of table
                    try:
                        df = self._parse_table_text(current_table)
                        if df is not None and not df.empty:
                            tables.append(df)
                    except Exception as e:
                        logger.warning(f"Failed to parse table on page {page_num}: {e}")
                    current_table = []
                    in_table = False

        logger.info(f"Extracted {len(tables)} tables from PDF")
        return tables

    def _parse_table_text(self, table_lines: List[str]) -> Optional[pd.DataFrame]:
        """Parse table text into DataFrame."""
        if len(table_lines) < 2:
            return None

        # Split by whitespace (simplified)
        rows = []
        for line in table_lines:
            # Split by multiple spaces
            cells = re.split(r'\s{2,}', line.strip())
            if cells:
                rows.append(cells)

        if not rows:
            return None

        # Use first row as header
        df = pd.DataFrame(rows[1:], columns=rows[0])
        return df

    def find_benchmark_table(self, benchmark_name: str) -> Optional[pd.DataFrame]:
        """
        Locate table containing benchmark results.

        Args:
            benchmark_name: "TruthfulQA" or "MMLU"

        Returns:
            DataFrame if found, else None
        """
        tables = self.extract_tables()
        for df in tables:
            # Check if benchmark name appears in any column or value
            df_str = df.to_string().lower()
            if benchmark_name.lower() in df_str:
                return df

        logger.warning(f"No table found for benchmark: {benchmark_name}")
        return None


class HTMLTableParser:
    """Extract tables from HTML technical reports."""

    def __init__(self, html_path: str):
        """
        Initialize parser.

        Args:
            html_path: Path to HTML file
        """
        if BeautifulSoup is None:
            raise ImportError("beautifulsoup4 not installed. Install with: pip install beautifulsoup4")

        self.html_path = Path(html_path)
        self.soup: Optional[BeautifulSoup] = None
        self._load_html()

    def _load_html(self):
        """Load HTML file."""
        try:
            with open(self.html_path, 'r', encoding='utf-8') as f:
                self.soup = BeautifulSoup(f.read(), 'html.parser')
        except Exception as e:
            logger.error(f"Failed to load HTML {self.html_path}: {e}")
            raise

    def extract_tables(self) -> List[pd.DataFrame]:
        """
        Extract all <table> elements from HTML.

        Returns:
            List of DataFrames parsed from <table> tags
        """
        if self.soup is None:
            return []

        tables = []
        table_elements = self.soup.find_all('table')

        for table in table_elements:
            try:
                df = pd.read_html(str(table))[0]
                tables.append(df)
            except Exception as e:
                logger.warning(f"Failed to parse HTML table: {e}")

        logger.info(f"Extracted {len(tables)} tables from HTML")
        return tables

    def find_benchmark_table(self, benchmark_name: str) -> Optional[pd.DataFrame]:
        """
        Locate table with benchmark results.

        Args:
            benchmark_name: Benchmark identifier

        Returns:
            DataFrame if found, else None
        """
        tables = self.extract_tables()
        for df in tables:
            df_str = df.to_string().lower()
            if benchmark_name.lower() in df_str:
                return df

        logger.warning(f"No table found for benchmark: {benchmark_name}")
        return None


class CategoryExtractor:
    """Extract and normalize category-level data."""

    def __init__(self, parser: Union[PDFTableParser, HTMLTableParser]):
        """
        Initialize extractor.

        Args:
            parser: Format-specific table parser
        """
        self.parser = parser

    def extract_category_data(
        self,
        benchmark: str,
        model_family: str,
        timepoint: str
    ) -> pd.DataFrame:
        """
        Extract category-level error rates.

        Args:
            benchmark: "TruthfulQA" or "MMLU"
            model_family: "GPT" | "Claude" | "Llama"
            timepoint: "baseline" | "current"

        Returns:
            DataFrame with schema:
                [model_family, timepoint, benchmark, category, error_rate]
        """
        # Find the benchmark table
        table = self.parser.find_benchmark_table(benchmark)

        if table is None or table.empty:
            logger.warning(f"No data found for {benchmark}")
            return pd.DataFrame(columns=[
                "model_family", "timepoint", "benchmark", "category", "error_rate"
            ])

        # Normalize schema
        normalized = self.normalize_schema(table)

        # Add metadata columns
        normalized['model_family'] = model_family
        normalized['timepoint'] = timepoint
        normalized['benchmark'] = benchmark

        # Ensure correct column order
        result = normalized[[
            'model_family', 'timepoint', 'benchmark', 'category', 'error_rate'
        ]]

        return result

    def normalize_schema(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize to standard schema.

        Args:
            raw_df: Raw extracted table

        Returns:
            Normalized DataFrame [category, error_rate]
        """
        # Detect category column (common names)
        category_col = None
        for col in raw_df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in ['category', 'domain', 'subject', 'topic', 'task']):
                category_col = col
                break

        if category_col is None:
            # Assume first column is category
            category_col = raw_df.columns[0]

        # Detect accuracy/error column
        value_col = None
        for col in raw_df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in ['accuracy', 'error', 'score', '%']):
                value_col = col
                break

        if value_col is None:
            # Assume last numeric column is the value
            for col in reversed(raw_df.columns):
                if pd.api.types.is_numeric_dtype(raw_df[col]):
                    value_col = col
                    break

        if value_col is None:
            logger.error("Could not detect value column in table")
            return pd.DataFrame(columns=['category', 'error_rate'])

        # Extract and rename
        normalized = pd.DataFrame({
            'category': raw_df[category_col],
            'value': pd.to_numeric(raw_df[value_col], errors='coerce')
        })

        # Convert accuracy to error rate if needed
        # Assume values > 1 are percentages, values <= 1 are proportions
        if normalized['value'].max() > 1:
            # Percentage format (0-100)
            normalized['error_rate'] = 100 - normalized['value']
        else:
            # Proportion format (0-1)
            normalized['error_rate'] = (1 - normalized['value']) * 100

        # Drop value column
        normalized = normalized[['category', 'error_rate']]

        # Remove rows with NaN
        normalized = normalized.dropna()

        return normalized
