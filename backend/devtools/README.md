# Devtools

This folder contains manual developer scripts and helpers that should not be
collected by pytest. If you need to run any of the moved test scripts, run them
explicitly (for example `python devtools/my_script.py`) from the `backend`
package root or adjust PYTHONPATH accordingly.

Files are intentionally simple placeholders to avoid accidental pytest
collection and to preserve historical scripts for manual execution.
This folder contains development and manual test scripts that are not intended to be run by pytest.

Move or run scripts here manually, e.g.:

    python -m backend.devtools.test_structured_output

Do not commit production tests into this folder.
