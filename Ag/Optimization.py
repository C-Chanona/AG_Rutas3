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
    
    def crossover(self, selected): # cruce de orden parcial (Partially Mapped Crossover, PMX)
        childrens = []
        for parent1, parent2 in selected:
            if random.random() > 0.5:
                start = random.randint(1, len(parent1)-1)
                end = random.randint(start+1, len(parent1))

                # Mantén el primer elemento y realiza el cruce en los elementos a partir del segundo índice
                child = [parent1[0]] + parent1[start:end]
                child += [poi for poi in parent2 if poi not in child]
                childrens.append(child)
        
        return childrens
    
    def mutation(self, childrens):
        for children in childrens:
            if random.random() > 0.5:
                i, j = random.sample(range(1, len(children)), 2)
                children[i], children[j] = children[j], children[i]

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