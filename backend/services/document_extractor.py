"""
services/document_extractor.py — Pipeline de procesamiento de documentos.

Soporta múltiples formatos:
  - PDF  → PyMuPDF (fitz)
  - TXT  → lectura directa
  - CSV  → lectura como texto tabular
  - XLSX → openpyxl, convierte filas a texto

Pipeline:
  extract_text() → clean_text() → chunk_text() → deduplicate_chunks()
"""

import csv
import hashlib
import io
import re
from pathlib import Path

import fitz  # PyMuPDF

# Extensiones soportadas
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".csv", ".xlsx"}


def extract_text(file_path: str) -> str:
    """
    Extrae texto de un archivo según su extensión.

    Formatos soportados: PDF, TXT, CSV, XLSX.

    Args:
        file_path: Ruta absoluta al archivo.

    Returns:
        Texto crudo extraído del documento.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si el formato no es soportado o no hay texto.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Formato no soportado: {ext}. "
            f"Formatos válidos: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    # Dispatch según extensión
    extractors = {
        ".pdf": _extract_pdf,
        ".txt": _extract_txt,
        ".csv": _extract_csv,
        ".xlsx": _extract_xlsx,
    }

    text = extractors[ext](file_path)

    if not text.strip():
        raise ValueError(f"El archivo no contiene texto extraíble: {file_path}")

    return text


def _extract_pdf(file_path: str) -> str:
    """Extrae texto de un PDF usando PyMuPDF."""
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        raise ValueError(f"No se pudo abrir el PDF: {e}")

    text_parts = []
    for page in doc:
        page_text = page.get_text("text")
        if page_text.strip():
            text_parts.append(page_text)

    doc.close()
    return "\n".join(text_parts)


def _extract_txt(file_path: str) -> str:
    """Lee un archivo de texto plano."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _extract_csv(file_path: str) -> str:
    """
    Lee un CSV y lo convierte en texto legible.
    Cada fila se convierte en: "columna1: valor1 | columna2: valor2 | ..."
    """
    lines = []
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convierte cada fila en texto clave:valor
            parts = [f"{key}: {value}" for key, value in row.items() if value]
            lines.append(" | ".join(parts))

    return "\n".join(lines)


def _extract_xlsx(file_path: str) -> str:
    """
    Lee un XLSX y lo convierte en texto legible.
    Usa los headers como claves, igual que CSV.
    """
    try:
        from openpyxl import load_workbook
    except ImportError:
        raise ImportError(
            "openpyxl es necesario para leer archivos XLSX. "
            "Instala con: pip install openpyxl"
        )

    wb = load_workbook(file_path, read_only=True, data_only=True)
    all_text = []

    for sheet in wb.sheetnames:
        ws = wb[sheet]
        rows = list(ws.iter_rows(values_only=True))

        if not rows:
            continue

        # Primera fila como headers
        headers = [str(h) if h else f"col_{i}" for i, h in enumerate(rows[0])]

        for row in rows[1:]:
            parts = []
            for header, value in zip(headers, row):
                if value is not None:
                    parts.append(f"{header}: {value}")
            if parts:
                all_text.append(" | ".join(parts))

    wb.close()
    return "\n".join(all_text)


def clean_text(text: str) -> str:
    """
    Limpia el texto crudo extraído.

    Operaciones:
      - Normaliza espacios en blanco
      - Elimina líneas que son solo números (pies de página)
      - Colapsa saltos de línea excesivos
      - Strip de cada línea
    """
    text = re.sub(r'[^\S\n\t]+', ' ', text)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[ \t]+', '', text, flags=re.MULTILINE)
    return text.strip()


def chunk_text(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    """
    Fragmenta el texto en chunks con solapamiento.

    Intenta cortar en espacios para no partir palabras.

    Args:
        text: Texto limpio.
        size: Tamaño de cada chunk (caracteres).
        overlap: Solapamiento entre chunks.

    Returns:
        Lista de chunks.
    """
    if not text:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + size

        if end < text_length:
            last_space = text.rfind(' ', start, end)
            if last_space > start:
                end = last_space

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap if end < text_length else text_length

    return chunks


def deduplicate_chunks(chunks: list[str]) -> list[str]:
    """
    Elimina chunks duplicados (SHA256). Preserva orden original.
    """
    seen: set[str] = set()
    unique: list[str] = []

    for chunk in chunks:
        h = hashlib.sha256(chunk.encode('utf-8')).hexdigest()
        if h not in seen:
            seen.add(h)
            unique.append(chunk)

    return unique
