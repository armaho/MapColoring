import unittest

from lib.backtrack_solver import BacktrackSolver, InconsistentCspError
from lib.csp import CSP, Variable, Constraint, InvalidValueError


class BasicCspTests(unittest.TestCase):
    def test_consistent_assignment(self):
        csp = CSP()

        var1 = Variable(domain={1, 2})
        var2 = Variable(domain={1, 2})
        constraint1 = Constraint(variables=[var1, var2], constraint_func=(lambda x, y: x != y))

        csp.add_variable(var1)
        csp.add_variable(var2)
        csp.add_constraint(constraint1)

        csp.assign(var1, 1)
        csp.assign(var2, 2)

        self.assertEqual(var1.value, 1)
        self.assertEqual(var2.value, 2)

    def test_invalid_value_assignment(self):
        csp = CSP()

        var1 = Variable(domain={1, 2})
        var2 = Variable(domain={1, 2})
        constraint1 = Constraint(variables=[var1, var2], constraint_func=(lambda x, y: x != y))

        csp.add_variable(var1)
        csp.add_variable(var2)
        csp.add_constraint(constraint1)

        with self.assertRaises(InvalidValueError):
            csp.assign(var1, 1)
            csp.assign(var2, 1)

    def test_backtrack_solver(self):
        csp = CSP()

        var1 = Variable(domain={1, 2})
        var2 = Variable(domain={1, 2})
        constraint1 = Constraint(variables=[var1, var2], constraint_func=(lambda x, y: x != y))

        csp.add_variable(var1)
        csp.add_variable(var2)
        csp.add_constraint(constraint1)

        solver = BacktrackSolver(csp)
        solver.solve()

        self.assertTrue(solver.csp.is_solved())

    def test_backtrack_solver_for_inconsistent_csp(self):
        csp = CSP()

        var1 = Variable(domain={1, 2})
        var2 = Variable(domain={1, 2})
        constraint1 = Constraint(variables=[var1, var2], constraint_func=(lambda x, y: False))

        csp.add_variable(var1)
        csp.add_variable(var2)
        csp.add_constraint(constraint1)

        solver = BacktrackSolver(csp)

        with self.assertRaises(InconsistentCspError):
            solver.solve()


if __name__ == '__main__':
    unittest.main()
