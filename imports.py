#!/usr/bin/env python3
import os
import sys
import subprocess
import tempfile
from typing import Optional
import datetime
import readline
import importlib
import ast
from pathlib import Path
# --- Style --------------------------------------------------------------------

from pygments.style import Style
from pygments.token import Token, Comment, Generic, Keyword, Name, String, Number, Operator, Error
from pygments.styles import STYLE_MAP


try:
    import numpy as np
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


try:
    from rich.console import Console
    from rich.table import Table as RichTable
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# --- Imports ------------------------------------------------------------------

try:
    from IPython.terminal.interactiveshell import TerminalInteractiveShell
except ImportError:
    print("IPython is required (pip install ipython)", file=sys.stderr)
    sys.exit(1)

try:
    import matplotlib
    from PIL import Image
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAS_MPL = True
except Exception:
    HAS_MPL = False

# --- SIXEL --------------------------------------------------------------------
from IPython import get_ipython
