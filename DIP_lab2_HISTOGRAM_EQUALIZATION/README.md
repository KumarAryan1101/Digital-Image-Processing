# DIP Lab 2: Histogram Equalization

## Overview
This folder contains the implementation for **Lab 2** of Digital Image Processing, focused on **histogram equalization** and **contrast enhancement** techniques.

The main application is an interactive Python dashboard that lets you:
- Load and visualize images
- Apply global histogram equalization
- Apply local/adaptive equalization using CLAHE
- Convert images to grayscale
- Inspect individual RGB channels
- Compare input and output histograms in both PDF and CDF forms

## Folder Contents
- `hist_eq_code.py`: Main Python Tkinter application for all processing workflows.
- `global_equalization_rgb.png`: Reference output for global equalization on color image.
- `global_equalization_grayscale.png`: Reference output for global equalization on grayscale image.
- `graysacle_img.png`: Reference grayscale conversion output.
- `grayscale_CLAHE_local_eq.png`: Reference output for grayscale CLAHE.
- `rgb_CLAHE_local_eq.png`: Reference output for color CLAHE.

## What This Code Does
The script builds a GUI-based DIP dashboard with OpenCV-powered processing modes:

1. Global Equalization (Color):
   - Converts image to YCrCb
   - Equalizes the luminance (Y) channel
   - Converts back to color space

2. Standard Grayscale Conversion:
   - Converts BGR image to single-channel grayscale

3. Global Equalization (Grayscale):
   - Computes histogram equalization over grayscale intensities

4. Local/Adaptive Equalization (Grayscale CLAHE):
   - Applies CLAHE with configurable clip limit and tile size

5. Local/Adaptive Equalization (Color CLAHE):
   - Applies CLAHE to luminance channel in YCrCb for balanced color enhancement

6. RGB Channel Visualization:
   - Isolates Red, Green, and Blue channels for analysis

The app also plots histograms of original and processed outputs to help understand intensity redistribution after each transformation.

## Academic and Practical Uses
This code is useful for:
- Understanding contrast enhancement fundamentals in DIP labs
- Visual comparison between global and local histogram equalization
- Studying over-enhancement control using CLAHE parameters
- Preprocessing low-contrast images for downstream computer vision tasks
- Demonstrating histogram behavior (PDF/CDF) for classroom presentation and viva

## Requirements
Install the following Python packages:
- opencv-python
- numpy
- pillow
- matplotlib

## Run Instructions
1. Open terminal in this folder.
2. Install dependencies:
   ```bash
   pip install opencv-python numpy pillow matplotlib
   ```
3. Run the application:
   ```bash
   python hist_eq_code.py
   ```

## Learning Outcomes
By using this project, students can:
- Interpret how histogram equalization changes image intensity distributions
- Compare global and adaptive methods in terms of detail visibility
- Understand why luminance-channel processing preserves color quality better
- Tune CLAHE parameters for controlled enhancement

---
Prepared for Digital Image Processing Lab coursework.