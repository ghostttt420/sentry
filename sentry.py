import requests
import os
import datetime
from PIL import Image, ImageChops, ImageEnhance

# --- CONFIGURATION ---
# LAGOS, NIGERIA (Approximate Bounding Box)
MIN_LON, MIN_LAT = 3.20, 6.30
MAX_LON, MAX_LAT = 3.60, 6.70

# NASA WMS API (The Source)
WMS_URL = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"
LAYER = "VIIRS_SNPP_DayNightBand_ENCC" # Enhanced Night Lights

def fetch_satellite_image(date_str, filename):
    print(f"🛰️ Fetching NASA Night Lights for {date_str}...")
    
    # We use WMS (Web Map Service) to get a single PNG for our bounding box
    params = {
        "SERVICE": "WMS",
        "VERSION": "1.1.1",
        "REQUEST": "GetMap",
        "LAYERS": LAYER,
        "FORMAT": "image/png",
        "TRANSPARENT": "true",
        "SRS": "EPSG:4326",
        "BBOX": f"{MIN_LON},{MIN_LAT},{MAX_LON},{MAX_LAT}",
        "WIDTH": "800",
        "HEIGHT": "800",
        "TIME": date_str
    }
    
    try:
        r = requests.get(WMS_URL, params=params, timeout=20)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(r.content)
            return True
    except Exception as e:
        print(f"Error: {e}")
    return False

def generate_dashboard():
    # Dates
    today = datetime.datetime.utcnow()
    date_str = today.strftime("%Y-%m-%d")
    
    # 1. Get Today's Image
    if not fetch_satellite_image(date_str, "latest.png"):
        print("Failed to get today's image (maybe upload delay). Exiting.")
        return

    # 2. Load Reference (Yesterday/Baseline)
    # If no reference exists, we just save today's as reference
    if not os.path.exists("reference.png"):
        print("No reference found. Setting today as baseline.")
        fetch_satellite_image(date_str, "reference.png")
        
    # 3. Create the "Diff" (The Outage Map)
    img_now = Image.open("latest.png").convert("RGB")
    img_ref = Image.open("reference.png").convert("RGB")
    
    # Calculate difference
    diff = ImageChops.difference(img_ref, img_now)
    
    # Boost contrast so you can see it clearly
    enhancer = ImageEnhance.Brightness(diff)
    diff_visible = enhancer.enhance(5.0) 
    diff_visible.save("diff_map.png")
    
    # 4. Update the README (The "Frontend")
    update_readme(date_str)

def update_readme(date):
    markdown = f"""
# 🛰️ Orbital Sentry: Power Tracker
**Target:** Lagos, Nigeria | **Last Scan:** {date}

### 1. Tonight's View (Live NASA Feed)
![Latest View](latest.png)

### 2. Change Detection (Red/Bright = Change)
If this is pitch black, lights are stable. If you see bright spots, lights turned ON or OFF compared to baseline.
![Difference Map](diff_map.png)

---
*Powered by GitHub Actions & NASA GIBS*
    """
    
    with open("README.md", "w") as f:
        f.write(markdown)

if __name__ == "__main__":
    generate_dashboard()
