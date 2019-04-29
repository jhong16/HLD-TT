from src.cli import TreeShell
import unittest
from src import util
from src.treeformulas import *

class TestDecompose(unittest.TestCase):
    def test_predicate(self):
        connector, decom1, decom2 = decompose_formula_argument("a")
        self.assertEqual(connector, None)
        self.assertEqual(decom1, "a")

    def test_simple(self):
        connector, decom1, decom2 = decompose_formula_argument("A")
        self.assertEqual(connector, None)
        self.assertEqual(decom1, "A")

    def test_complicated_and(self):
        connector, decom1, decom2 = decompose_formula_argument("and(or(a,c),if(b,c))")
        self.assertEqual(connector, "and")
        self.assertEqual(decom1, "or(a,c)")
        self.assertEqual(decom2, "if(b,c)")
        
    def test_not(self):
        connector, decom1, decom2 = decompose_formula_argument("not(a)")
        self.assertEqual(connector, None)
        self.assertEqual(decom1, "not(a)")
        self.assertEqual(decom2, None)

    def test_not_demorgan(self):
        connector, decom1, decom2 = decompose_formula_argument("not(and(a,b))")
        self.assertEqual(connector, "or")
        self.assertEqual(decom1, "not(a)")
        self.assertEqual(decom2, "not(b)")

        connector, decom1, decom2 = decompose_formula_argument("not(or(a,b))")
        self.assertEqual(connector, "and")
        self.assertEqual(decom1, "not(a)")
        self.assertEqual(decom2, "not(b)")

    def test_double_not(self):
        connector, decom1, decom2 = decompose_formula_argument("not(not(a))")
        self.assertEqual(connector, None)
        self.assertEqual(decom1, "a")
        self.assertEqual(decom2, None)

    def test_not_conditional(self):
        connector, decom1, decom2 = decompose_formula_argument("not(if(a,b))")
        self.assertEqual(connector, "and")
        self.assertEqual(decom1, "a")
        self.assertEqual(decom2,"not(b)")

    def test_not_iff(self):
        connector, decom1, decom2 = decompose_formula_argument("not(iff(a,b))")
        self.assertEqual(connector, "iff")
        self.assertEqual(decom2, "and(a,not(b))")
        self.assertEqual(decom1, "and(not(a),b)")

    def test_and(self):
        connector, decom1, decom2 = decompose_formula_argument("and(a,b)")
        self.assertEqual(connector, "and")
        self.assertEqual(decom1, "a")
        self.assertEqual(decom2, "b")

    def test_or(self):
        connector, decom1, decom2 = decompose_formula_argument("or(1,2)")
        self.assertEqual(connector, "or")
        self.assertEqual(decom1, "1")
        self.assertEqual(decom2, "2")

    def test_if(self):
        connector, decom1, decom2 = decompose_formula_argument("if(a,b)")
        self.assertEqual(connector, "or")
        self.assertEqual(decom1, "not(a)", decom1)
        self.assertEqual(decom2, "b", decom2)

    def test_iff(self):
        connector, decom1, decom2 = decompose_formula_argument("iff(a,b)")
        self.assertEqual(connector, "iff")
        self.assertEqual(decom1, "and(a,b)", decom1)
        self.assertEqual(decom2, "and(not(a),not(b))", decom2)

    def test_alternate_iff(self):
        decom1, decom2 = decompose_iff_into_if("iff(a,b)")
        self.assertEqual(decom1, "or(not(a),b)", decom1)
        self.assertEqual(decom2, "or(a,not(b))", decom2)

if __name__ == "__main__":
    unittest.main()

