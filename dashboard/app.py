"""Week 4 dashboard launcher."""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.load.loader import DEFAULT_DB_PATH
from src.visualization.ui import launch_dashboard


def main() -> None:
    """Launch the Tkinter dashboard."""
    launch_dashboard(DEFAULT_DB_PATH)


if __name__ == "__main__":
    main()
