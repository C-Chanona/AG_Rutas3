import random

class Optimization:
    def __init__(self, min_places=5, days=10):
        self.min_places = min_places
        self.days = days
    
    def selection(self, population_with_fitness):
        selected = []
        parents = []

        for _ in range(len(population_with_fitness)):
            tournament = random.sample(population_with_fitness, min(self.min_places, len(population_with_fitness)))
            winner = min(tournament, key=lambda x: x['fitness'])
            selected.append(winner['route'])
        
        while len(selected) >= 2:
            first_route = random.choice(selected)
            selected.remove(first_route)
            second_route = random.choice(selected)
            selected.remove(second_route)
            parents.append((first_route, second_route))
        
        return parents

    def crossover(self, selected):
        childrens = []
        for parent1, parent2 in selected:
            # Verifica si hay suficientes elementos para realizar un cruce
            if len(parent1) > 3:  # Deben ser al menos 4 elementos para seleccionar 2 puntos de cruce
                start, end = sorted(random.sample(range(1, len(parent1)), 2)) # sorted asegura que start sea menor que end

                # Realiza el cruce
                child = [parent1[0]] + parent1[start:end]
                child += [poi for poi in parent2 if poi not in child] # Se añaden los elementos del padre2 que no están ya en el hijo.
                childrens.append(child)
            else:
                # Si no hay suficientes elementos, solo copia uno de los padres
                childrens.append(parent1 if random.random() > 0.5 else parent2)
            
        return childrens

    def mutation(self, childrens):
        for child in childrens:
            if len(child) > 2 and random.random() > 0.1:  # Verifica si hay suficientes elementos y aplica la probabilidad de mutación
                i = random.randint(1, len(child) - 1)  # Selecciona un punto aleatorio para extraer
                poi = child.pop(i)
                j = random.randint(1, len(child) - 1)  # Selecciona una nueva posición aleatoria para insertar
                child.insert(j, poi)

        return childrens

    
    def poda(self, population_with_fitness):
        sorted_population = sorted(population_with_fitness, key=lambda x: x['fitness'])
        best_route = sorted_population[0]
        next_generation = [best_route['route']]
        
        # Selección basada en ranking inverso
        while len(next_generation) < self.days:
            rank = len(sorted_population) - 1 - random.randint(0, len(sorted_population) - 1)
            next_generation.append(sorted_population[rank]['route'])
        
        return next_generation, best_route