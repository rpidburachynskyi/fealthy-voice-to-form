"""Initialize Elasticsearch index and populate with data."""

import sys
import subprocess
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from logging_config import logger

# Get project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def run_script(script_path, description):
    """Run a Python script and return success status."""
    logger.info(f"Running: {description}")
    logger.info(f"Executing: {script_path}")

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(PROJECT_ROOT),
            check=True,
            capture_output=True,
            text=True,
        )
        if result.stdout:
            logger.info(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running {description}: {e}")
        if e.stdout:
            logger.error(f"stdout: {e.stdout}")
        if e.stderr:
            logger.error(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error running {description}: {e}")
        return False


def main():
    """Main initialization function."""
    logger.info("Starting Elasticsearch initialization...")

    scripts = [
        (
            PROJECT_ROOT / "elastic" / "create_businesses_index.py",
            "Step 1: Create Elasticsearch index",
        ),
        (
            PROJECT_ROOT
            / "_helpers"
            / "elasticsearch"
            / "add_bulk_from_json.py",
            "Step 2: Add businesses from JSON",
        ),
        (
            PROJECT_ROOT / "_helpers" / "elasticsearch" / "add_list.py",
            "Step 3: Add businesses from list",
        ),
    ]

    for script_path, description in scripts:
        if not script_path.exists():
            logger.error(f"Script not found: {script_path}")
            sys.exit(1)

        success = run_script(script_path, description)
        if not success:
            logger.error(f"Failed at: {description}")
            sys.exit(1)

        logger.info(f"Completed: {description}")

    logger.info("Elasticsearch initialization completed successfully!")


if __name__ == "__main__":
    main()
