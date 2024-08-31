import random
from Ag.Modeling import Model as md

class Initialization:
    def __init__(self, dataset, start_poi):
        self.dataset = dataset
        self.start_poi = start_poi
        self.cache = {}
        self.individual_cache = {}
        self.time_max = 720 # 12 horas en minutos

    def generate_population(self, p0=40):
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
                distances = [(poi, md.get_distance(current_poi, poi)) for poi in available_pois]
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
            # Cada individuo en la poblacion es una lista de diccionarios, donde cada diccionario representa un segmento de la ruta
            population.append(individual)

        print("POBLACION: ", population)
        return population

    def fitness(self, population):
        population_with_fitness = []
        for individual in population:
            # Convierte el individual a una tupla para usarla como clave de caché
            individual_key = tuple((poi['id_origen'], poi['id_destino'], poi['transport']) for poi in individual)
            if individual_key in self.individual_cache:
                fitness_data = self.individual_cache[individual_key]
            else:
                total_distance = 0
                total_time = 0
                total_cost = 0

                # Ordenar la ruta por proximidad geográfica
                individual = md.sort_by_proximity(individual) # Ayuda al algoritmo a encontrar soluciones mas optimaz y logicas
                # individual = md.filter_route(route)

                for poi_pair in individual: #itera sobre todos los segmentos de la ruta, sumando la distancia, tiempo y costo de cada segmento para obtener los totales de la ruta completa.
                    id_origen = poi_pair['id_origen']
                    id_destino = poi_pair['id_destino']
                    transport = poi_pair['transport']

                    # Crear una clave única para la caché
                    cache_key = (id_origen, id_destino, transport)

                    if cache_key in self.cache:
                        info = self.cache[cache_key]
                    else:
                        info = md.get_parameters(id_origen, id_destino, transport)
                        self.cache[cache_key] = info

                    if info is not None:
                        total_distance += info['distancia']
                        # total_time += info['tiempo_viaje']
                        total_time += md.total_time(info['tiempo_viaje'], id_origen)
                        total_cost += info['costo']
                    else:
                        # Penalizar rutas no encontradas
                        total_time += 999
                        total_cost += 999
                
                # Se invierte la relación porque queremos que las rutas con menor distancia, tiempo y costo sean consideradas mejores
                fitness_value = (1 / (1 + total_distance)) + (1 / (1 + total_time)) + (1 / (1 + total_cost)) # o sea que valores más bajos resultan en valores más altos de aptitud.
                # La suma de los tres componentes me permite considerar estas 3 variables simultáneamente en la evaluación de la ruta.
                # fitness_value = 0.5*(1 / (1 + total_distance)) + 5*(1 / (1 + total_time)) + 2*(1 / (1 + total_cost)) # o sea que valores más bajos resultan en valores más altos de aptitud.
                # dar más peso a un factor específico, aumenta la importancia de ese factor en la evaluación.
                
                if not total_time <= self.time_max:
                    last_poi = individual[-1]
                    individual.remove(last_poi)


                fitness_data = {
                    'route': individual,
                    'fitness': fitness_value,
                    'distance': total_distance,
                    'time': total_time,
                    'cost': total_cost
                }

                # Almacenar el resultado en la caché de individual
                self.individual_cache[individual_key] = fitness_data

            population_with_fitness.append(fitness_data)

        return population_with_fitness