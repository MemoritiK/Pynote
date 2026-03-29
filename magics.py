from imports import *
def magics(shell):
    def cls(_):
        os.system("clear")

    def savefig(name):
        if HAS_MPL and plt.get_fignums():
            today = str(datetime.date.today())
            plt.savefig(name or f"figure_{today}.png", dpi=150, bbox_inches="tight")

    def convert(line):
            
            # Parse arguments
            args = line.strip().split()
            if not args:
                print("Usage: %convert filename.ipynb [--to python|html|markdown]")
                return
            notebook = args[0]
            
            if not os.path.exists(notebook):
                print(f"Error: File '{notebook}' not found")
                return
            
            output_format = "python"
            if len(args) >= 3 and args[1] == "--to":
                output_format = args[2].lstrip('.')
            
            # Run nbconvert
            try:
                cmd = ["python", "-m", "nbconvert", f"--to", output_format, notebook]
                print(f"Converting {notebook} to {output_format}...")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    # Get output filename
                    notebook_path = Path(notebook)
                    output_file = notebook_path.with_suffix(f'.{output_format}')
                    print(f"Successfully converted to: {output_file}")
                    
                else:
                    print(f"Conversion failed:")
                    print(result.stderr)
                    
            except Exception as e:
                print(f"Error: {e}")
    
    def vars_magic(line):
            import types

            CYN   = "\033[1;96m"
            RST   = "\033[0m"
            SEP   = "─" * 80 + RST
            _SKIP_NAMES = {"In", "Out", "exit", "quit", "get_ipython", "open"}
            _SEED_ALIASES = {"np", "pd", "plt", "sns"}
     
            # Detect if a value looks like a trained ML model
            def _model_info(value):
                cls      = type(value)
                mod      = getattr(cls, "__module__", "") or ""
                typename = cls.__name__
     
                # sklearn
                if "sklearn" in mod:
                    params = {}
                    if hasattr(value, "get_params"):
                        p = value.get_params()
                        # show at most 2 key params
                        keys = list(p)[:2]
                        params = {k: p[k] for k in keys}
                    fitted = hasattr(value, "n_features_in_") or hasattr(value, "coef_") or hasattr(value, "feature_importances_")
                    tag = "fitted" if fitted else "unfitted"
                    detail = ", ".join(f"{k}={v}" for k, v in params.items())
                    return typename, tag, detail
     
                # torch nn.Module
                if "torch" in mod and hasattr(value, "parameters"):
                    try:
                        params = sum(p.numel() for p in value.parameters())
                        tag = f"{params:,} params"
                        device = next(value.parameters()).device
                        return typename, tag, str(device)
                    except StopIteration:
                        return typename, "no params", ""
     
                # keras / tf
                if "keras" in mod.lower() or "tensorflow" in mod.lower():
                    try:
                        p = value.count_params()
                        return typename, f"{p:,} params", ""
                    except Exception:
                        return typename, "", ""
     
                # transformers (HuggingFace)
                if "transformers" in mod:
                    cfg = getattr(value, "config", None)
                    detail = getattr(cfg, "model_type", "") if cfg else ""
                    return typename, "HF model", detail
     
                return None  # not a model
     
            ns       = shell.user_ns
            rows     = []   # (name, type_str, detail_str)
            models   = []   # (name, typename, tag, detail)
            imported = list(shell.run_line_magic('who_ls', ''))

            
            for name, value in ns.items():
                # Skip dunder, underscore-prefixed, IPython internals, modules
                if name.startswith("_") or name in _SKIP_NAMES:
                    continue

                   
                # Check for ML model first
                mi = _model_info(value)
                if mi:
                    typename, tag, detail = mi
                    models.append((name, typename, tag, detail))
                    continue
     
                # Regular variable — build a clean one-line description
                try:
                    typename = type(value).__name__
                    if typename == 'module' or typename=='?':
                        continue
                    if name in imported:
                       imported.remove(name)
                    # Shape / size annotation
                    if hasattr(value, "shape"):           # numpy, pandas, torch
                        shape = str(tuple(value.shape))
                        try:
                            dtype = str(value.dtype)
                        except Exception:
                            dtype = ""
                        detail = f"{shape}  {dtype}".strip()
                    elif hasattr(value, "__len__"):
                        detail = f"len={len(value)}"
                    else:
                        detail = ""
     
                    r = repr(value)
                    
                    # strip multiline (e.g. Series, DataFrame repr)
                    preview = r.split("\n")[0][:15]
                    if len(r) > 55 or "\n" in r:
                        preview += " …"
     
                    rows.append((name, typename + ("  " + detail if detail else ""), preview))
                except Exception:
                    rows.append((name, "?", ""))
     
            # ── render ────────────────────────────────────────────────────────────
            if imported:
                print(f"Libraries :{RST}  " + "  ".join(f"{a}{RST}" for a in sorted(imported)))
                print()
                
            if not rows and not models:
                return
     
            print()
     
     
            # Regular variables table
            if rows:
                print(SEP)
                print(f"  {CYN}{'Name':<18}{'Type / Shape':<28}{'Value'}{RST}")
                print(SEP)
                for name, typestr, preview in sorted(rows):
                    print(f"  {name:<18}{RST}{typestr:<28}{RST}{preview}")
                print(SEP)
     
            # ML models section
            if models:
                print(f"\n  {CYN}ML Models{RST}")
                print(SEP)
                for name, typename, tag, detail in sorted(models):
                    tag_s   = f"{tag}{RST}" if tag else ""
                    detail_s = f"  {detail}{RST}" if detail else ""
                    print(f"  {name:<18}{RST}{typename:<24}{RST}{tag_s}{detail_s}")
                print(SEP)
     
            print()


    def help_magic(line):
        """Show all important commands for PyNote REPL"""
        
        print("\n" + "-"*80)
        print(" PYNOTE REPL - COMPLETE COMMAND REFERENCE")
        
        # Custom PyNote Commands
        print("\n PYNOTE CUSTOM COMMANDS:")
        print("  %ss                      - Save session (input/output)")
        print("  %savefig [filename]      - Save matplotlib figure (default: figure.png)")
        print("  %convert notebook.ipynb  - Convert Jupyter notebook to Python script")
        print("  %convert notebook.ipynb --to markdown/html")
        print("  %step [filename]         - Stepwise file execution")        
        
        # File System Commands
        print("\n FILE SYSTEM COMMANDS:")
        print("  !ls / %ls               - List files in current directory")
        print("  !pwd / %pwd             - Print working directory")
        print("  !cd directory / %cd     - Change directory")
        print("  !cat file / %cat        - Display file contents")
        print("  %less file              - Page through file contents")
        print("  %mkdir dir              - Create directory")
        print("  %rm file                - Remove file")
        print("  %cp source dest         - Copy file")
        print("  %mv source dest         - Move/rename file")
        
        # Variable Inspection
        print("\n VARIABLE INSPECTION:")
        print("  %who                    - List all variables")
        print("  %whos                   - List variables with type information")
        print("  %who_ls                 - Return variables as list")
        print("  %vars                   - Enhanced display with ML detection and previews")
        print("  %reset                  - Reset namespace (clear all variables)")
        print("  %reset_selective regex  - Reset specific variables matching pattern")
        
        # Code Execution & Debugging
        print("\n CODE EXECUTION & DEBUGGING:")
        print("  %run script.py          - Run Python script")
        print("  %time statement         - Time execution of a statement")
        print("  %timeit statement       - Time multiple runs for accuracy")
        print("  %load file.py           - Load code from file into cell")
        print("  %edit                   - Open editor for code input")
        
        # System & Environment
        print("\n SYSTEM & ENVIRONMENT:")
        print("  %env                    - Show all environment variables")
        print("  %env VAR                - Show specific environment variable")
        print("  %alias                  - Create command aliases")
        print("  %history                - Show command history")
        print("  %save lines filename    - Save history lines to file")
        print("  !command                - Run any shell command")
        
        # Plotting & Visualization
        print("\n PLOTTING & VISUALIZATION:")
        print("  %savefig                - Save current matplotlib figure")       
        # Help
        print("-"*80)
        print("\n HELP:")
        print("  %help                   - Show this help")
        print("  ? command               - Show help for specific command")
        print("  command?                - Show docstring for command")        

        
    def step_load(line):
        args = line.strip().split()
        results = {}
        if not args:
            print("Usage: %step filename.py")
            return
        
        filename = args[0]
        
        if not os.path.exists(filename):
            print(f"Error: File '{filename}' not found")
            return
        
        try:
            with open(filename, 'r') as f:
                content = f.read()
                        
            blocks = []
            current_block = []
            lines = content.splitlines()
            
            i = 0
            while i < len(lines):
                 line = lines[i]
                 stripped = line.strip()
                 
                 current_block = [line]
                 
                 if stripped and (stripped.endswith(':') or 
                                stripped.startswith(('if ', 'for ', 'while ', 
                                                   'def ', 'class ', 'with ', 'try:', '@','#'))):
                     indent = len(line) - len(line.lstrip())
                     
                     j = i + 1
                     while j < len(lines):
                         next_line = lines[j]
                         next_stripped = next_line.strip()
                         
                         if not next_stripped or next_stripped.startswith('#'):
                             current_block.append(next_line)
                             j += 1
                             continue
                         
                         next_indent = len(next_line) - len(next_line.lstrip())

                         is_continuation = False
                         if next_indent == indent:
                             if (next_stripped.startswith(('elif ', 'else:', 'except:', 'finally:')) or
                                 next_stripped == 'else:' or next_stripped.startswith('except')):
                                 is_continuation = True
                                 
                         if next_indent <= indent and next_stripped and not is_continuation:
                             break
                         
                         current_block.append(next_line)
                         j += 1
                     
                     i = j
                 else:
                     # Single line
                     i += 1
                 
                 block_text = '\n'.join(current_block)
                 if block_text.strip():  
                     blocks.append(block_text)
    
            if not blocks:
                blocks = [line for line in lines if line.strip()]
            
            print(f" Loading: {filename}\n")
            
            modified = False
            current_blocks = blocks.copy()
            idx = 0
            
            while idx < len(current_blocks):
                block = current_blocks[idx]
                
                def show_block(b, i, n = None):
                    print(f"\033[95m──── Cell {i+1}/{len(current_blocks)} ────\033[0m")
                    for line in b.split('\n'):
                        if len(line) == 0:
                            continue
                        print(f"\033[90m> \033[0m {line}")
                    if n:
                        line =  n.split('\n')[0]
                        if len(line) == 0:
                           pass
                        print(f"\n\033[90m↓ \033[90m {line}")

                n = current_blocks[idx+1] if idx<len(current_blocks)-1 else None
                show_block(block, idx,n)
                
                while True:
                    choice = input(f"\033[1;32m▶\033[0m \033[90m[r]un [e]dit [d]elete [q]uit [a]dd cell above\033[0m ").strip().lower()
                    
                    if choice in ['', 'r', 'run']:
                        import io
                        import contextlib
                        
                        stdout_buffer = io.StringIO()
                        
                        with contextlib.redirect_stdout(stdout_buffer):
                            result = shell.run_cell(block)
                        
                        printed_output = stdout_buffer.getvalue()
                        execution_result = result.result
                        
                        if result.success:
                            results[idx] = ""
                            if printed_output:
                                print(f"\033[96m{printed_output}\033[0m", end="")
                                results[idx] += "Prints: " + str(printed_output).rstrip('\n')
                        
                            if execution_result:
                                if printed_output:
                                   if str(printed_output).strip().rstrip('\n') != str(execution_result).strip():
                                       results[idx] += " Out: " + str(execution_result)
                                else:
                                   results[idx] += " Out: " + str(execution_result)
                            print(f"\033[1;32m  ✓ done\033[0m\n")

                        else:
                            error = result.error_in_exec
                            results[idx] = 'error'
                            if error:
                               print(f"\033[1;31m  ✗ {error}\033[0m\n")
                               print(f"\033[90m  Cell failed. [e]dit and retry, [s]kip\033[0m")
                               retry = input(f"\033[1;32m  ▶\033[0m ").strip().lower()
                               
                               if retry in ['e', 'edit']:
                                   modified = True
                                   with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as tmp:
                                       tmp.write(block)
                                       tmp.flush()
                                       subprocess.call(['micro', tmp.name])
                                       tmp.seek(0)
                                       new_block = tmp.read()
                                       os.unlink(tmp.name)
                                   
                                   if new_block != block:
                                       current_blocks[idx] = new_block
                                       block = new_block
                                       print(f"\033[1;32m  ✓ updated\033[0m")
                                       show_block(block, idx)
                                       continue
                                   else:
                                       print(f"\033[90m  — no changes\033[0m")
                                       continue
                               
                               elif retry in ['s', 'skip']:
                                   print(f"\033[90m  — skipped\033[0m\n")
                                   idx += 1
                                   break
              
                        idx += 1
                        break
                    
                    elif choice in ['e', 'edit']:
                        modified = True
                        with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as tmp:
                            tmp.write(block)
                            tmp.flush()
                            subprocess.call(['micro', tmp.name])
                            tmp.seek(0)
                            new_block = tmp.read()
                            os.unlink(tmp.name)
                        
                        if new_block != block:
                            current_blocks[idx] = new_block
                            block = new_block
                            print(f"\033[1;32m  ✓ updated\033[0m\n")
                            show_block(block, idx)
                        else:
                            print(f"\033[90m  — no changes\033[0m\n")
                    

                    elif choice in ['a', 'add']:
                        modified = True
                        print(f"\033[90m  Enter new cell code (end with Ctrl+D on new line):\033[0m")
                        lines = []
                        try:
                            while True:
                                line = input()
                                lines.append(line)
                        except EOFError:
                            pass
                        new_block = '\n'.join(lines)
                        if new_block.strip():
                            current_blocks.insert(idx, new_block)
                            print(f"\033[1;32m  ✓ added new cell\033[0m\n")
                        else:
                            print(f"\033[90m  — empty cell, not added\033[0m\n")
                        print('\n')    
                        break
                     
                    elif choice in ['d', 'delete']:
                        modified = True
                        del current_blocks[idx]
                        print(f"\033[1;32m  ✓ deleted\033[0m\n")
                        if len(current_blocks) > 0:
                            break
                        else:
                            print(f"\033[90m  No cells left\033[0m")
                            return
                        break                 
                    
                    elif choice in ['q', 'quit']:
                        if modified:
                            save = input(f"\n\033[1;33mSave changes to {filename}? (y/n): \033[0m").strip().lower()
                            if save == 'y':
                                with open(filename, 'w') as f:
                                    f.write('\n\n'.join(current_blocks))
                                print(f"\033[1;32m✓ saved to {filename}\033[0m")
                        print(f"\n\033[1;33m⏹ stopped at cell {idx+1}\033[0m")
                        return
                    
                    else:
                        print(f"\033[90m  ? r/e/a/d/s/q\033[0m")

            if modified or results:
                save = input(f"\n\033[1;33mSave changes/results to {filename}? (y/n): \033[0m").strip().lower()
                if save == 'y':
                    with open(filename, 'w') as f:
                        for i, block in enumerate(current_blocks):
                            f.write(f"{block}\n")
                            f.write(f"# Cell {i+1}: {results[i]}\n\n")
                    
                    print(f"\033[1;32m Saved to {filename}\033[0m")
            
            print(f"\n\033[1;32m✓ Completed {len(blocks)} cells\033[0m")
                    
        except Exception as e:
                    print(f"Error: {e}")

    def save_session(line):
        import json
        from datetime import datetime
        
        args = line.strip().split()

        if args and args[0] == "restore":
                if len(args) < 2:
                    print("Usage: save_session restore <file.json>")
                    return
                
                filename = args[1]
        
                if not os.path.exists(filename):
                    print(f"File not found: {filename}")
                    return
        
                with open(filename, "r") as f:
                    data = json.load(f)
        
                for cell in data:
                    print(f"\n# Cell {cell['cell_num']}")
                    print(cell['input'])
        
                    if cell.get("prints"):
                        for p in cell["prints"]:
                            print(p)
        
                    out = cell.get("output")
                    if out:
                        print(out)
        
                return
                
        if args:
            base = args[0].rsplit('.', 1)[0]
        else:
            base = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        data = []
        code = []
        
        for _, _, inp in shell.history_manager.get_range():
            cell = len(data) + 1
            out = None
            if cell in shell.user_ns.get('Out', {}):
                try:
                    out = repr(shell.user_ns['Out'][cell])
                    if len(out) > 500: out = out[:500] + "..."
                except:
                    out = "<unprintable>"
            
            data.append({
                'cell_num': cell,
                'input': inp.strip(),
                'output': out,
                'prints': print_capture.captured.get(cell, [])
            })
            
            if inp.strip():
                code.append(f"# Cell {cell}")
                code.append(inp.strip())
                code.append("")
        
        with open(f"{base}.json", 'w') as f:
            json.dump(data, f, indent=2)
        
        with open(f"{base}.py", 'w') as f:
            f.write("\n".join(code))
        
        print(f"Saved: {base}.json + {base}.py")
            
    shell.register_magic_function(save_session, "line", "ss")              
    shell.register_magic_function(step_load, "line", "step")
    shell.register_magic_function(convert, "line", "convert")
    shell.register_magic_function(cls,      "line", "cls")
    shell.register_magic_function(savefig,  "line", "savefig")
    shell.register_magic_function(vars_magic, "line", "vars")
    shell.register_magic_function(help_magic, "line", "help")
