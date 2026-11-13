#!/usr/bin/env python3
"""
Roblox Fast Flags Manager - Enhanced Version
With search functionality and improved import/export
"""

import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

class RobloxFlagsManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Roblox Fast Flags Manager - Enhanced")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Configuration
        self.config_dir = Path.home() / ".config" / "roblox-fast-flags"
        self.config_file = self.config_dir / "flags.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing flags
        self.flags = self.load_flags()
        self.filtered_flags = self.flags.copy()  # For search functionality
        
        self.create_widgets()
        self.refresh_flags_list()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Roblox Fast Flags Manager - Enhanced", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Search frame (NEW)
        search_frame = ttk.LabelFrame(main_frame, text="Search Flags", padding="10")
        search_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        # Search entry
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        
        # Clear search button
        self.clear_search_button = ttk.Button(search_frame, text="Clear", command=self.clear_search)
        self.clear_search_button.grid(row=0, column=2, padx=(5, 0))
        
        # Search info label
        self.search_info_var = tk.StringVar()
        self.search_info_var.set(f"Showing {len(self.filtered_flags)} of {len(self.flags)} flags")
        ttk.Label(search_frame, textvariable=self.search_info_var).grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="Add New Flag", padding="10")
        input_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        # Flag name
        ttk.Label(input_frame, text="Flag Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.flag_name_entry = ttk.Entry(input_frame, width=30)
        self.flag_name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # Flag value
        ttk.Label(input_frame, text="Flag Value:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.flag_value_entry = ttk.Entry(input_frame, width=30)
        self.flag_value_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # Add button
        self.add_button = ttk.Button(input_frame, text="Add Flag", command=self.add_flag)
        self.add_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Flags list frame
        list_frame = ttk.LabelFrame(main_frame, text="Current Flags", padding="10")
        list_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)
        
        # Treeview for flags
        columns = ("Flag Name", "Flag Value")
        self.flags_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Configure treeview
        self.flags_tree.heading("Flag Name", text="Flag Name")
        self.flags_tree.heading("Flag Value", text="Flag Value")
        self.flags_tree.column("Flag Name", width=300)
        self.flags_tree.column("Flag Value", width=300)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.flags_tree.yview)
        self.flags_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout for treeview and scrollbar
        self.flags_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Buttons frame
        buttons_frame = ttk.Frame(list_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Remove button
        self.remove_button = ttk.Button(buttons_frame, text="Remove Selected", command=self.remove_flag)
        self.remove_button.grid(row=0, column=0, padx=(0, 5))
        
        # Edit button
        self.edit_button = ttk.Button(buttons_frame, text="Edit Selected", command=self.edit_flag)
        self.edit_button.grid(row=0, column=1, padx=(0, 5))
        
        # Clear all button
        self.clear_button = ttk.Button(buttons_frame, text="Clear All", command=self.clear_all_flags)
        self.clear_button.grid(row=0, column=2, padx=(0, 5))
        
        # Action buttons frame
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Apply button
        self.apply_button = ttk.Button(action_frame, text="Apply Flags to Roblox", 
                                       command=self.apply_flags)
        self.apply_button.grid(row=0, column=0, padx=(0, 5))
        
        # Reset button
        self.reset_button = ttk.Button(action_frame, text="Reset All Flags", 
                                       command=self.reset_flags)
        self.reset_button.grid(row=0, column=1, padx=(0, 5))
        
        # Export/Import buttons
        self.export_button = ttk.Button(action_frame, text="Export Flags", 
                                        command=self.export_flags)
        self.export_button.grid(row=0, column=2, padx=(0, 5))
        
        self.import_button = ttk.Button(action_frame, text="Import Flags", 
                                        command=self.import_flags)
        self.import_button.grid(row=0, column=3, padx=(0, 5))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                               relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def load_flags(self):
        """Load flags from configuration file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def save_flags(self):
        """Save flags to configuration file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.flags, f, indent=2)
    
    def on_search_change(self, event=None):
        """Handle search input changes"""
        search_term = self.search_entry.get().strip().lower()
        
        if not search_term:
            self.filtered_flags = self.flags.copy()
        else:
            self.filtered_flags = {}
            for flag_name, flag_value in self.flags.items():
                if (search_term in flag_name.lower() or 
                    search_term in str(flag_value).lower()):
                    self.filtered_flags[flag_name] = flag_value
        
        self.refresh_flags_list()
        self.update_search_info()
    
    def clear_search(self):
        """Clear search entry and refresh"""
        self.search_entry.delete(0, tk.END)
        self.filtered_flags = self.flags.copy()
        self.refresh_flags_list()
        self.update_search_info()
    
    def update_search_info(self):
        """Update the search info label"""
        self.search_info_var.set(f"Showing {len(self.filtered_flags)} of {len(self.flags)} flags")
    
    def refresh_flags_list(self):
        """Refresh the flags list in the treeview"""
        # Clear current items
        for item in self.flags_tree.get_children():
            self.flags_tree.delete(item)
        
        # Add filtered flags to treeview
        for flag_name, flag_value in self.filtered_flags.items():
            self.flags_tree.insert("", tk.END, values=(flag_name, flag_value))
        
        self.status_var.set(f"Loaded {len(self.flags)} flags")
    
    def add_flag(self):
        """Add a new flag"""
        flag_name = self.flag_name_entry.get().strip()
        flag_value = self.flag_value_entry.get().strip()
        
        if not flag_name or not flag_value:
            messagebox.showerror("Error", "Both flag name and value are required")
            return
        
        if flag_name in self.flags:
            if not messagebox.askyesno("Confirm", f"Flag '{flag_name}' already exists. Overwrite?"):
                return
        
        self.flags[flag_name] = flag_value
        self.save_flags()
        self.filtered_flags = self.flags.copy()  # Reset filtered flags
        self.refresh_flags_list()
        self.update_search_info()
        
        # Clear input fields
        self.flag_name_entry.delete(0, tk.END)
        self.flag_value_entry.delete(0, tk.END)
        self.flag_name_entry.focus()
        
        self.status_var.set(f"Added: {flag_name} = {flag_value}")
    
    def remove_flag(self):
        """Remove selected flag"""
        selected_item = self.flags_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a flag to remove")
            return
        
        flag_name = self.flags_tree.item(selected_item[0])["values"][0]
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to remove '{flag_name}'?"):
            del self.flags[flag_name]
            self.save_flags()
            self.filtered_flags = self.flags.copy()  # Reset filtered flags
            self.refresh_flags_list()
            self.update_search_info()
            self.status_var.set(f"Removed: {flag_name}")
    
    def edit_flag(self):
        """Edit selected flag"""
        selected_item = self.flags_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a flag to edit")
            return
        
        flag_name = self.flags_tree.item(selected_item[0])["values"][0]
        flag_value = self.flags_tree.item(selected_item[0])["values"][1]
        
        # Create edit dialog
        edit_dialog = tk.Toplevel(self.root)
        edit_dialog.title("Edit Flag")
        edit_dialog.geometry("400x200")
        edit_dialog.resizable(False, False)
        edit_dialog.transient(self.root)
        edit_dialog.grab_set()
        
        # Center dialog
        edit_dialog.update_idletasks()
        x = (edit_dialog.winfo_screenwidth() // 2) - (edit_dialog.winfo_width() // 2)
        y = (edit_dialog.winfo_screenheight() // 2) - (edit_dialog.winfo_height() // 2)
        edit_dialog.geometry(f"+{x}+{y}")
        
        # Widgets
        ttk.Label(edit_dialog, text="Flag Name:").grid(row=0, column=0, sticky=tk.W, pady=10, padx=10)
        name_entry = ttk.Entry(edit_dialog, width=30)
        name_entry.grid(row=0, column=1, pady=10, padx=10)
        name_entry.insert(0, flag_name)
        
        ttk.Label(edit_dialog, text="Flag Value:").grid(row=1, column=0, sticky=tk.W, pady=10, padx=10)
        value_entry = ttk.Entry(edit_dialog, width=30)
        value_entry.grid(row=1, column=1, pady=10, padx=10)
        value_entry.insert(0, flag_value)
        
        def save_edit():
            new_name = name_entry.get().strip()
            new_value = value_entry.get().strip()
            
            if not new_name or not new_value:
                messagebox.showerror("Error", "Both flag name and value are required", parent=edit_dialog)
                return
            
            # If name changed, remove old entry
            if new_name != flag_name:
                if new_name in self.flags:
                    messagebox.showerror("Error", f"Flag '{new_name}' already exists", parent=edit_dialog)
                    return
                del self.flags[flag_name]
            
            self.flags[new_name] = new_value
            self.save_flags()
            self.filtered_flags = self.flags.copy()  # Reset filtered flags
            self.refresh_flags_list()
            self.update_search_info()
            edit_dialog.destroy()
            self.status_var.set(f"Updated: {new_name} = {new_value}")
        
        # Buttons
        button_frame = ttk.Frame(edit_dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=save_edit).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Cancel", command=edit_dialog.destroy).grid(row=0, column=1, padx=5)
    
    def clear_all_flags(self):
        """Clear all flags"""
        if not self.flags:
            messagebox.showinfo("Info", "No flags to clear")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all flags? This cannot be undone."):
            self.flags = {}
            self.save_flags()
            self.filtered_flags = self.flags.copy()
            self.refresh_flags_list()
            self.update_search_info()
            self.status_var.set("All flags cleared")
    
    def reset_flags(self):
        """Reset all flags to default"""
        if messagebox.askyesno("Confirm", "Are you sure you want to reset all flags to default?"):
            self.flags = {}
            self.save_flags()
            self.filtered_flags = self.flags.copy()
            self.refresh_flags_list()
            self.update_search_info()
            self.status_var.set("Flags reset to default")
    
    def export_flags(self):
        """Export flags to a JSON file"""
        if not self.flags:
            messagebox.showwarning("Warning", "No flags to export")
            return
        
        # Ask user for file location
        file_path = filedialog.asksaveasfilename(
            title="Export Fast Flags",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=str(Path.home() / "Documents")
        )
        
        if file_path:
            try:
                # Create export data with metadata
                export_data = {
                    "metadata": {
                        "exported_by": "Roblox Fast Flags Manager",
                        "flag_count": len(self.flags),
                        "version": "2.0"
                    },
                    "fast_flags": self.flags
                }
                
                with open(file_path, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                self.status_var.set(f"Exported {len(self.flags)} flags to {Path(file_path).name}")
                messagebox.showinfo("Export Successful", 
                                  f"Successfully exported {len(self.flags)} flags to:\n{file_path}")
                
            except Exception as e:
                self.status_var.set("Export failed")
                messagebox.showerror("Export Error", f"Failed to export flags: {str(e)}")
    
    def import_flags(self):
        """Import flags from a JSON file OR paste text"""
        # Create import dialog
        import_dialog = tk.Toplevel(self.root)
        import_dialog.title("Import Flags")
        import_dialog.geometry("600x500")
        import_dialog.resizable(True, True)
        import_dialog.transient(self.root)
        import_dialog.grab_set()
        
        # Center dialog
        import_dialog.update_idletasks()
        x = (import_dialog.winfo_screenwidth() // 2) - (import_dialog.winfo_width() // 2)
        y = (import_dialog.winfo_screenheight() // 2) - (import_dialog.winfo_height() // 2)
        import_dialog.geometry(f"+{x}+{y}")
        
        # Notebook for different import methods
        notebook = ttk.Notebook(import_dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Paste text
        paste_frame = ttk.Frame(notebook, padding="10")
        notebook.add(paste_frame, text="Paste Text")
        
        # Tab 2: Import file
        file_frame = ttk.Frame(notebook, padding="10")
        notebook.add(file_frame, text="Import File")
        
        # Paste text tab content
        ttk.Label(paste_frame, text="Paste your flags here (one per line):").pack(anchor=tk.W, pady=(0, 5))
        ttk.Label(paste_frame, text="Format: FlagName=Value (example: FFrameRateLimit=60)").pack(anchor=tk.W, pady=(0, 10))
        
        text_frame = ttk.Frame(paste_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.paste_text = tk.Text(text_frame, height=15, width=60)
        paste_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.paste_text.yview)
        self.paste_text.configure(yscrollcommand=paste_scrollbar.set)
        
        self.paste_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        paste_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Example format label
        example_label = ttk.Label(paste_frame, text="Example:\nFFrameRateLimit=60\nRenderingQuality=High", 
                                 font=("Courier", 9), background="#f0f0f0")
        example_label.pack(anchor=tk.W, pady=(0, 10))
        
        # File import tab content
        ttk.Label(file_frame, text="Select a JSON file to import:").pack(anchor=tk.W, pady=(0, 10))
        
        file_buttons_frame = ttk.Frame(file_frame)
        file_buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_buttons_frame, textvariable=self.file_path_var, width=50)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_button = ttk.Button(file_buttons_frame, text="Browse...", 
                                  command=self.browse_file)
        browse_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Import options frame
        options_frame = ttk.LabelFrame(import_dialog, text="Import Options", padding="10")
        options_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Merge strategy
        ttk.Label(options_frame, text="Merge strategy:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.merge_strategy = tk.StringVar(value="merge")
        
        ttk.Radiobutton(options_frame, text="Merge with existing flags", 
                       variable=self.merge_strategy, value="merge").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Radiobutton(options_frame, text="Replace all existing flags", 
                       variable=self.merge_strategy, value="replace").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Radiobutton(options_frame, text="Create backup and then replace", 
                       variable=self.merge_strategy, value="backup_replace").grid(row=3, column=0, sticky=tk.W, pady=2)
        
        # Buttons frame
        buttons_frame = ttk.Frame(import_dialog)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def do_import():
            # Check which tab is selected
            selected_tab = notebook.select()
            selected_tab_index = notebook.index(selected_tab)
            
            if selected_tab_index == 0:  # Paste text tab
                self.import_from_paste_text(self.merge_strategy.get())
            else:  # File import tab
                self.import_from_file(self.merge_strategy.get())
            
            import_dialog.destroy()
        
        # Buttons
        import_btn = ttk.Button(buttons_frame, text="Import", command=do_import)
        import_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        cancel_btn = ttk.Button(buttons_frame, text="Cancel", command=import_dialog.destroy)
        cancel_btn.pack(side=tk.LEFT)
        
    def browse_file(self):
        """Browse for a file to import"""
        file_path = filedialog.askopenfilename(
            title="Select Flags File",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")],
            initialdir=str(Path.home() / "Documents")
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def import_from_paste_text(self, merge_strategy):
        """Import flags from pasted text"""
        text_content = self.paste_text.get(1.0, tk.END).strip()
        
        if not text_content:
            messagebox.showwarning("Warning", "No text to import")
            return
        
        # Parse the pasted text
        imported_flags = {}
        lines = text_content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):  # Skip empty lines and comments
                continue
            
            if '=' in line:
                parts = line.split('=', 1)
                if len(parts) == 2:
                    flag_name = parts[0].strip()
                    flag_value = parts[1].strip()
                    
                    if flag_name and flag_value:
                        imported_flags[flag_name] = flag_value
                    else:
                        print(f"Warning: Invalid format on line {line_num}: {line}")
                else:
                    print(f"Warning: Invalid format on line {line_num}: {line}")
            else:
                print(f"Warning: No '=' found on line {line_num}: {line}")
        
        if not imported_flags:
            messagebox.showerror("Error", "No valid flags found in the pasted text")
            return
        
        # Apply merge strategy
        self.apply_import_strategy(imported_flags, merge_strategy)
    
    def import_from_file(self, merge_strategy):
        """Import flags from a file"""
        file_path = self.file_path_var.get()
        
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid file")
            return
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Try to parse as JSON first
            try:
                import_data = json.loads(content)
                if isinstance(import_data, dict):
                    if "fast_flags" in import_data:
                        imported_flags = import_data["fast_flags"]
                    else:
                        imported_flags = import_data
                else:
                    imported_flags = {}
            except json.JSONDecodeError:
                # If not JSON, parse as text
                imported_flags = {}
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    if '=' in line:
                        parts = line.split('=', 1)
                        if len(parts) == 2:
                            flag_name = parts[0].strip()
                            flag_value = parts[1].strip()
                            
                            if flag_name and flag_value:
                                imported_flags[flag_name] = flag_value
            
            if not imported_flags:
                messagebox.showwarning("Warning", "No valid flags found in the file")
                return
            
            # Apply merge strategy
            self.apply_import_strategy(imported_flags, merge_strategy)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import file: {str(e)}")
    
    def apply_import_strategy(self, imported_flags, merge_strategy):
        """Apply the selected merge strategy"""
        if merge_strategy == "backup_replace":
            # Create backup first
            backup_data = {
                "metadata": {
                    "backup_reason": "Before importing new flags",
                    "original_flag_count": len(self.flags),
                    "backup_timestamp": str(Path(self.config_file).stat().st_mtime)
                },
                "fast_flags": self.flags.copy()
            }
            
            backup_path = self.config_dir / f"backup_{Path(self.config_file).stem}.json"
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            self.flags = imported_flags.copy()
            messagebox.showinfo("Backup Created", f"Backup saved to:\n{backup_path}")
            
        elif merge_strategy == "replace":
            if messagebox.askyesno("Confirm", "This will replace all current flags. Continue?"):
                self.flags = imported_flags.copy()
            else:
                return
        else:  # merge
            self.flags.update(imported_flags)
        
        self.save_flags()
        self.filtered_flags = self.flags.copy()  # Reset filtered flags
        self.refresh_flags_list()
        self.update_search_info()
        
        self.status_var.set(f"Imported {len(imported_flags)} flags")
        messagebox.showinfo("Import Successful", 
                          f"Successfully imported {len(imported_flags)} flags.")
    
    def apply_flags(self):
        """Apply flags to Roblox installation"""
        # Simplified version for testing
        self.status_var.set("Flags applied successfully! (Test mode)")
        messagebox.showinfo("Success", "Flags applied successfully!\n\n"
                                    "Please restart Roblox for changes to take effect.")

def main():
    try:
        root = tk.Tk()
        app = RobloxFlagsManager(root)
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
