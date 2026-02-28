"""
services/document_extractor.py — Pipeline de procesamiento de documentos.

Responsabilidades:
  1. Extraer texto de PDFs (PyMuPDF/fitz)
  2. Limpiar texto (regex)
  3. Fragmentar en chunks con solapamiento
  4. Deduplicar chunks (SHA256)

Uso:
    from services.document_extractor import extract_text, clean_text, chunk_text, deduplicate_chunks

    raw = extract_text("/path/to/file.pdf")
    clean = clean_text(raw)
    chunks = chunk_text(clean, size=500, overlap=50)
    unique = deduplicate_chunks(chunks)
"""

import hashlib
import re
from pathlib import Path

import fitz  # PyMuPDF


def extract_text(file_path: str) -> str:
    """
    Extrae todo el texto de un PDF usando PyMuPDF.

    Args:
        file_path: Ruta absoluta al archivo PDF.

    Returns:
        Texto crudo concatenado de todas las páginas.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si el archivo no es un PDF válido o no tiene texto.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

    try:
        doc = fitz.open(file_path)
    except Exception as e:
        raise ValueError(f"No se pudo abrir el PDF: {e}")

    text_parts = []
    for page_num, page in enumerate(doc):
        page_text = page.get_text("text")
        if page_text.strip():
            text_parts.append(page_text)

    doc.close()

    full_text = "\n".join(text_parts)
    if not full_text.strip():
        raise ValueError(f"El PDF no contiene texto extraíble: {file_path}")

    return full_text


def clean_text(text: str) -> str:
    """
    Limpia el texto crudo extraído de un PDF.

    Operaciones:
      - Elimina cabeceras/pies de página repetitivos (líneas con solo números)
      - Normaliza espacios en blanco (múltiples espacios → uno)
      - Elimina saltos de línea excesivos
      - Strip de caracteres no imprimibles
      - Elimina líneas vacías consecutivas

    Args:
        text: Texto crudo del PDF.

    Returns:
        Texto limpio.
    """
    # Elimina caracteres no imprimibles (excepto newlines y tabs)
    text = re.sub(r'[^\S\n\t]+', ' ', text)

    # Elimina líneas que son solo números (típicas cabeceras/pies con nº de página)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)

    # Colapsa múltiples saltos de línea en máximo 2
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Elimina espacios al inicio/final de cada línea
    text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[ \t]+', '', text, flags=re.MULTILINE)

    return text.strip()


def chunk_text(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    """
    Fragmenta el texto en chunks de tamaño fijo con solapamiento.

    El solapamiento evita que se pierda contexto en los bordes entre chunks.

    Args:
        text: Texto limpio.
        size: Tamaño de cada chunk en caracteres.
        overlap: Caracteres de solapamiento entre chunks consecutivos.

    Returns:
        Lista de strings, cada uno un chunk del texto.
    """
    if not text:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + size

        # Si no estamos al final, intenta cortar en un espacio para no partir palabras
        if end < text_length:
            # Busca el último espacio dentro del chunk
            last_space = text.rfind(' ', start, end)
            if last_space > start:
                end = last_space

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Avanza: tamaño del chunk - overlap
        start = end - overlap if end < text_length else text_length

    return chunks


def deduplicate_chunks(chunks: list[str]) -> list[str]:
    """
    Elimina chunks duplicados usando hash SHA256.

    Útil cuando el mismo PDF se sube varias veces o cuando el contenido
    se repite entre páginas (cabeceras, disclaimers, etc.).

    Args:
        chunks: Lista de chunks (pueden tener duplicados).

    Returns:
        Lista de chunks únicos, preservando el orden original.
    """
    seen_hashes: set[str] = set()
    unique_chunks: list[str] = []

    for chunk in chunks:
        chunk_hash = hashlib.sha256(chunk.encode('utf-8')).hexdigest()
        if chunk_hash not in seen_hashes:
            seen_hashes.add(chunk_hash)
            unique_chunks.append(chunk)

    return unique_chunks
