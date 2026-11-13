#!/usr/bin/env python3
"""
Roblox Fast Flags Manager - GUI Application
A simple GUI to manage Roblox Fast Flags on Linux
"""

import os
import json
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

class RobloxFlagsManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Roblox Fast Flags Manager")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Configuration
        self.config_dir = Path.home() / ".config" / "roblox-fast-flags"
        self.config_file = self.config_dir / "flags.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing flags
        self.flags = self.load_flags()
        
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
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Roblox Fast Flags Manager", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="Add New Flag", padding="10")
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
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
        list_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
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
        action_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Apply button
        self.apply_button = ttk.Button(action_frame, text="Apply Flags to Roblox", 
                                       command=self.apply_flags, style="Accent.TButton")
        self.apply_button.grid(row=0, column=0, padx=(0, 5))
        
        # Reset button
        self.reset_button = ttk.Button(action_frame, text="Reset All Flags", 
                                       command=self.reset_flags)
        self.reset_button.grid(row=0, column=1, padx=(0, 5))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                               relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
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
    
    def refresh_flags_list(self):
        """Refresh the flags list in the treeview"""
        # Clear current items
        for item in self.flags_tree.get_children():
            self.flags_tree.delete(item)
        
        # Add flags to treeview
        for flag_name, flag_value in self.flags.items():
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
        self.refresh_flags_list()
        
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
            self.refresh_flags_list()
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
            self.refresh_flags_list()
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
            self.refresh_flags_list()
            self.status_var.set("All flags cleared")
    
    def reset_flags(self):
        """Reset all flags to default"""
        if messagebox.askyesno("Confirm", "Are you sure you want to reset all flags to default?"):
            self.flags = {}
            self.save_flags()
            self.refresh_flags_list()
            self.status_var.set("Flags reset to default")
    
    def find_roblox_installation(self):
        """Find Roblox installation path"""
        possible_paths = [
            Path.home() / ".var/app/com.roblox.Roblox",  # Flatpak
            Path.home() / ".local/share/Roblox",         # Standard
            Path("/snap/roblox/current")                  # Snap
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
        
        return None
    
    def apply_flags(self):
        """Apply flags to Roblox installation"""
        roblox_path = self.find_roblox_installation()
        
        if not roblox_path:
            messagebox.showerror("Error", "Could not find Roblox installation!\n\n"
                                        "Please make sure Roblox is installed.")
            return
        
        self.status_var.set("Applying flags...")
        self.root.update()
        
        try:
            # Create ClientSettings.json if it doesn't exist
            settings_file = Path(roblox_path) / "ClientSettings.json"
            
            if not settings_file.exists():
                # Create directory if needed
                settings_file.parent.mkdir(parents=True, exist_ok=True)
                # Create empty settings
                with open(settings_file, 'w') as f:
                    json.dump({"fastFlags": {}}, f)
            
            # Read current settings
            with open(settings_file, 'r') as f:
                settings = json.load(f)
            
            # Update fast flags
            settings['fastFlags'] = self.flags
            
            # Save settings
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            # Handle different installation types
            if "com.roblox.Roblox" in roblox_path:
                # Flatpak - might need permissions
                try:
                    subprocess.run(['flatpak', 'override', 'com.roblox.Roblox', '--filesystem=home'], 
                                  check=True, capture_output=True)
                except:
                    pass
            
            self.status_var.set("Flags applied successfully!")
            messagebox.showinfo("Success", "Flags applied successfully!\n\n"
                                        "Please restart Roblox for changes to take effect.")
            
        except Exception as e:
            self.status_var.set("Error applying flags")
            messagebox.showerror("Error", f"Failed to apply flags: {str(e)}")

def main():
    root = tk.Tk()
    app = RobloxFlagsManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
