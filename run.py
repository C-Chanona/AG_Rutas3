from Ag.Initialization import Initialization
from Ag.Optimization import Optimization
from Ag.Modeling import Model as md
from Ag.Interface import Interface as ui
import pandas as pd

def main(dataset, start_poi="Parque de la marimba", generation=50):
    init = Initialization(dataset, start_poi)
    opt = Optimization()
    bests_by_generation = []

    population = init.generate_population()
    fitness_results = init.fitness(population)
    # best_route = min(fitness_results, key=lambda x: x['fitness'])
    best_route = max(fitness_results, key=lambda x: x['fitness'])
    bests_by_generation.append(best_route)
    
    for _ in range(generation):
        selected = opt.selection(fitness_results)
        children = opt.crossover(selected)
        children = opt.mutation(children)
        new_population = list(population) + list(children)
        fitness_results = init.fitness(new_population)
        # best_route = min(fitness_results, key=lambda x: x['fitness'])
        best_route = max(fitness_results, key=lambda x: x['fitness'])
        population, currently_best = opt.poda(fitness_results)
        
        if currently_best['fitness'] > best_route['fitness']:
            best_route = currently_best

        bests_by_generation.append(best_route)
    
    # print("\n", best_route)

    # route = md.create_path(best_route['route'])
    
    ui.update_table(best_route['route'])

    ui.create_plot(bests_by_generation)

if __name__ =='__main__':
    ui.create_window(main)
    # dataset = pd.read_excel("completo.xlsx")
    # main(dataset)