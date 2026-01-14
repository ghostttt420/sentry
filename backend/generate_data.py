import requests
import json
import os
import datetime

# CONFIGURATION
TARGETS = [
    {"id": "lagos", "name": "Lagos, Nigeria", "lat": 6.524, "lon": 3.379, "zoom": 0.1},
    {"id": "tokyo", "name": "Tokyo, Japan", "lat": 35.676, "lon": 139.650, "zoom": 0.1},
    {"id": "delta", "name": "Niger Delta (Flares)", "lat": 4.5, "lon": 7.0, "zoom": 0.5}
]

WMS_URL = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"

def fetch_image(target, date_str):
    # Fetch Visual Layer
    bbox = f"{target['lon']-target['zoom']},{target['lat']-target['zoom']},{target['lon']+target['zoom']},{target['lat']+target['zoom']}"
    
    params = {
        "SERVICE": "WMS", "VERSION": "1.1.1", "REQUEST": "GetMap",
        "LAYERS": "MODIS_Terra_CorrectedReflectance_TrueColor",
        "FORMAT": "image/jpeg", "SRS": "EPSG:4326", "BBOX": bbox,
        "WIDTH": "800", "HEIGHT": "600", "TIME": date_str
    }
    
    # Save to the React 'public' folder so the frontend can see it
    filename = f"public/images/{target['id']}_{date_str}.jpg"
    os.makedirs("public/images", exist_ok=True)
    
    try:
        r = requests.get(WMS_URL, params=params)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(r.content)
            return f"/images/{target['id']}_{date_str}.jpg"
    except:
        pass
    return None

def main():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    app_data = {
        "last_updated": today,
        "locations": []
    }
    
    print(f"🌍 Starting Sync for {today}...")
    
    for t in TARGETS:
        print(f"Processing {t['name']}...")
        img_url = fetch_image(t, today)
        
        if img_url:
            app_data["locations"].append({
                "id": t['id'],
                "name": t['name'],
                "coordinates": f"{t['lat']}, {t['lon']}",
                "image_url": img_url,
                "status": "Active"
            })
            
    # Save database for Frontend
    with open("public/satellite_data.json", "w") as f:
        json.dump(app_data, f, indent=2)

if __name__ == "__main__":
    main()
