import geopandas as gpd
import requests
import pandas as pd

# Load the shapefile and extract the bounding box
def load_shapefile(shapefile_path):
    gdf = gpd.read_file(shapefile_path)

    #Reproject to EPSG:4326 if needed
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")

    # Extract the first geometry's bounding box (you can modify for multiple geometries)
    polygon = gdf.geometry.iloc[0]
    minx, miny, maxx, maxy = polygon.bounds
    bbox = [miny, minx, maxy, maxx]  # Lat, Lon order
    return bbox

# Fetch churches or places of worship from the Overpass API within the bounding box
def fetch_churches_osm(bbox):
    url = "http://overpass-api.de/api/interpreter"
    
    # Overpass QL query to find places of worship and parish offices in the bounding box
    query = f"""
    [out:json];
    (
      node["amenity"="place_of_worship"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
      node["office"="religion"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
    );
    out body;
    >;
    out skel qt;
    """
    
    response = requests.get(url, params={'data': query})
    data = response.json()
    
    churches = []
    
    for element in data['elements']:
        if 'tags' in element:
            name = element['tags'].get('name', 'N/A')
            lat = element.get('lat', 'N/A')
            lon = element.get('lon', 'N/A')
            description = element['tags'].get('description', 'N/A')
            religion = element['tags'].get('religion', 'N/A')
            denomination = element['tags'].get('denomination', 'N/A')
            opening_hours = element['tags'].get('opening_hours', 'N/A')
            operator = element['tags'].get('operator', 'N/A')
            phone = element['tags'].get('phone', 'N/A')
            email = element['tags'].get('email', 'N/A')
            fax = element['tags'].get('fax', 'N/A')
            website = element['tags'].get('website', 'N/A')
            wheelchair = element['tags'].get('wheelchair', 'N/A')
            street = element['tags'].get('addr:street', 'N/A')
            city = element['tags'].get('addr:city', 'N/A')
            zipcode = element['tags'].get('addr:postcode', 'N/A')
            house_number = element['tags'].get('addr:housenumber', 'N/A')
            
            churches.append({
                'name': name,
                'latitude': lat,
                'longitude': lon,
                'description': description,
                'religion': religion,
                'denomination': denomination,
                'opening_hours': opening_hours,
                'operator': operator,
                'phone': phone,
                'email': email,
                'fax': fax,
                'website': website,
                'wheelchair_accessible': wheelchair,
                'street': street,
                'city': city,
                'zipcode': zipcode,
                'house_number': house_number
            })
    
    return pd.DataFrame(churches)

# Saves the churches to a CSV file in your Downloads folder
def save_churches_to_csv(churches_df):
    output_path = r"/mnt/c/Users/blunt/Downloads/churches2.0.csv"  # WSL path for Windows
    churches_df.to_csv(output_path, index=False)
    print(f"File saved to {output_path}")

# Main script execution
if __name__ == "__main__":
    shapefile_path = r'/root/K/labeler/Illinois_House_Boundaries (1)/Illinois_House_Boundaries.shp'
    bbox = load_shapefile(shapefile_path)
    
    print(f"Bounding Box: {bbox}")
    
    churches_df = fetch_churches_osm(bbox)
    
    if not churches_df.empty:
        save_churches_to_csv(churches_df)
        print("Churches found and saved!")
    else:
        print("No churches found in the specified area.")