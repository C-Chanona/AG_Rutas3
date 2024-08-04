import random
from Ag.Modeling import Model as md

class Initialization:
    def __init__(self, dataset, start_poi):
        self.dataset = dataset
        self.start_poi = start_poi

    def generate_population(self, p0=15):
        id_start_poi = int(self.dataset.loc[self.dataset['nombre'] == self.start_poi, 'id_lugar'].values[0])
        pois = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        pois.remove(id_start_poi)
        population = []

        for _ in range(p0):
            route = [id_start_poi]
            available_pois = pois.copy()
            
            while available_pois:
                # Encuentra el POI más cercano al último POI en la ruta
                current_poi = route[-1]
                distances = [(poi, self.get_distance(current_poi, poi)) for poi in available_pois]
                next_poi = min(distances, key=lambda x: x[1])[0]
                
                route.append(next_poi)
                available_pois.remove(next_poi)

            individual = []
            for i in range(len(route) - 1):
                available_transports = self.dataset.loc[
                    (self.dataset['id_origen'] == route[i]) &
                    (self.dataset['id_destino'] == route[i + 1])
                ]['transporte'].values
                transport = random.choice(available_transports)
                individual.append({
                    'id_origen': route[i],
                    'id_destino': route[i + 1],
                    'transport': transport
                })
            population.append(individual)

        print("POBLACION: ", population)
        return population

    def fitness(self, population):
        population_with_fitness = []

        for individual in population:
            total_distance = 0
            total_time = 0
            total_cost = 0

            # Ordenar la ruta por proximidad geográfica
            route = self.sort_by_proximity(individual)
            individual = self.filter_and_select_transport(route)

            for poi_pair in individual:
                id_origen = poi_pair['id_origen']
                id_destino = poi_pair['id_destino']
                transport = poi_pair['transport']

                info = md.get_parameters(id_origen, id_destino, transport)
                if info is not None:
                    total_distance += info['distancia']
                    total_time += info['tiempo_viaje']
                    total_cost += info['costo']
                else:
                    # Penalizar rutas no encontradas
                    total_time += 999
                    total_cost += 999

            fitness_value = self.calculate_fitness(total_distance, total_time, total_cost)
            population_with_fitness.append({
                'route': individual,
                'fitness': fitness_value,
                'distance': total_distance,
                'time': total_time,
                'cost': total_cost
            })

        return population_with_fitness
    
    def calculate_fitness(self, total_distance, total_time, total_cost):
        # Calcular el fitness
        fitness_value = (1 / (1 + total_distance)) + (1 / (1 + total_time)) + (1 / (1 + total_cost))
        return fitness_value

    def get_distance(self, id_origen, id_destino):
        if id_origen == id_destino:
            return 0  # O maneja esto de otra manera según tu lógica de negocio        
        try:
            return self.dataset.loc[
                (self.dataset['id_origen'] == id_origen) &
                (self.dataset['id_destino'] == id_destino)
            ]['distancia'].values[0]
        except IndexError:
            raise IndexError(f"No se encontró una distancia para los índices: {id_origen}, {id_destino}")

    def sort_by_proximity(self, route):
        sorted_route = [route[0]]  # Mantén el punto de inicio
        remaining = route[1:]
        while remaining:
            last_poi = sorted_route[-1]['id_destino']
            next_poi = min(remaining, key=lambda x, last_poi=last_poi: self.get_distance(last_poi, x['id_destino']))
            sorted_route.append(next_poi)
            remaining.remove(next_poi)
        return sorted_route
    
    def filter_and_select_transport(self, route):
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

    # def sort_by_proximity(self, route):
    #     sorted_route = [route[0]]  # Mantén el punto de inicio
    #     remaining = route[1:]
    #     visited_destinations = {route[0]['id_destino']}
        
    #     while remaining:
    #         last_poi = sorted_route[-1]['id_destino']
    #         next_poi = min(
    #             remaining, 
    #             key=lambda x, last_poi=last_poi: self.get_distance(last_poi, x['id_destino'])
    #         )
            
    #         if next_poi['id_destino'] in visited_destinations:
    #             remaining.remove(next_poi)
    #             continue
            
    #         sorted_route.append(next_poi)
    #         visited_destinations.add(next_poi['id_destino'])
    #         remaining.remove(next_poi)
        
    #     return sorted_route

    # def select_random_transport(self, route):
    #     transports = ['Caminando', 'Bicicleta', 'Taxi', 'Colectivo']
    #     for segment in route:
    #         segment['transport'] = random.choice(transports)
    #     return route