from src.cli import TreeShell
from src.truthtrees import TreeFormula
import unittest
import src.util
import src.treeformulas


class TestInDecomposition(unittest.TestCase):
    def test_and(self):
        form1 = TreeFormula("a")
        form2 = TreeFormula("and(a,b)")
        self.assertTrue(form2.in_decomposition(form1))

    def test_and2(self):
        form1 = TreeFormula("b")
        form2 = TreeFormula("and(a,and(b,c))")
        self.assertTrue(form2.in_decomposition(form1))

    def test_and3(self):
        form1 = TreeFormula("and(b,c)")
        form2 = TreeFormula("and(a,and(b,c))")
        self.assertTrue(form2.in_decomposition(form1))

    def test_or(self):
        form1 = TreeFormula("a")
        form2 = TreeFormula("or(a,b)")
        self.assertTrue( form2.in_decomposition(form1))

    def test_or2(self):
        form1 = TreeFormula("b")
        form2 = TreeFormula("or(a,or(b,c))")
        self.assertTrue(form2.in_decomposition(form1))

    def test_or3(self):
        form1 = TreeFormula("or(b,c)")
        form2 = TreeFormula("or(a,or(b,c))")
        self.assertTrue(form2.in_decomposition(form1))

    def test_not_in(self):
        form1 = TreeFormula("b")
        form2 = TreeFormula("or(a,and(b,c))")
        self.assertFalse(form2.in_decomposition(form1))

    def test_complicated(self):
        form1 = TreeFormula("and(a,and(b,c))")
        form2 = TreeFormula("or(a,and(b,and(a,c)))")
        self.assertTrue( form2.in_decomposition(form1))

    def test_not_in2(self):
        form1 = TreeFormula("b")
        form2 = TreeFormula("and(a,or(b,c))")
        self.assertFalse( form2.in_decomposition(form1))

    def test_not_in3(self):
        form1 = TreeFormula("b")
        form2 = TreeFormula("a")
        self.assertFalse( form2.in_decomposition(form1))

    def test_if(self):
        form1 = TreeFormula("a")
        form2 = TreeFormula("if(a,b)")
        self.assertFalse( form2.in_decomposition(form1))

    def test_if2(self):
        form1 = TreeFormula("or(not(a),b)")
        form2 = TreeFormula("if(a,b)")
        self.assertTrue(form2.in_decomposition(form1))

    def test_if3(self):
        form1 = TreeFormula("or(not(a),b)")
        form2 = TreeFormula("if(a,b)")
        self.assertTrue(form1.in_decomposition(form2))

    def test_if4(self):
        form1 = TreeFormula("or(if(a,b),b)")
        form2 = TreeFormula("if(a,b)")
        self.assertTrue(form1.in_decomposition(form2))

    def test_not_in4(self):
        form1 = TreeFormula("or(if(b,a),b)")
        form2 = TreeFormula("if(a,b)")
        self.assertFalse(form1.in_decomposition(form2))

    def test_not_iff(self):
        form1 = TreeFormula("if(a,b)")
        form2 = TreeFormula("iff(a,b)")
        self.assertTrue(form2.in_decomposition(form1))

    def test_not_iff2(self):
        form1 = TreeFormula("if(b,a)")
        form2 = TreeFormula("iff(a,b)")
        self.assertTrue(form2.in_decomposition(form1))

    def test_not_iff3(self):
        form1 = TreeFormula("a")
        form2 = TreeFormula("iff(a,b)")
        self.assertTrue(form2.in_decomposition(form1))

    def test_not_iff4(self):
        form1 = TreeFormula("not(a)")
        form2 = TreeFormula("iff(a,b)")
        self.assertTrue(form2.in_decomposition(form1))

    def test_not_iff4(self):
        form1 = TreeFormula("or(and(not(a),not(b)),and(a,b))")
        form2 = TreeFormula("iff(a,b)")
        self.assertTrue(form2.in_decomposition(form1))

    def test_and7(self):
        tf = TreeFormula("and(and(a,b),and(b,a))")
        tf2 = TreeFormula("and(a,b)")
        self.assertTrue(tf2.in_decomposition(tf))

    def test_and8(self):
        tf = TreeFormula("and(and(a,b),and(b,a))")
        tf2 = TreeFormula("and(a,b)")
        self.assertTrue(tf.in_decomposition(tf2))

if __name__ == "__main__":
    unittest.main()