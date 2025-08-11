import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font
import os
import shutil

class ExcelCombinerApp:
    def __init__(self, master):
        self.master = master
        master.title("Excel Combiner")
        master.geometry("600x400") # Set initial window size
        master.resizable(False, False) # Disable resizing for simplicity

        # Styling
        master.configure(bg="#e0f2f7") # Light blue background
        font_large = ('Arial', 14, 'bold')
        font_medium = ('Arial', 12)
        font_small = ('Arial', 10)

        # Title Label
        self.title_label = tk.Label(master, text="📁 Excel File Combiner 📊", font=('Arial', 20, 'bold'), bg="#e0f2f7", fg="#004d40")
        self.title_label.pack(pady=20)
        # Frame for folder selection
        self.folder_frame = tk.Frame(master, bg="#e0f2f7")
        self.folder_frame.pack(pady=10)

        self.folder_label = tk.Label(self.folder_frame, text="Root Directory:", font=font_medium, bg="#e0f2f7")
        self.folder_label.pack(side=tk.LEFT, padx=5)

        self.selected_folder_path = tk.StringVar()
        self.folder_entry = tk.Entry(self.folder_frame, textvariable=self.selected_folder_path, width=50, state='readonly', font=font_small, relief=tk.FLAT, bd=2, bg="#ffffff", fg="#333333")
        self.folder_entry.pack(side=tk.LEFT, padx=0)

        self.browse_button = tk.Button(self.folder_frame, text="Browse Folder", command=self.browse_folder, font=font_medium, bg="#4CAF50", fg="white", activebackground="#45a049", cursor="hand2", relief=tk.RAISED, bd=10, borderwidth=0, highlightthickness=0)
        self.browse_button.pack(side=tk.LEFT, padx=0)

        # Process Button
        self.process_button = tk.Button(master, text="🚀 Process Excel Files", command=self.process_files, font=font_large, bg="#2196F3", fg="white", activebackground="#1976D2", cursor="hand2", relief=tk.RAISED, bd=3, borderwidth=0, highlightthickness=0)
        self.process_button.pack(pady=20, ipadx=10, ipady=5)
        self.process_button.config(state=tk.DISABLED) # Disable initially

        # Output Path Display
        self.output_frame = tk.Frame(master, bg="#e0f2f7")
        self.output_frame.pack(pady=10)

        self.output_label = tk.Label(self.output_frame, text="Output File:", font=font_medium, bg="#e0f2f7")
        self.output_label.pack(side=tk.LEFT, padx=5)

        self.output_file_path = tk.StringVar()
        self.output_entry = tk.Entry(self.output_frame, textvariable=self.output_file_path, width=60, state='readonly', font=font_small, relief=tk.FLAT, bd=2, bg="#ffffff", fg="#333333")
        self.output_entry.pack(side=tk.LEFT, padx=5)

        # Status Message
        self.status_message = tk.StringVar()
        self.status_label = tk.Label(master, textvariable=self.status_message, font=font_medium, bg="#e0f2f7", fg="gray")
        self.status_label.pack(pady=10)

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.selected_folder_path.set(folder_path)
            self.process_button.config(state=tk.NORMAL) # Enable button once folder is selected
            self.status_message.set(f"Selected: {folder_path}")
            self.output_file_path.set("") # Clear previous output

    def process_files(self):
        root_dir_str = self.selected_folder_path.get()
        if not root_dir_str:
            messagebox.showwarning("Input Error", "Please select a root directory first.")
            return

        root_dir = Path(root_dir_str)
        output_file_name = f"Combined_Workbook_with_Index_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        output_file = root_dir / output_file_name

        self.status_message.set("Processing... Please wait.")
        self.master.update_idletasks() # Update UI to show message

        try:
            sheets_data = {}
            found_excel_files = False

            for folder in root_dir.iterdir():
                if folder.is_dir():
                    combined_df = pd.DataFrame()
                    for file in folder.glob("*.xls*"):
                        found_excel_files = True
                        try:
                            df = pd.read_excel(file)
                            df['SourceFile'] = file.name
                            combined_df = pd.concat([combined_df, df], ignore_index=True)
                        except Exception as e:
                            print(f"Error reading {file}: {e}")
                            self.status_message.set(f"Error reading {file.name}: {e}")
                            messagebox.showerror("File Read Error", f"Could not read {file.name}. Please check if it's a valid Excel file and not open.")
                            return
                    if not combined_df.empty:
                        sheets_data[folder.name[:31]] = combined_df

            if not found_excel_files and not sheets_data:
                self.status_message.set("No Excel files found in the selected directory's subfolders.")
                messagebox.showinfo("No Files Found", "No Excel files were found in any subfolders of the selected directory.")
                return

            if not sheets_data:
                self.status_message.set("No data could be extracted from the found Excel files.")
                messagebox.showinfo("No Data", "Excel files were found, but no data could be extracted to form sheets.")
                return

            # Create workbook and index sheet
            wb = Workbook()
            index_ws = wb.active
            index_ws.title = "Home"

            row = 1
            for sheet_name in sheets_data.keys():
                cell = index_ws.cell(row=row, column=1)
                cell.value = sheet_name
                cell.hyperlink = f"#'{sheet_name}'!A1"
                cell.font = Font(color="0000FF", underline="single")
                row += 1

            # Add each folder's data to a new sheet
            for sheet_name, df in sheets_data.items():
                ws = wb.create_sheet(title=sheet_name)
                ws['A1'] = "← Back to Home"
                ws['A1'].hyperlink = f"#'Home'!A1"
                ws['A1'].font = Font(color="0000FF", underline="single", bold=True)

                for col_num, col_name in enumerate(df.columns, start=1):
                    ws.cell(row=3, column=col_num, value=col_name).font = Font(bold=True)
                for row_idx, row_data in enumerate(df.values, start=4):
                    for col_idx, value in enumerate(row_data, start=1):
                        ws.cell(row=row_idx, column=col_idx, value=value)

            # Remove default sheet if still present
            if 'Sheet' in wb.sheetnames:
                del wb['Sheet']

            wb.save(output_file)
            self.output_file_path.set(output_file.as_posix())
            self.status_message.set(f"✅ Workbook created successfully!")
            messagebox.showinfo("Success", f"Workbook created successfully at: {output_file.as_posix()}")

        except Exception as e:
            self.status_message.set(f"❌ An error occurred: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelCombinerApp(root)
    root.mainloop()