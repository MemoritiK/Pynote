# PyNote

PyNote is a Python REPL built on top of IPython that adds enhanced terminal visualization and interactive code execution features. It provides a more visual and interactive experience than standard IPython while maintaining full compatibility with IPython magics and workflows.

## What It Is

PyNote wraps IPython's terminal shell and extends it with rich terminal rendering, graphics support, ML model introspection, and step-through code execution. It works as a drop-in replacement for the standard IPython terminal with additional capabilities.

## Extra Features Beyond IPython

- **DataFrame Visualization** - pandas DataFrames display as formatted tables with proper column alignment, intelligent truncation for large datasets, and type-aware value formatting. Series display as two-column tables with index and value columns.

- **Sixel Graphics** - Matplotlib plots and PIL images render directly in supported terminals using chafa. No need for external windows or file saving. Works automatically with `plt.show()`.

- **Easy Figure Saving** - The `%savefig` magic command saves the current matplotlib figure to a PNG file.

- **ML Model Detection** - Automatically recognizes trained models from scikit-learn, PyTorch, TensorFlow, and HuggingFace, displaying parameters, parameter counts, fit status, and device information.
 
- **Stepwise Execution** - Run Python files cell-by-cell (split on blank lines or control structures). Edit, delete, or insert cells during execution. Save modified code and execution results back to the file.

- **Session Export** - Save your REPL session as both JSON (with outputs and printed content) and Python script (code only) for later review or sharing. It can later be restored (including output images).
 
- **Notebook Conversion** - Convert Jupyter notebooks to Python scripts, HTML, or Markdown using nbconvert directly from the REPL.

- **Custom Syntax Styling** - PyNote uses a custom dark theme with carefully chosen colors for better readability. The prompt and output styling is also customized for visual clarity.

## Installation

```bash
pip install ipython numpy pandas rich pygments
```

Optional dependencies:

```bash
pip install matplotlib pillow          # plotting and figure saving
pip install scikit-learn torch tensorflow transformers  # ML detection
sudo apt install chafa                 # Sixel support (Linux)
brew install chafa                     # macOS
```

## Usage

Start the REPL:

```bash
python pynote.py
```

Create a plot and save it:

```python
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [4, 5, 6])
%savefig my_plot.png
```

View a DataFrame with rich formatting:

```python
import pandas as pd
df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
df
```

Run a file interactively:

```python
%step myscript.py
```

## Terminal Requirements

Sixel graphics require a terminal with Sixel support: iTerm2 (macOS), foot, WezTerm, mlterm, or Windows Terminal with Sixel enabled. Without Sixel, plots display as text representation.

## License

MIT
