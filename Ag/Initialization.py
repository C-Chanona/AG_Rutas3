import random
from Ag.Modeling import Model as md

class Initialization:
    def __init__(self, dataset, start_poi):
        self.dataset = dataset
        self.start_poi = start_poi
        self.calculate_min_max_values()

    # def generate_population(self, p0=50):
    #     id_start_poi = int(self.dataset.loc[self.dataset['nombre'] == self.start_poi, 'id_lugar'].values[0])
    #     pois = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    #     pois.remove(id_start_poi)
    #     routes = []
    #     population = []

    #     for _ in range(p0):
    #         total_pois = random.randint(2, len(pois))  # Número aleatorio de POIs
    #         route = [id_start_poi] + random.sample(pois, total_pois)  # Genera una ruta aleatoria con el punto de inicio elegido
    #         routes.append(route)

    #     for route in routes:
    #         individual = []
    #         for i in range(len(route) - 1):
    #             available_transports = self.dataset.loc[
    #                 (self.dataset['id_origen'] == route[i]) &
    #                 (self.dataset['id_destino'] == route[i + 1])
    #             ]['transporte'].values
    #             transport = random.choice(available_transports)
    #             individual.append({
    #                 'id_origen': route[i],
    #                 'id_destino': route[i + 1],
    #                 'transport': transport
    #             })
    #         population.append(individual)  # Agrega el individuo a la población

    #     print("POBLACION: ", population)
    #     # print(population)
    #     return population

    def generate_population(self, p0=50):
        id_start_poi = int(self.dataset.loc[self.dataset['nombre'] == self.start_poi, 'id_lugar'].values[0])
        pois = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        pois.remove(id_start_poi)
        population = []

        for _ in range(p0):
            route = [id_start_poi]
            available_pois = pois.copy()

            # Crear una ruta inicial basándose en la proximidad geográfica
            while len(route) < random.randint(3, len(pois)) and available_pois:
                current_poi = route[-1]
                # Encontrar el siguiente punto más cercano
                next_poi_distances = [
                    (poi, self.dataset[(self.dataset['id_origen'] == current_poi) & 
                                    (self.dataset['id_destino'] == poi)]['distancia'].values[0])
                    for poi in available_pois
                ]
                # Ordenar los posibles destinos por la distancia más cercana
                next_poi_distances.sort(key=lambda x: x[1])
                # Elegir el más cercano
                next_poi = next_poi_distances[0][0]
                route.append(next_poi)
                available_pois.remove(next_poi)
            
            # Convertir la ruta en un individuo, asignando transporte
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

        print("POBLACIÓN: ", population)
        return population

    
    def fitness(self, population):
        population_with_fitness = []
        for individual in population:
            distance, time, cost, places, penalty = self.calculate_fitness(individual)
        
            # Normalizar cada componente
            norm_distance = self.normalize(distance, self.min_distance, self.max_distance)
            norm_time = self.normalize(time, self.min_time, self.max_time)
            norm_cost = self.normalize(cost, self.min_cost, self.max_cost)
            norm_places = self.normalize(places, self.min_places, self.max_places)
            
            # Ajusta estos pesos según la importancia relativa de cada factor
            w_distance = 1.0
            w_time = 0.50
            w_cost = 0.25
            w_places = 1.50
            w_penalty = 1.0  # Peso para la penalización
            # w_distance = 0.25
            # w_time = 0.50
            # w_cost = 0.25
            # w_places = 0.50
            # w_penalty = 1.0  # Peso para la penalización

            fitness_value = (
                w_distance * norm_distance +
                w_time * norm_time +
                w_cost * norm_cost -
                w_places * norm_places +
                w_penalty * penalty
            )
            
            # print(f"Fitness: {fitness_value}")
            population_with_fitness.append({
                'route': individual,
                'fitness': fitness_value,
                'distance': distance,
                'time': time,
                'cost': cost,
                'places': places
            })

        return population_with_fitness

    def calculate_fitness(self, individual):
        total_distance = 0
        total_time = 0
        total_cost = 0
        num_places = len(individual) + 1
        visited = set([self.start_poi])
        penalty = 0
        big_jump_penalty = 0

        for segment in individual:
            if segment['id_destino'] in visited:
                penalty += 1000
            visited.add(segment['id_destino'])

            route_data = md.get_parameters(segment['id_origen'], segment['id_destino'], segment['transport'])
            
            total_distance += route_data['distancia']
            total_time += route_data['tiempo_viaje']
            total_cost += route_data['costo']
            
            # Penalizar saltos grandes
            if route_data['distancia'] > 10:  # Ajusta este valor según tus necesidades
                big_jump_penalty += (route_data['distancia'] - 10) * 10
            
            # Añadir tiempo de visita del destino
            total_time += self.dataset[self.dataset['id_lugar'] == segment['id_destino']]['tiempo_visita'].values[0]

        if num_places > 10:
            penalty += (num_places - 10) * 1000

        return total_distance, total_time, total_cost, num_places, penalty + big_jump_penalty
    
    def normalize(self, value, min_val, max_val):
        return (value - min_val) / (max_val - min_val)
    
    def calculate_min_max_values(self):
        # Distancia
        self.min_distance = self.dataset['distancia'].min()
        self.max_distance = self.dataset['distancia'].sum()  # Suma total como máximo teórico

        # Tiempo
        self.min_time = self.dataset['tiempo_viaje'].min()
        self.max_time = self.dataset['tiempo_viaje'].sum() + self.dataset['tiempo_visita'].sum()

        # Costo
        self.min_cost = self.dataset['costo'].min()
        self.max_cost = self.dataset['costo'].sum()

        # Lugares
        self.min_places = 2  # Mínimo 2 lugares (inicio y un destino)
        self.max_places = len(self.dataset['id_lugar'].dropna().unique())
        print("MAX PLACES: ", self.dataset['id_lugar'].dropna().unique())

        print(f"Min Distance: {self.min_distance}, Max Distance: {self.max_distance}")
        print(f"Min Time: {self.min_time}, Max Time: {self.max_time}")
        print(f"Min Cost: {self.min_cost}, Max Cost: {self.max_cost}")
        print(f"Min Places: {self.min_places}, Max Places: {self.max_places}")