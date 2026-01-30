import tkinter as tk
from tkinter import ttk, filedialog, font, messagebox
import os
import threading
import time  # 用于调试和性能分析

# --- Configuration Constants (mirrors the JS project) ---
# (常量部分保持不变)
IGNORED_DIRECTORIES = {'node_modules', 'venv', '.git', '__pycache__', '.idea', '.vscode'}
IGNORED_FILES = {
    '.DS_Store', 'Thumbs.db', '.env', '.pyc', '.jpg', '.jpeg', '.png', '.gif',
    '.mp4', '.mov', '.avi', '.webp', '.mkv', '.wmv', '.flv', '.svg', '.zip', '.tar', '.gz',
    '.rar', '.exe', '.bin', '.iso', '.dll', '.psd', '.ai', '.eps', '.tiff', '.woff',
    '.woff2', '.ttf', '.otf', '.flac', '.m4a', '.aac', '.3gp'
}
LIKELY_TEXT_EXTENSIONS = {
    '.txt', '.md', '.markdown', '.json', '.js', '.ts', '.jsx', '.tsx',
    '.css', '.scss', '.sass', '.less', '.html', '.htm', '.xml', '.yaml',
    '.yml', '.ini', '.conf', '.cfg', '.config', '.py', '.rb', '.php',
    '.java', '.c', '.cpp', '.h', '.hpp', '.cs', '.go', '.rs', '.swift',
    '.kt', '.kts', '.sh', '.bash', '.zsh', '.fish', '.sql', '.graphql',
    '.vue', '.svelte', '.astro', '.env.example', '.gitignore', '.dockerignore',
    '.editorconfig', '.eslintrc', '.prettierrc', '.babelrc', 'LICENSE',
    'README', 'CHANGELOG', 'TODO', '.csv', '.tsv'
}


# --- Main Application Class ---

class CodebaseToPromptApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Codebase to Prompt")
        try:
            # 在macOS/Linux上可能需要不同的方式设置图标
            if os.name == 'nt':
                self.iconbitmap('logo.ico')
        except tk.TclError:
            print("Warning: 'logo.ico' not found. Using default icon.")
        self.geometry("1400x900")

        # --- State Management ---
        self.root_path = None
        self.file_tree_data = None
        self.file_contents = {}
        self.selected_paths = set()
        self.iid_map = {}  # Maps item ID to its full path
        self.path_to_iid = {}  # OPTIMIZATION: Maps full path back to item ID
        self.is_updating_content = False  # OPTIMIZATION: Flag to prevent concurrent updates

        # --- UI Setup ---
        self._configure_styles()
        self._create_checkbox_images()
        self._create_widgets()

        # Initial state
        self._update_right_pane_text("Select files from the left to generate a prompt.")
        self._update_status_bar()

    def _configure_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure("TButton", padding=6, relief="flat", font=('Segoe UI', 9))
        self.style.configure("Blue.TButton", foreground="white", background="#2563eb")
        self.style.map("Blue.TButton", background=[('active', '#1d4ed8')])
        self.style.configure("Treeview", rowheight=25, font=('Segoe UI', 10))
        self.style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))

    def _create_checkbox_images(self):
        self.img_unchecked = tk.PhotoImage(width=16, height=16)
        self.img_unchecked.put("#c0c0c0", to=(0, 0, 15, 15))
        self.img_unchecked.put("white", to=(1, 1, 14, 14))
        self.img_checked = tk.PhotoImage(width=16, height=16)
        self.img_checked.put("#2563eb", to=(0, 0, 15, 15))
        self.img_checked.put("white", to=(3, 8, 6, 8))
        self.img_checked.put("white", to=(6, 8, 12, 8))
        self.img_checked.put("white", to=(6, 7, 6, 8))
        self.img_checked.put("white", to=(3, 7, 3, 8))
        self.img_checked.put("white", to=(12, 4, 12, 8))
        self.img_checked.put("white", to=(11, 5, 11, 6))
        self.img_tristate = tk.PhotoImage(width=16, height=16)
        self.img_tristate.put("#2563eb", to=(0, 0, 15, 15))
        self.img_tristate.put("white", to=(4, 7, 11, 8))

    def _create_widgets(self):
        top_bar = ttk.Frame(self, padding=5)
        top_bar.pack(side="top", fill="x")
        ttk.Button(top_bar, text="Select Directory", style="Blue.TButton", command=self._on_select_directory).pack(
            side="left", padx=5)
        ttk.Button(top_bar, text="Help", command=self._show_help).pack(side="left")

        ttk.Button(top_bar, text="Expand All", command=lambda: self._toggle_all(True)).pack(side="left", padx=(20, 2))
        ttk.Button(top_bar, text="Collapse All", command=lambda: self._toggle_all(False)).pack(side="left", padx=2)
        ttk.Button(top_bar, text="Select All", command=lambda: self._select_all(True)).pack(side="left", padx=(20, 2))
        ttk.Button(top_bar, text="Deselect All", command=lambda: self._select_all(False)).pack(side="left", padx=2)
        ttk.Button(top_bar, text="Clear", command=self._clear_all).pack(side="right", padx=5)

        paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned_window.pack(fill="both", expand=True, padx=5, pady=5)

        left_frame = ttk.Frame(paned_window)
        self.tree = ttk.Treeview(left_frame, show="tree", columns=())
        tree_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_scrollbar.grid(row=0, column=1, sticky="ns")
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        self.tree.tag_configure("unchecked", image=self.img_unchecked)
        self.tree.tag_configure("checked", image=self.img_checked)
        self.tree.tag_configure("tristate", image=self.img_tristate)
        self.tree.bind("<Button-1>", self._on_tree_click)

        right_frame = ttk.Frame(paned_window, padding=5)
        right_header = ttk.Frame(right_frame)
        right_header.pack(fill="x", pady=(0, 5))
        ttk.Label(right_header, text="Selected Files", font=("Segoe UI", 12, "bold")).pack(side="left")
        ttk.Button(right_header, text="Copy to Clipboard", command=self._copy_to_clipboard).pack(side="right")

        text_container = ttk.Frame(right_frame)
        text_container.pack(fill="both", expand=True)
        self.text_area = tk.Text(text_container, wrap="none", font=("Consolas", 10), state="disabled", borderwidth=0,
                                 highlightthickness=0, bg="#fdfdfd")
        v_scroll = ttk.Scrollbar(text_container, orient="vertical", command=self.text_area.yview)
        h_scroll = ttk.Scrollbar(text_container, orient="horizontal", command=self.text_area.xview)
        self.text_area.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        self.text_area.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        text_container.grid_rowconfigure(0, weight=1)
        text_container.grid_columnconfigure(0, weight=1)

        paned_window.add(left_frame, weight=1)
        paned_window.add(right_frame, weight=2)

        status_frame = ttk.Frame(self, padding=5)
        status_frame.pack(side="bottom", fill="x")
        self.status_label = ttk.Label(status_frame, text="")
        self.status_label.pack(side="left")

    def _show_help(self):
        messagebox.showinfo("Help", "1. Click 'Select Directory' to choose your project folder.\n"
                                    "2. Check/uncheck files and directories on the left.\n"
                                    "3. The generated prompt text will appear on the right.\n"
                                    "4. Click 'Copy to Clipboard' to copy the text.\n\n"
                                    "This tool helps you create a single text block from your codebase, "
                                    "perfect for pasting into Large Language Models (LLMs) like GPT or Claude.")

    # --- Event Handlers and Core Logic ---

    def _on_select_directory(self):
        path = filedialog.askdirectory()
        if not path:
            return
        self._clear_all()
        self.root_path = path
        self.status_label.config(text=f"Scanning {path}...")
        self.update_idletasks()
        threading.Thread(target=self._scan_and_populate, daemon=True).start()

    def _scan_and_populate(self):
        MAX_FILES_THRESHOLD = 10000
        file_count = 0
        try:
            for dirpath, dirnames, filenames in os.walk(self.root_path, topdown=True):
                dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRECTORIES]
                valid_files = [f for f in filenames if not any(
                    f.lower().endswith(ext) for ext in IGNORED_FILES if ext.startswith('.')) and f not in IGNORED_FILES]
                file_count += len(valid_files)
                if file_count > MAX_FILES_THRESHOLD:
                    self.after(0, lambda: messagebox.showerror(
                        "Too Many Files",
                        f"The selected directory contains over {MAX_FILES_THRESHOLD} files.\n\nPlease select a smaller, more specific project folder to avoid performance issues."
                    ))
                    self.after(0, self._clear_all)
                    return
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"An error occurred during pre-scan: {e}"))
            self.after(0, self._clear_all)
            return

        self.file_tree_data = self._scan_directory(self.root_path)
        self.after(0, self._populate_tree)

    def _clear_all(self):
        self.root_path = None
        self.file_tree_data = None
        self.file_contents = {}
        self.selected_paths = set()
        self.iid_map = {}
        self.path_to_iid = {}
        self.tree.delete(*self.tree.get_children())
        self._update_right_pane_text("Select files from the left to generate a prompt.")
        self._update_status_bar()
        self.status_label.config(text="")

    # --- START OF FIX ---
    def _on_tree_click(self, event):
        """
        处理 Treeview 上的点击事件。
        此版本能正确区分对展开/折叠图标的点击和对复选框/文本的点击。
        """
        # 识别被点击的具体区域和元素
        region = self.tree.identify_region(event.x, event.y)
        element = self.tree.identify_element(event.x, event.y)

        # 如果点击的是展开/折叠器('+' 或 '>')或者不在有效的'tree'区域内, 则不执行任何操作。
        # 让 Treeview 的默认行为处理展开/折叠。
        # 检查元素名称中是否包含'expander'是判断是否点击了展开/折叠器的最可靠方法。
        # AI 元素名称检查与实际不匹配
        if region != 'tree' or 'Treeitem.indicator' in element:
            return

        # 如果代码执行到这里, 说明点击的是项目的图标(复选框)或文本。
        # 继续执行切换选择状态的逻辑。
        iid = self.tree.identify_row(event.y)
        if not iid:
            return

        is_dir = bool(self.tree.get_children(iid))
        current_tag = self.tree.item(iid, "tags")[0]
        select_action = current_tag == "unchecked" or current_tag == "tristate"

        if is_dir:
            self._update_descendants_check_state(iid, select_action)
        else:
            path = self.iid_map.get(iid)
            if path:
                if select_action:
                    self.selected_paths.add(path)
                else:
                    self.selected_paths.discard(path)
                self.tree.item(iid, tags=("checked" if select_action else "unchecked",))

        self._update_ancestors_check_state(iid)
        self._trigger_content_update()
    # --- END OF FIX ---

    def _toggle_all(self, expand=True):
        for iid in self.iid_map:
            if self.tree.exists(iid):
                self.tree.item(iid, open=expand)

    def _select_all(self, select=True):
        if not self.root_path: return

        if select:
            all_files = {path for iid, path in self.iid_map.items() if not self.tree.get_children(iid)}
            self.selected_paths = all_files
        else:
            self.selected_paths.clear()

        new_tag = "checked" if select else "unchecked"
        for iid in self.iid_map:
            if self.tree.exists(iid):
                self.tree.item(iid, tags=(new_tag,))

        self._trigger_content_update()

    def _copy_to_clipboard(self):
        content = self.text_area.get("1.0", "end-1c")
        if content and content != "Loading...":
            try:
                self.clipboard_clear()
                self.clipboard_append(content)
                self.update()
                self.status_label.config(text=f"{self.status_label.cget('text')} | Copied to clipboard!")
            except tk.TclError:
                messagebox.showwarning("Copy Failed", "Could not copy content to clipboard. It might be too large.")

    # --- Data Processing and Population ---

    def _is_text_likely(self, filepath):
        try:
            with open(filepath, 'rb') as f:
                chunk = f.read(4096)
            if b'\0' in chunk:
                return False
            chunk.decode('utf-8')
            return True
        except (UnicodeDecodeError, PermissionError):
            return False
        except Exception:
            return False

    def _scan_directory(self, root_path):
        tree = {'name': os.path.basename(root_path), 'path': root_path, 'is_dir': True, 'children': []}
        path_map = {root_path: tree}
        for dirpath, dirnames, filenames in os.walk(root_path, topdown=True):
            dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRECTORIES]
            parent_node = path_map[dirpath]
            for dirname in sorted(dirnames):
                path = os.path.join(dirpath, dirname)
                node = {'name': dirname, 'path': path, 'is_dir': True, 'children': []}
                parent_node['children'].append(node)
                path_map[path] = node
            for filename in sorted(filenames):
                is_ignored = any(filename.lower().endswith(ext) for ext in IGNORED_FILES if
                                 ext.startswith('.')) or filename in IGNORED_FILES
                if is_ignored: continue
                path = os.path.join(dirpath, filename)
                try:
                    is_text = any(
                        filename.lower().endswith(ext) for ext in LIKELY_TEXT_EXTENSIONS) or self._is_text_likely(
                        path)
                    if is_text:
                        node = {'name': filename, 'path': path, 'is_dir': False, 'size': os.path.getsize(path)}
                        parent_node['children'].append(node)
                except (IOError, OSError):
                    # Skip files that can't be accessed (e.g. permission denied)
                    continue
        return tree

    def _populate_tree(self):
        self.tree.delete(*self.tree.get_children())
        self.iid_map.clear()
        self.path_to_iid.clear()

        def _insert(node, parent_iid=""):
            name = node['name']
            path = node['path']
            if not node['is_dir']:
                size_str = f" ({self._format_size(node.get('size', 0))})"
                display_text = f"📄 {name}{size_str}"
            else:
                display_text = f"📁 {name}"

            iid = self.tree.insert(parent_iid, "end", text=display_text, open=True, tags=("unchecked",))
            self.iid_map[iid] = path
            self.path_to_iid[path] = iid

            if node.get('is_dir'):
                for child in node.get('children', []):
                    _insert(child, iid)

        if self.file_tree_data:
            _insert(self.file_tree_data)
            self._update_status_bar()
            self.status_label.config(text=f"Loaded {self.root_path}")

    # --- UI and State Update Helpers ---

    def _update_descendants_check_state(self, iid, select):
        children = self.tree.get_children(iid)
        new_tag = "checked" if select else "unchecked"
        self.tree.item(iid, tags=(new_tag,))

        for child_iid in children:
            path = self.iid_map.get(child_iid)
            if not path: continue

            if not self.tree.get_children(child_iid):
                if select:
                    self.selected_paths.add(path)
                else:
                    self.selected_paths.discard(path)
                self.tree.item(child_iid, tags=(new_tag,))
            else:
                self._update_descendants_check_state(child_iid, select)

    def _update_ancestors_check_state(self, iid):
        parent_iid = self.tree.parent(iid)
        while parent_iid:
            children = self.tree.get_children(parent_iid)
            if not children:
                self.tree.item(parent_iid, tags=("unchecked",))
                parent_iid = self.tree.parent(parent_iid)
                continue

            num_checked = 0
            num_tristate = 0
            for child_iid in children:
                tag = self.tree.item(child_iid, "tags")[0]
                if tag == "checked":
                    num_checked += 1
                elif tag == "tristate":
                    num_tristate += 1

            if num_tristate > 0 or (num_checked > 0 and num_checked < len(children)):
                self.tree.item(parent_iid, tags=("tristate",))
            elif num_checked == len(children):
                self.tree.item(parent_iid, tags=("checked",))
            else:
                self.tree.item(parent_iid, tags=("unchecked",))

            parent_iid = self.tree.parent(parent_iid)

    def _trigger_content_update(self):
        if self.is_updating_content:
            return

        self.is_updating_content = True

        self._update_right_pane_text("Loading...")
        count = len(self.selected_paths)
        self.status_label.config(text=f"Selected Files: {count} | Estimated Tokens: Calculating...")
        self.update_idletasks()

        paths_to_process = self.selected_paths.copy()

        threading.Thread(
            target=self._load_content_in_background,
            args=(paths_to_process,),
            daemon=True
        ).start()

    def _load_content_in_background(self, paths):
        local_file_contents = {}
        total_chars = 0

        sorted_paths = sorted(list(paths))

        for path in sorted_paths:
            if path in self.file_contents:
                content = self.file_contents[path]
            else:
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    self.file_contents[path] = content
                except Exception:
                    content = f"Error reading file: {os.path.basename(path)}"

            local_file_contents[path] = content
            total_chars += len(content)

        prompt_text = self._generate_prompt_text(sorted_paths, local_file_contents)
        self.after(0, self._on_content_update_complete, prompt_text, len(paths), total_chars)

    def _on_content_update_complete(self, prompt_text, count, total_chars):
        self._update_right_pane_text(prompt_text)
        tokens = (total_chars + 3) // 4
        self.status_label.config(
            text=f"Selected Files: {count} | Estimated Tokens: ~{tokens:,} | Total Chars: {total_chars:,}")
        self.is_updating_content = False

    def _update_right_pane_text(self, text):
        self.text_area.config(state="normal")
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", text)
        self.text_area.config(state="disabled")

    def _update_status_bar(self):
        count = len(self.selected_paths)
        self.status_label.config(text=f"Selected Files: {count}")

    def _generate_prompt_text(self, selected_paths, file_contents):
        if not selected_paths:
            return "Select files from the left to generate a prompt."

        structure_str = self._generate_ascii_tree(selected_paths)

        doc_blocks = []
        for path in selected_paths:  # Already sorted from the calling function
            content = file_contents.get(path, "")
            relative_path = os.path.relpath(path, os.path.dirname(self.root_path))
            doc_blocks.append(f'<document path="{relative_path}">\n{content}\n</document>')

        return f"<folder-structure>\n{structure_str}\n</folder-structure>\n\n" + "\n\n".join(doc_blocks)

    def _generate_ascii_tree(self, selected_paths):
        if not self.root_path or not selected_paths:
            return ""

        # Build a tree structure where directories are dicts and files are None
        tree = {}
        root_parent = os.path.dirname(self.root_path)
        for path in selected_paths:
            relative_path = os.path.relpath(path, root_parent)
            parts = relative_path.split(os.sep)
            current_level = tree
            # Create directory structure
            for part in parts[:-1]:
                current_level = current_level.setdefault(part, {})
            # Mark the last part as a file
            if parts:
                current_level[parts[-1]] = None

        def build_lines_recursive(subtree, prefix=""):
            lines = []
            # Separate keys into dirs and files to sort them nicely
            dirs = sorted([k for k, v in subtree.items() if isinstance(v, dict)])
            files = sorted([k for k, v in subtree.items() if v is None])
            children = dirs + files

            for i, name in enumerate(children):
                is_last = (i == len(children) - 1)
                connector = "└── " if is_last else "├── "
                lines.append(prefix + connector + name)

                # Only recurse if it's a directory (its value is a dict)
                if isinstance(subtree[name], dict):
                    child_prefix = "    " if is_last else "│   "
                    lines.extend(build_lines_recursive(subtree[name], prefix + child_prefix))
            return lines

        root_name = os.path.basename(self.root_path)
        if root_name in tree:
            lines = [root_name]
            lines.extend(build_lines_recursive(tree[root_name]))
            return "\n".join(lines)
        return ""

    def _format_size(self, size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        size_kb = size_bytes / 1024
        if size_kb < 1024:
            return f"{size_kb:.1f} KB"
        size_mb = size_kb / 1024
        return f"{size_mb:.1f} MB"


if __name__ == "__main__":
    app = CodebaseToPromptApp()
    app.mainloop()

