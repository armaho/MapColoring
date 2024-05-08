import random
from argparse import ArgumentParser, Namespace

from graphics.graphics import draw
from lib.backtrack_solver import BacktrackBinaryCspSolver
from lib.constraint import BinaryConstraint
from lib.csp import BinaryCsp
from lib.variable import Variable
from maps.map_generator import generate_borders_by_continent


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
        "-c",
        "--number-of-colors",
        type=int,
        default=4,
        help="number of colors to be used in the map"
    )

    return parser.parse_args()


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
    for country, neighbors in countries.items():
        for neighbor in neighbors:
            if (neighbor in visited_countries) or (neighbor not in countries.keys()):
                continue

            csp.add_constraint(BinaryConstraint(variables=[country_variable[country], country_variable[neighbor]],
                                                constraint_func=(lambda x, y: x != y)))

        visited_countries.add(country)

    solver = BacktrackBinaryCspSolver(csp, use_ac3=args.arc_consistency)

    solver.solve()

    solution = {country: colors[solver.csp.get_variable_used_in_csp(variable).value]
                for variable, country in variable_country.items()}
    draw(solution=solution, continent=str(args.map), assignments_number=solver.csp.assignments_number)


if __name__ == '__main__':
    main()
