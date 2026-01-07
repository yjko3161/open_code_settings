import tkinter as tk
from tkinter import scrolledtext, font, ttk
import subprocess
import threading
import sys
import os
import re
import time

class OpencodeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Opencode GUI Wrapper")
        self.root.geometry("900x700")
        
        # --- Theme Configuration (Dark Mode) ---
        self.bg_color = "#1e1e1e"
        self.fg_color = "#d4d4d4"
        self.input_bg = "#2d2d2d"
        self.input_fg = "#ffffff"
        self.accent_color = "#007acc"
        
        self.root.configure(bg=self.bg_color)
        
        # --- Custom Font ---
        self.custom_font = font.Font(family="Consolas", size=10)

        # --- Style for Notebook ---
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background="#333333", foreground="white", padding=[10, 5], font=('Segoe UI', 9))
        style.map("TNotebook.Tab", background=[("selected", self.accent_color)], foreground=[("selected", "white")])
        style.configure("TFrame", background=self.bg_color)

        # --- UI Layout ---
        self.create_widgets()
        
        # --- Process Control ---
        self.process = None
        # Defer process start slightly to let UI render
        self.root.after(100, self.setup_process)

        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # 0. Tab Control
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=(10, 5))

        # --- Tab 1: Terminal ---
        self.tab_terminal = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_terminal, text="Terminal")

        # Output Area (ScrolledText)
        self.output_area = scrolledtext.ScrolledText(
            self.tab_terminal, 
            state='disabled', 
            bg=self.bg_color, 
            fg=self.fg_color, 
            insertbackground=self.fg_color, 
            font=self.custom_font,
            bd=0,
            padx=10,
            pady=10
        )
        self.output_area.pack(expand=True, fill='both')

        # --- Tab 2: History ---
        self.tab_history = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_history, text="Command History")

        self.history_list = tk.Listbox(
            self.tab_history,
            bg=self.bg_color,
            fg=self.fg_color,
            font=self.custom_font,
            bd=0,
            highlightthickness=0
        )
        self.history_list.pack(expand=True, fill='both', padx=10, pady=10)

        # 1. Input Area (Bottom)
        input_frame = tk.Frame(self.root, bg=self.bg_color)
        input_frame.pack(fill='x', padx=10, pady=(5, 10))

        # Debug Checkbox (Moved inside input_frame to avoid header overlap)
        self.debug_var = tk.BooleanVar(value=False)
        self.debug_chk = tk.Checkbutton(
            input_frame, 
            text="Debug Mode", 
            variable=self.debug_var, 
            bg=self.bg_color, 
            fg=self.fg_color,
            selectcolor=self.input_bg,
            activebackground=self.bg_color,
            activeforeground=self.fg_color,
            font=("Segoe UI", 9)
        )
        self.debug_chk.pack(side='left', padx=(0, 10))


        # Input Field
        self.input_entry = tk.Entry(
            input_frame, 
            bg=self.input_bg, 
            fg=self.input_fg, 
            insertbackground=self.input_fg,
            font=self.custom_font,
            bd=0,
            relief=tk.FLAT
        )
        self.input_entry.pack(side='left', expand=True, fill='x', ipady=8, padx=(0, 5))
        self.input_entry.bind("<Return>", self.send_command)
        self.input_entry.config(highlightbackground=self.accent_color, highlightthickness=1)

        # Send Button
        self.send_btn = tk.Button(
            input_frame, 
            text="Send", 
            command=self.send_command,
            bg=self.accent_color,
            fg="#ffffff",
            activebackground="#005f9e",
            activeforeground="#ffffff",
            bd=0,
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=5
        )
        self.send_btn.pack(side='right')

        self.input_entry.focus_set()

    def setup_process(self):
        try:
            # Run straightforward cmd.exe first.
            # This is safer than trying to run 'opencode' directly if it's a batch file or alias.
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            self.append_text("[System] Starting cmd.exe shell...\n")
            
            # Prepare environment to force unbuffered Python output
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"

            self.process = subprocess.Popen(
                ["cmd.exe"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=False,
                startupinfo=startupinfo,
                bufsize=0, # Unbuffered
                env=env
            )
            
            # Start reader thread
            self.read_thread = threading.Thread(target=self.read_output, daemon=True)
            self.read_thread.start()

            # Now try to launch opencode inside the shell
            # giving it a moment to stabilize
            self.root.after(1000, lambda: self.inject_startup_command("opencode"))
            
        except Exception as e:
            self.append_text(f"[System Error] Could not start process: {e}\n")

    def inject_startup_command(self, cmd):
        if self.process:
            self.append_text(f"[System] Attempting to run '{cmd}'...\n")
            try:
                # We send the command just like a user would.
                self.process.stdin.write((cmd + "\n").encode('cp949'))
                self.process.stdin.flush()
            except Exception as e:
                self.append_text(f"[System Error] Failed to inject startup command: {e}\n")

    def read_output(self):
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

        if not self.process:
            return

        while True:
            try:
                # Read byte-by-byte for responsiveness
                chunk = self.process.stdout.read(1)
                if not chunk:
                    break 
                
                # Removed peek() optimization as it causes AttributeError on FileIO


                try:
                    text = chunk.decode('cp949', errors='replace')
                except:
                     text = chunk.decode('utf-8', errors='replace')

                clean_text = ansi_escape.sub('', text)
                self.root.after(0, lambda t=clean_text: self.append_text(t))
                
            except Exception as e:
                self.root.after(0, lambda msg=f"\n[Read Error] {e}\n": self.append_text(msg))
                break

    def append_text(self, text):
        self.output_area.config(state='normal')
        self.output_area.insert(tk.END, text)
        self.output_area.see(tk.END)
        self.output_area.config(state='disabled')

    def send_command(self, event=None):
        cmd = self.input_entry.get()
        if not cmd:
            return

        # Echo locally
        self.append_text(f"> {cmd}\n")
        
        # Add to history
        self.history_list.insert(tk.END, cmd)
        self.history_list.yview(tk.END)

        try:
            # Send to process
            input_data = cmd + "\n"
            data_bytes = input_data.encode('cp949')
            self.process.stdin.write(data_bytes)
            self.process.stdin.flush()
            
            if self.debug_var.get():
                self.append_text(f"[DEBUG] Sent {len(data_bytes)} bytes to stdin.\n")
                
        except Exception as e:
            self.append_text(f"[Send Error] {e}\n")

        self.input_entry.delete(0, tk.END)

    def on_closing(self):
        if self.process:
            self.process.terminate()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = OpencodeGUI(root)
    root.mainloop()
