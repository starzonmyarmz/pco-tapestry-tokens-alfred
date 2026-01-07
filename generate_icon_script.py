#!/usr/bin/env python3
import json
import re
import os
from PIL import Image, ImageDraw

def parse_hsl(hsl_str):
    """Parse HSL/HSLA string to RGB"""
    match = re.search(r'hsla?\((\d+),\s*(\d+)%,\s*(\d+)%(?:,\s*([\d.]+))?\)', hsl_str)
    if not match:
        return None
    
    h, s, l = int(match.group(1)), int(match.group(2)), int(match.group(3))
    a = float(match.group(4)) if match.group(4) else 1.0
    
    # Convert HSL to RGB
    h = h / 360.0
    s = s / 100.0
    l = l / 100.0
    
    if s == 0:
        r = g = b = l
    else:
        def hue_to_rgb(p, q, t):
            if t < 0: t += 1
            if t > 1: t -= 1
            if t < 1/6: return p + (q - p) * 6 * t
            if t < 1/2: return q
            if t < 2/3: return p + (q - p) * (2/3 - t) * 6
            return p
        
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)
    
    return (int(r * 255), int(g * 255), int(b * 255), int(a * 255))

def create_gradient_image(gradient_str, size=(64, 64)):
    """Create a gradient image from linear-gradient CSS"""
    img = Image.new('RGBA', size, (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Extract all HSL colors from the gradient
    colors = re.findall(r'hsl\([^)]+\)', gradient_str)
    if not colors:
        return img
    
    # Parse colors
    parsed_colors = []
    for color in colors:
        rgba = parse_hsl(color)
        if rgba:
            parsed_colors.append(rgba)
    
    if len(parsed_colors) == 0:
        return img
    
    # Create horizontal gradient
    for x in range(size[0]):
        progress = x / (size[0] - 1)
        color_idx = progress * (len(parsed_colors) - 1)
        idx1 = int(color_idx)
        idx2 = min(idx1 + 1, len(parsed_colors) - 1)
        blend = color_idx - idx1
        
        c1 = parsed_colors[idx1]
        c2 = parsed_colors[idx2]
        
        r = int(c1[0] * (1 - blend) + c2[0] * blend)
        g = int(c1[1] * (1 - blend) + c2[1] * blend)
        b = int(c1[2] * (1 - blend) + c2[2] * blend)
        a = int(c1[3] * (1 - blend) + c2[3] * blend)
        
        draw.line([(x, 0), (x, size[1])], fill=(r, g, b, a))
    
    return img

def create_solid_image(rgba, size=(64, 64)):
    """Create a solid color image"""
    img = Image.new('RGBA', size, rgba)
    return img

# Load tokens from current directory
with open('tokens.json', 'r') as f:
    tokens = json.load(f)

# Create images directory if it doesn't exist
os.makedirs('images', exist_ok=True)

# Generate icons for all color tokens
count = 0
for name, value in tokens.items():
    if not value.startswith(('hsl(', 'hsla(', 'linear-gradient(')):
        continue
    
    # Create safe filename
    safe_name = re.sub(r'[^a-zA-Z0-9-]', '_', name)
    icon_path = os.path.join('images', f"{safe_name}.png")
    
    try:
        if value.startswith('linear-gradient('):
            img = create_gradient_image(value)
        else:
            rgba = parse_hsl(value)
            if rgba:
                img = create_solid_image(rgba)
            else:
                continue
        
        img.save(icon_path, 'PNG')
        count += 1
        if count % 50 == 0:
            print(f"Generated {count} icons...")
    except Exception as e:
        print(f"Error generating {name}: {e}")

print(f"\nTotal icons generated: {count}")
