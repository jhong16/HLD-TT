import cmd
import forseti.parser
import shlex
import sys

from src import truthtrees
from src import util
from src import treeformulas


class TreeShell(cmd.Cmd):
    def __init__(self, completekey='tab', stdin=None, stdout=None):
        super().__init__(completekey=completekey, stdin=stdin, stdout=stdout)
        self.intro = "Welcome to the tree shell.\nType help or ? to list commands.\n"
        self.prompt = "~/ $ "
        self.tree = truthtrees.TruthTree()
        self.root = self.tree.root
        self.current_node = self.root
        self.history = list()
        self.history_arg = list()
        self.current_command = 0
        self.PREMISE_FORMULA = truthtrees.TreeFormula(None, "PREMISE", 0, 0)
        self.PREMISE_FORMULA.valid = True
        self.finish = False

    def do_reset(self, arg):
        """
        Allow the user to reset the tree.
        WARNING: Cannot be undone

        Usage:
            reset
        """
        self.reset()

    def reset(self):
        """
        Reset the tree and the history
        """
        self.intro = "Welcome to the tree shell.\nType help or ? to list commands.\n"
        self.prompt = "~/ $ "
        self.tree = truthtrees.TruthTree()
        self.root = self.tree.root
        self.current_node = self.root
        self.history = list()
        self.history_arg = list()
        self.current_command = 0
        self.finish = False
        print("Resetting tree and command history", file=self.stdout)
        print(str(self.intro), file=self.stdout)

    def add_history(self, command, his_arg):
        """
        @param: command is a string corresponding to the command being stored into history
        @param: his_arg is a string the argumenent needed for undo-redo
        """
        if self.current_command == 0:
            self.history.clear()
            self.history_arg.clear()
            self.history.append(command)
            self.history_arg.append(his_arg)
        else: 
            g = self.history[0:self.current_command]
            g.append(command)
            self.history = g
            v = self.history_arg[0: self.current_command]
            v.append(his_arg)
            self.history_arg = v
        self.current_command += 1

    def delete_leaf_branch_helper(self, argument):
        """
        Delete the branch of a node only if its children are leaf nodes
        @param: argument contains the unique id of the children sepereated by a space
        @effect: The nodes with those unique id are deleted from the tree 
        """
        parent_unique_id, child_u_ids = util.history_parser(argument)
        child_u_id1, child_u_id2 = util.history_parser(child_u_ids)
        node = util.return_element_from_list(int(parent_unique_id), self.tree.node_memory)
        print(len(self.tree.node_memory))
        self.tree.delete_node(int(child_u_id2))
        self.tree.delete_node(int(child_u_id1))
        node.children.clear()

    def do_delete_branch(self, arg):
        """
        Delete branch on current node.
        Current node children must be leaves

        Usage:
            delete_branch
        """
        if len(self.current_node.children) == 0:
            print("Current node has no children", file=self.stdout)
            return

        child1 = self.current_node.children[0]
        child2 = self.current_node.children[1]

        if len(child1.children) != 0 or len(child2.children) != 0:
            print("Current node's children are not leaves", file=self.stdout)
            return

        self.tree.delete_node(child2.unique_id)
        self.tree.delete_node(child1.unique_id)
        print(f"Deleted node {child1.node_id} and {child2.node_id}", file=self.stdout)
        self.add_history(f"delete_branch", f"{self.current_node.unique_id} {child1.unique_id} {child2.unique_id}")
        return

    def delete_formula_again(self, arguments):
        """
        Helper function to help delete a formula again. Used for redo and undo.

        @param: arguments is the unique_id of the formula to be deleted
        """
        tf = util.return_element_from_list(int(arguments), self.tree.formulas_memory)
        self.tree.delete_formula(tf)

    def redo_branch(self, arguments):
        """
        Helper function to redo a branch again.

        arguments:
           argument is in the form "[parent_unique__id] [child_unique_id1] [child_unique_id2]"
        """
        parent_u_id, child_nodes = util.history_parser(arguments)
        child1_u_id, child2_u_id = util.history_parser(child_nodes)
        parent_node = util.return_element_from_list(int(parent_u_id), self.tree.node_memory)

        self.tree.readd_node(child1_u_id)
        self.tree.readd_node(child2_u_id)
        self.tree.readjust_formula_id()

    def do_go_to(self, arg):
        """
        Moves to a node
        
        Usage: go_to [node_id]
        """
        if not arg.isdigit():
            print(f"Invalid argument: {arg}", file=self.stdout)
            return

        node_id = int(arg)
        n = util.return_element_from_list(node_id, self.tree.nodes)
        if n is None:
            print(f"Node {node_id} does not exist", file=self.stdout)
            return

        print(f"Going to node {node_id}", file=self.stdout)
        self.add_history(f"go_to {node_id}", f"{self.current_node.node_id}")
        self.current_node = self.tree.nodes[node_id]
        return

    def do_print_tree(self, arg):
        """
        Print the Tree to the cli

        Usage:
            print_tree
        """
        tree = self.tree.print()
        return tree

    def do_print_current_node(self, arg):
        """
        Print the current node to the cli

        Usage:
            print_current_node
        """
        self.current_node.print()

    def do_add_root_formula(self, arg):
        """
        Add formula to the root

        Usage:
            add_root_formula [formula]
        """
        if self.root.closed:
            print("Root node is closed", file=self.stdout)
            return
        formula, error = util.parse_formula(arg)
        arg = arg.replace(' ','')
        if formula:
            print(f"Adding formula {formula} as {len(self.tree.formulas)}", file=self.stdout)
            tf = self.tree.add_premise_formula(arg, formula)
            tf.parent = self.PREMISE_FORMULA
            tf.valid = True
            self.add_history(f"add_root_formula {arg}", f"{tf.unique_id}")
            return
        print(f"{error}", file=self.stdout)
        return

    def do_add_formula(self, arg):
        """
        Add formula to the root

        Usage:
            add_formula [formula]
        """
        if self.current_node.closed:
            print("Current node is closed", file=self.stdout)
            return
        # Validate Formula
        formula, error = util.parse_formula(arg)
        if formula:
            arg = arg.replace(' ','')
            print(f"Adding formula {formula} as {len(self.tree.formulas)}", file=self.stdout)
            tf = self.tree.add_formula(self.current_node, arg, formula)
            self.add_history(f"add_formula {arg}", f"{tf.unique_id}")
            return
            print(f"{error}", file=self.stdout)
        return 

    def do_delete_formula(self, arg):
        """
        Delete formula based on id

        Usage:
            delete_formula [formula_id]
        """

        if not arg.isdigit():
            print(f"Invalid argument: {arg}")
            return

        formula_id = int(arg)
        tf = util.return_element_from_list(formula_id, self.tree.formulas)

        if tf is None:
            print(f"Formula {formula_id} not found", file=self.stdout)
            return

        if len(tf.node_children) > 0:
            output_str = "Cannot delete. Formula branched to nodes "
            for n in tf.node_children:
                output_str += str(n.node_id) + " "
            print(output_str, file=self.stdout)
            return

        self.tree.delete_formula(tf)
        self.add_history(f"delete_formula {tf.node.node_id}", f"{tf.unique_id}")
        print( f"Deleting formula {formula_id}", file=self.stdout)
        return

    def do_branch(self, arg):
        """
        Branch on current node using a formula

        Usage:
            branch [formula_id]
        """
        if self.current_node.closed:
            print("Current Node is closed", file=self.stdout)
            return

        if not arg.isdigit():
            print("Invalid Argument", file=self.stdout)
            return

        arg = arg.replace(' ','')
        tf = util.return_element_from_list(int(arg), self.tree.formulas)

        if tf is None:
            print("Formula not found", file=self.stdout)
            return

        if not self.current_node.in_ancestry(tf):
            print("Formula not in ancestry", file=self.stdout)
            return

        main_connector, dummy, dummy = tf.decompose()
        if main_connector == "and" or main_connector is None:
            print("Formula does not branch", file=self.stdout)
            return

        try:
            self.tree.branch(self.current_node, tf)
            child1 = self.current_node.children[0]
            child2 = self.current_node.children[1]
            self.add_history(f"branch {arg}", f"{self.current_node.unique_id} {child1.unique_id} {child2.unique_id}")
            print(f"branched on node {self.current_node.node_id} to create node {child1.node_id} and {child2.node_id}", file=self.stdout)
        except truthtrees.TreeError as te:
            print(str(te), file=self.stdout)
        return

    def do_print_formulas(self, arg):
        """
        Print all of the formula to the cli

        Usage: 
            print_formulas
        """
        self.tree.print_formulas()

    def do_print_history(self, arg):
        """
        Print the history of tree commands to the cli

        Usage:
            print_history
        """
        print("\n\nHistory:")
        for i in range(len(self.history)):
            if self.history[i]:
                print(f"{i}: {self.history[i]}")

    def do_EOF(self, arg):
        print("\nExiting. Bye-bye")
        return True

    def do_undo(self, dummy):
        """
        Undo the previous command on the trees

        Usage:
            undo
        """
        if self.current_command == 0:
            print("Nothing to undo", file=self.stdout)
            return
        self.current_command -= 1
        last_command = self.history[self.current_command]
        command, arguments = util.history_parser(last_command)
        arg = self.history_arg[self.current_command]

        if command is None:
            command = last_command

        if command == "add_root_formula":
            tf = util.return_element_from_list(int(arg), self.tree.formulas_memory)
            self.tree.delete_formula(tf)
        elif command == "add_formula":
            self.delete_formula_again(arg)
        elif command == "go_to":
            self.current_node = self.tree.nodes[int(arg)]
        elif command == "branch":
            self.delete_leaf_branch_helper(arg)
        elif command == "delete_formula":
            self.tree.undelete_formula(arg) 
        elif command == "checkmarked":
            tf = util.return_element_from_list(int(arg), self.tree.formulas_memory)
            tf.uncheckmark()
        elif command == "closed":
            node = util.return_element_from_list(int(arg), self.tree.nodes_memory)
            node.closed = False
        elif command == f"marked_formula_parent":
            child_id, parent_id = util.history_parser(arg)
            child_f = util.return_element_from_list(int(child_id), self.tree.formulas_memory) 
            child_f.remove_parent()
        elif command == "All_Closed" or command == "Mark_Open":
            print("Tree is finished. Nothing to undo.", file=self.stdout)
            self.current_command += 1
            return
        elif command == f"delete_branch":
            self.redo_branch(arg)
        else:
            print(f"ERROR: Undo for {command} not yet implemented", file=self.stdout)
            return
        print("undo successful", file=self.stdout)
        return

    def do_redo(self, arg):
        """
        Redo the previously undo command

        Usage:
            redo
        """
        if self.current_command >= len(self.history):
            print("Nothing to redo", file=self.stdout)
            return
        else:
            last_command = self.history[self.current_command]
            command, arguments = util.history_parser(last_command)
            arg = self.history_arg[self.current_command]

            if command is None:
                command = last_command

            if command == "add_root_formula":
                self.tree.undelete_formula(arg)
            elif command == "add_formula":
                self.tree.undelete_formula(arg)
            elif command == "go_to":
                self.current_node = self.tree.nodes[int(arguments)]
            elif command == "branch":
                self.redo_branch(arg)
            elif command == "delete_formula":
                self.delete_formula_again(arg)
            elif command == "checkmarked":
                tf = util.return_element_from_list(int(arg), self.tree.formulas_memory)
                tf.checkmark()
            elif command == "closed":
                node = util.return_element_from_list(int(arg), self.tree.formulas_memory)
                node.closed = True
            elif command == f"marked_formula_parent":
                child_id, parent_id = util.history_parser(arguments)
                parent_f = util.return_element_from_list(int(parent_id), self.tree.formulas) 
                child_f = util.return_element_from_list(int(child_id), self.tree.formulas) 
                parent_f.children.append(child_f)
                child_f.parent = parent_f
                if parent_f.valid:
                    child_f.valid = True
                    child_f.mark_child_valid()
            elif command == "All_Closed" or command == "Mark_Open":
                print("Tree is finished. Nothing to undo.", file=self.stdout)
                self.current_command -= 1
                return
            elif command == "delete_branch":
                self.delete_leaf_branch_helper(arg)
            else:
                print(f"ERROR: Redo for {command} not yet implemented", file=self.stdout)
                return
            self.current_command += 1
            print("redo successful", file=self.stdout)
            return

    def do_mark_parent(self, arg):
        """
        Mark a parent for a formula

        Usage:
            mark_formula [child_node] [parent_node]
        """
        output_string = ""
        child_id, parent_id = util.history_parser(arg)
        if child_id is None:
            print("Invalid Argument. Needs two arguments", file=self.stdout)
            return 
        child_id.replace(' ','')
        parent_id.replace(' ','')
        if not parent_id.isdigit():
            print(f"Invalid Argument {parent_id}", file=self.stdout)
            return
        if not child_id.isdigit():
            print(f"Invalid Argument {child_id}", file=self.stdout)
            return
        if child_id <= parent_id:
            print("Child Node should have id greater then parent", file=self.stdout)
            return
        parent_formula = util.return_element_from_list(int(parent_id), self.tree.formulas)
        child_formula = util.return_element_from_list(int(child_id), self.tree.formulas)               
        if parent_formula is None:
            print(f"Formula {parent_id} not found", file=self.stdout)
            return
        if child_formula is None:
            print(f"Formula {child_id} not found", file=self.stdout)
            return
        if child_formula.parent and child_formula.parent.arg == "PREMISE":
            print(f"Formula {child_id} is a premise and therefore does not need a parent", file=self.stdout)
            return

        if parent_formula == child_formula:
            parent_formula.add_formula_children(child_formula)
            print( f"Marked formula {child_id}'s parent as {parent_id}", file=self.stdout)
            self.add_history(f"marked_formula_parent {child_id} {parent_id}", f"{child_formula.unique_id} {parent_formula.unique_id}")
            return
        if parent_formula.in_decomposition(child_formula):
            main_connector, dummy, dummy = parent_formula.decompose()
            if main_connector == "or" or main_connector == "if":
                if child_formula.node.parent_formula is None:
                    string = f"Cannot decompose parent_formula into root node"
                    print(string, file=self.stdout)
                    return
                if child_formula.node.parent_formula is None or child_formula.node.parent_formula != parent_formula:
                    print(f"Node decomposed from {child_formula.node.parent_formula.formula_id} not {parent_formula.formula_id}", file=self.stdout)
                    return
            parent_formula.add_formula_children(child_formula)
            print( f"Marked formula {child_id}'s parent as {parent_id}", file=self.stdout)
            self.add_history(f"marked_formula_parent {child_id} {parent_id}", f"{child_formula.unique_id} {parent_formula.unique_id}")
            return
        
        string = f"Formula {child_formula} does not decompose from {parent_formula} "
        print(string, file=self.stdout)
        return

    def do_close(self, arg):
        """
        Closes Current Node using formula from it's ancestry

        Usage:
            close [formula_id1] [formula_id2]
        """
        child_id, parent_id = util.history_parser(arg)
        if child_id is None:
            return "Invalid Argument. Needs two arguments"
        child_id.replace(' ','')
        parent_id.replace(' ','')

        # Error checking
        if not child_id.isdigit():
            print(f"Invalid Argument {child_id}")
            return
        if not parent_id.isdigit():
            print(f"Invalid Argument {parent_id}")
            return

        formula_1 = util.return_element_from_list(int(parent_id), self.tree.formulas)
        formula_2 = util.return_element_from_list(int(child_id), self.tree.formulas)
        
        # Error Checking
        if not formula_1:
            print(f"Formula {parent_id} not found", file=self.stdout)
            return
        if not formula_2:
            print(f"Formula {child_id} not found", file=self.stdout)
            return
        if not formula_1.valid:
            print(f"Formula {parent_id} does not have parent", file=self.stdout)
            return
        if not formula_2.valid:
            print(f"Formula {child_id} does not have parent", file=self.stdout)
            return
        if not self.current_node.in_ancestry(formula_1):
            print(f"Formula {parent_id} is not in acestory of current node", file=self.stdout)
            return
        if not self.current_node.in_ancestry(formula_2):
            print(f"Formula {child_id} is not in acestory of current node", file=self.stdout)
            return

        #Checking if negation of formula 1 equal formula 2
        not_formula_1 = truthtrees.TreeFormula(f"not({formula_1.arg})", "d")
        if not_formula_1 == formula_2:
            self.current_node.closed = True
            print(f"Current Node Successfully Closed", file=self.stdout)
            self.add_history(f"closed {self.current_node.node_id}", None)
            return
        else:
            print(f"Formula are not negation of each other", file=self.stdout)
            return
    
    def do_reopen(self, arg):
        """
        Reopen a closed node

        Usage:
            reopen [node-id]
        """
        if arg.isdigit():
            node =util.return_element_from_list(int(arg), self.tree.nodes)
            if node is None:
                print(f"Node {arg} not found", file=self.stdout)
            elif node.closed:
                node.closed = False
                self.add_history(f"reopen {arg}", None)
                print(f"reopen {arg}", file=self.stdout)
            else:
                print(f"Node {arg} not closed", file=self.stdout)
        else:
            print(f"Invalid Argument", file=self.stdout)
        return

    def and_check(self,formula, formula_l, node, in_current):
        """
        Helper function for checkmark
        Go through the tree and check if the formula list are in the correct position of the tree
        """
        if node.closed:
            return True
        #Collecting 
        for f in formula_l:
            if f.node.node_id == node.node_id:
                in_current.append(f)
        
        if len(in_current) == 1:
            if in_current[0] == formula:
                return True

        if len(in_current) >= 2:
            and_total = f"and({in_current[0].arg},{in_current[1].arg})"
            if truthtrees.TreeFormula(and_total, "d") == formula:
                return True

            for i in range(2,len(in_current)):
                if truthtrees.TreeFormula(f"and({and_total},{in_current[i].arg})", "d") == formula:
                    return True

        if len(node.children) == 0:
            return False
        l = list(in_current)
        r = list(in_current)
        return self.and_check(formula, formula_l, node.children[0],l) and self.and_check(formula, formula_l, node.children[1],r)

    def or_check(self, formula, formula_l, node):
        """
        Helper function for checkmark
        Go through the tree and check if the formula list are in the correct position of the tree
        """
        if node.closed:
            return True
        if len(node.children) == 0:
            print(f"Not branched on {node.node_id}")
            return False

        #Collecting 
        in_left = list()
        in_right = list()
        left_child_id = node.children[0].node_id
        right_child_id = node.children[1].node_id
        for f in formula_l:
            if f.node.node_id == left_child_id:
                if f.node.parent_formula.unique_id != formula.unique_id:
                    return False
                in_left.append(f)
            if f.node.node_id == right_child_id:
                if f.node.parent_formula.unique_id != formula.unique_id:
                    return False
                in_right.append(f)

        if len(in_left) > 0 and len(in_right) > 0:
            left_conjunction = ""
            right_conjunction =""

            if len(in_left) >= 2:
                left_conjunction = f"and({in_left[0].arg},{in_left[1].arg})"
                for i in range(2, len(in_left)):
                    left_conjunction = f"and({in_left[i].arg},{left_conjunction})"

            if len(in_right) >= 2:
                right_conjunction = f"and({in_right[0].arg},{in_right[1].arg})"
                for i in range(2, len(in_right)):
                    right_conjunction = f"and({in_right[i].arg},{right_conjunction})"

            if len(in_right) == 1:
                right_conjunction = in_right[0].arg

            if len(in_left) == 1:
                left_conjunction = in_left[0].arg

            if truthtrees.TreeFormula(f"or({left_conjunction},{right_conjunction})", "d") == formula:
                return True

        return self.or_check(formula, formula_l, node.children[0]) and self.or_check(formula, formula_l, node.children[1])

    def do_checkmark(self, arg):
        """
        Checkmark a formula based on it's children 

        Usage:
            checkmark [node-id]
        """
        # Error checking
        if not arg.isdigit():
            print(f"Invalid Argument {arg}")
            return

        formula_1 = util.return_element_from_list(int(arg), self.tree.formulas)
        node = util.return_element_from_list(formula_1.node.node_id, self.tree.nodes)

        # Error checking
        if formula_1 is None:
            print(f"Formula {arg} not found", file=self.stdout)
            return

        # Formula is already checkmarked
        if formula_1.checkmarked:
            print(f"Formula {arg} is already heckmarked", file=self.stdout)
            return
        
        # Checking if checkmark is possible
        main_connector, arg1, arg2 = formula_1.decompose()
        if main_connector is None:
            formula_1.checkmark()
            print(f"Formula {arg} checkmarked", file=self.stdout)
            self.add_history(f"checkmarked {arg}", f"{formula_1.unique_id}")
            return
        elif main_connector == "and":
            in_current = list()
            if self.and_check(formula_1, formula_1.children, node, in_current):
                formula_1.checkmark()
                print(f"Formula {arg} checkmarked", file=self.stdout)
                self.add_history(f"checkmarked {arg}", f"{formula_1.unique_id}")
                return
            else:
                print(f"Cannot checkmark", file=self.stdout)
                return
        elif main_connector == "or":
            if self.or_check(formula_1, formula_1.children, node):
                formula_1.checkmark()
                print(f"Formula {arg} checkmarked", file=self.stdout)
                self.add_history(f"checkmarked {arg}", f"{formula_1.unique_id}")
                return
            else:
                print(f"Cannot checkmark", file=self.stdout)
                return
        # Checking for iff
        else:
            in_current = list()
            if self.or_check(formula_1, formula_1.children, node):
                formula_1.checkmark()
                print(f"Formula {arg} checkmarked", file=self.stdout)
                self.add_history(f"checkmarked {arg}", f"{formula_1.unique_id}")
                return
            elif self.and_check(formula_1, formula_1.children, node, in_current):
                formula_1.checkmark()
                print(f"Formula {arg} checkmarked", file=self.stdout)
                self.add_history(f"checkmarked {arg}", f"{formula_1.unique_id}")
                return
            else:
                print(f"Cannot checkmark", file=self.stdout)
                return

    def find_path(self, n, l):
        """
        Helper Function for mark open.
        Store the path from the current node to the root node

        @return: A list of node_id that is in the path from the current node to the root
        """
        l.insert(0, n.node_id)
        if n.node_id == 1:
            return 
        self.find_path(n.parent, l)

    def do_mark_open(self, arg):
        """
        Mark the current node as open

        Usage: 
            mark_open
        """
        if len(self.current_node.children) != 0:
            print("Current Node has children", file=self.stdout)
            return

        path_to_root = list()
        self.find_path(self.current_node, path_to_root)
        for node_id in path_to_root:
            node = util.return_element_from_list(node_id, self.tree.nodes)
            for formula in node.formulas:
                if formula.checkmarked:
                    continue
                if formula.parent is None:
                    print(f"Formula {formula.formula_id} doesn't have a parent", file=self.stdout)
                    return
                main_connector, decom1, decom2 = formula.decompose()
                if main_connector is None:
                    continue

                if len(formula.children) == 0:
                    string = f"Formula {formula.formula_id} has not decomposed"
                    print(string, file=self.stdout)
                    return

                and_conjecture = ""
                for f in formula.children:
                    if f.node.node_id in path_to_root:
                        if and_conjecture == "":
                            and_conjecture = f.arg
                        else:
                            and_conjecture = f"and({and_conjecture},{f.arg})"
                if main_connector == "and":
                    if truthtrees.TreeFormula(and_conjecture, "d") == formula:
                            continue
                    else: 
                        print(f"Incorrect decomposition of {formula.formula_id}", file=self.stdout)
                        return
                if main_connector == "or":
                    if formula.in_decomposition(truthtrees.TreeFormula(and_conjecture, "d")):
                        count = 0
                        for cn in formula.node_children:
                            if cn.node_id in path_to_root:
                                count += 1
                        if count == 0:
                            string = f"{formula.formula_id} has not been decomposed into this branch yet"
                            print(string, file=self.stdout)
                            return
                        continue
                    else: 
                        print(f"Incorrect decomposition of {formula.formula_id}", file=self.stdout)
                        return
                else:
                    if truthtrees.TreeFormula(and_conjecture, "d") == formula:
                        continue
                    if formula.in_decomposition(truthtrees.TreeFormula(and_conjecture, "d")):
                        continue
                    else: 
                        print(f"Incorrect decomposition of {formula.formula_id}", file=self.stdout)
                        return
        self.finish = True
        self.add_history("Mark_Open", None)
        self.current_node.open = True
        print(f"Finish. Path to {self.current_node.node_id} open.", file=self.stdout)
        return
        
    def find_closed_branch(self, node):
        """
        Helper function for check all closed 

        """
        if node.parent_formula is not None and not node.parent_formula.checkmarked:
            return False, f"Formula {node.parent_formula.formula_id} is not checkmarked" 
        if len(node.children) == 0:
            if node.closed:
                return True, None
            else:
                return False, f"Node {node.node_id} not closed"
        success1, failure1 = self.find_closed_branch(node.children[0])
        success2, failure2 = self.find_closed_branch(node.children[1])
        if success1 and success2:
            return True, None
        if success1:
            return False, failure2
        return False, failure1

    def do_check_all_closed(self, arg):
        """
        Check if all branches are closed

        Usage:
            check_all_closed
        """
        success, failure = self.find_closed_branch(self.root)
        if success:
            self.finish = True
            self.add_history("All_Closed", None)
            print(f"Finish. All Branches closed", file=self.stdout)
            return "True"
        print(failure, file=self.stdout)
        return "False"

    def do_check_any_open(self, arg):
        """
        Check if any branches are open

        Usage:
            check_any_open
        """
        success = False
        for node in self.tree.nodes:
            if node is None:
                continue
            if len(node.children) == 0:
                if node.open:
                    success = True
        if success:
            self.finish = True
            self.add_history("1_Open", None)
            print(f"Finish. At least 1 branch open", file=self.stdout)
            return "True"
        else:
            print("No Branches Marked Open.", file=self.stdout)
            return "False"
            
if __name__ == '__main__':
    try:
        TreeShell(stdout=sys.stdout).cmdloop()
    except KeyboardInterrupt:
        print("\nExiting. Bye-bye")
