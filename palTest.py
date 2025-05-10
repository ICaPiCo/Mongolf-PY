from PIL import Image
import numpy as np
import os

# Define Pyxel palette (RGB)
pyxel_palette = [
    (0, 0, 0), (43, 51, 95), (126, 32, 114), (25, 149, 156),
    (139, 72, 82), (57, 92, 152), (169, 193, 255), (238, 238, 238),
    (212, 24, 108), (211, 132, 65), (233, 195, 91), (112, 198, 169),
    (118, 150, 222), (163, 163, 163), (255, 151, 152), (237, 199, 176)
]

def rgb_to_lab(rgb):
    """Convert RGB to LAB color space for better perceptual matching"""
    r, g, b = rgb
    
    # Normalize RGB values
    r /= 255
    g /= 255
    b /= 255
    
    # Convert to XYZ
    r = ((r > 0.04045) and ((r + 0.055) / 1.055) ** 2.4) or (r / 12.92)
    g = ((g > 0.04045) and ((g + 0.055) / 1.055) ** 2.4) or (g / 12.92)
    b = ((b > 0.04045) and ((b + 0.055) / 1.055) ** 2.4) or (b / 12.92)
    
    x = (r * 0.4124 + g * 0.3576 + b * 0.1805) * 100
    y = (r * 0.2126 + g * 0.7152 + b * 0.0722) * 100
    z = (r * 0.0193 + g * 0.1192 + b * 0.9505) * 100
    
    # Convert XYZ to Lab
    x /= 95.047
    y /= 100.0
    z /= 108.883
    
    x = ((x > 0.008856) and x ** (1/3)) or (7.787 * x + 16/116)
    y = ((y > 0.008856) and y ** (1/3)) or (7.787 * y + 16/116)
    z = ((z > 0.008856) and z ** (1/3)) or (7.787 * z + 16/116)
    
    L = (116 * y) - 16
    a = 500 * (x - y)
    b = 200 * (y - z)
    
    return (L, a, b)

def color_distance(rgb1, rgb2):
    """Calculate perceptual color distance using LAB color space"""
    # Convert to LAB color space
    lab1 = rgb_to_lab(rgb1)
    lab2 = rgb_to_lab(rgb2)
    
    # Calculate Euclidean distance in LAB space
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2
    
    deltaL = L1 - L2
    deltaA = a1 - a2
    deltaB = b1 - b2
    
    # Weight factors to better represent human perception
    # L channel (lightness) is weighted more heavily
    return np.sqrt((2 * deltaL**2) + deltaA**2 + deltaB**2)

def closest_color(rgb):
    """Find the closest color in the palette using perceptual color distance"""
    # Don't calculate for exact matches (optimization)
    if rgb in pyxel_palette:
        return rgb
        
    return min(pyxel_palette, key=lambda palette_color: color_distance(rgb, palette_color))

def apply_no_dithering(image_path, output_path):
    """Convert image using perceptual color matching without dithering"""
    img = Image.open(image_path).convert("RGB")
    width, height = img.size
    
    img_array = np.array(img)
    result_array = np.zeros_like(img_array)
    
    for y in range(height):
        for x in range(width):
            old_pixel = img_array[y, x]
            result_array[y, x] = closest_color(tuple(old_pixel))
    
    result_img = Image.fromarray(result_array.astype('uint8'), 'RGB')
    result_img.save(output_path)
    print(f"No dithering image saved to {output_path}")

def apply_floyd_steinberg(image_path, output_path, dither_strength=1.0):
    """Apply Floyd-Steinberg dithering with adjustable strength"""
    img = Image.open(image_path).convert("RGB")
    width, height = img.size
    
    img_array = np.array(img).astype(np.float64)
    result_array = np.zeros_like(img_array)
    
    for y in range(height):
        for x in range(width):
            old_pixel = img_array[y, x].copy()
            new_pixel = closest_color(tuple(old_pixel.astype(int)))
            result_array[y, x] = new_pixel
            
            quant_error = old_pixel - np.array(new_pixel)
            quant_error *= dither_strength  # Adjust dithering strength
            
            # Distribute the error to neighboring pixels
            if x + 1 < width:
                img_array[y, x + 1] = np.clip(img_array[y, x + 1] + quant_error * 7/16, 0, 255)
            if x - 1 >= 0 and y + 1 < height:
                img_array[y + 1, x - 1] = np.clip(img_array[y + 1, x - 1] + quant_error * 3/16, 0, 255)
            if y + 1 < height:
                img_array[y + 1, x] = np.clip(img_array[y + 1, x] + quant_error * 5/16, 0, 255)
            if x + 1 < width and y + 1 < height:
                img_array[y + 1, x + 1] = np.clip(img_array[y + 1, x + 1] + quant_error * 1/16, 0, 255)
    
    result_img = Image.fromarray(result_array.astype('uint8'), 'RGB')
    result_img.save(output_path)
    print(f"Floyd-Steinberg (strength {dither_strength}) saved to {output_path}")

def apply_ordered_dithering(image_path, output_path, matrix_size=4, dither_strength=1.0):
    """Apply ordered dithering with adjustable strength"""
    img = Image.open(image_path).convert("RGB")
    width, height = img.size
    
    # Define dither matrices (Bayer matrices)
    if matrix_size == 2:
        dither_matrix = np.array([[0, 2], [3, 1]]) / 4.0
    elif matrix_size == 4:
        dither_matrix = np.array([
            [0, 8, 2, 10],
            [12, 4, 14, 6],
            [3, 11, 1, 9],
            [15, 7, 13, 5]
        ]) / 16.0
    elif matrix_size == 8:
        dither_matrix = np.array([
            [0, 32, 8, 40, 2, 34, 10, 42],
            [48, 16, 56, 24, 50, 18, 58, 26],
            [12, 44, 4, 36, 14, 46, 6, 38],
            [60, 28, 52, 20, 62, 30, 54, 22],
            [3, 35, 11, 43, 1, 33, 9, 41],
            [51, 19, 59, 27, 49, 17, 57, 25],
            [15, 47, 7, 39, 13, 45, 5, 37],
            [63, 31, 55, 23, 61, 29, 53, 21]
        ]) / 64.0
    else:
        raise ValueError("matrix_size must be 2, 4, or 8")
    
    img_array = np.array(img)
    result_array = np.zeros_like(img_array)
    
    for y in range(height):
        for x in range(width):
            # Get original pixel value
            old_pixel = img_array[y, x].astype(np.float64)
            
            # Get threshold from dither matrix
            threshold = dither_matrix[y % matrix_size, x % matrix_size]
            
            # Adjust threshold based on dither strength
            adjusted_threshold = 0.5 + (threshold - 0.5) * dither_strength
            
            # Find closest colors for comparison
            closest_colors = []
            for channel in range(3):  # R, G, B
                palette_values = [c[channel] for c in pyxel_palette]
                palette_values = sorted(set(palette_values))
                
                value = old_pixel[channel]
                
                # Find the lower and upper bounds
                lower = max([v for v in palette_values if v <= value], default=0)
                upper = min([v for v in palette_values if v >= value], default=255)
                
                if lower == upper:
                    closest_colors.append(lower)
                else:
                    # Apply dithering decision
                    normalized_pos = (value - lower) / (upper - lower) if upper != lower else 0
                    closest_colors.append(upper if normalized_pos > adjusted_threshold else lower)
            
            # Find the closest color in the palette to our dithered RGB value
            result_array[y, x] = closest_color(tuple(closest_colors))
    
    result_img = Image.fromarray(result_array.astype('uint8'), 'RGB')
    result_img.save(output_path)
    print(f"Ordered dithering (matrix size {matrix_size}, strength {dither_strength}) saved to {output_path}")

def apply_blue_noise_dithering(image_path, output_path, dither_strength=1.0):
    """Apply blue noise dithering with adjustable strength"""
    img = Image.open(image_path).convert("RGB")
    width, height = img.size
    
    # Create blue noise pattern (approximation)
    np.random.seed(42)  # For reproducibility
    noise = np.random.rand(height, width)
    
    # Blur the noise to make it more "blue"
    from scipy.ndimage import gaussian_filter
    noise = gaussian_filter(noise, sigma=1.0)
    
    # Normalize the noise
    noise = (noise - noise.min()) / (noise.max() - noise.min())
    
    img_array = np.array(img)
    result_array = np.zeros_like(img_array)
    
    for y in range(height):
        for x in range(width):
            # Get original pixel value
            old_pixel = img_array[y, x].astype(np.float64)
            
            # Get threshold from blue noise
            threshold = noise[y, x]
            
            # Adjust threshold based on dither strength
            adjusted_threshold = 0.5 + (threshold - 0.5) * dither_strength
            
            # Find closest colors for comparison
            closest_colors = []
            for channel in range(3):  # R, G, B
                palette_values = [c[channel] for c in pyxel_palette]
                palette_values = sorted(set(palette_values))
                
                value = old_pixel[channel]
                
                # Find the lower and upper bounds
                lower = max([v for v in palette_values if v <= value], default=0)
                upper = min([v for v in palette_values if v >= value], default=255)
                
                if lower == upper:
                    closest_colors.append(lower)
                else:
                    # Apply dithering decision
                    normalized_pos = (value - lower) / (upper - lower) if upper != lower else 0
                    closest_colors.append(upper if normalized_pos > adjusted_threshold else lower)
            
            # Find the closest color in the palette to our dithered RGB value
            result_array[y, x] = closest_color(tuple(closest_colors))
    
    result_img = Image.fromarray(result_array.astype('uint8'), 'RGB')
    result_img.save(output_path)
    print(f"Blue noise dithering (strength {dither_strength}) saved to {output_path}")

def apply_pattern_dithering(image_path, output_path, dither_strength=1.0):
    """Apply pattern dithering with adjustable strength"""
    img = Image.open(image_path).convert("RGB")
    width, height = img.size
    
    # Define a pattern dither matrix (8x8)
    pattern = np.array([
        [24, 10, 12, 26, 35, 47, 49, 37],
        [8, 0, 2, 14, 45, 59, 61, 51],
        [22, 6, 4, 16, 43, 57, 63, 53],
        [30, 20, 18, 28, 33, 41, 55, 39],
        [34, 46, 48, 36, 25, 11, 13, 27],
        [44, 58, 60, 50, 9, 1, 3, 15],
        [42, 56, 62, 52, 23, 7, 5, 17],
        [32, 40, 54, 38, 31, 21, 19, 29]
    ]) / 64.0
    
    img_array = np.array(img)
    result_array = np.zeros_like(img_array)
    
    for y in range(height):
        for x in range(width):
            # Get original pixel value
            old_pixel = img_array[y, x].astype(np.float64)
            
            # Get threshold from pattern
            threshold = pattern[y % 8, x % 8]
            
            # Adjust threshold based on dither strength
            adjusted_threshold = 0.5 + (threshold - 0.5) * dither_strength
            
            # Find closest colors for comparison
            closest_colors = []
            for channel in range(3):  # R, G, B
                palette_values = [c[channel] for c in pyxel_palette]
                palette_values = sorted(set(palette_values))
                
                value = old_pixel[channel]
                
                # Find the lower and upper bounds
                lower = max([v for v in palette_values if v <= value], default=0)
                upper = min([v for v in palette_values if v >= value], default=255)
                
                if lower == upper:
                    closest_colors.append(lower)
                else:
                    # Apply dithering decision
                    normalized_pos = (value - lower) / (upper - lower) if upper != lower else 0
                    closest_colors.append(upper if normalized_pos > adjusted_threshold else lower)
            
            # Find the closest color in the palette to our dithered RGB value
            result_array[y, x] = closest_color(tuple(closest_colors))
    
    result_img = Image.fromarray(result_array.astype('uint8'), 'RGB')
    result_img.save(output_path)
    print(f"Pattern dithering (strength {dither_strength}) saved to {output_path}")

def apply_color_dithering(image_path, output_path, dither_strength=1.0):
    """Apply color-preserving dithering with adjustable strength"""
    # This method tries to keep colors close to original while still dithering
    img = Image.open(image_path).convert("RGB")
    width, height = img.size
    
    img_array = np.array(img).astype(np.float64)
    result_array = np.zeros_like(img_array)
    
    # Pre-compute the closest colors for each unique RGB combination
    # This is an optimization to avoid recomputing for identical pixels
    color_cache = {}
    
    for y in range(height):
        for x in range(width):
            old_pixel = tuple(img_array[y, x].astype(int))
            
            # Use cache for performance
            if old_pixel in color_cache:
                new_pixel = color_cache[old_pixel]
            else:
                new_pixel = closest_color(old_pixel)
                color_cache[old_pixel] = new_pixel
                
            result_array[y, x] = new_pixel
            
            # Calculate error with reduced strength
            quant_error = (img_array[y, x] - np.array(new_pixel)) * dither_strength
            
            # Use a modified error diffusion pattern that spreads less aggressively
            if x + 1 < width:
                img_array[y, x + 1] = np.clip(img_array[y, x + 1] + quant_error * 5/16, 0, 255)
            if x - 1 >= 0 and y + 1 < height:
                img_array[y + 1, x - 1] = np.clip(img_array[y + 1, x - 1] + quant_error * 1/16, 0, 255)
            if y + 1 < height:
                img_array[y + 1, x] = np.clip(img_array[y + 1, x] + quant_error * 3/16, 0, 255)
            if x + 1 < width and y + 1 < height:
                img_array[y + 1, x + 1] = np.clip(img_array[y + 1, x + 1] + quant_error * 1/16, 0, 255)
    
    result_img = Image.fromarray(result_array.astype('uint8'), 'RGB')
    result_img.save(output_path)
    print(f"Color-preserving dithering (strength {dither_strength}) saved to {output_path}")

def apply_pyxel_palette(image_path, output_dir="output"):
    """Generate multiple versions with different dithering methods and strengths"""
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get filename without extension
    base_filename = os.path.splitext(os.path.basename(image_path))[0]
    
    # No dithering (just perceptual color matching)
    apply_no_dithering(
        image_path, 
        f"{output_dir}/{base_filename}_no_dither.png"
    )
    
    # Floyd-Steinberg dithering with different strengths
    for strength in [0.2, 0.4, 0.6, 0.8, 1.0]:
        apply_floyd_steinberg(
            image_path, 
            f"{output_dir}/{base_filename}_floyd_{int(strength*100)}.png",
            dither_strength=strength
        )
    
    # Ordered dithering with different matrix sizes and strengths
    for size in [2, 4, 8]:
        for strength in [0.4, 0.8]:
            apply_ordered_dithering(
                image_path, 
                f"{output_dir}/{base_filename}_ordered_m{size}_s{int(strength*100)}.png",
                matrix_size=size,
                dither_strength=strength
            )
    
    # Pattern dithering with different strengths
    for strength in [0.3, 0.6, 0.9]:
        apply_pattern_dithering(
            image_path, 
            f"{output_dir}/{base_filename}_pattern_{int(strength*100)}.png",
            dither_strength=strength
        )
    
    # Color-preserving dithering with different strengths
    for strength in [0.3, 0.6, 0.9]:
        apply_color_dithering(
            image_path, 
            f"{output_dir}/{base_filename}_color_dither_{int(strength*100)}.png",
            dither_strength=strength
        )
    
    # Blue noise dithering (if scipy available)
    try:
        for strength in [0.5, 1.0]:
            apply_blue_noise_dithering(
                image_path, 
                f"{output_dir}/{base_filename}_blue_noise_{int(strength*100)}.png",
                dither_strength=strength
            )
    except ImportError:
        print("SciPy not available, skipping blue noise dithering")

# Example usage
if __name__ == "__main__":
    input_file = "input.png"
    
    # Generate multiple versions with different dithering methods and strengths
    apply_pyxel_palette(input_file)
    
    print("\nGenerated multiple versions with different dithering methods and strengths.")
    print("Check the 'output' directory for all the generated images.")
    print("Find the one that looks best for your needs!")