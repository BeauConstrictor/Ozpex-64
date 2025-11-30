import os
import sys
import json
import shutil
import subprocess
import tkinter as tk
from time import sleep
from tkinter import messagebox

os.chdir(os.path.dirname(os.path.abspath(__file__)))

class MachinesList(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.listbox = tk.Listbox(self)
        self.listbox.bind('<<ListboxSelect>>', self.onselect)
        self.listbox.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.listbox.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.listbox.config(yscrollcommand=self.scrollbar.set)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.machines = []

        for m in os.listdir("machines/"):
            with open(f"machines/{m}", "r") as f:
                machine = json.load(f)
            self.listbox.insert(tk.END, machine["Name"])
            self.machines.append(machine)
            
    def onselect(self, event):
        index = int(self.listbox.curselection()[0])
        machine = self.machines[index]
        
        self.master.machine_view.show_machine(machine)
        
class MachineView(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.default_label = tk.Label(self, text="Select a machine, or create "
                                                 "a new one.")
        self.default_label.pack(expand=True, fill=tk.BOTH)
    
    def show_machine(self, machine_json: dict) -> None:
        self.default_label.destroy()
        
    def show_machine(self, attributes) -> None:
        if hasattr(self, 'default_label'):
            self.default_label.destroy()
        
        for widget in self.winfo_children():
            widget.destroy()

        title = tk.Label(self, text=f"{attributes["Name"]}", font=("Arial", 14, "bold"))
        title.pack(pady=5)

        attr_label = tk.Label(self, text="Configuration:")
        attr_label.pack(anchor="w", padx=5)

        attr_listbox = tk.Listbox(self)
        for k,v in attributes.items():
            attr_listbox.insert(tk.END, f"{k}: {v}")
        attr_listbox.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        buttons_section = tk.Frame(self)
        buttons_section.pack(pady=10)
        
        delete_button = tk.Button(buttons_section, text="Remove",
                                 command=lambda: print(f"removed!"))
        delete_button.grid(row=0, column=0, padx=5)
        
        start_button = tk.Button(buttons_section, text="Start",
                                 command=lambda: self.start_machine(attributes))
        start_button.grid(row=0, column=1, padx=5)
    
    def start_machine(self, config: dict) -> None:
        command = []
        
        crt = shutil.which("cool-retro-term")
        if crt:
            command += [crt,
                "--workdir", os.getcwd(),
                "-T", config["Name"],
                "-e",
            ]
        else:
            messagebox.showerror("Error", "Ozpex 64 "
                                 "requires Cool Retro Term to be installed and "
                                 "in the system PATH.")
            return
        
        command += [sys.executable, "../main.py", "--rom", config["ROM"]]
        if config["Cartridge A"] is not None:
            command += ["-1", config["Cartridge A"]]
        if config["Cartridge B"] is not None:
            command += ["-1", config["Cartridge B"]]
            
        subprocess.Popen(command, cwd=os.getcwd())
            
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Ozpex 64")
        self.geometry("700x500")

        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)
        
        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="Quit", command=self.quit)
        self.menubar.add_cascade(label="File", menu=file_menu)
        
        machine_menu = tk.Menu(self.menubar, tearoff=0)
        machine_menu.add_command(label="New", command=self.quit)
        machine_menu.add_command(label="Open", command=self.quit)
        self.menubar.add_cascade(label="Machine", menu=machine_menu)

        self.machines_list = MachinesList(self, bd=2, relief=tk.SUNKEN)
        self.machines_list.grid(row=0, column=0, sticky="nsew")

        self.machine_view = MachineView(self, bd=2, relief=tk.SUNKEN)
        self.machine_view.grid(row=0, column=1, sticky="nsew")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        
if __name__ == "__main__":
    App().mainloop()