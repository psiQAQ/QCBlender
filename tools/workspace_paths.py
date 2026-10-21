"""Small directory helpers shared by local validation entry points."""
from pathlib import Path


def temporary_tests_root(repo):
    """Create the ignored test workspace without relying on other test runners."""
    directory = Path(repo) / '.tmp/tests'
    directory.mkdir(parents=True, exist_ok=True)
    return directory
