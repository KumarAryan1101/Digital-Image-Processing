import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

import cv2
import numpy as np
from PIL import Image, ImageTk

import matplotlib

# Force Matplotlib to use a quiet non-interactive backend
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class FinalDIPDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title(
            "Digital Image Processing Lab - Complete Histogram Engineering Dashboard"
        )
        self.root.geometry("1400x900")
        self.root.configure(bg="#121214")

        # ---------------------------------------------------------
        # STYLE CONFIGURATION
        # ---------------------------------------------------------
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TCombobox",
            fieldbackground="#252532",
            background="#323242",
            foreground="white",
            arrowcolor="white",
        )

        # ---------------------------------------------------------
        # CORE STATE VARIABLES
        # ---------------------------------------------------------
        self.cv_img_original = None
        self.cv_img_processed = None
        self.file_path = ""

        # ---------------------------------------------------------
        # TOP CONTROL DASHBOARD
        # ---------------------------------------------------------
        ctrl_panel = tk.Frame(
            self.root,
            bg="#1a1a24",
            bd=0
        )
        ctrl_panel.pack(
            fill="x",
            side="top",
            padx=20,
            pady=15
        )

        # ---------------------------------------------------------
        # LEFT ACTION FRAME
        # ---------------------------------------------------------
        left_actions = tk.Frame(
            ctrl_panel,
            bg="#1a1a24"
        )
        left_actions.pack(
            side="left",
            fill="y",
            pady=5
        )

        self.btn_upload = tk.Button(
            left_actions,
            text="📸 Upload Image",
            font=("Segoe UI", 10, "bold"),
            bg="#00adb5",
            fg="white",
            activebackground="#008c9e",
            activeforeground="white",
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2",
            relief="flat",
            command=self.upload_image_asset,
        )
        self.btn_upload.pack(
            side="left",
            padx=(0, 20)
        )

        lbl_op = tk.Label(
            left_actions,
            text="Processing Method:",
            font=("Segoe UI", 10, "bold"),
            bg="#1a1a24",
            fg="#eeeeee",
        )
        lbl_op.pack(
            side="left",
            padx=(0, 10)
        )

        self.operations = [
            "1. Global Equalization (Color Image)",
            "2. Convert to Standard Grayscale",
            "3. Global Equalization (Grayscale Image)",
            "4. Local / Adaptive Equalization (Grayscale CLAHE)",
            "5. Local / Adaptive Equalization (Color CLAHE/RGB)",
            "6. View RGB Channels (Red)",
            "7. View RGB Channels (Green)",
            "8. View RGB Channels (Blue)",
        ]

        self.combo_op = ttk.Combobox(
            left_actions,
            values=self.operations,
            state="readonly",
            width=42,
            font=("Segoe UI", 10),
        )
        self.combo_op.current(0)
        self.combo_op.pack(side="left")
        self.combo_op.bind(
            "<<ComboboxSelected>>",
            self.on_method_dropdown_change
        )

        # ---------------------------------------------------------
        # PARAMETER PANEL
        # ---------------------------------------------------------
        self.parameter_frame = tk.LabelFrame(
            ctrl_panel,
            text=" 🎛️ CLAHE Parameters (Only Active in Mode 4 & 5) ",
            font=("Segoe UI", 9, "bold"),
            bg="#1a1a24",
            fg="#00adb5",
            bd=1,
            relief="solid",
        )
        self.parameter_frame.pack(
            side="right",
            padx=(20, 0),
            fill="both",
            expand=True,
        )

        # Clip Limit Slider
        tk.Label(
            self.parameter_frame,
            text="Clip Limit:",
            bg="#1a1a24",
            fg="#ccc",
            font=("Segoe UI", 9, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=(15, 5),
            pady=10,
            sticky="w",
        )

        self.slider_clip = tk.Scale(
            self.parameter_frame,
            from_=1.0,
            to=10.0,
            resolution=0.5,
            orient="horizontal",
            bg="#1a1a24",
            fg="#eee",
            highlightthickness=0,
            troughcolor="#2d2d3a",
            activebackground="#00adb5",
            command=lambda val: self.trigger_reactive_update(),
        )
        self.slider_clip.set(2.0)
        self.slider_clip.grid(
            row=0,
            column=1,
            padx=5,
            pady=5,
        )

        # Grid Block Size Slider
        tk.Label(
            self.parameter_frame,
            text="Grid Size (NxN):",
            bg="#1a1a24",
            fg="#ccc",
            font=("Segoe UI", 9, "bold"),
        ).grid(
            row=0,
            column=2,
            padx=(15, 5),
            pady=10,
            sticky="w",
        )

        self.slider_grid = tk.Scale(
            self.parameter_frame,
            from_=2,
            to=32,
            resolution=2,
            orient="horizontal",
            bg="#1a1a24",
            fg="#eee",
            highlightthickness=0,
            troughcolor="#2d2d3a",
            activebackground="#00adb5",
            command=lambda val: self.trigger_reactive_update(),
        )
        self.slider_grid.set(8)
        self.slider_grid.grid(
            row=0,
            column=3,
            padx=5,
            pady=5,
        )

        # Histogram Type Dropdown
        tk.Label(
            self.parameter_frame,
            text="Hist Type:",
            bg="#1a1a24",
            fg="#ccc",
            font=("Segoe UI", 9, "bold"),
        ).grid(
            row=0,
            column=4,
            padx=(15, 5),
            pady=10,
            sticky="w",
        )

        self.hist_type_string_var = tk.StringVar(
            value="Standard (PDF)"
        )

        self.combo_hist_type = ttk.Combobox(
            self.parameter_frame,
            textvariable=self.hist_type_string_var,
            values=[
                "Standard (PDF)",
                "Cumulative (CDF)"
            ],
            state="readonly",
            width=15,
            font=("Segoe UI", 9),
        )
        self.combo_hist_type.grid(
            row=0,
            column=5,
            padx=(5, 15),
            pady=5,
        )

        self.combo_hist_type.bind(
            "<<ComboboxSelected>>",
            lambda event: self.trigger_reactive_update()
        )

        self.toggle_parameter_controls(False)

        # ---------------------------------------------------------
        # CORE WORKSPACE VIEW DISPLAY PANEL
        # ---------------------------------------------------------
        self.workspace_panel = tk.Frame(
            self.root,
            bg="#121214"
        )
        self.workspace_panel.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=5,
        )

        self.workspace_panel.rowconfigure(
            0,
            weight=5,
            minsize=350
        )
        self.workspace_panel.rowconfigure(
            1,
            weight=4,
            minsize=300
        )

        self.workspace_panel.columnconfigure(
            0,
            weight=1
        )
        self.workspace_panel.columnconfigure(
            1,
            weight=1
        )

        # ---------------------------------------------------------
        # ORIGINAL IMAGE FRAME
        # ---------------------------------------------------------
        self.frame_orig = tk.LabelFrame(
            self.workspace_panel,
            text=" 📥 Source Visual Matrix ",
            font=("Segoe UI", 10, "bold"),
            bg="#1a1a24",
            fg="#ffffff",
            bd=1,
            relief="solid",
        )
        self.frame_orig.grid(
            row=0,
            column=0,
            padx=10,
            pady=10,
            sticky="nsew",
        )

        self.lbl_orig = tk.Label(
            self.frame_orig,
            bg="#1a1a24",
            text="Upload structural source asset matrix",
            fg="#666677",
            font=("Segoe UI", 10),
        )
        self.lbl_orig.pack(
            fill="both",
            expand=True
        )

        # ---------------------------------------------------------
        # PROCESSED IMAGE FRAME
        # ---------------------------------------------------------
        self.frame_proc = tk.LabelFrame(
            self.workspace_panel,
            text=" 📤 Computed Output Frame ",
            font=("Segoe UI", 10, "bold"),
            bg="#1a1a24",
            fg="#ffffff",
            bd=1,
            relief="solid",
        )
        self.frame_proc.grid(
            row=0,
            column=1,
            padx=10,
            pady=10,
            sticky="nsew",
        )

        self.lbl_proc = tk.Label(
            self.frame_proc,
            bg="#1a1a24",
            text="Awaiting algorithmic pipeline processing execution",
            fg="#666677",
            font=("Segoe UI", 10),
        )
        self.lbl_proc.pack(
            fill="both",
            expand=True
        )

        # ---------------------------------------------------------
        # MATPLOTLIB GRAPH CANVAS
        # ---------------------------------------------------------
        self.fig, (self.ax_orig, self.ax_proc) = plt.subplots(
            1,
            2,
            figsize=(12, 3.2)
        )

        self.fig.patch.set_facecolor("#1a1a24")

        for ax in [self.ax_orig, self.ax_proc]:
            ax.set_facecolor("#121214")
            ax.tick_params(
                colors="#888899",
                labelsize=9
            )
            ax.xaxis.label.set_color("#888899")
            ax.yaxis.label.set_color("#888899")
            ax.grid(
                True,
                color="#252532",
                linestyle="--",
                alpha=0.5
            )

        self.canvas = FigureCanvasTkAgg(
            self.fig,
            master=self.workspace_panel
        )

        self.canvas.get_tk_widget().grid(
            row=1,
            column=0,
            columnspan=2,
            padx=10,
            pady=10,
            sticky="nsew",
        )

        # Load default sample
        self.load_default_sample()

    # =============================================================
    # LOAD DEFAULT SAMPLE
    # =============================================================
    def load_default_sample(self):
        np.random.seed(101)

        base_noise = np.random.normal(
            loc=140,
            scale=18,
            size=(450, 450, 3)
        )

        cv2.circle(
            base_noise,
            (180, 225),
            90,
            (230, 40, 50),
            -1
        )

        cv2.rectangle(
            base_noise,
            (220, 120),
            (360, 280),
            (40, 220, 60),
            -1
        )

        cv2.circle(
            base_noise,
            (280, 300),
            70,
            (50, 60, 240),
            -1
        )

        self.cv_img_original = np.clip(
            base_noise,
            0,
            255
        ).astype(np.uint8)

        self.display_matrix_to_ui(
            self.cv_img_original,
            self.lbl_orig
        )

        self.execute_processing_pipeline()

    # =============================================================
    # UPLOAD IMAGE
    # =============================================================
    def upload_image_asset(self):
        self.file_path = filedialog.askopenfilename(
            filetypes=[
                (
                    "Images",
                    "*.jpg *.jpeg *.png *.bmp *.webp"
                )
            ]
        )

        if not self.file_path:
            return

        self.cv_img_original = cv2.imread(
            self.file_path
        )

        if self.cv_img_original is None:
            messagebox.showerror(
                "Error",
                "Unable to load the selected image."
            )
            return

        self.display_matrix_to_ui(
            self.cv_img_original,
            self.lbl_orig
        )

        self.execute_processing_pipeline()

    # =============================================================
    # METHOD DROPDOWN CHANGE
    # =============================================================
    def on_method_dropdown_change(self, event=None):
        selected_mode = self.combo_op.get()

        if (
            "4. Local / Adaptive" in selected_mode
            or "5. Local / Adaptive" in selected_mode
        ):
            self.toggle_parameter_controls(True)

            self.parameter_frame.config(
                text=" 🎛️ CLAHE Parameters (ACTIVE) "
            )

        else:
            self.toggle_parameter_controls(False)

            self.parameter_frame.config(
                text=" 🎛️ CLAHE Parameters (Locked: Choose Mode 4 or 5) "
            )

        self.execute_processing_pipeline()

    # =============================================================
    # ENABLE / DISABLE CLAHE PARAMETERS
    # =============================================================
    def toggle_parameter_controls(self, enable=True):
        state = "normal" if enable else "disabled"

        self.slider_clip.config(
            state=state,
            fg="#eee" if enable else "#555"
        )

        self.slider_grid.config(
            state=state,
            fg="#eee" if enable else "#555"
        )

    # =============================================================
    # REACTIVE PARAMETER UPDATE
    # =============================================================
    def trigger_reactive_update(self):
        if self.cv_img_original is not None:
            self.execute_processing_pipeline()

    # =============================================================
    # MAIN IMAGE PROCESSING PIPELINE
    # =============================================================
    def execute_processing_pipeline(self):
        if self.cv_img_original is None:
            return

        selected_mode = self.combo_op.get()

        # ---------------------------------------------------------
        # MODE 1: GLOBAL EQUALIZATION - COLOR
        # ---------------------------------------------------------
        if "1. Global Equalization (Color Image)" in selected_mode:

            ycrcb = cv2.cvtColor(
                self.cv_img_original,
                cv2.COLOR_BGR2YCrCb
            )

            ycrcb[:, :, 0] = cv2.equalizeHist(
                ycrcb[:, :, 0]
            )

            self.cv_img_processed = cv2.cvtColor(
                ycrcb,
                cv2.COLOR_YCrCb2BGR
            )

        # ---------------------------------------------------------
        # MODE 2: STANDARD GRAYSCALE
        # ---------------------------------------------------------
        elif "2. Convert to Standard Grayscale" in selected_mode:

            self.cv_img_processed = cv2.cvtColor(
                self.cv_img_original,
                cv2.COLOR_BGR2GRAY
            )

        # ---------------------------------------------------------
        # MODE 3: GLOBAL EQUALIZATION - GRAYSCALE
        # ---------------------------------------------------------
        elif "3. Global Equalization (Grayscale Image)" in selected_mode:

            gray = cv2.cvtColor(
                self.cv_img_original,
                cv2.COLOR_BGR2GRAY
            )

            self.cv_img_processed = cv2.equalizeHist(
                gray
            )

        # ---------------------------------------------------------
        # MODE 4: LOCAL / ADAPTIVE EQUALIZATION - GRAYSCALE
        # ---------------------------------------------------------
        elif "4. Local / Adaptive Equalization (Grayscale CLAHE)" in selected_mode:

            gray = cv2.cvtColor(
                self.cv_img_original,
                cv2.COLOR_BGR2GRAY
            )

            clip_limit_value = float(
                self.slider_clip.get()
            )

            grid_tile_value = int(
                self.slider_grid.get()
            )

            clahe_object = cv2.createCLAHE(
                clipLimit=clip_limit_value,
                tileGridSize=(
                    grid_tile_value,
                    grid_tile_value
                )
            )

            self.cv_img_processed = clahe_object.apply(
                gray
            )

        # ---------------------------------------------------------
        # MODE 5: LOCAL / ADAPTIVE EQUALIZATION - COLOR
        # ---------------------------------------------------------
        elif "5. Local / Adaptive Equalization (Color CLAHE/RGB)" in selected_mode:

            ycrcb = cv2.cvtColor(
                self.cv_img_original,
                cv2.COLOR_BGR2YCrCb
            )

            clip_limit_value = float(
                self.slider_clip.get()
            )

            grid_tile_value = int(
                self.slider_grid.get()
            )

            clahe_object = cv2.createCLAHE(
                clipLimit=clip_limit_value,
                tileGridSize=(
                    grid_tile_value,
                    grid_tile_value
                )
            )

            ycrcb[:, :, 0] = clahe_object.apply(
                ycrcb[:, :, 0]
            )

            self.cv_img_processed = cv2.cvtColor(
                ycrcb,
                cv2.COLOR_YCrCb2BGR
            )

        # ---------------------------------------------------------
        # MODE 6: RED CHANNEL
        # ---------------------------------------------------------
        elif "6. View RGB Channels (Red)" in selected_mode:

            red_channel = self.cv_img_original[:, :, 2]

            blank = np.zeros_like(
                red_channel
            )

            self.cv_img_processed = cv2.merge(
                [
                    blank,
                    blank,
                    red_channel
                ]
            )

        # ---------------------------------------------------------
        # MODE 7: GREEN CHANNEL
        # ---------------------------------------------------------
        elif "7. View RGB Channels (Green)" in selected_mode:

            green_channel = self.cv_img_original[:, :, 1]

            blank = np.zeros_like(
                green_channel
            )

            self.cv_img_processed = cv2.merge(
                [
                    blank,
                    green_channel,
                    blank
                ]
            )

        # ---------------------------------------------------------
        # MODE 8: BLUE CHANNEL
        # ---------------------------------------------------------
        elif "8. View RGB Channels (Blue)" in selected_mode:

            blue_channel = self.cv_img_original[:, :, 0]

            blank = np.zeros_like(
                blue_channel
            )

            self.cv_img_processed = cv2.merge(
                [
                    blue_channel,
                    blank,
                    blank
                ]
            )

        # ---------------------------------------------------------
        # DISPLAY RESULT
        # ---------------------------------------------------------
        if self.cv_img_processed is not None:

            self.display_matrix_to_ui(
                self.cv_img_processed,
                self.lbl_proc
            )

            self.render_canvas_histograms()

    # =============================================================
    # RENDER HISTOGRAMS
    # =============================================================
    def render_canvas_histograms(self):
        self.ax_orig.clear()
        self.ax_proc.clear()

        selected_graph_format = (
            self.hist_type_string_var.get()
        )

        selected_mode = self.combo_op.get()

        # ---------------------------------------------------------
        # HISTOGRAM COMPUTATION FUNCTION
        # ---------------------------------------------------------
        def compute_and_plot(
            axis,
            img_matrix,
            title_text,
            force_single_channel_color=None
        ):
            axis.set_title(
                title_text,
                color="#00adb5",
                fontsize=10,
                fontweight="bold"
            )

            axis.set_xlim([0, 256])

            # Grayscale image
            if len(img_matrix.shape) == 2:

                plot_color = "#a6a6a4"

                if selected_graph_format == "Standard (PDF)":

                    axis.hist(
                        img_matrix.ravel(),
                        bins=256,
                        range=(0, 256),
                        color=plot_color,
                        alpha=0.7
                    )

                else:

                    axis.hist(
                        img_matrix.ravel(),
                        bins=256,
                        range=(0, 256),
                        color=plot_color,
                        cumulative=True,
                        density=True,
                        histtype="step",
                        linewidth=2
                    )

            # Color image
            else:

                if force_single_channel_color:

                    channel_idx = (
                        2
                        if force_single_channel_color == "r"
                        else (
                            1
                            if force_single_channel_color == "g"
                            else 0
                        )
                    )

                    hist_data = cv2.calcHist(
                        [img_matrix],
                        [channel_idx],
                        None,
                        [256],
                        [0, 256]
                    )

                    if selected_graph_format == "Standard (PDF)":

                        axis.plot(
                            hist_data,
                            color=force_single_channel_color,
                            linewidth=1.5
                        )

                    else:

                        cdf = np.cumsum(
                            hist_data
                        )

                        if cdf.max() > 0:
                            cdf = cdf / cdf.max()

                        axis.plot(
                            cdf,
                            color=force_single_channel_color,
                            linewidth=2
                        )

                else:

                    color_channels = (
                        "b",
                        "g",
                        "r"
                    )

                    for idx, color in enumerate(
                        color_channels
                    ):

                        hist_data = cv2.calcHist(
                            [img_matrix],
                            [idx],
                            None,
                            [256],
                            [0, 256]
                        )

                        if selected_graph_format == "Standard (PDF)":

                            axis.plot(
                                hist_data,
                                color=color,
                                linewidth=1.5
                            )

                        else:

                            cdf_curve = np.cumsum(
                                hist_data
                            )

                            if cdf_curve.max() > 0:
                                cdf_normalized_curve = (
                                    cdf_curve /
                                    cdf_curve.max()
                                )
                            else:
                                cdf_normalized_curve = cdf_curve

                            axis.plot(
                                cdf_normalized_curve,
                                color=color,
                                linewidth=2
                            )

        # ---------------------------------------------------------
        # ORIGINAL IMAGE HISTOGRAM
        # ---------------------------------------------------------
        compute_and_plot(
            self.ax_orig,
            self.cv_img_original,
            "Input Signal Distribution"
        )

        # ---------------------------------------------------------
        # PROCESSED IMAGE HISTOGRAM
        # ---------------------------------------------------------
        proc_color = None

        if "Red" in selected_mode:
            proc_color = "r"

        elif "Green" in selected_mode:
            proc_color = "g"

        elif "Blue" in selected_mode:
            proc_color = "b"

        compute_and_plot(
            self.ax_proc,
            self.cv_img_processed,
            "Processed Transform Signature",
            force_single_channel_color=proc_color
        )

        self.fig.tight_layout()
        self.canvas.draw()

    # =============================================================
    # DISPLAY IMAGE IN TKINTER
    # =============================================================
    def display_matrix_to_ui(
        self,
        cv_img,
        target_label
    ):
        if cv_img is None:
            return

        h, w = cv_img.shape[:2]

        scaling_ratio = min(
            550 / w,
            350 / h
        )

        new_width = max(
            1,
            int(w * scaling_ratio)
        )

        new_height = max(
            1,
            int(h * scaling_ratio)
        )

        resized_image = cv2.resize(
            cv_img,
            (new_width, new_height),
            interpolation=cv2.INTER_AREA
        )

        # Convert OpenCV BGR/GRAY to RGB
        if len(resized_image.shape) == 2:

            render_ready_rgb = cv2.cvtColor(
                resized_image,
                cv2.COLOR_GRAY2RGB
            )

        else:

            render_ready_rgb = cv2.cvtColor(
                resized_image,
                cv2.COLOR_BGR2RGB
            )

        pil_image_wrapper = Image.fromarray(
            render_ready_rgb
        )

        tk_render_photo_image = ImageTk.PhotoImage(
            image=pil_image_wrapper
        )

        target_label.config(
            image=tk_render_photo_image
        )

        # Keep a reference so Tkinter doesn't garbage-collect it
        target_label.image = tk_render_photo_image


# =============================================================
# APPLICATION ENTRY POINT
# =============================================================
if __name__ == "__main__":

    root = tk.Tk()

    app = FinalDIPDashboard(root)

    root.mainloop()

