from geopy.geocoders import Nominatim # Para OpenStreetMap
from Ag.Interface import Interface as ui
import pandas as pd

class Model:
    geolocator = Nominatim(user_agent="AG_routes")
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
            return 0      
        try:
            return Model.dataset.loc[
                (Model.dataset['id_origen'] == id_origen) &
                (Model.dataset['id_destino'] == id_destino)
            ]['distancia'].values[0]
        except IndexError:
            raise IndexError(f"No se encontró una distancia para los índices: {id_origen}, {id_destino}")

    @staticmethod
    def sort_by_proximity(route): #Ordena la ruta basandose en la proximidad geografica de los puntos de interes
        unique_route = Model.filter_route(route)

        sorted_route = [unique_route[0]]  # Mantén el punto de inicio
        remaining = unique_route[1:]
        while remaining:
            last_poi = sorted_route[-1]['id_destino'] # Selección del último punto de interés añadido. [-1] selecciona el último elemento de la lista porque los indices negativos cuentan desde el final.
            next_poi = min(remaining, key=lambda x, last_poi=last_poi: Model.get_distance(last_poi, x['id_destino'])) # Calcula la distancia erntre last_poi y cada punto de interes restante, y selecciona el más cercano.
            sorted_route.append(next_poi)
            remaining.remove(next_poi)
        return sorted_route # Esta implementación asegura que la ruta se optimiza en términos de distancia entre puntos consecutivos
    
    @staticmethod
    def filter_route(route):
        seen = set()
        unique_route = []
        for segment in route:
            if segment['id_destino'] not in seen:
                unique_route.append(segment)
                seen.add(segment['id_destino'])
        
        return unique_route

    @staticmethod
    def total_time(travel_time, origin_id):
        poi_info = Model.dataset.loc[Model.dataset['id_lugar'] == origin_id]
        if not poi_info.empty:
            poi_info = poi_info.iloc[0]

        return travel_time + poi_info['tiempo_visita']