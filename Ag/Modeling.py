from geopy.geocoders import Nominatim # Para OpenStreetMap
from Ag.Interface import Interface as ui
import requests
import random
import polyline
import pandas as pd

class PointOfInterest:
    def __init__(self, id_place, name, lat, lon, time=0):
        self.id = id_place
        self.name = name
        # self.visit_time = time
        self.lat = lat
        self.lon = lon

class Model:
    geolocator = Nominatim(user_agent="AG_routes")
    api_key = "AIzaSyDiNQCvlhBC6mxdLF9MXFHXfFflEYuDUGY"
    dataset = pd.read_excel("completo.xlsx")

    @staticmethod
    def get_poi_info(poi_id):
        poi_info = Model.dataset.loc[Model.dataset['id_lugar'] == poi_id]
        if not poi_info.empty:
            poi_info = poi_info.iloc[0]
            return poi_info['nombre'], poi_info['lat'], poi_info['lon']
        else:
            return None, None, None
        
    @staticmethod
    def get_data_with_api(coordinates):
        url = "https://routes.googleapis.com/directions/v2:computeRoutes"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": Model.api_key,
            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline"
        }

        origin = {"location": {"latLng": {"latitude": coordinates[0][0], "longitude": coordinates[0][1]}}}
        destination = {"location": {"latLng": {"latitude": coordinates[-1][0], "longitude": coordinates[-1][1]}}}
        intermediates = [{"location": {"latLng": {"latitude": lat, "longitude": lng}}} for lat, lng in coordinates[1:-1]]

        payload = {
            "origin": origin,
            "destination": destination,
            "intermediates": intermediates,
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE_OPTIMAL",
            "polylineQuality": "HIGH_QUALITY",
            "computeAlternativeRoutes": False,
            "routeModifiers": {
                "avoidTolls": False,
                "avoidHighways": False,
                "avoidFerries": False
            },
            "languageCode": "en-US"
        }

        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if "routes" in data and len(data["routes"]) > 0:
                route = data["routes"][0]
                distance = route["distanceMeters"] / 1000  # Convertir a kilómetros
                duration = route["duration"]  # Duración en segundos
                polyline_encoded = route["polyline"]["encodedPolyline"]  # Polilínea codificada
                
                return distance, float(duration.split('s')[0]) / 3600  , polyline.decode(polyline_encoded)
            else:
                print("Error: La respuesta no contiene las rutas esperadas.")
                return None, None, None
        else:
            print("Error al obtener la ruta:", response.status_code, response.text)
            return None, None, None

    @staticmethod
    def create_path(route):
        ui.map_widget.delete_all_path()
        ui.map_widget.delete_all_marker()
        markers = []
        
        for i, segment in enumerate(route):
            print(type(segment))
            name_origen, lat_origen, lon_origen = Model.get_poi_info(segment['id_origen'])
            name_destino, lat_destino, lon_destino = Model.get_poi_info(segment['id_destino'])
            ui.map_widget.set_marker(
                lat_origen, lon_origen, 
                text=f"{i+1}. {name_origen}", 
                text_color='black', 
                font='Candara 11 bold', 
                marker_color_outside='red', 
                marker_color_circle='brown'
            )
            # markers.append((lat_origen, lon_origen))


        # Obtener la polilinea con la API de Google Maps
        distance, duration, polyline_encoded = Model.get_data_with_api(markers)
        # Crear la ruta conectando los puntos en orden
        ui.map_widget.set_path(polyline_encoded, name="Tour_Route", color='blue', width=3)

        return route

    @staticmethod
    def get_parameters(id_origen, id_destino, transporte):
        resultado = Model.dataset.loc[
            (Model.dataset['id_origen'] == id_origen) & 
            (Model.dataset['id_destino'] == id_destino) & 
            (Model.dataset['transporte'] == transporte)
        ]
        
        if not resultado.empty:
            return {
                'distancia': resultado['distancia'].values[0],
                'tiempo_viaje': resultado['tiempo_viaje'].values[0],
                'costo': resultado['costo'].values[0]
            }
        else:
            print(f"Ruta no encontrada: origen={id_origen}, destino={id_destino}, transporte={transporte}")
            return None
    
    @staticmethod
    def get_distance(id_origen, id_destino): #Obtiene la distancia entre dos puntos de interes del conjunto de datos
        if id_origen == id_destino:
            return 0  # O maneja esto de otra manera según tu lógica de negocio        
        try:
            return Model.dataset.loc[
                (Model.dataset['id_origen'] == id_origen) &
                (Model.dataset['id_destino'] == id_destino)
            ]['distancia'].values[0]
        except IndexError:
            raise IndexError(f"No se encontró una distancia para los índices: {id_origen}, {id_destino}")

    @staticmethod
    def sort_by_proximity(route): #Ordena la ruta basandose en la proximidad geografica de los puntos de interes
        sorted_route = [route[0]]  # Mantén el punto de inicio
        remaining = route[1:]
        while remaining:
            last_poi = sorted_route[-1]['id_destino']
            next_poi = min(remaining, key=lambda x, last_poi=last_poi: Model.get_distance(last_poi, x['id_destino']))
            sorted_route.append(next_poi)
            remaining.remove(next_poi)
        return sorted_route
    
    @staticmethod
    def filter_route(route):
        unique_routes = {}
        
        # Agrupar transportes por (id_origen, id_destino)
        for segment in route:
            key = (segment['id_origen'], segment['id_destino'])
            if key not in unique_routes:
                unique_routes[key] = []
            unique_routes[key].append(segment['transport'])
        
        # Seleccionar aleatoriamente un transporte para cada ruta única
        filtered_route = []
        for (id_origen, id_destino), transports in unique_routes.items():
            selected_transport = random.choice(transports)
            filtered_route.append({
                'id_origen': id_origen,
                'id_destino': id_destino,
                'transport': selected_transport
            })
        
        return filtered_route
