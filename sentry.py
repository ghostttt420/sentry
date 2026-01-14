import requests
import os
import datetime
from PIL import Image, ImageChops, ImageEnhance

# --- CONFIGURATION: TARGET ---
# Currently set to: Lagos Island / Lekki Axis
# Change this BBOX to track any square on Earth.
MIN_LON, MIN_LAT = 3.35, 6.40
MAX_LON, MAX_LAT = 3.55, 6.60

# --- NASA LAYERS ---
LAYERS = {
    "day": "MODIS_Terra_CorrectedReflectance_TrueColor",  # Physical Terrain
    "night": "VIIRS_SNPP_DayNightBand_ENCC"               # Human Activity/Lights
}

WMS_URL = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"

def fetch_layer(layer_name, layer_id, date_str):
    filename = f"{layer_name}_latest.png"
    print(f"🛰️ Fetching {layer_name.upper()} data for {date_str}...")
    
    params = {
        "SERVICE": "WMS", "VERSION": "1.1.1", "REQUEST": "GetMap",
        "LAYERS": layer_id, "FORMAT": "image/png", "TRANSPARENT": "true",
        "SRS": "EPSG:4326",
        "BBOX": f"{MIN_LON},{MIN_LAT},{MAX_LON},{MAX_LAT}",
        "WIDTH": "1024", "HEIGHT": "1024", 
        "TIME": date_str
    }
    
    try:
        r = requests.get(WMS_URL, params=params, timeout=30)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(r.content)
            return True
    except Exception as e:
        print(f"Error fetching {layer_name}: {e}")
    return False

def process_visuals(mode):
    """
    Compares 'latest.png' vs 'reference.png' for a specific mode (day/night)
    Returns: The 'Difference' image path.
    """
    latest = f"{mode}_latest.png"
    ref = f"{mode}_ref.png"
    diff_file = f"{mode}_diff.png"

    # 1. Check if we have data
    if not os.path.exists(latest):
        return None

    # 2. Establish Reference
    if not os.path.exists(ref):
        print(f"Creating baseline for {mode}...")
        img = Image.open(latest).convert("RGB")
        img.save(ref)
        return None # No diff possible on first run

    # 3. Calculate Change (The "Spy" Logic)
    img_now = Image.open(latest).convert("RGB")
    img_ref = Image.open(ref).convert("RGB")
    
    # Compute mathematical difference
    diff = ImageChops.difference(img_ref, img_now)
    
    # Boost visibility of changes (Night needs more boost than Day)
    boost = 7.0 if mode == "night" else 3.0
    enhancer = ImageEnhance.Brightness(diff)
    diff_visible = enhancer.enhance(boost)
    
    diff_visible.save(diff_file)
    return diff_file

def update_dashboard(date_str):
    markdown = f"""
# 👁️ The All-Seeing Sentry
**Target Coordinates:** {MIN_LAT}, {MIN_LON} | **Scan Date:** {date_str}

## ☀️ Daylight Surveillance (Physical Reality)
Tracks construction, deforestation, and coastline changes.
| Current View | Change Detection (Red = Altered) |
| :---: | :---: |
| ![Day View](day_latest.png) | ![Day Diff](day_diff.png) |

## 🌙 Night Surveillance (Human Activity)
Tracks power outages, urban expansion, and industrial activity.
| Current View | Change Detection (White = Light Change) |
| :---: | :---: |
| ![Night View](night_latest.png) | ![Night Diff](night_diff.png) |

---
*Powered by GitHub Actions & NASA GIBS*
    """
    with open("README.md", "w") as f:
        f.write(markdown)

def main():
    today = datetime.datetime.utcnow()
    date_str = today.strftime("%Y-%m-%d")
    
    # 1. Fetch Data
    for mode, layer_id in LAYERS.items():
        fetch_layer(mode, layer_id, date_str)
        
    # 2. Process Intelligence
    for mode in LAYERS.keys():
        process_visuals(mode)
        
    # 3. Publish Report
    update_dashboard(date_str)

if __name__ == "__main__":
    main()
