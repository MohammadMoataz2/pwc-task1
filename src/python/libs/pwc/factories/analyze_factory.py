"""Factory for analyzing contract clauses using AI"""

import logging

from pwc.ai import AIFactory
from pwc.settings import settings


class AnalyzeFactory:
    """Factory for analyzing contract clauses using AI client based on environment"""

    @classmethod
    async def analyze(cls, document_text: str, logger: logging.Logger = None):
        """Analyze contract using AI client configured in environment"""
        if logger is None:
            logger = logging.getLogger(__name__)

        logger.info(f"[ANALYZE INPUT] Starting contract analysis")
        logger.info(f"[ANALYZE INPUT] Provider: {settings.analysis_provider}")
        logger.info(f"[ANALYZE INPUT] Model: {settings.openai_model}")
        logger.info(f"[ANALYZE INPUT] Text length: {len(document_text)} characters")
        logger.debug(f"[ANALYZE INPUT] Text preview: {document_text[:500]}...")

        try:
            # Use AI factory to get the configured AI client
            ai_client = AIFactory.create_client(
                settings.analysis_provider,
                api_key=settings.openai_api_key,
                model=settings.openai_model
            )

            logger.info(f"[ANALYZE] AI client created: {settings.analysis_provider}")

            # Call the analyze_contract method from the AI client
            result = await ai_client.analyze_contract(document_text)

            logger.info(f"[ANALYZE OUTPUT] Analysis completed using {settings.analysis_provider}")
            logger.info(f"[ANALYZE OUTPUT] Found {len(result.clauses)} clauses")
            for i, clause in enumerate(result.clauses):
                logger.debug(f"[ANALYZE OUTPUT] Clause {i+1}: {clause.type} (confidence: {clause.confidence})")

            return result

        except Exception as e:
            logger.error(f"[ANALYZE ERROR] Contract analysis failed with {settings.analysis_provider}: {e}")
            raise Exception(f"Analysis failed: {str(e)}")