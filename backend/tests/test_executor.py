import os
import sys
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))
from executor import is_low_risk, run_command


def test_is_low_risk():
    assert is_low_risk('npm run lint')
    assert is_low_risk('pytest -q') or is_low_risk(f'{sys.executable} -m pytest')
    assert not is_low_risk('git push origin main')


def test_run_command_success():
    res = run_command('echo hello')
    assert res['returncode'] == 0
    assert 'hello' in res['stdout']


def test_run_command_timeout():
    # Use a small timeout to force timeout on a sleep command
    res = run_command('python -c "import time; time.sleep(2)"', timeout=1)
    assert res['returncode'] is None
    assert 'Timeout' in res['stderr']
