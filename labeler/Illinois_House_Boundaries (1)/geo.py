import geopandas as gpd
import requests
import pandas as pd

#Load the shapefile and extract the bounding box
def load_shapefile(shapefile_path):
    gdf = gpd.read_file(shapefile_path)

    # Reproject to EPSG:4326 if needed
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")

    # Extract the first geometry's bounding box (you can modify for multiple geometries)
    polygon = gdf.geometry.iloc[0]
    minx, miny, maxx, maxy = polygon.bounds
    bbox = [miny, minx, maxy, maxx]  # Lat, Lon order
    return bbox

# Step 2: Fetch restaurants from the Overpass API within the bounding box
def fetch_restaurants_osm(bbox):
    url = "http://overpass-api.de/api/interpreter"
    
    # Overpass QL query to find restaurants in the bounding box
    query = f"""
    [out:json];
    (
      node["amenity"="place_of_worship"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
    );
    out body;
    >;
    out skel qt;
    """
    
    response = requests.get(url, params={'data': query})
    data = response.json()
    
    restaurants = []
    
    for element in data['elements']:
        if 'tags' in element and 'name' in element['tags']:
            name = element['tags'].get('name', 'N/A')
            lat = element.get('lat', 'N/A')
            lon = element.get('lon', 'N/A')
            street = element['tags'].get('addr:street', 'N/A')
            city = element['tags'].get('addr:city', 'N/A')
            zipcode = element['tags'].get('addr:postcode', 'N/A')  # Add postal/zip code
            phone_number = element['tags'].get('phone', 'N/A')  # Add phone number
            house_number = element['tags'].get('addr:housenumber', 'N/A')
            tags = element['tags']
            
            # Add these fields into your dictionary
            restaurants.append({
                'name': name,
                'latitude': lat,
                'longitude': lon,
                'street': street,
                'city': city,
                'zipcode': zipcode,
                'phone_number': phone_number,
                'House_number': house_number,
                'tags': tags
            })
    
    return pd.DataFrame(restaurants)

#Saves the restaurants to a CSV file in your Downloads folder
def save_restaurants_to_csv(restaurants_df):
    output_path = r"/mnt/c/Users/blunt/Downloads/churches.csv" #wsl path for windows
    restaurants_df.to_csv(output_path, index=False)
    print(f"File saved to {output_path}")

#Main script execution
if __name__ == "__main__":
    shapefile_path = r'/root/K/labeler/Illinois_House_Boundaries (1)/Illinois_House_Boundaries.shp'
    bbox = load_shapefile(shapefile_path)
    
    print(f"Bounding Box: {bbox}")
    
    restaurants_df = fetch_restaurants_osm(bbox)
    
    if not restaurants_df.empty:
        save_restaurants_to_csv(restaurants_df)
        print("Restaurants found and saved!")
    else:
        print("No restaurants found in the specified area.")
