import unittest

from lib.backtrack_solver import BacktrackCspSolver, InconsistentCspError, BacktrackBinaryCspSolver
from lib.constraint import BinaryConstraint
from lib.csp import BinaryCsp, Variable, Constraint, InvalidValueError, Csp


class CspTests(unittest.TestCase):
    def test_consistent_assignment(self):
        csp = BinaryCsp()

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
        csp = Csp()

        var1 = Variable(domain={1, 2})
        var2 = Variable(domain={1, 2})
        constraint1 = Constraint(variables=[var1, var2], constraint_func=(lambda x, y: x != y))

        csp.add_variable(var1)
        csp.add_variable(var2)
        csp.add_constraint(constraint1)

        with self.assertRaises(InvalidValueError):
            csp.assign(var1, 1)
            csp.assign(var2, 1)

    def test_ac3(self):
        csp = BinaryCsp()

        var1 = Variable(domain={1, 2})
        var2 = Variable(domain={2})
        constraint1 = BinaryConstraint(variables=[var1, var2], constraint_func=(lambda x, y: x == y))

        csp.add_variable(var1)
        csp.add_variable(var2)
        csp.add_constraint(constraint1)

        csp.apply_ac3()

        self.assertEqual(len(var1.domain), 1)
        self.assertEqual(next(iter(var1.domain)), 2)

class SolverTest(unittest.TestCase):
    def test_backtrack_solver(self):
        csp = Csp()

        var1 = Variable(domain={1, 2})
        var2 = Variable(domain={1, 2})
        constraint1 = Constraint(variables=[var1, var2], constraint_func=(lambda x, y: x != y))

        csp.add_variable(var1)
        csp.add_variable(var2)
        csp.add_constraint(constraint1)

        solver = BacktrackCspSolver(csp)
        solver.solve()

        self.assertTrue(solver.csp.is_solved())

    def test_backtrack_solver_for_inconsistent_csp(self):
        csp = Csp()

        var1 = Variable(domain={1, 2})
        var2 = Variable(domain={1, 2})
        constraint1 = Constraint(variables=[var1, var2], constraint_func=(lambda x, y: False))

        csp.add_variable(var1)
        csp.add_variable(var2)
        csp.add_constraint(constraint1)

        solver = BacktrackCspSolver(csp)

        with self.assertRaises(InconsistentCspError):
            solver.solve()

    def test_backtrack_solver_with_ac3(self):
        csp = BinaryCsp()

        var1 = Variable(domain={1, 2})
        var2 = Variable(domain={2})
        constraint1 = BinaryConstraint(variables=[var1, var2], constraint_func=(lambda x, y: x == y))

        csp.add_variable(var1)
        csp.add_variable(var2)
        csp.add_constraint(constraint1)

        solver = BacktrackBinaryCspSolver(csp, use_ac3=True)

        solver.solve()

        self.assertEqual(len(solver.csp.get_variable_used_in_csp(var1).domain), 1)
        self.assertEqual(next(iter(solver.csp.get_variable_used_in_csp(var1).domain)), 2)

    def test_backtrack_solver_with_mrv(self):
        csp = BinaryCsp(use_mrv=True)

        var1 = Variable(domain={1})
        var2 = Variable(domain={1, 2})
        var3 = Variable(domain={1, 3})
        constraint1 = BinaryConstraint(variables=[var1, var3], constraint_func=(lambda x, y: x != y))
        constraint2 = BinaryConstraint(variables=[var2, var3], constraint_func=(lambda x, y: x != y))

        csp.add_variable(var1)
        csp.add_variable(var2)
        csp.add_variable(var3)
        csp.add_constraint(constraint1)
        csp.add_constraint(constraint2)

        solver = BacktrackBinaryCspSolver(csp)
        solver.solve()

        self.assertTrue(solver.csp.is_solved())

    def test_backtrack_solver_with_(self):
        csp = BinaryCsp(use_lcv=True)

        var1 = Variable(domain={1, 2})
        var2 = Variable(domain={2})
        constraint1 = BinaryConstraint(variables=[var1, var2], constraint_func=(lambda x, y: x == y))

        csp.add_variable(var1)
        csp.add_variable(var2)
        csp.add_constraint(constraint1)

        solver = BacktrackBinaryCspSolver(csp)

        solver.solve()

        self.assertTrue(solver.csp.is_solved())


if __name__ == '__main__':
    unittest.main()
