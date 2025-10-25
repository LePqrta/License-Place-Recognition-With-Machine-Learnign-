import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import prediction
import threading
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend to work with tkinter

class LicensePlateGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("License Plate Recognition")
        self.root.geometry("600x700")
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(False, False)
        
        # Configure styles
        self.bg_color = "#f0f0f0"
        self.primary_color = "#2c3e50"
        self.accent_color = "#3498db"
        self.success_color = "#27ae60"
        
        # Selected image path
        self.selected_image_path = None
        self.is_processing = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # Header
        header_frame = tk.Frame(self.root, bg=self.primary_color, height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        
        title_label = tk.Label(
            header_frame,
            text="🚗 License Plate Recognition",
            font=("Helvetica", 24, "bold"),
            bg=self.primary_color,
            fg="white"
        )
        title_label.pack(pady=20)
        
        # Main content frame
        content_frame = tk.Frame(self.root, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Image preview section
        preview_label = tk.Label(
            content_frame,
            text="Image Preview",
            font=("Helvetica", 12, "bold"),
            bg=self.bg_color,
            fg=self.primary_color
        )
        preview_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.preview_frame = tk.Frame(
            content_frame,
            bg="white",
            border=2,
            relief=tk.SUNKEN,
            width=500,
            height=250
        )
        self.preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.preview_frame.pack_propagate(False)
        
        self.preview_label = tk.Label(
            self.preview_frame,
            text="No image selected",
            font=("Helvetica", 14),
            bg="white",
            fg="#999"
        )
        self.preview_label.pack(expand=True)
        
        # Button frame
        button_frame = tk.Frame(content_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Select image button
        self.select_btn = tk.Button(
            button_frame,
            text="📁 Select Image",
            command=self.select_image,
            font=("Helvetica", 11, "bold"),
            bg=self.accent_color,
            fg="white",
            padx=20,
            pady=10,
            border=0,
            cursor="hand2",
            relief=tk.RAISED
        )
        self.select_btn.pack(side=tk.LEFT, padx=5)
        
        # Predict button
        self.predict_btn = tk.Button(
            button_frame,
            text="🔍 Recognize Plate",
            command=self.predict_license_plate,
            font=("Helvetica", 11, "bold"),
            bg=self.success_color,
            fg="white",
            padx=20,
            pady=10,
            border=0,
            cursor="hand2",
            relief=tk.RAISED,
            state=tk.DISABLED
        )
        self.predict_btn.pack(side=tk.LEFT, padx=5)
        
        # Result section
        result_label = tk.Label(
            content_frame,
            text="Recognition Result",
            font=("Helvetica", 12, "bold"),
            bg=self.bg_color,
            fg=self.primary_color
        )
        result_label.pack(anchor=tk.W, pady=(15, 5))
        
        self.result_frame = tk.Frame(
            content_frame,
            bg="white",
            border=2,
            relief=tk.SUNKEN
        )
        self.result_frame.pack(fill=tk.BOTH, pady=(0, 10))
        
        self.result_text = tk.Label(
            self.result_frame,
            text="Awaiting recognition...",
            font=("Helvetica", 28, "bold"),
            bg="white",
            fg=self.primary_color,
            pady=30
        )
        self.result_text.pack(expand=True)
        
        # Status frame
        status_frame = tk.Frame(content_frame, bg=self.bg_color)
        status_frame.pack(fill=tk.X, pady=10)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready",
            font=("Helvetica", 10),
            bg=self.bg_color,
            fg="#666"
        )
        self.status_label.pack(anchor=tk.W)
        
        # File info frame
        self.file_info_label = tk.Label(
            content_frame,
            text="",
            font=("Helvetica", 9),
            bg=self.bg_color,
            fg="#999"
        )
        self.file_info_label.pack(anchor=tk.W, pady=(5, 0))
    
    def select_image(self):
        """Open file dialog to select an image"""
        file_path = filedialog.askopenfilename(
            title="Select License Plate Image",
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            self.selected_image_path = file_path
            self.display_image_preview(file_path)
            self.predict_btn.config(state=tk.NORMAL)
            self.update_status("Image selected. Ready to recognize.")
            
            # Show file info
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / 1024  # KB
            self.file_info_label.config(text=f"File: {file_name} ({file_size:.1f} KB)")
    
    def display_image_preview(self, image_path):
        """Display a preview of the selected image"""
        try:
            # Open and resize image
            img = Image.open(image_path)
            img.thumbnail((480, 240), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Update label
            self.preview_label.config(image=photo, text="")
            self.preview_label.image = photo
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image preview:\n{e}")
    
    def predict_license_plate(self):
        """Run license plate recognition in a separate thread"""
        if not self.selected_image_path:
            messagebox.showwarning("Warning", "Please select an image first.")
            return
        
        if self.is_processing:
            messagebox.showinfo("Processing", "Please wait for the current recognition to complete.")
            return
        
        # Disable buttons and show processing state
        self.is_processing = True
        self.select_btn.config(state=tk.DISABLED)
        self.predict_btn.config(state=tk.DISABLED)
        self.result_text.config(text="Processing...", fg="#3498db")
        self.update_status("Processing image...")
        
        # Run prediction in a separate thread to avoid freezing the GUI
        thread = threading.Thread(target=self._run_prediction)
        thread.daemon = True
        thread.start()
    
    def _run_prediction(self):
        """Background thread for prediction"""
        try:
            result = prediction.predict_license_plate(self.selected_image_path)
            
            # Update GUI on main thread
            self.root.after(0, self._display_result, result)
        except Exception as e:
            # Update GUI on main thread
            self.root.after(0, self._display_error, str(e))
    
    def _display_result(self, result):
        """Display the recognition result"""
        self.is_processing = False
        self.select_btn.config(state=tk.NORMAL)
        self.predict_btn.config(state=tk.NORMAL)
        
        if result and result != "Plate Not Found":
            self.result_text.config(text=result, fg=self.success_color)
            self.update_status(f"✓ Recognition successful: {result}")
        else:
            self.result_text.config(text="No Plate Detected", fg="#e74c3c")
            self.update_status("✗ Could not recognize license plate")
    
    def _display_error(self, error_msg):
        """Display an error message"""
        self.is_processing = False
        self.select_btn.config(state=tk.NORMAL)
        self.predict_btn.config(state=tk.NORMAL)
        
        self.result_text.config(text="Error", fg="#e74c3c")
        self.update_status(f"✗ Error: {error_msg}")
        messagebox.showerror("Recognition Error", f"An error occurred:\n{error_msg}")
    
    def update_status(self, message):
        """Update the status label"""
        self.status_label.config(text=message)


if __name__ == "__main__":
    root = tk.Tk()
    app = LicensePlateGUI(root)
    root.mainloop()
