import math
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Global variables to store coordinates
ground_lat, ground_lon = 48.5665, -81.3721  # Timmins Airport coordinates
ground_alt = 0  # Altitude of the ground station in meters

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_directions', methods=['POST'])
def get_directions():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    altitude = data.get('altitude')
    
    if latitude is None or longitude is None or altitude is None:
        return jsonify(error="Latitude, longitude or altitude missing in request")
    
    # Calculate balloon direction relative to ground station (Timmins Airport)
    balloon_direction = calculate_direction(latitude, longitude, ground_lat, ground_lon)
    
    # Calculate ground direction relative to balloon
    ground_direction = calculate_direction(ground_lat, ground_lon, latitude, longitude)
    
    # Calculate elevation angle
    elevation_angle = calculate_elevation_angle(latitude, longitude, altitude, ground_lat, ground_lon, ground_alt)
    
    return jsonify(balloon_direction=balloon_direction, ground_direction=ground_direction, elevation_angle=elevation_angle)

def calculate_direction(lat1, lon1, lat2, lon2):
    """Calculate direction from (lat1, lon1) to (lat2, lon2)"""
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Calculate difference in longitudes
    delta_lon = lon2_rad - lon1_rad
    
    # Calculate direction angle using arctan2
    y = math.sin(delta_lon) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)
    
    direction_rad = math.atan2(y, x)
    direction_deg = math.degrees(direction_rad)
    
    # Normalize to 0-360 degrees
    direction_deg = (direction_deg + 360) % 360
    
    # Convert direction to compass direction
    compass_directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = round(direction_deg / 45) % 8
    compass_direction = compass_directions[index]
    
    return compass_direction

def calculate_elevation_angle(lat1, lon1, alt1, lat2, lon2, alt2):
    """Calculate the elevation angle from the ground station to the balloon"""
    # Calculate the distance on the ground (horizontal distance)
    horizontal_distance = haversine_distance(lat1, lon1, lat2, lon2)
    
    # Calculate the vertical distance
    vertical_distance = alt1 - alt2
    
    # Calculate the elevation angle
    elevation_angle_rad = math.atan2(vertical_distance, horizontal_distance)
    elevation_angle_deg = math.degrees(elevation_angle_rad)
    
    return elevation_angle_deg

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points on the Earth's surface"""
    R = 6371000  # Earth radius in meters
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Differences in coordinates
    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance

if __name__ == '__main__':
    app.run(debug=True)
