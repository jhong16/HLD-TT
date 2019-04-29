from src.cli import TreeShell
import unittest

class TestVerificationEdits(unittest.TestCase):
    def test_undo_delete_branch(self):
        """
        Testing undo and redo interaction with delete_branch
        """
        print("\n\nUndo Test branch delete=======================================================")
        shell = TreeShell()
        shell.reset()
        shell.do_add_root_formula("or(a,b)")
        shell.do_branch("1")
        shell.do_go_to("2")
        shell.do_add_formula("a")
        shell.do_go_to("3")
        shell.do_add_formula("b")
        shell.do_mark_parent("3 1")
        shell.do_go_to("1")

        shell.do_delete_branch("")
        self.assertEqual(len(shell.tree.formulas[1].children), 0)
        self.assertEqual(len(shell.current_node.children), 0)

        shell.do_undo("")
        print(shell.tree.formulas)
        self.assertEqual(len(shell.tree.formulas[1].children), 1)
        self.assertEqual(len(shell.current_node.children), 2)

    def test_checkmark_edits(self):
        """
        Testing undo and redo interaction with checkmark system
        """
        print("\n\nUndo Test checkmark edit1=======================================================")
        shell = TreeShell()
        shell.reset()
        shell.do_add_root_formula("or(a,b)")
        shell.do_branch("1")
        shell.do_go_to("2")
        shell.do_add_formula("a")
        shell.do_mark_parent("2 1")
        shell.do_go_to("3")
        shell.do_add_formula("b")
        shell.do_mark_parent("3 1")
        shell.do_checkmark("1")
        self.assertTrue(shell.tree.formulas[1].checkmarked)

        #Using undo and redo on checkmark
        shell.do_undo(None)
        self.assertFalse(shell.tree.formulas[1].checkmarked)
        shell.do_redo(None)
        self.assertTrue(shell.tree.formulas[1].checkmarked)

        shell.do_delete_formula("2")
        self.assertFalse(shell.tree.formulas[1].checkmarked)
        shell.do_undo(None)
        self.assertTrue(shell.tree.formulas[1].checkmarked)
        shell.do_redo(None)
        self.assertFalse(shell.tree.formulas[1].checkmarked)
        shell.do_undo(None)
        self.assertTrue(shell.tree.formulas[1].checkmarked)

    def test_checkmark_edits2(self):
        """
        Testing delete_formula interaction with checkmark system
        """
        print("\n\nUndo Test checkmark edits 2=======================================================")
        shell = TreeShell()
        shell.reset()
        shell.do_add_root_formula("and(a,b)")
        shell.do_add_formula("a")
        shell.do_mark_parent("2 1")
        shell.do_add_formula("b")
        shell.do_mark_parent("3 1")
        shell.do_checkmark("1")
        self.assertTrue(shell.tree.formulas[1].checkmarked)

        #Using undo and redo on checkmark
        shell.do_undo(None)
        self.assertFalse(shell.tree.formulas[1].checkmarked)
        shell.do_redo(None)
        self.assertTrue(shell.tree.formulas[1].checkmarked)

        shell.do_delete_formula("1")
        shell.do_undo(None)
        shell.do_delete_formula("2")
        self.assertFalse(shell.tree.formulas[1].checkmarked)
        shell.do_undo(None)
        self.assertTrue(shell.tree.formulas[1].checkmarked)

    def test_BiCondition(self):  
        print("\n\nBiconditional Test=======================================================")
        shell = TreeShell()
        shell.reset()  
        shell.do_add_formula("iff(a,b)")
        shell.do_branch("1")
        shell.do_go_to("2")
        shell.do_add_formula("a")
        shell.do_add_formula("b")
        shell.do_go_to("3")
        shell.do_add_formula("not(a)")
        shell.do_add_formula("not(b)")
        shell.do_mark_parent("2 1")
        shell.do_mark_parent("3 1")
        shell.do_mark_parent("4 1")
        shell.do_mark_parent("5 1")
        shell.do_checkmark("1")
        shell.do_add_root_formula("iff(a,b)")
        shell.do_mark_parent("2 1")
        shell.do_checkmark("1")

        self.assertTrue(shell.tree.formulas[1].checkmark)
        self.assertTrue(shell.tree.formulas[2].checkmark)
        for i in range(1, len(shell.tree.formulas)):
            self.assertTrue(shell.tree.formulas[i].valid)

        shell.do_undo(None)
        self.assertFalse(shell.tree.formulas[1].checkmarked)
        shell.do_undo(None)
        for i in range(2, len(shell.tree.formulas)):
            self.assertFalse(shell.tree.formulas[i].valid, i)

        shell.do_redo(None)
        for i in range(2, len(shell.tree.formulas)):
            self.assertTrue(shell.tree.formulas[i].valid, i)

        shell.do_redo(None)
        self.assertTrue(shell.tree.formulas[1].checkmarked)
        shell.do_go_to("2")
        shell.do_mark_open("")
        self.assertTrue(shell.finish)
        



if __name__ == "__main__":
    unittest.main()


