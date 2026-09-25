import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import os

class BitPlaneSlicingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grayscale Bit-Plane Slicing")
        self.root.geometry("850x750")
        
        self.image_path = None
        self.original_image = None
        self.gray_image_np = None
        self.current_plane_image = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Top Buttons Frame
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Upload Image", command=self.upload_image, font=("Arial", 11)).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="View All Planes", command=self.view_all_planes, font=("Arial", 11)).grid(row=0, column=1, padx=10)
        tk.Button(btn_frame, text="Save Current Plane", command=self.save_current_plane, font=("Arial", 11)).grid(row=0, column=2, padx=10)
        tk.Button(btn_frame, text="Save Output Sheet", command=self.save_output_sheet, font=("Arial", 11)).grid(row=0, column=3, padx=10)
        
        # Slider Frame
        slider_frame = tk.Frame(self.root)
        slider_frame.pack(pady=10)
        
        tk.Label(slider_frame, text="Select Bit Plane:", font=("Arial", 11)).pack(side=tk.LEFT)
        self.plane_slider = tk.Scale(slider_frame, from_=0, to=7, orient=tk.HORIZONTAL, length=300, command=self.update_plane, font=("Arial", 10))
        self.plane_slider.set(7)
        self.plane_slider.pack(side=tk.LEFT, padx=10)
        
        # Image Display Label
        self.img_label = tk.Label(self.root, bg="gray")
        self.img_label.pack(pady=10, expand=True, fill=tk.BOTH)

    def upload_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp")]
        )
        if file_path:
            try:
                self.image_path = file_path
                self.original_image = Image.open(file_path).convert("L")
                self.gray_image_np = np.array(self.original_image)
                self.update_plane(self.plane_slider.get())
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")
            
    def update_plane(self, k):
        if self.gray_image_np is None:
            return
            
        k = int(k)
        # Algorithm: plane(k) = ((p >> k) & 1) * 255
        plane_np = ((self.gray_image_np >> k) & 1) * 255
        plane_np = plane_np.astype(np.uint8)
        
        self.current_plane_image = Image.fromarray(plane_np)
        
        # Resize for display to fit the window comfortably
        display_img = self.current_plane_image.copy()
        display_img.thumbnail((800, 600))
        
        self.photo = ImageTk.PhotoImage(display_img)
        self.img_label.config(image=self.photo)
        
    def generate_all_planes(self):
        if self.gray_image_np is None:
            return None
            
        h, w = self.gray_image_np.shape
        # Create a 2x4 grid for 8 planes
        sheet_h = h * 2
        sheet_w = w * 4
        
        sheet = np.zeros((sheet_h, sheet_w), dtype=np.uint8)
        
        for k in range(8):
            plane_np = ((self.gray_image_np >> k) & 1) * 255
            plane_np = plane_np.astype(np.uint8)
            
            # Arranging from bit 7 (top-left) to bit 0 (bottom-right)
            row = (7 - k) // 4
            col = (7 - k) % 4
            
            sheet[row*h:(row+1)*h, col*w:(col+1)*w] = plane_np
            
        return Image.fromarray(sheet)

    def view_all_planes(self):
        if self.gray_image_np is None:
            messagebox.showwarning("Warning", "Please upload an image first.")
            return
            
        all_planes_image = self.generate_all_planes()
        
        top = tk.Toplevel(self.root)
        top.title("All Bit Planes (7 to 0)")
        top.geometry("1000x600")
        
        display_img = all_planes_image.copy()
        display_img.thumbnail((1000, 600))
        
        photo = ImageTk.PhotoImage(display_img)
        lbl = tk.Label(top, image=photo, bg="gray")
        lbl.image = photo
        lbl.pack(expand=True, fill=tk.BOTH)

    def save_current_plane(self):
        if self.current_plane_image is None:
            messagebox.showwarning("Warning", "No plane to save.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=f"bit_plane_{self.plane_slider.get()}.png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.current_plane_image.save(file_path)
                messagebox.showinfo("Success", "Plane saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {e}")
            
    def save_output_sheet(self):
        if self.gray_image_np is None:
            messagebox.showwarning("Warning", "Please upload an image first.")
            return
            
        sheet_img = self.generate_all_planes()
        if sheet_img:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                initialfile="bit_plane_slicing_output.png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
            )
            if file_path:
                try:
                    sheet_img.save(file_path)
                    messagebox.showinfo("Success", "Output sheet saved successfully.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save image: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BitPlaneSlicingApp(root)
    root.mainloop()
