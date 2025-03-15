#!/usr/bin/env python3
import os
import sys
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import subprocess
import threading
import multiprocessing
import queue
import time

class MTSConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MTS to MP4 Converter")
        self.root.geometry("650x500")
        self.root.resizable(True, True)
        
        # Set style
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, font=('Helvetica', 12))
        self.style.configure("TLabel", font=('Helvetica', 12))
        
        # Variables
        self.files_to_convert = []
        self.max_processes = max(1, int(multiprocessing.cpu_count() * 0.75))
        self.total_files = 0
        self.converted_files = 0
        self.failed_files = 0
        self.is_converting = False
        self.active_conversions = 0
        self.conversion_queue = queue.Queue()
        self.status_queue = queue.Queue()
        
        # Create UI elements
        self.create_widgets()
        
        # Start status update thread
        self.status_thread = threading.Thread(target=self.update_status, daemon=True)
        self.status_thread.start()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # File selection area
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        select_btn = ttk.Button(file_frame, text="Select MTS Files", command=self.select_files)
        select_btn.pack(side=tk.TOP, pady=5)
        
        # File list
        list_frame = ttk.Frame(file_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.file_list = tk.Listbox(list_frame, height=10, width=60, selectmode=tk.EXTENDED)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_list.yview)
        self.file_list.config(yscrollcommand=scrollbar.set)
        
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.clear_btn = ttk.Button(btn_frame, text="Clear Selection", command=self.clear_selection)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.remove_btn = ttk.Button(btn_frame, text="Remove Selected", command=self.remove_selected)
        self.remove_btn.pack(side=tk.LEFT, padx=5)
        
        self.convert_btn = ttk.Button(btn_frame, text="Start Conversion", command=self.start_conversion)
        self.convert_btn.pack(side=tk.RIGHT, padx=5)
        
        # CPU usage
        cpu_frame = ttk.Frame(main_frame)
        cpu_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(cpu_frame, text="Parallel Conversions:").pack(side=tk.LEFT, padx=5)
        
        self.cpu_scale = ttk.Scale(cpu_frame, from_=1, to=self.max_processes*2, 
                                  orient=tk.HORIZONTAL, length=200,
                                  command=self.update_cpu_value)
        self.cpu_scale.set(self.max_processes)
        self.cpu_scale.pack(side=tk.LEFT, padx=10)
        
        self.cpu_label = ttk.Label(cpu_frame, text=str(self.max_processes))
        self.cpu_label.pack(side=tk.LEFT)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Conversion Progress", padding="10")
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=10)
        
        stats_frame = ttk.Frame(progress_frame)
        stats_frame.pack(fill=tk.X)
        
        self.status_label = ttk.Label(stats_frame, text="Ready to convert")
        self.status_label.pack(fill=tk.X)
        
        self.details_label = ttk.Label(stats_frame, text="")
        self.details_label.pack(fill=tk.X)
        
        # Current conversions
        current_frame = ttk.LabelFrame(main_frame, text="Current Conversions", padding="10")
        current_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.current_text = tk.Text(current_frame, height=4, width=60, state=tk.DISABLED)
        current_scroll = ttk.Scrollbar(current_frame, orient=tk.VERTICAL, command=self.current_text.yview)
        self.current_text.config(yscrollcommand=current_scroll.set)
        
        self.current_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        current_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Select MTS files", 
            filetypes=(("MTS files", "*.MTS *.mts"), ("All files", "*.*"))
        )
        
        if files:
            for file in files:
                if file not in self.files_to_convert:
                    self.files_to_convert.append(file)
                    self.file_list.insert(tk.END, os.path.basename(file))
            
            self.total_files = len(self.files_to_convert)
            self.status_label.config(text=f"{self.total_files} files selected")
    
    def clear_selection(self):
        self.files_to_convert = []
        self.file_list.delete(0, tk.END)
        self.total_files = 0
        self.status_label.config(text="Ready to convert")
        self.details_label.config(text="")
    
    def remove_selected(self):
        selected_indices = self.file_list.curselection()
        if not selected_indices:
            return
            
        # Remove in reverse order to avoid index shifting
        for i in sorted(selected_indices, reverse=True):
            del self.files_to_convert[i]
            self.file_list.delete(i)
            
        self.total_files = len(self.files_to_convert)
        self.status_label.config(text=f"{self.total_files} files selected")
    
    def update_cpu_value(self, value):
        value = int(float(value))
        self.max_processes = value
        self.cpu_label.config(text=str(value))
    
    def update_text_widget(self, widget, text):
        widget.config(state=tk.NORMAL)
        widget.delete(1.0, tk.END)
        widget.insert(tk.END, text)
        widget.config(state=tk.DISABLED)
    
    def start_conversion(self):
        if not self.files_to_convert:
            messagebox.showinfo("No Files", "Please select MTS files to convert")
            return
            
        if self.is_converting:
            messagebox.showinfo("Conversion Running", "Conversion is already in progress")
            return
            
        # Reset counters
        self.converted_files = 0
        self.failed_files = 0
        self.progress_var.set(0)
        self.is_converting = True
        self.current_conversions = {}
        
        # Disable buttons during conversion
        self.convert_btn.config(state=tk.DISABLED)
        self.clear_btn.config(state=tk.DISABLED)
        
        # Start worker threads
        self.status_label.config(text="Starting conversion...")
        
        # Fill the queue with files
        for file in self.files_to_convert:
            self.conversion_queue.put(file)
        
        # Start worker threads
        for _ in range(self.max_processes):
            thread = threading.Thread(target=self.worker_thread, daemon=True)
            thread.start()
    
    def worker_thread(self):
        while not self.conversion_queue.empty() and self.is_converting:
            try:
                file = self.conversion_queue.get(block=False)
                output_file = os.path.splitext(file)[0] + ".mp4"
                
                # Update current conversions
                thread_id = threading.get_ident()
                self.status_queue.put(("add", thread_id, os.path.basename(file)))
                
                cmd = [
                    "ffmpeg", "-y", "-threads", "1", "-i", file,
                    "-c:v", "libx264", "-preset", "medium",
                    "-c:a", "aac", "-b:a", "192k",
                    "-hide_banner", "-loglevel", "warning",
                    output_file
                ]
                
                process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                if process.returncode == 0:
                    # Success - delete original file
                    os.remove(file)
                    self.status_queue.put(("success", thread_id, os.path.basename(file)))
                else:
                    self.status_queue.put(("fail", thread_id, os.path.basename(file)))
                
                self.conversion_queue.task_done()
                
            except queue.Empty:
                break
            except Exception as e:
                self.status_queue.put(("error", threading.get_ident(), str(e)))
    
    def update_status(self):
        """Update the status information from the queue"""
        while True:
            time.sleep(0.1)  # Reduce CPU usage
            
            # Process status updates
            current_conversions = {}
            update_needed = False
            
            try:
                while True:
                    action, thread_id, data = self.status_queue.get(block=False)
                    
                    if action == "add":
                        current_conversions[thread_id] = f"Converting: {data}"
                        update_needed = True
                        
                    elif action == "success":
                        self.converted_files += 1
                        if thread_id in current_conversions:
                            del current_conversions[thread_id]
                        update_needed = True
                        
                    elif action == "fail":
                        self.failed_files += 1
                        if thread_id in current_conversions:
                            del current_conversions[thread_id]
                        update_needed = True
                        
                    elif action == "error":
                        if thread_id in current_conversions:
                            del current_conversions[thread_id]
                        update_needed = True
                        
                    self.status_queue.task_done()
            except queue.Empty:
                pass
            
            # If we need to update the UI
            if update_needed:
                # Update current conversions display
                conversion_text = "\n".join(current_conversions.values())
                self.root.after(0, lambda: self.update_text_widget(self.current_text, conversion_text))
                
                # Update progress
                completed = self.converted_files + self.failed_files
                if self.total_files > 0:
                    progress = (completed / self.total_files) * 100
                    self.root.after(0, lambda p=progress: self.progress_var.set(p))
                
                # Update status labels
                status = f"Converting: {completed}/{self.total_files} complete"
                details = f"Success: {self.converted_files} | Failed: {self.failed_files}"
                self.root.after(0, lambda s=status: self.status_label.config(text=s))
                self.root.after(0, lambda d=details: self.details_label.config(text=d))
                
                # Check if we're done
                if completed >= self.total_files and self.is_converting:
                    self.root.after(0, self.conversion_complete)
    
    def conversion_complete(self):
        self.is_converting = False
        self.convert_btn.config(state=tk.NORMAL)
        self.clear_btn.config(state=tk.NORMAL)
        
        # Show completion message
        messagebox.showinfo(
            "Conversion Complete", 
            f"Conversion finished!\n\n"
            f"Total files: {self.total_files}\n"
            f"Successfully converted: {self.converted_files}\n"
            f"Failed: {self.failed_files}"
        )
        
        # Clear file list if everything was successful
        if self.failed_files == 0:
            self.clear_selection()

if __name__ == "__main__":
    # Check if FFmpeg is installed
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        messagebox.showerror(
            "FFmpeg Not Found", 
            "Error: FFmpeg is not installed. Please install it using:\nbrew install ffmpeg"
        )
        sys.exit(1)
    
    # Start the app
    root = tk.Tk()
    app = MTSConverterApp(root)
    root.mainloop()
