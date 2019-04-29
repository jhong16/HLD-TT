from src.cli import TreeShell
import unittest


class TestCLI(unittest.TestCase):

    def test_history(self):
        print("\nHistory Test===================================")
        shell = TreeShell()
        shell.reset()
        shell.do_add_root_formula("if(A, B)")
        print(shell.tree.formulas)
        shell.do_branch("1")
        shell.do_go_to("2")
        shell.do_add_formula("not(A)")
        shell.do_add_formula("B")
        shell.do_go_to("3")
        shell.do_add_formula("B")
        shell.do_delete_formula("3")
        shell.do_go_to("1")
        shell.do_delete_branch("")
        shell.do_delete_formula("1")
        self.assertEqual(len(shell.history), 11)
        print("\n\nPrinting History\n\n")
        shell.do_print_history("")

    def test_simple_function_deletion(self):
        print("\n Deletion Test===================================")
        shell = TreeShell()
        shell.reset()
        shell.do_add_root_formula("if(A, B)")
        print(shell.tree.formulas)
        shell.do_add_root_formula("if(A, B)")
        shell.do_add_root_formula("if(A, B)")
        shell.do_add_formula("if(A, B)")
        shell.do_delete_formula("2")
        self.assertEqual(len(shell.tree.formulas), 4)
        shell.do_delete_formula("1")
        self.assertEqual(len(shell.tree.formulas), 3)
        shell.do_delete_formula("1")
        self.assertEqual(len(shell.tree.formulas), 2)
        shell.do_delete_formula("1")
        self.assertEqual(len(shell.tree.formulas), 1) # All formulas are deleted at this point

    def test_root_id_set_one(self):
        print("\n Root ID Test===================================")
        shell = TreeShell()
        shell.reset()
        # print(f"shell.root.node_id == 1: {shell.root.node_id == 1}")
        self.assertEqual(shell.root.node_id, 1)

    def test_can_branch_on_root(self):
        print("\n Branch on Root Test===================================")
        shell = TreeShell()
        shell.reset()
        shell.do_add_root_formula("if(A, B)")
        shell.do_branch("")

    def test_can_traverse_between_nodes(self):
        print("\n Node Tranversal Test===================================")
        shell = TreeShell()
        shell.reset()
        shell.do_add_root_formula("if(A, B)")
        shell.do_branch("1")
        shell.do_go_to("2")
        self.assertEqual(shell.current_node.node_id, 2)
        shell.do_go_to("3")
        self.assertEqual(shell.current_node.node_id, 3)
        shell.do_go_to("1")
        self.assertEqual(shell.current_node.node_id, 1)

    def test_can_add_formula_on_middle_node(self):
        print("\n Add Formula in Middle Test===================================")
        shell = TreeShell()
        shell.reset()
        shell.do_add_root_formula("if(A, B)")
        shell.do_branch("1")
        shell.do_go_to("2")
        self.assertEqual(shell.current_node.node_id, 2)
        shell.do_add_formula("and(C, D)")

    def test_can_branch_on_middle_node(self):
        print("\n Branch in Middle Test===================================")
        shell = TreeShell()
        shell.reset()
        shell.do_add_root_formula("if(A, B)")
        shell.do_branch("1")
        shell.do_go_to("2")
        self.assertEqual(shell.current_node.node_id, 2)
        shell.do_add_formula("and(C, D)")
        shell.do_branch("2")
        self.assertEqual(len(shell.current_node.children), 0)
        shell.do_add_formula("or(C, D)")
        shell.do_branch("3")
        self.assertEqual(len(shell.current_node.children), 2)

    def test_can_branch_on_middle_node_twice(self):
        print("\n Branch in Middle Twice Test===================================")
        shell = TreeShell()
        shell.reset()
        shell.do_add_root_formula("if(A, B)")
        shell.do_branch("1")

        shell.do_go_to("2")
        self.assertEqual(shell.current_node.node_id, 2)
        shell.do_print_current_node(None)

        shell.do_add_formula("or(C, D)")
        shell.do_branch("2")

        shell.do_go_to("3")
        self.assertEqual(shell.current_node.node_id, 3)
        shell.do_add_formula("or(E, D)")
        shell.do_branch("3")
        shell.do_print_tree(None)

    def test_can_branch_on_middle_node_twice2(self):
        print("\n Branch in Middle Complicated 2 Test===================================")
        shell = TreeShell()
        shell.reset()
        shell.do_add_root_formula("if(A, B)")
        shell.do_branch("1")

        shell.do_go_to("2")
        self.assertEqual(shell.current_node.node_id, 2)
        shell.do_print_current_node(None)

        shell.do_add_formula("and(C, D)")
        shell.do_add_formula("and(E, G)")
        shell.do_add_formula("and(H, J)")
        shell.do_add_formula("or(K, L)")
        shell.do_branch("5")

        shell.do_go_to("3")
        self.assertEqual(shell.current_node.node_id, 3)
        shell.do_add_formula("or(E, D)")
        shell.do_add_formula("and(P, I)")
        shell.do_branch("6")

        shell.do_go_to("7")
        shell.do_add_formula("and(Q, T)")
        shell.do_add_formula("and(W, Y)")
        shell.do_add_formula("and(E, U)")
        shell.do_add_formula("and(R, I)")

        shell.do_go_to("4")
        shell.do_add_formula("iff(W, Y)")
        shell.do_add_formula("iff(E, U)")
        shell.do_add_formula("iff(R, I)")
        shell.do_print_formulas(None)

    def test_redo(self):
        print("\n\nRedo Test=======================================================")
        shell = TreeShell()
        shell.reset()

        # Testing add_root_formula
        shell.do_add_root_formula("if(A, B)")
        shell.do_undo("")
        shell.do_print_formulas("")

        self.assertEqual(len(shell.tree.formulas), 1)
        shell.do_redo("")
        self.assertEqual(len(shell.tree.formulas), 2)
        shell.do_undo("")

        # Testing add_formula
        shell.do_add_formula("if(A, B)")
        shell.do_undo("")
    
        shell.do_redo("")

        self.assertEqual(len(shell.tree.formulas), 2)
        shell.do_undo("")

        # Testing go_to
        shell.do_add_formula("or(a,b)")
        shell.do_branch("1")
        shell.do_go_to("2")
        shell.do_undo("")

        shell.do_redo("")
        self.assertEqual(shell.current_node.node_id, 2)
        shell.do_undo("")
        self.assertEqual(shell.current_node.node_id, 1)

        # Testing branch
        shell.do_undo("")
        self.assertEqual(len(shell.current_node.children), 0)
        shell.do_redo("")
        self.assertEqual(len(shell.current_node.children), 2)
        shell.do_undo("")

        shell.do_undo("")

        # Testing delete
        shell.do_add_formula("and(a, b)")
        shell.do_delete_formula("1")
        shell.do_undo("")
        self.assertNotEqual(len(shell.tree.formulas), 1)
        shell.do_redo("")
        self.assertEqual(len(shell.tree.formulas), 1)

        shell.do_print_history("")

    def test_undo(self):
        print("\n\nUndo Test=======================================================")
        shell = TreeShell()
        shell.reset()

        # Testing add_root_formula
        shell.do_add_root_formula("if(A, B)")
        shell.do_undo("")
        shell.do_print_formulas("")
        self.assertEqual(len(shell.tree.formulas), 1)

        # Testing add_formula
        shell.do_add_formula("if(A, B)")
        shell.do_undo("")
        shell.do_print_formulas("")
        self.assertEqual(len(shell.tree.formulas), 1)

        # Testing go_to
        shell.do_branch("")
        shell.do_go_to("2")
        shell.do_undo("")
        self.assertEqual(shell.current_node.node_id, 1)

        # Testing branch
        shell.do_undo("")
        self.assertEqual(len(shell.current_node.children), 0)

        # Testing delete
        shell.do_add_root_formula("and(a, b)")
        shell.do_delete_formula("1")
        shell.do_undo("")
        self.assertNotEqual(shell.tree.formulas[1], None)
        self.assertEqual(shell.tree.formulas[1].parent.formula, "PREMISE")

        shell.do_undo("")
        shell.do_print_current_node("")

        shell.do_add_formula("a")
        shell.do_add_formula("b")
        shell.do_delete_formula("1")
        shell.do_undo(None)
        print(shell.current_node)

    def test_undo2(self):
        print("\n\nUndo Test=======================================================")
        shell = TreeShell()
        shell.reset()

        shell.do_add_formula("or(a,b)")
        shell.do_add_formula("or(a,b)")
        shell.do_branch("1")
        shell.do_go_to("3")
        shell.do_add_formula("c")
        shell.do_delete_formula("2")
        print(shell.tree.formulas)
        print(shell.tree.nodes[1])

    def test_undo3(self):
        print("\n\nUndo Test 3=======================================================")
        shell = TreeShell()
        shell.reset()

        shell.do_add_formula("or(a,b)")
        shell.do_add_formula("or(a,b)")
        shell.do_branch("1")
        shell.do_go_to("2")
        shell.do_add_formula("c")
        shell.do_go_to("3")
        shell.do_add_formula("c")
        shell.do_delete_formula("4")
        shell.do_delete_formula("3")
        shell.do_undo("")
        shell.do_delete_formula("3")
        shell.do_undo("")
        print(shell.tree.formulas)
        print(shell.tree.nodes[1])

    def test_undo4(self):
        print("\n\nUndo Test 4=======================================================")
        shell = TreeShell()
        shell.reset()   
        
        shell.do_add_formula("or(a,b)")
        shell.do_add_formula("or(a,b)")
        shell.do_branch("1")
        shell.do_add_formula("b")
        shell.do_delete_formula("3")
        shell.do_go_to("2")
        shell.do_add_formula("b")
        shell.do_go_to("3")
        shell.do_add_formula("b")
        shell.do_delete_formula("4")
        shell.do_delete_formula("3")
        shell.do_delete_formula("2")
        shell.do_undo("")
        shell.do_undo("")
        shell.do_undo("")
        shell.do_delete_formula("3")
        shell.do_undo("")
        print(shell.tree.formulas)
        print(shell.tree.nodes[1])

if __name__ == "__main__":
    unittest.main()