import random
from Ag.Modeling import Model as md

class Initialization:
    def __init__(self, dataset, start_poi):
        self.dataset = dataset
        self.start_poi = start_poi
        self.calculate_min_max_values()

    def generate_population(self, p0=50):
        id_start_poi = int(self.dataset.loc[self.dataset['nombre'] == self.start_poi, 'id_lugar'].values[0])
        pois = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        pois.remove(id_start_poi)
        routes = []
        population = []

        for _ in range(p0):
            total_pois = random.randint(2, len(pois))  # Número aleatorio de POIs
            route = [id_start_poi] + random.sample(pois, total_pois)  # Genera una ruta aleatoria con el punto de inicio elegido
            routes.append(route)

        print(routes, "\n")

        for route in routes:
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
            population.append(individual)  # Agrega el individuo a la población

        # print(population)
        return population

    def calculate_fitness(self, individual):
        total_distance = 0
        total_time = 0
        total_cost = 0
        num_places = len(individual) + 1  # +1 porque el último destino también cuenta como lugar

        for segment in individual:
            # route_data = self.dataset.loc[
            #     (self.dataset['id_origen'] == segment['id_origen']) &
            #     (self.dataset['id_destino'] == segment['id_destino']) &
            #     (self.dataset['transporte'] == segment['transport'])
            # ].values[0]

            route_data = md.get_parameters(segment['id_origen'], segment['id_destino'], segment['transport'])
            
            total_distance += route_data['distancia']
            total_time += route_data['tiempo_viaje']
            total_cost += route_data['costo']
            
            # Añadir tiempo de visita del destino
            total_time += self.dataset[self.dataset['id_lugar'] == segment['id_destino']]['tiempo_visita'].values[0]

        return total_distance, total_time, total_cost, num_places
    
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
    
    def fitness(self, population):
        population_with_fitness = []
        for individual in population:
            distance, time, cost, places = self.calculate_fitness(individual)
        
            # Normalizar cada componente
            norm_distance = self.normalize(distance, self.min_distance, self.max_distance)
            norm_time = self.normalize(time, self.min_time, self.max_time)
            norm_cost = self.normalize(cost, self.min_cost, self.max_cost)
            norm_places = self.normalize(places, self.min_places, self.max_places)
            
            # Ajusta estos pesos según la importancia relativa de cada factor
            w_distance = 0.25
            w_time = 0.50
            w_cost = 0.25
            w_places = 0.50

            fitness_value = (
                w_distance * norm_distance +
                w_time * norm_time +
                w_cost * norm_cost -
                w_places * norm_places
            )
            
            print(f"Fitness: {fitness_value}")
            population_with_fitness.append({
                'route': individual,
                'fitness': fitness_value,
                'distance': distance,
                'time': time,
                'cost': cost,
                'places': places
            })

        return population_with_fitness