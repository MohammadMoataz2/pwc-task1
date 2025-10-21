"""Factory for evaluating contract health using AI"""

import logging
from typing import List

from pwc.ai import AIFactory
from pwc.settings import settings


class EvaluateFactory:
    """Factory for evaluating contract health using AI client based on environment"""

    @classmethod
    async def evaluate(cls, clauses: List, logger: logging.Logger = None):
        """Evaluate contract using AI client configured in environment"""
        if logger is None:
            logger = logging.getLogger(__name__)

        logger.info(f"[EVALUATE INPUT] Starting contract evaluation")
        logger.info(f"[EVALUATE INPUT] Provider: {settings.evaluation_provider}")
        logger.info(f"[EVALUATE INPUT] Model: {settings.openai_model}")
        logger.info(f"[EVALUATE INPUT] Number of clauses: {len(clauses)}")

        for i, clause in enumerate(clauses):
            logger.debug(f"[EVALUATE INPUT] Clause {i+1}: {clause.type} - {clause.content[:100]}...")

        try:
            # Use AI factory to get the configured AI client
            ai_client = AIFactory.create_client(
                settings.evaluation_provider,
                api_key=settings.openai_api_key,
                model=settings.openai_model
            )

            logger.info(f"[EVALUATE] AI client created: {settings.evaluation_provider}")

            # Call the evaluate_contract method from the AI client
            result = await ai_client.evaluate_contract(clauses)
            logger.info(f"[EVALUATE] AI evaluation completed", result)
            logger.info(f"[EVALUATE OUTPUT] Evaluation completed using {settings.evaluation_provider}")
            logger.info(f"[EVALUATE OUTPUT] Approved: {result.approved}")
            logger.info(f"[EVALUATE OUTPUT] Score: {getattr(result, 'score', 'N/A')}")
            logger.info(f"[EVALUATE OUTPUT] Recommendations: {len(getattr(result, 'recommendations', []))}")
            logger.info(f"[EVALUATE OUTPUT] Critical issues: {len(getattr(result, 'critical_issues', []))}")
            logger.debug(f"[EVALUATE OUTPUT] Reasoning: {result.reasoning}")

            return result

        except Exception as e:
            logger.error(f"[EVALUATE ERROR] Contract evaluation failed with {settings.evaluation_provider}: {e}")
            raise Exception(f"Evaluation failed: {str(e)}")