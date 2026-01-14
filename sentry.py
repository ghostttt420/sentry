import requests
import os
import datetime
from PIL import Image, ImageEnhance, ImageOps

# --- CONFIGURATION ---
TARGETS = [
    {"name": "LAGOS_HEATMAP", "lat": 6.524, "lon": 3.379, "zoom": 1.0},
    {"name": "NIGER_DELTA_FLARES", "lat": 4.5, "lon": 7.0, "zoom": 1.5} # Wide view for gas flares
]

# NASA LAYERS
LAYERS = {
    "visual": "MODIS_Terra_CorrectedReflectance_TrueColor",
    "thermal": "MODIS_Terra_Thermal_Anomalies_All"  # Predator Vision
}

WMS_URL = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"

# ASCII CHARS (Dark to Light)
ASCII_CHARS = ["@", "%", "#", "*", "+", "=", "-", ":", ".", " "]

def fetch_layer(target, layer_key, layer_name, date_str):
    filename = f"images/{target['name']}_{layer_key}.png"
    
    # Calculate BBOX
    z = target['zoom']
    bbox = f"{target['lon']-z},{target['lat']-z},{target['lon']+z},{target['lat']+z}"
    
    params = {
        "SERVICE": "WMS", "VERSION": "1.1.1", "REQUEST": "GetMap",
        "LAYERS": layer_name, "FORMAT": "image/png", "TRANSPARENT": "true",
        "SRS": "EPSG:4326", "BBOX": bbox, "WIDTH": "400", "HEIGHT": "400", 
        "TIME": date_str
    }
    
    try:
        r = requests.get(WMS_URL, params=params, timeout=20)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(r.content)
            return True
    except:
        pass
    return False

def image_to_ascii(image_path, width=60):
    try:
        img = Image.open(image_path).convert("L") # Grayscale
        
        # Resize to maintain aspect ratio (Text is taller than it is wide)
        aspect_ratio = img.height / img.width
        new_height = int(aspect_ratio * width * 0.55)
        img = img.resize((width, new_height))
        
        pixels = img.getdata()
        
        # Map pixels to ASCII chars
        new_pixels = [ASCII_CHARS[pixel // 25] for pixel in pixels]
        new_pixels = "".join(new_pixels)
        
        # Split string into multiple lines
        ascii_art = "\n".join([new_pixels[index:index + width] for index in range(0, len(new_pixels), width)])
        return ascii_art
    except:
        return "ASCII GENERATION FAILED"

def generate_dashboard(date_str):
    md = f"""
# ☢️ SATELLITE INTERCEPT: {date_str}
**STATUS:** PREDATOR VISION ACTIVE

"""
    for t in TARGETS:
        name = t['name']
        
        # Generate ASCII from the Visual Layer
        ascii_view = image_to_ascii(f"images/{name}_visual.png")
        
        md += f"## TARGET: {name}\n"
        md += "| VISUAL (OPTICAL) | THERMAL (HEAT SIGNATURE) |\n"
        md += "| :---: | :---: |\n"
        md += f"| ![{name}](images/{name}_visual.png) | ![{name}](images/{name}_thermal.png) |\n"
        
        md += "\n### 📟 ENCRYPTED VISUAL FEED (ASCII)\n"
        md += f"```text\n{ascii_view}\n```\n"
        md += "---\n"
        
    with open("README.md", "w") as f:
        f.write(md)

def main():
    if not os.path.exists("images"): os.makedirs("images")
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    print(f"🛰️ INITIALIZING MULTI-SPECTRAL SCAN: {today}")
    
    for t in TARGETS:
        print(f" > Targeting: {t['name']}")
        # 1. Get Visual
        fetch_layer(t, "visual", LAYERS["visual"], today)
        # 2. Get Thermal
        fetch_layer(t, "thermal", LAYERS["thermal"], today)
        
    generate_dashboard(today)

if __name__ == "__main__":
    main()
