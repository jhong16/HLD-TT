from src.cli import TreeShell
from src.truthtrees import TreeFormula
import unittest
import src.util

class TestFormulaEquality(unittest.TestCase):
    def test_and_commutativity(self):
        tf = TreeFormula("And(a,b )")
        tf2 = TreeFormula("and( b, a)")
        self.assertEqual(tf, tf2)

    def test_and_commutativity_complicated(self):
        tf = TreeFormula("And(a,and(b,c) )")
        tf2 = TreeFormula("and( and(c,b), a)")
        self.assertEqual(tf, tf2)

    def test_and_commutativity2(self):
        tf = TreeFormula("And(a,and(b,c) )")
        tf2 = TreeFormula("and( and(a, b), c)")
        self.assertEqual(tf, tf2)

    def test_or_commutativity(self):
        tf = TreeFormula("or(a,b )")
        tf2 = TreeFormula("OR( b, a)")
        self.assertEqual(tf, tf2)

    def test_simple(self):
        tf = TreeFormula("a")
        tf2 = TreeFormula("A")
        self.assertNotEqual(tf, tf2)

    def test_demorgan_and(self):
        tf = TreeFormula("not(and(a,b))")
        tf2 = TreeFormula("or(not(a),not(b))")
        self.assertEqual(tf, tf2)

    def test_demorgan_or(self):
        tf = TreeFormula("not(or(a,b))")
        tf2 = TreeFormula("and(not(a),not(b))")
        self.assertEqual(tf, tf2)

    def test_if(self):
        tf = TreeFormula("if(a,b)")
        tf2 = TreeFormula("or(not(a),b)")
        self.assertEqual(tf, tf2)

    def test_demorgan_if(self):
        tf = TreeFormula("not(if(a,b))")
        tf2 = TreeFormula("and(a, not(b))")
        tf3 = TreeFormula("and(not(b), a)")
        self.assertEqual(tf, tf2)
        self.assertEqual(tf, tf3)

    def test_complicated_not_if(self):
        tf = TreeFormula("not(if(a,b))")
        tf2 = TreeFormula("not(or(not(a), b))")
        self.assertEqual(tf, tf2)

    def test_iff(self):
        tf = TreeFormula("iff(a,b)")
        tf2 = TreeFormula("or(and(a,b), and(not(a), not(b)))")
        self.assertEqual(tf, tf2)
        self.assertEqual(tf2, tf)

    def test_complicated_iff(self):
        tf = TreeFormula("iff(a,b)")
        tf2 = TreeFormula("and(if(a,b),if(b,a))")
        self.assertEqual(tf, tf2)
        self.assertEqual(tf2, tf)

    def test_if2(self):
        tf = TreeFormula("if(a,b)")
        tf2 = TreeFormula("if(b,a)")
        self.assertNotEqual(tf, tf2)

    def test_iff2(self):
        tf = TreeFormula("iff(a,b)")
        tf2 = TreeFormula("iff(b,a)")
        self.assertEqual(tf, tf2)

    def test_iff3(self):
        tf = TreeFormula("iff(not(a),not(b))")
        tf2 = TreeFormula("iff(b,a)")
        self.assertEqual(tf, tf2)

    def test_and9(self):
        tf = TreeFormula("and(and(a,b),and(b,a))")
        tf2 = TreeFormula("and(a,b)")
        self.assertEqual(tf, tf2)

if __name__ == "__main__":
    unittest.main()