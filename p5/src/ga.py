import copy
import heapq
import metrics
import multiprocessing.pool as mpool
import os
import random
import time
import math

# Global parameters: grid width and height.
width = 200
height = 14  # Rows 0-13; row 13 is the ground.
options = [
    "-",  # empty space
    "X",  # solid wall
    "?",  # question mark block with coin
    "M",  # question mark block with mushroom
    "B",  # breakable block
    "o",  # coin
    "|",  # pipe segment
    "T",  # pipe top
    "E",  # enemy
]

#########################################
# Postprocessing: Enforce design rules  #
#########################################
def postprocess_level(level):
    # --- Ground and Ravine Enforcement ---
    # Row 13 is the ground. Ensure any gap (ravine) is no wider than 3 columns.
    gap_length = 0
    start_gap = 0
    for x in range(width):
        if level[13][x] == "-":
            if gap_length == 0:
                start_gap = x
            gap_length += 1
        else:
            if gap_length > 3:
                for i in range(start_gap, start_gap + gap_length):
                    level[13][i] = "X"
            gap_length = 0
    if gap_length > 3:
        for i in range(start_gap, start_gap + gap_length):
            level[13][i] = "X"
    # For any column where ground is missing, clear all tiles above.
    for x in range(width):
        if level[13][x] == "-":
            for y in range(0, 13):
                level[y][x] = "-"

    # --- Clear items over the player ---
    # Ensure that in column 0 (player's column), no items or enemies block the space above.
    for y in range(0, 12):
        level[y][0] = "-"

    # --- Main Character and Flagpole ---
    # Main character always spawns at (row 12, col 0).
    level[12][0] = "m"
    # Flagpole: top "v" is now at row 5, rows 6-11 are "f", and row 12 (just above ground) is "X".
    flag_col = width - 1
    level[5][flag_col] = "v"
    for r in range(6, 12):
        level[r][flag_col] = "f"
    level[12][flag_col] = "X"

    # --- Pipe Structures ---
    # Restrict pipes to rows 8-12 (row 13 is ground).
    for x in range(width):
        for y in range(0, 8):
            if level[y][x] in ["T", "|"]:
                level[y][x] = "-"
    for x in range(width):
        pipe_rows = [y for y in range(8, 13) if level[y][x] in ["T", "|"]]
        if pipe_rows:
            # Enforce connection: the lowest pipe must be in row 12.
            if max(pipe_rows) != 12:
                for y in range(8, 13):
                    if level[y][x] in ["T", "|"]:
                        level[y][x] = "-"
            else:
                top_pipe = min(pipe_rows)
                for y in range(top_pipe, 13):
                    if level[y][x] not in ["T", "|"]:
                        level[y][x] = "|"
                if top_pipe > 8 and level[top_pipe-1][x] != "T":
                    level[top_pipe-1][x] = "T"
    # Remove isolated pipe tops: a "T" must have a "|" immediately below.
    for x in range(width):
        for y in range(8, 12):
            if level[y][x] == "T" and level[y+1][x] != "|":
                level[y][x] = "-"

    # --- Blocks (Walls, Breakable, etc.) ---
    # Ensure that contiguous blocks (["X", "B", "?", "M"]) do not extend more than 4 rows above the ground.
    for x in range(1, width-1):
        col_blocks = []
        for y in range(0, 13):
            if level[y][x] in ["X", "B", "?", "M"]:
                col_blocks.append(y)
            else:
                if col_blocks:
                    break
        if col_blocks:
            max_allowed = 13 - 4  # row 9 is the highest allowed.
            for y in col_blocks:
                if y < max_allowed:
                    level[y][x] = "-"

    # --- Ravines (again) ---
    gap_length = 0
    start_gap = 0
    for x in range(width):
        if level[13][x] == "-":
            if gap_length == 0:
                start_gap = x
            gap_length += 1
        else:
            if gap_length > 3:
                for i in range(start_gap, start_gap + gap_length):
                    level[13][i] = "X"
            gap_length = 0
    if gap_length > 3:
        for i in range(start_gap, start_gap + gap_length):
            level[13][i] = "X"

    # --- Enemy Placement ---
    # Enemies ("E") may only spawn if the tile directly below is an allowed support.
    allowed_support = ["X", "B", "?", "M", "T"]
    for y in range(0, 12):
        for x in range(width):
            if level[y][x] == "E":
                if level[y+1][x] not in allowed_support:
                    level[y][x] = "-"

    return level

#############################################
# Individual (Grid Encoding) Implementation #
#############################################
class Individual_Grid(object):
    __slots__ = ["genome", "_fitness"]

    def __init__(self, genome):
        self.genome = copy.deepcopy(genome)
        self._fitness = None

    def calculate_fitness(self):
        measurements = metrics.metrics(self.to_level())
        coefficients = {
            "meaningfulJumpVariance": 0.8,
            "negativeSpace": 1.5,
            "pathPercentage": 0.6,
            "emptyPercentage": 0.5,
            "linearity": -0.3,
            "solvability": 2.5,
            "decorationPercentage": 0.4,
            "leniency": -0.3,
            "rhythm": 0.4,
            "verticalVariety": 0.1,
            "enemySpacing": 2.2,
        }
        self._fitness = sum(coefficients[m] * measurements[m] for m in coefficients if m in measurements)
        consecutive = 0
        max_consecutive = 0
        for row in self.genome:
            for tile in row:
                if tile in ['E', '-']:
                    consecutive += 1
                    max_consecutive = max(max_consecutive, consecutive)
                else:
                    consecutive = 0
        if max_consecutive > 4:
            self._fitness -= (max_consecutive - 4) * 0.5
        for y in range(14):
            for x in range(1, width-1):
                if self.genome[y][x] == 'M':
                    clear = 0
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if 0 <= y+dy < 14 and self.genome[y+dy][x+dx] == '-':
                                clear += 1
                    if clear >= 5:
                        self._fitness += 0.2
        return self

    def fitness(self):
        if self._fitness is None:
            self.calculate_fitness()
        return self._fitness

    def mutate(self, genome):
        mutation_rate = 0.05
        # Restore coin weight to original (0.005) so coins remain rare.
        weights = [0.6, 0.15, 0.03, 0.03, 0.1, 0.005, 0.03, 0.005, 0.005]
        for y in range(0, 13):  # Only rows 0-12 mutate; row 13 is fixed ground.
            for x in range(1, width-1):
                if random.random() < mutation_rate:
                    if genome[y][x] not in ['m', 'f', 'v']:
                        new_tile = random.choices(options, weights=weights)[0]
                        genome[y][x] = new_tile
                        if y < 13 and new_tile in ['X', 'B', '?', 'M']:
                            if genome[y+1][x] == "-":
                                genome[y][x] = "-"
                        if new_tile == '|':
                            if y == 0 or genome[y-1][x] not in ['T', '|']:
                                genome[y][x] = "-"
                        if new_tile == 'T':
                            if y >= 12:
                                genome[y][x] = "-"
                            else:
                                genome[y+1][x] = '|'
                        if new_tile == 'E':
                            if y < 12 or genome[y+1][x] not in ["X", "B", "?", "M", "T"]:
                                genome[y][x] = "-"
        return genome

    def generate_children(self, other):
        new_genome = []
        fitness_self = self.fitness()
        fitness_other = other.fitness()
        total = fitness_self + fitness_other
        prob_self = fitness_self / total if total > 0 else 0.5
        for y in range(14):
            row = []
            for x in range(width):
                if x == 0 or x == width - 1:
                    row.append(self.genome[y][x])
                else:
                    row.append(self.genome[y][x] if random.random() < prob_self else other.genome[y][x])
            new_genome.append(row)
        child = Individual_Grid(new_genome)
        child.genome = child.mutate(child.genome)
        return (child,)

    def to_level(self):
        processed = postprocess_level(self.genome)
        return processed

    @classmethod
    def empty_individual(cls):
        g = [["-" for _ in range(width)] for _ in range(14)]
        g[13] = ["X"] * width
        g[12][0] = "m"  # main character spawn
        # Provisional flagpole: top "v" at row 5, rows 6-11 "f", row 12 "X"
        g[5][-1] = "v"
        for r in range(6, 12):
            g[r][-1] = "f"
        g[12][-1] = "X"
        return cls(g)

    @classmethod
    def random_individual(cls):
        g = [random.choices(options, k=width) for _ in range(14)]
        g[13] = ["X"] * width
        g[12][0] = "m"
        g[5][-1] = "v"
        for r in range(6, 12):
            g[r][-1] = "f"
        g[12][-1] = "X"
        return cls(g)

    @classmethod
    def seeded_individual(cls):
        base = cls.empty_individual().to_level()
        seed_rate = 0.02
        for y in range(0, 13):
            for x in range(1, width-1):
                if random.random() < seed_rate:
                    base[y][x] = random.choice(options)
        return cls(base)

Individual = Individual_Grid

##################################
# GA Main Loop and Selection     #
##################################
def generate_successors(population):
    new_population = []
    pop_size = len(population)
    elite_count = max(1, pop_size // 10)
    sorted_pop = sorted(population, key=lambda ind: ind.fitness(), reverse=True)
    new_population.extend(sorted_pop[:elite_count])
    def tournament_select(k=3):
        candidates = random.sample(population, k)
        return max(candidates, key=lambda ind: ind.fitness())
    def roulette_select():
        total_fit = sum(ind.fitness() for ind in population)
        pick = random.uniform(0, total_fit)
        current = 0
        for ind in population:
            current += ind.fitness()
            if current >= pick:
                return ind
        return random.choice(population)
    while len(new_population) < pop_size:
        if random.random() < 0.5:
            p1 = tournament_select()
            p2 = tournament_select()
        else:
            p1 = roulette_select()
            p2 = roulette_select()
        children = p1.generate_children(p2)
        new_population.extend(children)
        if len(new_population) > pop_size:
            new_population = new_population[:pop_size]
    return new_population

def ga():
    pop_limit = 480
    batches = os.cpu_count()
    batch_size = int(math.ceil(pop_limit / batches))
    pool = None
    population = []
    try:
        pool = mpool.Pool(processes=os.cpu_count())
        init_time = time.time()
        for _ in range(pop_limit):
            if random.random() < 0.8:
                population.append(Individual.random_individual())
            else:
                population.append(Individual.seeded_individual())
        population = pool.map(Individual.calculate_fitness, population, batch_size)
        init_done = time.time()
        print("Created and calculated initial population in:", init_done - init_time, "seconds")
        generation = 0
        start = time.time()
        print("Use ctrl-c to terminate this loop manually.")
        while True:
            now = time.time()
            if generation > 0:
                best = max(population, key=Individual.fitness)
                print("Generation:", generation)
                print("Max fitness:", best.fitness())
                print("Average generation time:", (now - start) / generation)
                print("Net time:", now - start)
                with open("levels/last.txt", 'w') as f:
                    for row in best.to_level():
                        f.write("".join(row) + "\n")
            generation += 1
            next_population = generate_successors(population)
            next_population = pool.map(Individual.calculate_fitness, next_population, batch_size)
            population = next_population
    except KeyboardInterrupt:
        print("\nCaught keyboard interrupt. Saving current best level...")
        pool.terminate()
        pool.join()
    except Exception as e:
        print(f"Error occurred: {e}")
        if pool:
            pool.terminate()
            pool.join()
        raise
    finally:
        if pool:
            pool.close()
            pool.join()
    return population if population else []

if __name__ == "__main__":
    try:
        final_gen = sorted(ga(), key=Individual.fitness, reverse=True)
        best = final_gen[0]
        print("Best fitness:", best.fitness())
        now = time.strftime("%m_%d_%H_%M_%S")
        for k in range(10):
            with open("levels/" + now + "_" + str(k) + ".txt", 'w') as f:
                for row in final_gen[k].to_level():
                    f.write("".join(row) + "\n")
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Program finished.")
