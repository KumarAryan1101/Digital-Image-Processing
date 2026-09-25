import numpy as np
from PIL import Image, ImageDraw, ImageFont
import heapq
import os
import argparse
from collections import Counter
import matplotlib.pyplot as plt

class Node:
    def __init__(self, prob, symbol, left=None, right=None):
        self.prob = prob
        self.symbol = symbol
        self.left = left
        self.right = right
        
    def __lt__(self, other):
        return self.prob < other.prob

def build_huffman_tree(probs):
    heap = [Node(p, sym) for sym, p in probs.items() if p > 0]
    heapq.heapify(heap)
    
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        parent = Node(left.prob + right.prob, None, left, right)
        heapq.heappush(heap, parent)
        
    return heap[0] if heap else None

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

def process_huffman(input_path, output_dir="Output"):
    os.makedirs(output_dir, exist_ok=True)
    
    # Load image
    img = Image.open(input_path).convert('L')
    img_np = np.array(img)
    img.save(os.path.join(output_dir, "huffman_original_grey.png"))
    
    total_pixels = img_np.size
    counts = Counter(img_np.flatten())
    probs = {sym: count / total_pixels for sym, count in counts.items()}
    
    root = build_huffman_tree(probs)
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
    Image.fromarray(decoded_np).save(os.path.join(output_dir, "huffman_decoded.png"))
    
    is_lossless = np.array_equal(img_np, decoded_np)
    
    # Bit-length map
    length_map = np.vectorize(lambda px: len(codebook[px]))(img_np)
    # Normalize map to 0-255 for visualization
    min_len = length_map.min()
    max_len = length_map.max()
    if max_len > min_len:
        norm_map = (length_map - min_len) / (max_len - min_len) * 255.0
    else:
        norm_map = np.zeros_like(length_map)
    Image.fromarray(norm_map.astype(np.uint8)).save(os.path.join(output_dir, "huffman_bit_length_map.png"))
    
    # Length distribution (Bar chart using Matplotlib)
    lengths = [len(code) for code in codebook.values()]
    plt.figure(figsize=(8, 6))
    plt.hist(lengths, bins=range(min(lengths), max(lengths) + 2), align='left', rwidth=0.8, color='skyblue', edgecolor='black')
    plt.title('Codeword Length Distribution')
    plt.xlabel('Length in bits')
    plt.ylabel('Frequency (Number of symbols)')
    plt.grid(axis='y', alpha=0.75)
    plt.savefig(os.path.join(output_dir, "huffman_length_distribution.png"))
    plt.close()
    
    # Metrics summary image using Pillow
    summary_img = Image.new('RGB', (600, 300), color=(255, 255, 255))
    draw = ImageDraw.Draw(summary_img)
    # Try to load a font, otherwise use default
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        title_font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
        
    y_offset = 20
    draw.text((20, y_offset), "Huffman Coding Metrics", fill=(0,0,0), font=title_font)
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
        
    summary_img.save(os.path.join(output_dir, "huffman_metrics_summary.png"))
    
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
    process_huffman(args.input)
