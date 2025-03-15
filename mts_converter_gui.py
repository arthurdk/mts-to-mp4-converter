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
import random

class MTSConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MTS to MP4 Converter")
        self.root.geometry("800x800")  # Made taller to accommodate puns
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
        self.current_conversions = {}
        self.pun_index = 0
        self.last_pun_time = 0
        
        # Create UI elements
        self.create_widgets()
        
        # Start status update thread
        self.status_thread = threading.Thread(target=self.update_status, daemon=True)
        self.status_thread.start()
        
        # Setup regular UI update
        self.update_ui()
        
        # List of conversion puns
        self.puns = [
            "Converting files faster than a cheetah on caffeine!",
            "Transforming your videos... it's like magic, but with more CPUs!",
            "Your videos are getting a digital makeover!",
            "Converting: Because 'MTS' sounds like a disease and 'MP4' sounds cool!",
            "Turning your MTS files into MP4s... like turning pumpkins into carriages!",
            "Compressing bits and bytes like a digital sandwich maker!",
            "MP4: Making Practically 4-midable videos from your MTS files!",
            "If videos were currency, you'd be getting a great exchange rate!",
            "Your videos are leveling up! Achievement unlocked: MP4 Format!",
            "Converting with the speed of light... minus about 299,792,458 m/s!",
            "Video conversion: Like translating from MTS-ish to MP4-anese!",
            "Working harder than a squirrel gathering nuts for winter!",
            "These files are getting more conversion than a religious retreat!",
            "FFmpeg: The superhero your videos deserve!",
            "Converting faster than you can say 'supercalifragilisticexpialidocious'!",
            "Turning MTS into MP4 like alchemy, but it actually works!",
            "These videos are getting more processed than cheese!",
            "Your patience is appreciated more than pizza at midnight!",
            "If this were any faster, we'd need a speeding ticket!",
            "Converting videos and making terrible puns... multitasking at its finest!"
        ]
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # File selection area
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.select_btn = ttk.Button(file_frame, text="Select MTS Files", command=self.select_files)
        self.select_btn.pack(side=tk.TOP, pady=5)
        
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
        
        self.cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self.cancel_conversion, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.RIGHT, padx=5)
        
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
        
        # Single progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=10)
        
        stats_frame = ttk.Frame(progress_frame)
        stats_frame.pack(fill=tk.X)
        
        self.status_label = ttk.Label(stats_frame, text="Ready to convert")
        self.status_label.pack(fill=tk.X)
        
        self.details_label = ttk.Label(stats_frame, text="")
        self.details_label.pack(fill=tk.X)
        
        # Pun display
        self.pun_label = ttk.Label(progress_frame, text="", font=('Helvetica', 10, 'italic'),
                                  wraplength=580, justify=tk.CENTER)
        self.pun_label.pack(fill=tk.X, pady=5)
        
        # Current conversions
        current_frame = ttk.LabelFrame(main_frame, text="Current Conversions", padding="10")
        current_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Make the text widget taller and ensure it uses a monospace font
        self.current_text = tk.Text(current_frame, height=8, width=60, 
                                   font=('Courier', 10),
                                   wrap=tk.WORD,
                                   state=tk.DISABLED)
        current_scroll = ttk.Scrollbar(current_frame, orient=tk.VERTICAL, 
                                     command=self.current_text.yview)
        self.current_text.config(yscrollcommand=current_scroll.set)
        
        self.current_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
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
        # Fix: Check if cpu_label exists before trying to update it
        if hasattr(self, 'cpu_label'):
            self.cpu_label.config(text=str(value))
        else:
            print("Warning: cpu_label not found")
    
    def update_text_widget(self, widget, text):
        widget.config(state=tk.NORMAL)
        widget.delete(1.0, tk.END)
        widget.insert(tk.END, text)
        widget.config(state=tk.DISABLED)
    
    def display_random_pun(self):
        """Display a random pun from the list"""
        current_time = time.time()
        # Change pun every 5 seconds
        if current_time - self.last_pun_time >= 5:
            self.last_pun_time = current_time
            self.pun_index = random.randint(0, len(self.puns) - 1)
            self.pun_label.config(text=self.puns[self.pun_index])
    
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
        self.current_conversions.clear()  # Clear any previous conversions
        
        # Disable UI elements during conversion
        self.convert_btn.config(state=tk.DISABLED)
        self.clear_btn.config(state=tk.DISABLED)
        self.remove_btn.config(state=tk.DISABLED)
        self.select_btn.config(state=tk.DISABLED)
        self.file_list.config(state=tk.DISABLED)
        self.cpu_scale.config(state=tk.DISABLED)
        
        # Try a more direct approach to enable the cancel button
        try:
            # Try multiple approaches to ensure the button is enabled
            self.cancel_btn.configure(state="normal")
            self.cancel_btn.state(["!disabled"])
            # Force update the button
            self.root.update_idletasks()
        except Exception as e:
            print(f"Error enabling cancel button: {e}")
        
        # Show first pun
        self.display_random_pun()
        
        # Start worker threads
        self.status_label.config(text="Starting conversion...")
        
        # Initialize status for all files
        for file in self.files_to_convert:
            self.current_conversions[file] = f"Waiting: {os.path.basename(file)}"
        self.update_text_widget(self.current_text, "\n".join(self.current_conversions.values()))
        
        # Fill the queue with files
        for file in self.files_to_convert:
            self.conversion_queue.put(file)
        
        # Start worker threads
        for _ in range(self.max_processes):
            thread = threading.Thread(target=self.worker_thread, daemon=True)
            thread.start()
    
    def cancel_conversion(self):
        if not self.is_converting:
            return
            
        # Ask for confirmation
        if messagebox.askyesno("Cancel Conversion", "Are you sure you want to cancel the conversion?"):
            self.is_converting = False
            # Clear the queue
            while not self.conversion_queue.empty():
                try:
                    self.conversion_queue.get_nowait()
                    self.conversion_queue.task_done()
                except queue.Empty:
                    break
            
            # Re-enable UI elements
            self.convert_btn.config(state=tk.NORMAL)
            self.clear_btn.config(state=tk.NORMAL)
            self.remove_btn.config(state=tk.NORMAL)
            self.select_btn.config(state=tk.NORMAL)
            self.file_list.config(state=tk.NORMAL)
            self.cpu_scale.config(state=tk.NORMAL)
            
            # Fix: Use ttk state method instead of config
            self.cancel_btn.state(['disabled'])
            
            # Update status
            self.status_label.config(text="Conversion cancelled")
            self.pun_label.config(text="")
            
            # Clear the current conversions section
            self.current_conversions.clear()
            self.update_text_widget(self.current_text, "")
    
    def worker_thread(self):
        while not self.conversion_queue.empty() and self.is_converting:
            try:
                file = self.conversion_queue.get(block=False)
                output_file = os.path.splitext(file)[0] + ".mp4"
                
                # Update current conversions
                self.status_queue.put(("converting", file, f"Converting: {os.path.basename(file)}"))
                
                cmd = [
                    "ffmpeg", "-y", "-threads", "1", "-i", file,
                    "-c:v", "libx264", "-preset", "medium",
                    "-c:a", "aac", "-b:a", "192k",
                    "-hide_banner", "-loglevel", "warning",
                    output_file
                ]
                
                process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                if process.returncode == 0:
                    self.status_queue.put(("success", file, f"Completed: {os.path.basename(file)}"))
                else:
                    self.status_queue.put(("fail", file, f"Failed: {os.path.basename(file)}"))
                
                self.conversion_queue.task_done()
                
            except queue.Empty:
                break
            except Exception as e:
                self.status_queue.put(("error", file, str(e)))

    def update_status(self):
        """Process status updates from the queue"""
        while True:
            time.sleep(0.1)  # Reduce CPU usage
            
            try:
                while True:  # Process all available updates
                    action, file, data = self.status_queue.get(block=False)
                    
                    if action == "converting":
                        self.current_conversions[file] = data
                        self.active_conversions += 1
                        
                    elif action == "success":
                        self.converted_files += 1
                        self.current_conversions[file] = data
                        self.active_conversions -= 1
                        
                    elif action == "fail":
                        self.failed_files += 1
                        self.current_conversions[file] = data
                        self.active_conversions -= 1
                        
                    elif action == "error":
                        self.current_conversions[file] = f"Error: {os.path.basename(file)} - {data}"
                        self.active_conversions -= 1
                        self.failed_files += 1
                        messagebox.showerror("Conversion Error", f"Error converting file: {data}")
                    
                    # Check if all conversions are complete
                    if self.active_conversions == 0 and self.is_converting:
                        completed = self.converted_files + self.failed_files
                        if completed >= self.total_files:
                            self.conversion_complete()
                
            except queue.Empty:
                continue  # No more updates to process
            except Exception as e:
                print(f"Error in status update thread: {e}")
                continue

    def update_ui(self):
        """Update the UI at regular intervals"""
        if self.is_converting:
            # Display a random pun
            self.display_random_pun()
            
            # Update current conversions display
            if self.current_conversions:
                # Sort the conversions by status for better readability
                sorted_conversions = sorted(self.current_conversions.values(), key=lambda x: 
                    "0" if x.startswith("Converting") else
                    "1" if x.startswith("Waiting") else
                    "2" if x.startswith("Completed") else
                    "3" if x.startswith("Failed") else "4"
                )
                conversion_text = "\n".join(sorted_conversions)
            else:
                conversion_text = "No active conversions"
            
            # Force update of conversion status
            self.update_text_widget(self.current_text, conversion_text)
            self.current_text.see(tk.END)  # Auto-scroll to bottom
            
            # Update progress bar and status
            completed = self.converted_files + self.failed_files
            if self.total_files > 0:
                progress = (completed / self.total_files) * 100
                self.progress_var.set(progress)
            
            status = f"Converting: {completed}/{self.total_files} complete"
            details = f"Success: {self.converted_files} | Failed: {self.failed_files}"
            self.status_label.config(text=status)
            self.details_label.config(text=details)
            
            # Check if conversion is complete
            if completed >= self.total_files:
                self.conversion_complete()
        
        # Schedule next update more frequently
        self.root.after(50, self.update_ui)  # Update every 50ms instead of 100ms
    
    def conversion_complete(self):
        """Handle completion of all conversions"""
        self.is_converting = False
        
        # Re-enable UI elements
        self.convert_btn.config(state=tk.NORMAL)
        self.clear_btn.config(state=tk.NORMAL)
        self.remove_btn.config(state=tk.NORMAL)
        self.select_btn.config(state=tk.NORMAL)
        self.file_list.config(state=tk.NORMAL)
        self.cpu_scale.config(state=tk.NORMAL)
        
        # Fix: Use ttk state method instead of config
        self.cancel_btn.state(['disabled'])
        
        # Update status
        self.status_label.config(text="Conversion complete!")
        self.pun_label.config(text="")
        self.update_text_widget(self.current_text, "")
        
        # Show completion message
        messagebox.showinfo("Conversion Complete", 
                          f"Converted: {self.converted_files}\nFailed: {self.failed_files}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MTSConverterApp(root)
    root.mainloop()
