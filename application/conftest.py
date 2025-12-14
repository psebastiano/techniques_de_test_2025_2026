"""Set the absolute path for correct pytest module import."""

import os
import sys

# Add the 'application' directory (which is a sibling to this conftest.py) 
# to the system path so that absolute imports work from the 'application' package.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'application')))