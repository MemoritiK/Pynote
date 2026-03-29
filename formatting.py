from imports import *
class RichOutputFormatter:
    def __init__(self, shell):
        self.shell = shell
        self.console = Console()
        
    def format_dataframe(self, df, max_rows=10, max_cols=None):
            import shutil
            from rich.text import Text
            from rich.style import Style
            
            if not HAS_RICH or not HAS_PANDAS:
                return str(df)
            
            terminal_width = shutil.get_terminal_size().columns
            n_rows, n_cols = df.shape
            
            if max_cols is None:
                max_cols = min(n_cols, max(5, terminal_width // 15))
            
            df_view = df.head(max_rows).iloc[:, :max_cols]
            show_rows, show_cols = df_view.shape
            
            str_df = df_view.astype(str)
            
            col_widths = []
            for col in str_df.columns:
                header_len = len(str(col))
                max_content_len = str_df[col].str.len().max() if show_rows > 0 else 0
                col_widths.append(min(max(header_len, max_content_len) + 2, 50))
            
            # Create table with styles
            table = RichTable(
                title=f"DataFrame - {n_rows} rows × {n_cols} columns",
                box=box.ROUNDED,
                title_style="blue",
                header_style="bold magenta"
            )
            
            # Add columns with headers
            for col, width in zip(df_view.columns, col_widths):
                table.add_column(
                    str(col),
                    width=width,
                    overflow="fold",
                    no_wrap=False
                )
            
            # Add rows with colored values
            for idx in range(show_rows):
                row_cells = []
                for col in df_view.columns:
                    val = df_view.iloc[idx][col]
                    
                    if isinstance(val, float):
                        val = f"{val:.3f}"
                
                    text = Text(str(val), style="white")
                    
                    row_cells.append(text)
                
                table.add_row(*row_cells)
            
            if n_rows > max_rows:
                ellipsis_row = [Text("...", style="bold") for _ in range(show_cols)]
                table.add_row(*ellipsis_row, style="bold")
            
            if n_cols > max_cols:
                table.caption = f"... and {n_cols - max_cols} more columns"
            
            return table
    
    def format_series(self, series, max_rows=10):
        if not HAS_RICH:
            return str(series)
        
        table = RichTable(title=f"Series - {len(series)} items",
                         box=box.ROUNDED,
                         title_style="bold cyan")
        
        table.add_column("Index", style="cyan")
        table.add_column("Value", style="green")
        
        for idx, val in series.head(max_rows).items():
            if isinstance(val, float):
                val = f"{val:.3f}"
            table.add_row(str(idx), str(val)[:50])
        
        if len(series) > max_rows:
            table.add_row("...", f"... and {len(series) - max_rows} more")
        
        return table


class PyNoteStyle(Style):
    background_color = "#0f111a"
    default_style = ""

    styles = {
        # Base text
        Token: "#c9d1d9",

        # Comments (muted warm gray)
        Comment: "#8b7a7a",

        # Keywords (soft purple)
        Keyword: "#c678dd",
        Keyword.Type: "#ebc275",

        # Names (core identity system)
        Name: "#e6edf3",
        Name.Builtin: "#ff4fd8",      # bright pink (your preference)
        Name.Function: "#5ab0f6",
        Name.Class: "#ebc275",
        Name.Decorator: "#61afef",
        Name.Exception: "#e06c75",
        Name.Namespace: "#5ab0f6",

        # Strings / Numbers
        String: "#79E845",
        Number: "#ff9f43",            # vibrant orange

        # Operators
        Operator: "#8a8787",
        Operator.Word: "#c678dd",

        # Output / prompt
        Generic.Prompt: "#50da73",
        Generic.OutPrompt: "#f22b59",
        Generic.Traceback: "#e06c75",

        # Errors
        Error: "bg:#1E1E1E #e06c75",
    }

STYLE_MAP["pynote"] = "pynote::PyNoteStyle"
