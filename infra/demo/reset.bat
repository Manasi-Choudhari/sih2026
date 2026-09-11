@echo off
REM ==============================================================================
REM VAJRA (SIH 26183) — Fast Demo Reset Script (Windows CMD) (T6 Task 8)
REM Resets the databases and caches to a clean state for live judging rehearsals.
REM ==============================================================================

echo ========================================================
echo  VAJRA DEMO RESET: Restoring clean evaluation state... 
echo ========================================================

echo [1/3] Clearing ephemeral audit events...
python -c "from infra.audit import audit_event_store; audit_event_store.clear(); print('Audit trail reset.')" 2>nul

echo [2/3] Verifying scenario acceptance harness...
python scenarios\acceptance\test_runner.py --stub

echo [3/3] Sanity check environment...
python -c "import os; print('ML_DEVICE:', os.getenv('ML_DEVICE', 'cpu')); print('NCRP_MOCK_MODE:', os.getenv('NCRP_MOCK_MODE', 'true'))"

echo ========================================================
echo  VAJRA DEMO RESET COMPLETE: Ready for live presentation!
echo ========================================================
