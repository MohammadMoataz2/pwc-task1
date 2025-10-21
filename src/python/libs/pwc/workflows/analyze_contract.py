from uuid import uuid4
from pathlib import Path
from celery import chain, group
import logging

from pwc.task_interface.base import TaskInfo
from pwc.task_interface.schema import ContractState
from pwc.task_interface.contract_analysis import (
    change_contract_state,
    analyze_contract_clauses,
    evaluate_contract_health,
    report_contract_failure
)
from pwc.settings import settings

logger = logging.getLogger(__name__)


def create_analysis_workflow(contract_id: str, api_base_url: str, internal_token: str):
    """
    Create a Celery workflow for contract analysis following the reference pattern

    Returns:
        tuple: (pipeline, run_id) where pipeline is the Celery chain and run_id is unique identifier
    """
    run_id = str(uuid4())

    # Create task info for this workflow run
    task_info = TaskInfo(
        run_id=run_id,
        contract_id=contract_id,
        storage_root_path=Path(settings.local_storage_path) / "contracts" / contract_id / run_id,
        api_auth_token=internal_token,
        api_base_url=api_base_url
    )

    # Convert TaskInfo to dict for serialization
    task_info_dict = {
        "run_id": task_info.run_id,
        "contract_id": task_info.contract_id,
        "storage_root_path": str(task_info.storage_root_path),
        "api_auth_token": task_info.api_auth_token,
        "api_base_url": task_info.api_base_url
    }

    # Create workflow pipeline following reference project pattern
    pipeline = (
        # Step 1: Change state to processing
        change_contract_state.si(ContractState.processing.value, task_info_dict)
        .on_error(report_contract_failure.si("Failed to change state to processing", task_info_dict))

        # Step 2: Analyze contract clauses
        | analyze_contract_clauses.s(task_info_dict)
        .on_error(report_contract_failure.si("Failed to analyze contract clauses", task_info_dict))

        # Step 3: Evaluate contract health
        | evaluate_contract_health.s(task_info_dict)
        .on_error(report_contract_failure.si("Failed to evaluate contract health", task_info_dict))

        # Step 4: Change state to completed
        | change_contract_state.si(ContractState.completed.value, task_info_dict)
        .on_error(report_contract_failure.si("Failed to change state to completed", task_info_dict))
    )

    logger.info(f"Created analysis workflow for contract {contract_id} with run_id {run_id}")
    return pipeline, run_id


def create_parallel_analysis_workflow(contract_id: str, api_base_url: str, internal_token: str):
    """
    Create a parallel Celery workflow for contract analysis (advanced pattern)

    This version runs clause analysis and health evaluation in parallel for faster processing
    """
    run_id = str(uuid4())

    task_info = TaskInfo(
        run_id=run_id,
        contract_id=contract_id,
        storage_root_path=Path(settings.local_storage_path) / "contracts" / contract_id / run_id,
        api_auth_token=internal_token,
        api_base_url=api_base_url
    )

    task_info_dict = {
        "run_id": task_info.run_id,
        "contract_id": task_info.contract_id,
        "storage_root_path": str(task_info.storage_root_path),
        "api_auth_token": task_info.api_auth_token,
        "api_base_url": task_info.api_base_url
    }

    # Parallel analysis group
    analysis_group = group(
        analyze_contract_clauses.s(task_info_dict),
        evaluate_contract_health.s(task_info_dict)
    )

    # Create pipeline with parallel processing
    pipeline = (
        # Step 1: Change state to processing
        change_contract_state.si(ContractState.processing.value, task_info_dict)
        .on_error(report_contract_failure.si("Failed to change state to processing", task_info_dict))

        # Step 2: Run analysis and evaluation in parallel
        | analysis_group
        .on_error(report_contract_failure.si("Failed during parallel analysis", task_info_dict))

        # Step 3: Change state to completed
        | change_contract_state.si(ContractState.completed.value, task_info_dict)
        .on_error(report_contract_failure.si("Failed to change state to completed", task_info_dict))
    )

    logger.info(f"Created parallel analysis workflow for contract {contract_id} with run_id {run_id}")
    return pipeline, run_id