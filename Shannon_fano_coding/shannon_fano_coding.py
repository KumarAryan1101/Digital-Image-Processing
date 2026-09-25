import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import argparse
from collections import Counter
import matplotlib.pyplot as plt

class Node:
    def __init__(self, symbol=None):
        self.symbol = symbol
        self.left = None
        self.right = None

def build_shannon_fano_tree(probs_list):
    if len(probs_list) == 1:
        return Node(symbol=probs_list[0][0])
    
    total = sum(p for s, p in probs_list)
    min_diff = float('inf')
    split_idx = 1
    current_sum = 0
    
    for i in range(len(probs_list) - 1):
        current_sum += probs_list[i][1]
        diff = abs(total - 2 * current_sum)
        if diff < min_diff:
            min_diff = diff
            split_idx = i + 1
            
    left_list = probs_list[:split_idx]
    right_list = probs_list[split_idx:]
    
    node = Node()
    if len(left_list) > 0:
        node.left = build_shannon_fano_tree(left_list)
    if len(right_list) > 0:
        node.right = build_shannon_fano_tree(right_list)
    
    return node

def generate_codes(node, prefix="", codebook=None):
    if codebook is None:
        codebook = {}
    if node is not None:
        if node.symbol is not None:
            codebook[node.symbol] = prefix
        generate_codes(node.left, prefix + "0", codebook)
        generate_codes(node.right, prefix + "1", codebook)
    return codebook

def encode_image(img_array, codebook):
    flat = img_array.flatten()
    encoded = "".join([codebook[px] for px in flat])
    return encoded

def decode_image(encoded, root, shape):
    decoded = []
    current = root
    for bit in encoded:
        if bit == "0":
            current = current.left
        else:
            current = current.right
            
        if current.symbol is not None:
            decoded.append(current.symbol)
            current = root
            
    return np.array(decoded, dtype=np.uint8).reshape(shape)

def process_shannon_fano(input_path, output_dir="Output"):
    os.makedirs(output_dir, exist_ok=True)
    
    # Load image
    img = Image.open(input_path).convert('L')
    img_np = np.array(img)
    img.save(os.path.join(output_dir, "shannon_fano_original_grey.png"))
    
    total_pixels = img_np.size
    counts = Counter(img_np.flatten())
    probs = {sym: count / total_pixels for sym, count in counts.items()}
    
    sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
    
    root = build_shannon_fano_tree(sorted_probs)
    codebook = generate_codes(root, "", {})
    
    # Entropy
    entropy = -sum(p * np.log2(p) for p in probs.values())
    
    # Average code length
    avg_len = sum(probs[sym] * len(code) for sym, code in codebook.items())
    
    # Efficiency
    efficiency = entropy / avg_len if avg_len > 0 else 0
    
    # Compression ratio
    comp_ratio = 8.0 / avg_len if avg_len > 0 else 0
    
    # Space saving
    space_saving = 1.0 - (avg_len / 8.0)
    
    # Encode and Decode
    encoded = encode_image(img_np, codebook)
    decoded_np = decode_image(encoded, root, img_np.shape)
    Image.fromarray(decoded_np).save(os.path.join(output_dir, "shannon_fano_decoded.png"))
    
    is_lossless = np.array_equal(img_np, decoded_np)
    
    # Bit-length map
    length_map = np.vectorize(lambda px: len(codebook[px]))(img_np)
    min_len = length_map.min()
    max_len = length_map.max()
    if max_len > min_len:
        norm_map = (length_map - min_len) / (max_len - min_len) * 255.0
    else:
        norm_map = np.zeros_like(length_map)
    Image.fromarray(norm_map.astype(np.uint8)).save(os.path.join(output_dir, "shannon_fano_bit_length_map.png"))
    
    # Length distribution (Bar chart)
    lengths = [len(code) for code in codebook.values()]
    plt.figure(figsize=(8, 6))
    plt.hist(lengths, bins=range(min(lengths), max(lengths) + 2), align='left', rwidth=0.8, color='lightgreen', edgecolor='black')
    plt.title('Shannon-Fano Codeword Length Distribution')
    plt.xlabel('Length in bits')
    plt.ylabel('Frequency (Number of symbols)')
    plt.grid(axis='y', alpha=0.75)
    plt.savefig(os.path.join(output_dir, "shannon_fano_length_distribution.png"))
    plt.close()
    
    # Metrics summary image
    summary_img = Image.new('RGB', (600, 300), color=(255, 255, 255))
    draw = ImageDraw.Draw(summary_img)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        title_font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
        
    y_offset = 20
    draw.text((20, y_offset), "Shannon-Fano Coding Metrics", fill=(0,0,0), font=title_font)
    y_offset += 40
    
    lines = [
        f"Lossless Verification: {'PASSED' if is_lossless else 'FAILED'}",
        f"Shannon Entropy (H): {entropy:.4f} bits/symbol",
        f"Average Code Length (L): {avg_len:.4f} bits/symbol",
        f"Coding Efficiency (η): {efficiency:.4%} (H/L)",
        f"Compression Ratio: {comp_ratio:.4f}:1 (8/L)",
        f"Theoretical Space Savings: {space_saving:.2%} (1 - L/8)"
    ]
    
    for line in lines:
        draw.text((20, y_offset), line, fill=(0,0,0), font=font)
        y_offset += 35
        
    summary_img.save(os.path.join(output_dir, "shannon_fano_metrics_summary.png"))
    
    return {
        "entropy": entropy,
        "avg_len": avg_len,
        "efficiency": efficiency,
        "comp_ratio": comp_ratio,
        "space_saving": space_saving,
        "is_lossless": is_lossless
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="Path to input image")
    args = parser.parse_args()
    process_shannon_fano(args.input)
