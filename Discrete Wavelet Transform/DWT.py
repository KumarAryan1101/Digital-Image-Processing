import numpy as np
from PIL import Image
import os
import argparse

def haar_2d(img):
    img = img.astype(float)
    h, w = img.shape
    pad_h = h % 2
    pad_w = w % 2
    if pad_h or pad_w:
        img = np.pad(img, ((0, pad_h), (0, pad_w)), mode='edge')
    
    L_rows = (img[0::2, :] + img[1::2, :]) / 2.0
    H_rows = (img[0::2, :] - img[1::2, :]) / 2.0
    
    LL = (L_rows[:, 0::2] + L_rows[:, 1::2]) / 2.0
    LH = (L_rows[:, 0::2] - L_rows[:, 1::2]) / 2.0
    HL = (H_rows[:, 0::2] + H_rows[:, 1::2]) / 2.0
    HH = (H_rows[:, 0::2] - H_rows[:, 1::2]) / 2.0
    
    return LL, LH, HL, HH, (h, w)

def ihaar_2d(LL, LH, HL, HH, orig_shape):
    H_half, W_half = LL.shape
    
    L_rows = np.empty((H_half, W_half*2))
    L_rows[:, 0::2] = LL + LH
    L_rows[:, 1::2] = LL - LH
    
    H_rows = np.empty((H_half, W_half*2))
    H_rows[:, 0::2] = HL + HH
    H_rows[:, 1::2] = HL - HH
    
    img = np.empty((H_half*2, W_half*2))
    img[0::2, :] = L_rows + H_rows
    img[1::2, :] = L_rows - H_rows
    
    h, w = orig_shape
    return img[:h, :w]

def normalize_detail(detail):
    # Scale to 0-255 for visualization
    return np.clip(detail + 128, 0, 255).astype(np.uint8)

def process_dwt(input_path, output_dir="Output"):
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Load image and convert to grayscale
    img = Image.open(input_path).convert('L')
    img_np = np.array(img)
    img.save(os.path.join(output_dir, "dwt_original_grey.png"))
    
    # 2. Level 1 DWT
    LL, LH, HL, HH, orig_shape1 = haar_2d(img_np)
    
    # Save individual subbands
    Image.fromarray(LL.astype(np.uint8)).save(os.path.join(output_dir, "dwt_LL_approximation.png"))
    Image.fromarray(normalize_detail(LH)).save(os.path.join(output_dir, "dwt_LH_horizontal.png"))
    Image.fromarray(normalize_detail(HL)).save(os.path.join(output_dir, "dwt_HL_vertical.png"))
    Image.fromarray(normalize_detail(HH)).save(os.path.join(output_dir, "dwt_HH_diagonal.png"))
    
    # Level 1 mosaic
    h_half, w_half = LL.shape
    mosaic_1 = np.zeros((h_half*2, w_half*2), dtype=np.uint8)
    mosaic_1[0:h_half, 0:w_half] = LL.astype(np.uint8)
    mosaic_1[0:h_half, w_half:] = normalize_detail(LH)
    mosaic_1[h_half:, 0:w_half] = normalize_detail(HL)
    mosaic_1[h_half:, w_half:] = normalize_detail(HH)
    
    # Crop mosaic to the original padded dimension if it was padded
    # But mosaic_1 matches the padded dimension exactly
    mosaic_1_cropped = mosaic_1[:orig_shape1[0], :orig_shape1[1]]
    Image.fromarray(mosaic_1_cropped).save(os.path.join(output_dir, "dwt_subbands_1level.png"))
    
    # 3. Level 2 DWT
    LL2, LH2, HL2, HH2, orig_shape2 = haar_2d(LL)
    h_half2, w_half2 = LL2.shape
    
    mosaic_2_inner = np.zeros((h_half2*2, w_half2*2), dtype=np.uint8)
    mosaic_2_inner[0:h_half2, 0:w_half2] = LL2.astype(np.uint8)
    mosaic_2_inner[0:h_half2, w_half2:] = normalize_detail(LH2)
    mosaic_2_inner[h_half2:, 0:w_half2] = normalize_detail(HL2)
    mosaic_2_inner[h_half2:, w_half2:] = normalize_detail(HH2)
    
    # Level 2 mosaic
    mosaic_2 = mosaic_1.copy()
    h_ll, w_ll = orig_shape2
    mosaic_2[0:h_ll, 0:w_ll] = mosaic_2_inner[:h_ll, :w_ll]
    mosaic_2_cropped = mosaic_2[:orig_shape1[0], :orig_shape1[1]]
    Image.fromarray(mosaic_2_cropped).save(os.path.join(output_dir, "dwt_subbands_2level.png"))
    
    # 4. Reconstruct and check error
    LL_recon = ihaar_2d(LL2, LH2, HL2, HH2, orig_shape2)
    img_recon = ihaar_2d(LL_recon, LH, HL, HH, orig_shape1)
    
    mse = np.mean((img_np - img_recon)**2)
    print(f"Reconstruction MSE: {mse}")
    
    img_recon_clipped = np.clip(img_recon, 0, 255).astype(np.uint8)
    Image.fromarray(img_recon_clipped).save(os.path.join(output_dir, "dwt_reconstructed.png"))
    
    # 5. Complete comparison overview
    # All resized to same height (original height)
    h, w = orig_shape1
    
    def resize_to_h(img_arr, target_h):
        im = Image.fromarray(img_arr)
        target_w = int(im.width * (target_h / im.height))
        return np.array(im.resize((target_w, target_h)))
        
    m1_r = resize_to_h(mosaic_1_cropped, h)
    m2_r = resize_to_h(mosaic_2_cropped, h)
    
    overview = np.hstack((img_np, m1_r, m2_r, img_recon_clipped))
    Image.fromarray(overview).save(os.path.join(output_dir, "dwt_comparison_overview.png"))
    
    return mse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True, help="Path to input image")
    args = parser.parse_args()
    process_dwt(args.input)
