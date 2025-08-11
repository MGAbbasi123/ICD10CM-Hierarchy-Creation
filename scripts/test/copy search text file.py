import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
import sys

# Define supported text file extensions
SUPPORTED_TEXT_EXTENSIONS = [
    ".txt", ".py", ".log", ".csv", ".html", ".css", ".js", ".json", ".xml", ".md",
    ".bat", ".sh", ".c", ".cpp", ".h", ".hpp", ".java", ".go", ".php", ".rb",
    ".pl", ".swift", ".kt", ".ts", ".vue", ".jsx", ".tsx", ".yaml", ".yml",
    ".ini", ".cfg", ".conf", ".sql", ".ps1", ".vbs", ".srt", ".tsv",
    ".go", ".rb", ".php", ".cs", ".aspx", ".asp", ".jsp", ".scala", ".groovy",
    ".r", ".jl", ".f90", ".for", ".asm", ".s", ".coffee", ".less", ".scss", ".sass",
    ".dockerfile", ".gitattributes", ".gitignore", ".editorconfig", ".npmrc",
    ".prettierrc", ".eslintrc", ".babelrc", ".browserslistrc", ".gemfile",
    ".rake", ".mix", ".leex", ".eex", ".ex", ".zig", ".rs", ".elm", ".fs",
    ".erl", ".hrl", ".clj", ".cljs", ".cljc", ".edn", ".lhs", ".purs", ".dhall",
    ".liquid", ".hbs", ".mustache", ".pug", ".jade", ".slim", ".haml", ".twig",
    ".svelte", ".astro", ".mdx", ".toml", ".env"
]
# Sort extensions alphabetically for better presentation
SUPPORTED_TEXT_EXTENSIONS.sort()


class FileTypeSelector(ctk.CTkToplevel):
    def __init__(self, parent, initial_selection):
        super().__init__(parent)
        self.parent = parent
        self.title("Select File Types")
        self.geometry("400x500")
        self.transient(parent) # Makes the popup appear on top of the parent
        self.grab_set()       # Makes the popup modal (blocks interaction with parent)
        self.lift()           # Bring to front

        self.selected_types = set(initial_selection) # Use a set for efficient checking
        self.checkboxes = {} # To store {extension: CTkCheckBox}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Scrollable frame for checkboxes

        # Search Entry
        self.search_entry = ctk.CTkEntry(self, placeholder_text="Search file types...", font=ctk.CTkFont(size=12))
        self.search_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self._filter_checkboxes)

        # Buttons Frame (Select All / Deselect All)
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        self.select_all_button = ctk.CTkButton(self.button_frame, text="Select All", command=self._select_all, font=ctk.CTkFont(size=12))
        self.select_all_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.deselect_all_button = ctk.CTkButton(self.button_frame, text="Deselect All", command=self._deselect_all, font=ctk.CTkFont(size=12))
        self.deselect_all_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")

        # Scrollable Frame for Checkboxes
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Available Types", corner_radius=10)
        self.scrollable_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self._create_checkboxes()
        self._filter_checkboxes() # Apply initial filter (empty search shows all)

        # Apply / Cancel Buttons
        self.action_button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_button_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self.action_button_frame.grid_columnconfigure((0, 1), weight=1)

        self.apply_button = ctk.CTkButton(self.action_button_frame, text="Apply", command=self._apply_selection, font=ctk.CTkFont(size=14, weight="bold"), fg_color="green")
        self.apply_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.cancel_button = ctk.CTkButton(self.action_button_frame, text="Cancel", command=self.destroy, font=ctk.CTkFont(size=14, weight="bold"), fg_color="red")
        self.cancel_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")

        # Center the Toplevel window relative to its parent
        self.update_idletasks() # Ensure window dimensions are calculated
        x = parent.winfo_x() + (parent.winfo_width() / 2) - (self.winfo_width() / 2)
        y = parent.winfo_y() + (parent.winfo_height() / 2) - (self.winfo_height() / 2)
        self.geometry(f"+{int(x)}+{int(y)}")

    def _create_checkboxes(self):
        """Creates checkboxes for all supported extensions."""
        for i, ext in enumerate(SUPPORTED_TEXT_EXTENSIONS):
            var = ctk.StringVar(value="on" if ext in self.selected_types else "off")
            cb = ctk.CTkCheckBox(self.scrollable_frame, text=ext, variable=var, onvalue="on", offvalue="off", font=ctk.CTkFont(size=12))
            # No initial grid call here, _filter_checkboxes will handle initial placement
            self.checkboxes[ext] = {'checkbox': cb, 'var': var, 'row': i} # Store for later grid management

    def _filter_checkboxes(self, event=None):
        """
        Filters and re-grids checkboxes based on search entry text.
        Hides all first, then explicitly grids only the matches.
        """
        search_term = self.search_entry.get().lower()

        # Step 1: Hide all checkboxes first
        for ext, cb_info in self.checkboxes.items():
            cb_info['checkbox'].grid_remove()

        # Step 2: Show only matching checkboxes and re-grid them sequentially
        row_counter = 0
        for ext in SUPPORTED_TEXT_EXTENSIONS: # Iterate original sorted list
            if search_term in ext.lower():
                cb_info = self.checkboxes[ext]
                checkbox_widget = cb_info['checkbox']
                checkbox_widget.grid(row=row_counter, column=0, sticky="w", padx=5, pady=2)
                row_counter += 1

    def _select_all(self):
        """Selects all currently visible (filtered) checkboxes."""
        search_term = self.search_entry.get().lower()
        for ext, cb_info in self.checkboxes.items():
            if search_term in ext.lower(): # Only select visible ones
                cb_info['var'].set("on")

    def _deselect_all(self):
        """Deselects all currently visible (filtered) checkboxes."""
        search_term = self.search_entry.get().lower()
        for ext, cb_info in self.checkboxes.items():
            if search_term in ext.lower(): # Only deselect visible ones
                cb_info['var'].set("off")

    def _apply_selection(self):
        """Collects selected types and passes them back to the parent."""
        self.selected_types.clear()
        for ext, cb_info in self.checkboxes.items():
            if cb_info['var'].get() == "on":
                self.selected_types.add(ext)

        # Pass the selected types back to the main app
        self.parent.update_selected_file_types(list(self.selected_types))
        self.destroy() # Close the Toplevel window

    def get_selected_types(self):
        """Returns the set of selected file types."""
        return self.selected_types


class FileSearchApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🔍 Advanced File Searcher")
        self.geometry("800x700") # Set initial window size
        self.minsize(600, 500) # Minimum size for resizing

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1) # Allow results textbox to expand
        self.grid_rowconfigure(6, weight=0) # "Created by" row won't expand (now row 6)

        # Initial file types selection
        self.selected_file_types_list = [] # Initially empty

        # --- UI Elements ---

        # 1. Folder Selection Frame
        self.folder_frame = ctk.CTkFrame(self)
        self.folder_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        self.folder_frame.grid_columnconfigure(1, weight=1)

        self.folder_label = ctk.CTkLabel(self.folder_frame, text="Scan Folder/Drive:", font=ctk.CTkFont(size=14, weight="bold"))
        self.folder_label.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")

        self.selected_folder_path = ctk.StringVar()
        self.folder_entry = ctk.CTkEntry(self.folder_frame, textvariable=self.selected_folder_path, placeholder_text="No folder selected", font=ctk.CTkFont(size=12))
        self.folder_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        self.browse_button = ctk.CTkButton(self.folder_frame, text="Browse", command=self.browse_folder, font=ctk.CTkFont(size=12, weight="bold"))
        self.browse_button.grid(row=0, column=2, padx=(5, 10), pady=10)

        # 2. Search Text Input Frame
        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        self.search_frame.grid_columnconfigure(1, weight=1)

        self.search_label = ctk.CTkLabel(self.search_frame, text="Search Text:", font=ctk.CTkFont(size=14, weight="bold"))
        self.search_label.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")

        self.search_text_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(self.search_frame, textvariable=self.search_text_var, placeholder_text="Enter text to search...", font=ctk.CTkFont(size=12))
        self.search_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        # 3. File Type Selector Button and Display
        self.type_selection_frame = ctk.CTkFrame(self)
        self.type_selection_frame.grid(row=2, column=0, padx=20, pady=(5, 10), sticky="ew")
        self.type_selection_frame.grid_columnconfigure(1, weight=1)

        self.selected_types_label = ctk.CTkLabel(self.type_selection_frame, text="Selected Types:", font=ctk.CTkFont(size=14, weight="bold"))
        self.selected_types_label.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")

        self.selected_types_display = ctk.CTkLabel(self.type_selection_frame, text="None selected", font=ctk.CTkFont(size=12), wraplength=350, anchor="w")
        self.selected_types_display.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        self.select_types_button = ctk.CTkButton(self.type_selection_frame, text="Select Types...", command=self.open_type_selector, font=ctk.CTkFont(size=12, weight="bold"))
        self.select_types_button.grid(row=0, column=2, padx=(5, 10), pady=10)


        # 4. Action Buttons Frame (shifted to row 4)
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=4, column=0, padx=20, pady=(5, 10), sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.search_button = ctk.CTkButton(self.button_frame, text="🚀 Start Search", command=self.start_search_thread, font=ctk.CTkFont(size=14, weight="bold"), fg_color="green", hover_color="darkgreen")
        self.search_button.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")

        self.clear_button = ctk.CTkButton(self.button_frame, text="🧹 Clear Results", command=self.clear_results, font=ctk.CTkFont(size=14, weight="bold"), fg_color="orange", hover_color="darkorange")
        self.clear_button.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        self.stop_button = ctk.CTkButton(self.button_frame, text="🛑 Stop Search", command=self.stop_search, font=ctk.CTkFont(size=14, weight="bold"), fg_color="red", hover_color="darkred", state="disabled")
        self.stop_button.grid(row=0, column=2, padx=(5, 10), pady=10, sticky="ew")

        # 5. Results Display (Textbox) - remains row 3, but now above button_frame
        self.results_textbox = ctk.CTkTextbox(self, wrap="word", font=ctk.CTkFont(family="Consolas", size=12), corner_radius=10)
        self.results_textbox.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        self.results_textbox.insert("end", "Search results will appear here.\n")
        self.results_textbox.configure(state="disabled")

        # 6. Status Bar (shifted to row 5)
        self.status_bar_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_bar_frame.grid(row=5, column=0, padx=20, pady=(0, 5), sticky="ew")
        self.status_bar_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(self.status_bar_frame, text="Ready.", font=ctk.CTkFont(size=12), anchor="w")
        self.status_label.grid(row=0, column=0, sticky="ew")

        # 7. "Created by MG" Label (shifted to row 6)
        self.creator_label = ctk.CTkLabel(self, text="Created by MG", font=ctk.CTkFont(size=10, slant="italic"), text_color="gray")
        self.creator_label.grid(row=6, column=0, padx=20, pady=(5, 10), sticky="s")

        self.search_thread = None
        self._stop_event = threading.Event()

    def update_selected_file_types(self, new_selection_list):
        """Callback from FileTypeSelector to update main app's selection."""
        self.selected_file_types_list = new_selection_list
        if self.selected_file_types_list:
            display_text = ", ".join(self.selected_file_types_list)
            if len(display_text) > 60: # Truncate for display if too long
                display_text = display_text[:57] + "..."
            self.selected_types_display.configure(text=display_text)
        else:
            self.selected_types_display.configure(text="None selected")

    def open_type_selector(self):
        """Opens the FileTypeSelector Toplevel window."""
        FileTypeSelector(self, self.selected_file_types_list)


    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.selected_folder_path.set(folder_selected)
            self.status_label.configure(text=f"Folder selected: {folder_selected}")

    def clear_results(self):
        self.results_textbox.configure(state="normal")
        self.results_textbox.delete("1.0", "end")
        self.results_textbox.insert("end", "Search results will appear here.\n")
        self.results_textbox.configure(state="disabled")
        self.status_label.configure(text="Ready.")

    def start_search_thread(self):
        folder_path = self.selected_folder_path.get()
        search_text = self.search_text_var.get()
        selected_types_for_search = self.selected_file_types_list

        if not folder_path:
            messagebox.showwarning("Input Error", "Please select a folder or drive to scan.")
            return
        if not search_text:
            messagebox.showwarning("Input Error", "Please enter text to search for.")
            return

        if not os.path.isdir(folder_path):
            messagebox.showerror("Invalid Path", "The selected path is not a valid directory.")
            return

        # If no specific types selected, default to all supported types
        if not selected_types_for_search:
            # Create a shallow copy to avoid modifying the global constant if user selects/deselects later
            selected_types_for_search = list(SUPPORTED_TEXT_EXTENSIONS)
            self.status_label.configure(text="No file types selected, searching all supported text files.")
            self.update_idletasks()


        # Disable buttons and enable stop button
        self.search_button.configure(state="disabled")
        self.browse_button.configure(state="disabled")
        self.select_types_button.configure(state="disabled") # Disable type selector button
        self.search_entry.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.clear_results()
        self.status_label.configure(text="Searching... This might take a while for large drives.")

        self._stop_event.clear()
        self.search_thread = threading.Thread(target=self._perform_search,
                                              args=(folder_path, search_text.lower(), selected_types_for_search))
        self.search_thread.daemon = True
        self.search_thread.start()

    def stop_search(self):
        if self.search_thread and self.search_thread.is_alive():
            self._stop_event.set()
            self.status_label.configure(text="Stopping search...")
        else:
            self.status_label.configure(text="No active search to stop.")


    def _perform_search(self, folder_path, search_text_lower, selected_types_for_search):
        found_count = 0
        self.results_textbox.configure(state="normal")

        # Convert selected types list to a set for faster lookup
        selected_types_set = set(selected_types_for_search)

        for root, _, files in os.walk(folder_path):
            if self._stop_event.is_set():
                self.results_textbox.insert("end", "\n--- Search stopped by user ---\n")
                break

            for file in files:
                if self._stop_event.is_set():
                    self.results_textbox.insert("end", "\n--- Search stopped by user ---\n")
                    break

                file_extension = os.path.splitext(file)[1].lower()
                # Optimized: Skip if file extension is not in the selected set
                if file_extension not in selected_types_set:
                    continue

                file_path = os.path.join(root, file)
                self.status_label.configure(text=f"Scanning: {file_path}")
                self.update_idletasks()

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if self._stop_event.is_set():
                                self.results_textbox.insert("end", "\n--- Search stopped by user ---\n")
                                break
                            if search_text_lower in line.lower():
                                found_count += 1
                                result_line = f"Found in: {file_path}, Line {line_num}: {line.strip()}\n"
                                self.results_textbox.insert("end", result_line)
                                self.results_textbox.see("end")
                                self.update_idletasks()

                except Exception as e:
                    error_msg = f"Could not read {file_path} (possible non-text file or permission issue): {e}\n"
                    self.results_textbox.insert("end", f"Error: {error_msg}")
                    self.results_textbox.see("end")
                    self.update_idletasks()

        self.results_textbox.configure(state="disabled")
        if not self._stop_event.is_set():
            self.status_label.configure(text=f"Search complete. Found {found_count} occurrences.")

        # Re-enable/disable buttons after search
        self.search_button.configure(state="normal")
        self.browse_button.configure(state="normal")
        self.select_types_button.configure(state="normal") # Re-enable type selector button
        self.search_entry.configure(state="normal")
        self.stop_button.configure(state="disabled")


# Main execution block
if __name__ == "__main__":
    app = FileSearchApp()
    app.mainloop()
