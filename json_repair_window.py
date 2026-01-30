import tkinter as tk
from tkinter import ttk, messagebox
import json
from json_repair import repair_json
from pygments import lex
from pygments.lexers import JsonLexer
from pygments.token import Token


class JsonRepairWindow(tk.Toplevel):
    """JSON-Repair utility tool window for extracting and fixing JSON from LLM responses"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("JSON-Repair Tool")
        self.geometry("850x750")
        self.transient(parent)  # Keep window on top of parent
        
        # Center the window relative to parent
        self._center_on_parent(parent)
        
        self._create_widgets()
        self._configure_styles()
    
    def _center_on_parent(self, parent):
        """Center this window on the parent window"""
        # Update the window to ensure geometry is calculated
        self.update_idletasks()
        
        # Get parent window dimensions and position
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # Get this window's dimensions
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        
        # Calculate center position
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
        
        # Ensure the window is not positioned off-screen
        x = max(0, x)
        y = max(0, y)
        
        # Set the position
        self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create all UI components"""
        # Top instruction label
        top_label = ttk.Label(
            self, 
            text="Paste LLM response text below to extract and repair JSON:",
            font=("Segoe UI", 10)
        )
        top_label.pack(pady=(10, 5))
        
        # Input area container
        input_frame = ttk.LabelFrame(self, text="Input", padding=5)
        input_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Input text box + scrollbar
        input_container = ttk.Frame(input_frame)
        input_container.pack(fill="both", expand=True)
        
        self.input_text = tk.Text(
            input_container,
            wrap="word",
            font=("Consolas", 10),
            borderwidth=1,
            relief="solid"
        )
        input_scrollbar = ttk.Scrollbar(
            input_container,
            orient="vertical",
            command=self.input_text.yview
        )
        self.input_text.configure(yscrollcommand=input_scrollbar.set)
        self.input_text.grid(row=0, column=0, sticky="nsew")
        input_scrollbar.grid(row=0, column=1, sticky="ns")
        input_container.grid_rowconfigure(0, weight=1)
        input_container.grid_columnconfigure(0, weight=1)
        
        # Button group
        button_frame = ttk.Frame(self, padding=5)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        # Configure button style
        style = ttk.Style(self)
        style.configure("Blue.TButton", foreground="white", background="#2563eb", padding=6)
        style.map("Blue.TButton", background=[('active', '#1d4ed8')])
        
        ttk.Button(
            button_frame,
            text="Extract & Repair JSON",
            command=self._repair_json,
            style="Blue.TButton"
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="Clear All",
            command=self._clear_all
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="Copy Result",
            command=self._copy_result
        ).pack(side="left", padx=5)
        
        # Output area container
        output_frame = ttk.LabelFrame(self, text="Output (JSON)", padding=5)
        output_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Output text box + scrollbar
        output_container = ttk.Frame(output_frame)
        output_container.pack(fill="both", expand=True)
        
        self.output_text = tk.Text(
            output_container,
            wrap="word",
            font=("Consolas", 10),
            borderwidth=1,
            relief="solid",
            state="disabled",
            bg="#f9f9f9"
        )
        output_scrollbar = ttk.Scrollbar(
            output_container,
            orient="vertical",
            command=self.output_text.yview
        )
        self.output_text.configure(yscrollcommand=output_scrollbar.set)
        self.output_text.grid(row=0, column=0, sticky="nsew")
        output_scrollbar.grid(row=0, column=1, sticky="ns")
        output_container.grid_rowconfigure(0, weight=1)
        output_container.grid_columnconfigure(0, weight=1)
        
        # Status bar
        status_frame = ttk.Frame(self, relief="sunken", borderwidth=1)
        status_frame.pack(fill="x", side="bottom", padx=10, pady=(0, 10))
        self.status_label = ttk.Label(
            status_frame,
            text="Ready",
            font=("Segoe UI", 9)
        )
        self.status_label.pack(side="left", padx=5, pady=2)
    
    def _configure_styles(self):
        """Configure JSON syntax highlighting styles using Pygments token types"""
        # Define color mappings for different token types
        self.token_colors = {
            Token.Name.Tag: "#0066cc",           # JSON keys - blue
            Token.String.Double: "#008000",      # String values - green
            Token.Literal.Number: "#ff6600",     # Numbers - orange
            Token.Keyword.Constant: "#9900cc",   # true/false/null - purple
            Token.Punctuation: "#666666",        # Symbols - dark gray
        }
        
        # Configure text tags for each token type
        for token_type, color in self.token_colors.items():
            tag_name = str(token_type)
            if token_type == Token.Name.Tag:
                # Keys are bold
                self.output_text.tag_configure(tag_name, foreground=color, font=("Consolas", 10, "bold"))
            else:
                self.output_text.tag_configure(tag_name, foreground=color)
    
    def _repair_json(self):
        """Extract, repair, and format JSON"""
        input_text = self.input_text.get("1.0", "end-1c").strip()
        
        if not input_text:
            self.status_label.config(text="✗ Error: Input is empty")
            return
        
        try:
            # Use json-repair to extract and fix JSON
            repaired = repair_json(input_text)
            
            # Parse and format
            parsed = json.loads(repaired)
            formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
            
            # Display in output box
            self.output_text.config(state="normal")
            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", formatted)
            
            # Apply syntax highlighting
            self._highlight_json(formatted)
            
            self.output_text.config(state="disabled")
            
            # Update status
            lines = len(formatted.splitlines())
            chars = len(formatted)
            self.status_label.config(
                text=f"✓ JSON extracted and repaired successfully ({lines} lines, {chars} chars)"
            )
            
        except Exception as e:
            self.output_text.config(state="normal")
            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", f"Failed to extract/repair JSON.\n\nError: {str(e)}")
            self.output_text.config(state="disabled")
            error_msg = str(e)[:50] + "..." if len(str(e)) > 50 else str(e)
            self.status_label.config(text=f"✗ Error: {error_msg}")
    
    def _highlight_json(self, json_text):
        """Apply JSON syntax highlighting using Pygments lexer"""
        # Use Pygments to tokenize JSON
        lexer = JsonLexer()
        tokens = list(lex(json_text, lexer))
        
        # Clear all existing tags
        for tag in self.output_text.tag_names():
            self.output_text.tag_remove(tag, "1.0", "end")
        
        # Build position tracking
        current_pos = "1.0"
        
        for token_type, value in tokens:
            # Calculate end position
            value_len = len(value)
            
            # Get the tag name for this token type
            tag_name = str(token_type)
            
            # Apply color only for tokens we care about
            if token_type in self.token_colors or any(token_type in t for t in self.token_colors):
                # Find matching base token type
                for base_token, color in self.token_colors.items():
                    if token_type in base_token or str(token_type).startswith(str(base_token)):
                        tag_name = str(base_token)
                        break
                
                # Calculate end position
                end_pos = self.output_text.index(f"{current_pos}+{value_len}c")
                self.output_text.tag_add(tag_name, current_pos, end_pos)
                current_pos = end_pos
            else:
                # Move position forward without highlighting
                current_pos = self.output_text.index(f"{current_pos}+{value_len}c")
    
    def _clear_all(self):
        """Clear input and output"""
        self.input_text.delete("1.0", "end")
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.config(state="disabled")
        self.status_label.config(text="Ready")
    
    def _copy_result(self):
        """Copy output result to clipboard"""
        content = self.output_text.get("1.0", "end-1c")
        if not content or content.strip() == "":
            self.status_label.config(text="✗ Nothing to copy")
            return
        
        try:
            self.clipboard_clear()
            self.clipboard_append(content)
            self.update()
            self.status_label.config(text="✓ Copied to clipboard!")
        except tk.TclError:
            messagebox.showwarning(
                "Copy Failed",
                "Could not copy content to clipboard. It might be too large."
            )

