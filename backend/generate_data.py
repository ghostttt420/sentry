import requests
import json
import os
import datetime

# NASA LAYERS
LAYERS = {
    "visual": "MODIS_Terra_CorrectedReflectance_TrueColor",
    "thermal": "MODIS_Terra_Thermal_Anomalies_All" # The "Predator" View
}
WMS_URL = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"

def fetch_image(target, layer_type, date_str):
    bbox = f"{target['lon']-target['zoom']},{target['lat']-target['zoom']},{target['lon']+target['zoom']},{target['lat']+target['zoom']}"
    filename = f"public/images/{target['id']}_{layer_type}.jpg"
    os.makedirs("public/images", exist_ok=True)
    
    params = {
        "SERVICE": "WMS", "VERSION": "1.1.1", "REQUEST": "GetMap",
        "LAYERS": LAYERS[layer_type], "FORMAT": "image/jpeg", "SRS": "EPSG:4326", 
        "BBOX": bbox, "WIDTH": "800", "HEIGHT": "600", "TIME": date_str
    }
    try:
        r = requests.get(WMS_URL, params=params)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(r.content)
            return f"/images/{target['id']}_{layer_type}.jpg"
    except:
        pass
    return None

def main():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Load Targets from JSON file
    if os.path.exists("targets.json"):
        with open("targets.json", "r") as f:
            targets = json.load(f)
    else:
        targets = []

    app_data = {"last_updated": today, "locations": []}
    
    print(f"🌍 Starting Multi-Spectral Sync for {today}...")
    
    for t in targets:
        print(f"Scanning {t['name']}...")
        # Fetch Visual
        vis_url = fetch_image(t, "visual", today)
        # Fetch Thermal
        therm_url = fetch_image(t, "thermal", today)
        
        if vis_url:
            app_data["locations"].append({
                "id": t['id'],
                "name": t['name'],
                "coordinates": f"{t['lat']}, {t['lon']}",
                "image_visual": vis_url,
                "image_thermal": therm_url, # New thermal link
                "status": "Active"
            })
            
    with open("public/satellite_data.json", "w") as f:
        json.dump(app_data, f, indent=2)

if __name__ == "__main__":
    main()
