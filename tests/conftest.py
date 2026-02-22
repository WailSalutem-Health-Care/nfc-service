"""
Pytest Configuration and Fixtures

Developers:
  - Muhammad Faizan
  - Roozbeh Kouchaki
  - Fatemehalsadat Sabaghjafari
  - Dipika Bhandari

Description:
    Pytest configuration file with shared test setup and fixtures.
    Ensures the app module can be imported during tests.
"""
# Development Team: Muhammad Faizan, Roozbeh Kouchaki, Fatemehalsadat Sabaghjafari, Dipika Bhandari

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
