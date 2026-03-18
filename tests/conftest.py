import sys
import os

# Add the parent directory (programa/) to sys.path so tests can import modules
_parent = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, _parent)

# Change working directory to programa/ so relative paths like "data/" work
os.chdir(_parent)
