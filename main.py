import random
import time
from argparse import ArgumentParser, Namespace
from collections import deque

from graphics.graphics import draw
from lib.backtrack_solver import BacktrackBinaryCspSolver, InconsistentCspError
from lib.constraint import BinaryConstraint
from lib.csp import BinaryCsp
from lib.variable import Variable
from maps.map_generator import generate_borders_by_continent


not_colored_country_color = 'lightgrey'


def parse_arguments() -> Namespace:
    parser = ArgumentParser(
        prog="Map Coloring",
        description="Utilizing CSP to solve map coloring problem",
    )

    parser.add_argument(
        "-m",
        "--map",
        type=str,
        help="Map must be: [Asia, Africa, America, Europe]",
    )
    parser.add_argument(
        "-lcv",
        "--lcv",
        action="store_true",
        help="Enable least constraint value (LCV) as a order-type optimizer"
    )
    parser.add_argument(
        "-mrv",
        "--mrv",
        action="store_true",
        help="Enable minimum remaining values (MRV) as a order-type optimizer"
    )
    parser.add_argument(
        "-ac3",
        "--arc-consistency",
        action="store_true",
        help="Enable arc consistency as a mechanism to eliminate the domain of variables achieving an optimized "
             "solution"
    )
    parser.add_argument(
        "-n",
        "--neighborhood-distance",
        type=int,
        default=1,
        help="The value determines the threshold for neighboring regions' similarity in color, with a default of 1 "
             "ensuring adjacent regions have distinct colors; increasing it, for instance to 2, extends this "
             "dissimilarity to the neighbors of neighbors."
    )
    parser.add_argument(
        "-c",
        "--number-of-colors",
        type=int,
        default=4,
        help="number of colors to be used in the map"
    )

    return parser.parse_args()

def get_neighbors(countries: dict[str, list[str]], initial_country: str, max_distance: int) -> set[str]:
    if initial_country not in countries.keys():
        return set()

    mark = {country: False for country in countries.keys()}
    bfs_queue: deque[tuple[str, int]] = deque()
    neighbors: set[str] = set()

    bfs_queue.append((initial_country, 0))
    mark[initial_country] = True

    while len(bfs_queue) > 0:
        country, distance = bfs_queue.popleft()

        if distance < max_distance:
            for neighbor in countries[country]:
                if (neighbor in countries.keys()) and (not mark[neighbor]):
                    bfs_queue.append((neighbor, distance + 1))
                    mark[neighbor] = True
                    neighbors.add(neighbor)

    return neighbors


def main():
    args = parse_arguments()

    colors = ["#{:06x}".format(random.randint(0x0F0F0F, 0xF0F0F0)) for _ in range(int(args.number_of_colors))]

    csp = BinaryCsp(use_mrv=args.mrv, use_lcv=args.lcv)

    countries = generate_borders_by_continent(continent=str(args.map))
    country_variable = {country: Variable({i for i in range(len(colors))}) for country in countries.keys()}
    variable_country = {variable: country for country, variable in country_variable.items()}

    for variable in country_variable.values():
        csp.add_variable(variable)

    visited_countries = set()
    for country in countries.keys():
        for neighbor in get_neighbors(countries, country, int(args.neighborhood_distance)):
            if (neighbor in visited_countries) or (neighbor not in countries.keys()):
                continue

            csp.add_constraint(BinaryConstraint(variables=[country_variable[country], country_variable[neighbor]],
                                                constraint_func=(lambda x, y: x != y)))

        visited_countries.add(country)

    solver = BacktrackBinaryCspSolver(csp, use_ac3=args.arc_consistency)

    start_time = time.time()

    try:
        solver.solve()
        print("Solved CSP!")
    except InconsistentCspError as ice:
        print(str(ice))

    end_time = time.time()

    print(f"Time taken to solve: {end_time - start_time}")

    solution: dict[str, any] = {}
    for variable, country in variable_country.items():
        csp_variable = solver.csp.get_variable_used_in_csp(variable)

        if csp_variable.value is not None:
            solution[country] = colors[csp_variable.value]
        else:
            solution[country] = not_colored_country_color

    draw(solution=solution, continent=str(args.map), assignments_number=solver.csp.assignments_number)


if __name__ == '__main__':
    main()
