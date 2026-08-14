# Basics of Image Processing

This lab covers the fundamentals of digital image representation and basic manipulations using MATLAB.

## Theory & Concepts

### 1. Image Representation in Digital Systems
A digital image is represented as a multidimensional matrix where each element corresponds to a pixel's intensity:
- **Grayscale Images:** Represented as a 2D matrix $M \times N$, where each cell contains a single intensity value (typically $0$ for black to $255$ for white in a standard 8-bit image).
- **RGB Color Images:** Represented as a 3D matrix $M \times N \times 3$, where the third dimension corresponds to the three primary color channels:
  1. Red Channel
  2. Green Channel
  3. Blue Channel

### 2. RGB to Grayscale Conversion
Conversion of a color image to grayscale is achieved by calculating a weighted sum of the R, G, and B channels. The weights reflect human perception of brightness (luminance-weighted):
$$Y = 0.2989 \cdot R + 0.5870 \cdot G + 0.1140 \cdot B$$

### 3. Color Channel Isolation
To isolate a single primary color channel (e.g., Red) in a color representation, the other two color channels (Green and Blue) are zeroed out while keeping the target channel intact.

---

## Code Overview

The script [`basics_of_image_processing.m`](basics_of_image_processing.m) performs the following tasks:
1. **Load and Display Image:** Reads `sample_img.png`, displays it, and prints its size and class type.
2. **Convert to Grayscale:** Converts the RGB image to a grayscale representation using `rgb2gray`.
3. **Channel Extraction:** Isolates individual Red, Green, and Blue color channels by zeroing out the non-target channels.

---

## File Structure

| File Name | Description |
| :--- | :--- |
| [`basics_of_image_processing.m`](basics_of_image_processing.m) | Main MATLAB execution script |
| [`sample_img.png`](sample_img.png) | Input test image |
| [`gray_scale.png`](gray_scale.png) | Output: Grayscale converted image |
| [`red_channel.png`](red_channel.png) | Output: Isolated Red channel image |
| [`green_channel.png`](green_channel.png) | Output: Isolated Green channel image |
| [`blue_channel.png`](blue_channel.png) | Output: Isolated Blue channel image |

---

## How to Run

1. Open MATLAB.
2. Navigate to this directory:
   ```matlab
   cd('basics_dip/Basics_of_image_processing')
   ```
3. Run the script:
   ```matlab
   basics_of_image_processing
   ```
