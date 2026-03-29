#!/usr/bin/env python3
from magics import *
from imports import *
from formatting import *

def has_sixel():
    term = os.environ.get("TERM", "").lower()
    if "sixel" in term:
        return True
    try:
        return subprocess.run(["chafa", "--version"], capture_output=True).returncode == 0
    except Exception:
        return False

def show_sixel(path: str, width: Optional[int] = 80):
    try:
        cmd = ["chafa", "--format", "sixel", "--align", "center", "--dither", "none"]
        if width:
            cmd += ["--size", f"{width}x"]
        cmd.append(path)
        out = subprocess.run(cmd, capture_output=True, text=True)
        if out.stdout:
            print(out.stdout, end="")
    except Exception:
        pass

_original_show = None

def _sixel_show(*args, **kwargs):
    import inspect
    frame = inspect.currentframe()
    caller_frame = frame.f_back
    caller_function = caller_frame.f_code.co_name if caller_frame else None
    
    if caller_function in ['_save', '_encode_tile', 'save', 'print_figure']:
        if args and hasattr(args[0], 'savefig'):
            return _original_show(*args, **kwargs)
        return _original_image_open(*args, **kwargs)
    
    if not args and not kwargs:
        figs = [plt.figure(i) for i in plt.get_fignums()]
        if figs:
            for fig in figs:
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    path = tmp.name
                try:
                    fig.savefig(path, dpi=100, bbox_inches="tight", facecolor=fig.get_facecolor())
                    print()
                    show_sixel(path)
                    print()
                finally:
                    try:
                        os.unlink(path)
                    except Exception:
                        pass
            plt.close("all")
        return
    
    if len(args) == 1 and isinstance(args[0], Image.Image):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            path = tmp.name
        try:
            args[0].save(path, format='PNG')
            print()
            show_sixel(path)
            print()
        finally:
            try:
                os.unlink(path)
            except Exception:
                pass
        return args[0]
        

def create_img(*args,**kwargs):
    pil_img = _original_image_new(*args, **kwargs)
    _sixel_show(pil_img)

def enable_sixel():
    global _original_show, _original_image_new
    if not HAS_MPL or not has_sixel():
        return
    _original_show = plt.show
    plt.show = _sixel_show


    try:
            ip = get_ipython()
            if ip:
                ip.display_formatter.formatters['text/plain'].for_type(
                    Image.Image,
                    lambda img, pp, cycle: _sixel_show(img)
                )
                

    except Exception as e:
            print(f"Could not register display formatters: {e}")

# --- Magics -------------------------------------------------------------------

def intro():
    print("PyNote Kernel (Stable IPython-like REPL)")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Working dir: {os.getcwd()}")
    print("\n")


class PrintCapture:
    def __init__(self):
        self.original_print = print
        self.captured = {}  
        self.current_cell = None
        
    def capture(self, *args, **kwargs):
        self.original_print(*args, **kwargs)
        
        if self.current_cell is not None:
            sep = kwargs.get('sep', ' ')
            end = kwargs.get('end', '\n')
            output = sep.join(str(arg) for arg in args) + end
            
            if self.current_cell not in self.captured:
                self.captured[self.current_cell] = []
            self.captured[self.current_cell].append(output.rstrip('\n'))
    
    def start_cell(self, cell_num):
        self.current_cell = cell_num
    
    def end_cell(self):
        self.current_cell = None
        
print_capture = PrintCapture()

def setup_capture(shell):
    def pre_execute():
        print_capture.start_cell(shell.execution_count + 1)
    
    def post_execute():
        print_capture.end_cell()
    
    shell.events.register('pre_execute', pre_execute)
    shell.events.register('post_execute', post_execute)   
     
# --- Prompt -------------------------------------------------------------------
def prompt(shell):
    from IPython.terminal.prompts import Prompts, Token

    class P(Prompts):
        def in_prompt_tokens(self, cli=None):
            return [
                (Token.Prompt,    "In ["),
                (Token.PromptNum, str(self.shell.execution_count)),
                (Token.Prompt,    "]: "),
            ]

        def out_prompt_tokens(self):
            return [
                (Token.OutPrompt,    "   ["),
                (Token.OutPromptNum, str(self.shell.execution_count)),
                (Token.OutPrompt,    "]: "),
            ]

    return P(shell)



_SEED_IMPORTS = [
    ("numpy",   "np"),
    ("pandas",  "pd"),
    ("seaborn", "sns"),
]

def _seed_namespace(shell) -> None:
    injected = []
    for module, alias in _SEED_IMPORTS:
        try:
            mod = importlib.import_module(module)
            shell.user_ns[alias] = mod
            injected.append(alias)
        except ImportError:
            pass

    if HAS_MPL:
        shell.user_ns["plt"] = plt
        injected.append("plt")
    if injected:
        pass


# --- Main ---------------------------------------------------------------------

def main():
    os.system('clear' if os.name == 'posix' else 'cls')
    intro()
    
    from traitlets.config import Config
    c = Config()
    c.TerminalInteractiveShell.banner = ""
    c.TerminalInteractiveShell.confirm_exit = False
    c.TerminalInteractiveShell.colors = "Linux"
    c.TerminalInteractiveShell.highlighting_style = PyNoteStyle
    
    shell = TerminalInteractiveShell.instance(config=c)

    def setup_rich_display(shell):        
        ip = get_ipython()
        
        def display_dataframe(df):
            if HAS_RICH:
                formatter = RichOutputFormatter(shell)
                table = formatter.format_dataframe(df)
                if table:
                    console = Console()
                    console.print(table)
                    return True
            return False
        
        def display_series(series):
            if HAS_RICH:
                formatter = RichOutputFormatter(shell)
                table = formatter.format_series(series)
                if table:
                    console = Console()
                    console.print(table)
                    return True
            return False
        
        if HAS_PANDAS and HAS_RICH:
            ip.display_formatter.formatters['text/plain'].for_type(
                pd.DataFrame, 
                lambda df, pp, cycle: display_dataframe(df)
            )
            
            ip.display_formatter.formatters['text/plain'].for_type(
                pd.Series, 
                lambda s, pp, cycle: display_series(s)
            )
    
    setup_rich_display(shell)
    shell.prompts = prompt(shell)
    magics(shell)
    enable_sixel()
    setup_capture(shell)
    
    _seed_namespace(shell)
        
    import builtins
    builtins.print = print_capture.capture
    
    try:
        shell.run_line_magic("load_ext", "autoreload")
        shell.run_line_magic("autoreload", "2")
    except Exception:
        pass
    
    try:
        from prompt_toolkit.styles import merge_styles
        from prompt_toolkit.styles.pygments import style_from_pygments_cls
        from prompt_toolkit.styles import Style as PTStyle
        
        base_style = style_from_pygments_cls(PyNoteStyle)
        
        custom = PTStyle.from_dict({
            "pygments.prompt":        "#50DA73",
            "pygments.outprompt":     "#F22B59",
            "pygments.promptnum":     "#F6F5CF bold",
            "pygments.outpromptnum":  "#FCE9D8 bold",
            "pygments.name.attribute":"#ebc275",
        })
        
        shell.pt_app.style = merge_styles([base_style, custom])
        import warnings
        warnings.filterwarnings("ignore")
        shell.interact()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
