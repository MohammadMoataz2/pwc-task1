import json
from typing import List, Dict, Any
from openai import AsyncOpenAI

from .base import AIInterface, ContractClause, ContractAnalysisResult, ContractEvaluationResult


class OpenAIClient(AIInterface):
    """OpenAI implementation for contract analysis"""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def analyze_contract(self, pdf_content: bytes) -> ContractAnalysisResult:
        """Analyze contract PDF and extract clauses using OpenAI"""

        # Note: For now, we'll simulate PDF text extraction
        # In production, you'd use a PDF parser like PyPDF2 or pdfplumber
        contract_text = "Sample contract text extracted from PDF"

        prompt = f"""
        Analyze the following contract and extract key clauses.
        Classify each clause by type (e.g., payment_terms, liability, termination, etc.).
        Return the result as a JSON object with the following structure:
        {{
            "clauses": [
                {{
                    "type": "clause_type",
                    "content": "clause_content",
                    "confidence": 0.95
                }}
            ],
            "metadata": {{
                "total_clauses": 5,
                "contract_type": "service_agreement"
            }}
        }}

        Contract text:
        {contract_text}
        """

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a legal expert analyzing contracts."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        try:
            result_data = json.loads(response.choices[0].message.content)
            clauses = [ContractClause(**clause) for clause in result_data["clauses"]]
            return ContractAnalysisResult(
                clauses=clauses,
                metadata=result_data.get("metadata", {})
            )
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback response
            return ContractAnalysisResult(
                clauses=[
                    ContractClause(
                        type="payment_terms",
                        content="Payment terms clause",
                        confidence=0.8
                    )
                ],
                metadata={"error": f"Parse error: {str(e)}"}
            )

    async def evaluate_contract(self, clauses: List[ContractClause]) -> ContractEvaluationResult:
        """Evaluate contract health based on extracted clauses"""

        clauses_text = "\n".join([f"- {clause.type}: {clause.content}" for clause in clauses])

        prompt = f"""
        Evaluate the following contract clauses and determine if the contract should be approved.
        Consider factors like completeness, risk level, and compliance.
        Return a JSON response with this structure:
        {{
            "approved": true/false,
            "reasoning": "Explanation of the decision",
            "score": 0.85
        }}

        Contract clauses:
        {clauses_text}
        """

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a legal expert evaluating contract risk."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        try:
            result_data = json.loads(response.choices[0].message.content)
            return ContractEvaluationResult(
                approved=result_data["approved"],
                reasoning=result_data["reasoning"],
                score=result_data.get("score", 0.0)
            )
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback response
            return ContractEvaluationResult(
                approved=False,
                reasoning=f"Unable to evaluate contract due to parse error: {str(e)}",
                score=0.0
            )