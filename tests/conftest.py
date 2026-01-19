"""
Pytest configuration file.

This file ensures the app module can be imported during tests.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
