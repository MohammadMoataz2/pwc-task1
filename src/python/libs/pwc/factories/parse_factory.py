"""Factory for parsing contract documents using AI and libraries"""

import logging
import tempfile
import os
from typing import Union

from pwc.ai.base import ParsedDocument
from pwc.ai import AIFactory
from pwc.settings import settings


class ParseFactory:
    """Factory for parsing contract documents with fallback to libraries"""

    @classmethod
    async def parse(cls, file_content: bytes, filename: str, logger: logging.Logger = None) -> ParsedDocument:
        """Parse document using AI or fallback to library parsing"""
        if logger is None:
            logger = logging.getLogger(__name__)

        logger.info(f"[PARSE INPUT] Starting document parsing for {filename}")
        logger.info(f"[PARSE INPUT] File size: {len(file_content)} bytes")
        logger.info(f"[PARSE INPUT] Provider: {settings.parsing_provider}")

        # Try AI parsing first
        if settings.parsing_provider != "library":
            try:
                result = await cls._parse_with_ai(file_content, filename, logger)
                logger.info(f"[PARSE OUTPUT] AI parsing successful - extracted {len(result.text)} characters from {result.page_count} pages")
                return result
            except Exception as e:
                logger.warning(f"[PARSE ERROR] AI parsing failed, falling back to library: {e}")

        # Fallback to library parsing
        result = await cls._parse_with_library(file_content, filename, logger)
        logger.info(f"[PARSE OUTPUT] Library parsing successful - extracted {len(result.text)} characters from {result.page_count} pages")
        return result

    @classmethod
    async def _parse_with_ai(cls, file_content: bytes, filename: str, logger: logging.Logger) -> ParsedDocument:
        """Parse using AI provider"""
        ai_client = AIFactory.create_client(
            settings.parsing_provider,
            api_key=settings.openai_api_key,
            model=settings.openai_model
        )

        # Save file to temporary location for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        try:
            result = await ai_client.parse_document(temp_file_path, filename)
            logger.info(f"AI parsing completed for {filename}")
            return result
        finally:
            os.unlink(temp_file_path)

    @classmethod
    async def _parse_with_library(cls, file_content: bytes, filename: str, logger: logging.Logger) -> ParsedDocument:
        """Parse using library (PyPDF2/pdfplumber)"""
        try:
            import PyPDF2
            import io

            logger.info(f"[LIBRARY PARSE] Using PyPDF2 for {filename}")

            # Parse PDF using PyPDF2
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            logger.info(f"[LIBRARY PARSE] PDF loaded, pages: {len(pdf_reader.pages)}")

            # Extract text from all pages
            text = ""
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text += page_text + "\n"
                logger.debug(f"[LIBRARY PARSE] Page {i+1}: extracted {len(page_text)} characters")

            result = ParsedDocument(
                text=text.strip(),
                page_count=len(pdf_reader.pages),
                metadata={
                    "parser": "PyPDF2",
                    "filename": filename,
                    "file_size": len(file_content)
                }
            )

            logger.info(f"[LIBRARY PARSE] Completed for {filename} - total {len(result.text)} characters")
            return result

        except ImportError as e:
            logger.error(f"[LIBRARY PARSE ERROR] PyPDF2 not available: {e}")
            raise Exception("PDF parsing library not available")
        except Exception as e:
            logger.error(f"[LIBRARY PARSE ERROR] Failed for {filename}: {e}")
            raise Exception(f"Library parsing failed: {str(e)}")