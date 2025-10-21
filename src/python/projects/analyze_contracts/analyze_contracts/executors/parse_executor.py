from typing import Dict, Any

from pwc.task_interface.base import ContractTaskExecutor
from pwc.factories import ParseFactory
from pwc.storage import StorageFactory
from pwc.settings import settings


class ParseContractExecutor(ContractTaskExecutor):
    """Executor for parsing contract documents using AI-based factory"""

    async def run(self, task_info_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Parse contract document and extract text"""
        self.logger.info(f"[EXECUTOR] Starting contract parsing for {self.task_info.contract_id}")

        try:
            # Get contract details from API
            self.logger.info(f"[EXECUTOR] Fetching contract details from API")
            contract = await self.api.get_contract(self.task_info.contract_id)
            self.logger.info(f"[EXECUTOR] Contract loaded: {contract.get('filename', 'unknown')}")

            # Initialize storage
            storage = StorageFactory.create_storage(
                settings.storage_type,
                base_path=settings.local_storage_path
            )

            # Load contract file
            self.logger.info(f"[EXECUTOR] Loading file from: {contract['file_path']}")
            file_content = await storage.load(contract["file_path"])
            self.logger.info(f"[EXECUTOR] File loaded: {len(file_content)} bytes")

            # Parse document using factory
            parsed_doc = await ParseFactory.parse(
                file_content,
                contract["filename"],
                logger=self.logger
            )

            # Save parsed text to storage
            text_file_path = f"parsed/{self.task_info.contract_id}/{self.task_info.run_id}/text.txt"
            await storage.save(parsed_doc.text.encode('utf-8'), text_file_path)

            result = {
                "contract_id": self.task_info.contract_id,
                "run_id": self.task_info.run_id,
                "text_file_path": text_file_path,
                "page_count": parsed_doc.page_count,
                "characters_extracted": len(parsed_doc.text),
                "metadata": parsed_doc.metadata
            }

            self.logger.info(f"[EXECUTOR] Contract parsing completed for {self.task_info.contract_id}")
            self.logger.info(f"[EXECUTOR] Result: {result['page_count']} pages, {result['characters_extracted']} characters")
            return result

        except Exception as e:
            self.logger.error(f"Contract parsing failed: {e}")
            await self.api.report_failure(
                self.task_info.contract_id,
                f"Parsing failed: {str(e)}",
                "parsing_error"
            )
            raise