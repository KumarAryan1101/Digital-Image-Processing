import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import threading
from huffman_coding import process_huffman

class HuffmanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Manual Huffman Coding")
        self.root.geometry("1000x800")
        
        self.image_path = None
        self.output_dir = "Output"
        
        self.setup_ui()
        
    def setup_ui(self):
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Choose Image", command=self.choose_image, font=("Arial", 11)).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Encode with Huffman", command=self.process_image, font=("Arial", 11)).grid(row=0, column=1, padx=10)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        tk.Label(self.root, textvariable=self.status_var, fg="blue").pack()
        
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.canvas = tk.Canvas(canvas_frame)
        self.scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def choose_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp")]
        )
        if file_path:
            self.image_path = file_path
            self.status_var.set(f"Selected: {os.path.basename(file_path)}")
            
    def process_image(self):
        if not self.image_path:
            messagebox.showwarning("Warning", "Please choose an image first.")
            return
            
        self.status_var.set("Processing (this may take a few seconds)...")
        self.root.update()
        
        def run_task():
            try:
                metrics = process_huffman(self.image_path, self.output_dir)
                self.root.after(0, self.display_results, metrics)
            except Exception as e:
                self.root.after(0, lambda e=e: messagebox.showerror("Error", str(e)))
                self.root.after(0, lambda: self.status_var.set("Error"))
                
        threading.Thread(target=run_task, daemon=True).start()

    def display_results(self, metrics):
        self.status_var.set("Encoding & Decoding Complete!")
        
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        images_to_show = [
            ("Original Greyscale", "huffman_original_grey.png"),
            ("Decoded (Lossless)", "huffman_decoded.png"),
            ("Bit-Length Map", "huffman_bit_length_map.png"),
            ("Length Distribution", "huffman_length_distribution.png"),
            ("Metrics Summary", "huffman_metrics_summary.png")
        ]
        
        for title, filename in images_to_show:
            filepath = os.path.join(self.output_dir, filename)
            if os.path.exists(filepath):
                try:
                    img = Image.open(filepath)
                    if img.width > 800:
                        img = img.resize((800, int(800 * img.height / img.width)))
                        
                    photo = ImageTk.PhotoImage(img)
                    
                    frame = tk.Frame(self.scrollable_frame)
                    frame.pack(pady=10)
                    
                    tk.Label(frame, text=title, font=("Arial", 12, "bold")).pack()
                    lbl = tk.Label(frame, image=photo)
                    lbl.image = photo 
                    lbl.pack()
                except Exception as e:
                    print(f"Error loading {filename}: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HuffmanApp(root)
    root.mainloop()
