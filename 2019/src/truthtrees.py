# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import argparse
from forseti.formula import Formula, Predicate, Symbol, Not, And, Or, If, Iff
import forseti.parser
from six import string_types
from src import util
from src.treeformulas import *

class TreeError(Exception):
    pass

class TreeNode(object):
    def __init__(self, node_id=None, unique_id = None):
        """
        @param: node_id is an integer corresponding to the printed id of the node
        @param: unique_id is the id of the node object
        @effect: Create a node class
        """
        self.formulas = []
        self.parent = None
        self.children = []
        self.closed = False
        self.open = False
        self.number = None
        self.node_id = node_id
        self.unique_id = unique_id
        self.parent_formula = None

    def __repr__(self):
        s = f"\nFormulas:\n"
        for formula in self.formulas:
            s += f"   {formula}\n"
        s += f"Closed: {self.closed}\n"
        s += f"ID: {self.node_id}\n"
        s += f"Parent: {self.parent.node_id if self.parent is not None else None}\n"
        s += f"Children: {[child.node_id for child in self.children]}\n"
        return s

    def print(self):
        print(self)

    def insert_formula(self, tf):
        """
        Add a formula into the correct location based on formula_id

        @param: tf is a TreeFormula object that is going to be inserted into the node
        @effect: tf is inserted into self.formulas in the correct location
        """
        for i in range(len(self.formulas)):
            if tf.formula_id <= self.formulas[i].formula_id:
                self.formulas.insert(i, tf)
                return
        self.formulas.append(tf)

    def add_formula(self, formula):
        """
        Add a formula to the node.

        @param: formula is a TreeFormula
        @effect:
            formula is added to the node
            formula node is marked as self
        """
        formula.node = self
        self.formulas.append(formula)

    def has_formula(self, check_formula):
        """
        Check to see if check_formula is in the current node

        @param: check_formula is a TreeFormula object
        @return: True if check_formula is in self.formulas
        """
        for formula in self.formulas:
            if formula.formula == check_formula:
                return True
        if self.parent is not None:
            return self.parent.has_formula(check_formula)
        return False

    def add_child(self, child_id, unique_id):
        """
        Add a child node to the self

        @parem: child_id and unique_id are integer corresponding to the id of child to be added
        @effect: Create a TreeNode using child_id and unique_id and add it to self.children
        @return: Return the node added
        """
        if self.closed:
            return [[], []]
        elif len(self.children) == 2:
            raise TreeError(f"Cannot add another child to {self.node_id}")
        else:
            child_node = TreeNode(child_id, unique_id)
            child_node.parent = self
            child_node.node_id = child_id
            child_node.parent.children.append(child_node)
            return child_node

    def in_ancestry(self, formula):
        """
        Check if a formula is in the ancestry of the node

        @param: formula is a TreeFormula object
        @return: Returns True if formula is in the current node or if it is in one of its ancestry node
        """
        if formula in self.formulas:
            return True
        if self.parent:
            return self.parent.in_ancestry(formula)
        return False

class TreeFormulaError(Exception):
    pass

class TruthTree(object):
    def __init__(self):
        self.root = TreeNode()
        self.root.unique_id = 1
        self.root.node_id = 1
        self.nodes = list() 
        self.formulas = list()
        self.node_memory = list()
        self.formulas_memory = list()
        self.offset_list()
        self.nodes.append(self.root)
        self.node_memory.append(self.root)

    def offset_list(self):
        """
        Helper function for TruthTree __init__

        Offset all of the lists in the truthtree so that id matches index

        @effect: Add None to all of the list in TreeFormula
        """
        self.nodes.append(None)
        self.formulas.append(None)
        self.node_memory.append(None)
        self.formulas_memory.append(None)

    def print(self):
        """
        For DEBUGGING

        Print out the list of nodes

        @return: Return an output_string that corresponds to what is being printed
        """
        output_string = "Printing List of Nodes.\n"
        print("Printing List of Nodes")
        for node in self.nodes:
            if node:
                output_string += str(node)
                node.print()
        return output_string

    def print_formulas(self):
        """
        For DEBUGGING

        Print all of the formula in the Tree
        """
        for formula in self.formulas:
            if formula:
                print(formula)

    def add_formula(self, node, arg,  formula = None):
        """
        Add a formula to node

        @param: node is a TreeNode 
        @param: arg is the arg argument for the TreeFormula object
        @param: formula is a string corresponding to the forsetti parsed arg
        @effect: Create a TreeFormula object using arg and Formula and add it to node
        @return: Return the TreeFormula added to the node
        """
        tf = TreeFormula(arg, formula, len(self.formulas), len(self.formulas_memory))
        node.add_formula(tf)
        self.formulas.append(tf)
        self.formulas_memory.append(tf)
        return tf

    def add_premise_formula(self, arg, formula = None):
        """
        Add a premise to the tree

        @param: arg is the arg argument for the TreeFormula object
        @param: formula is a string corresponding to the forsetti parsed arg
        @effect: Create a TreeFormula object using arg and Formula and add it to node
        @return: Return the TreeFormula added to the node
        """
        index = 1
        while (index < len(self.formulas)):
            if self.formulas[index].parent is None:
                break
            if self.formulas[index].parent.formula != "PREMISE":
                break
            index += 1


        tf = TreeFormula(arg, formula, index, len(self.formulas_memory))
        tf.node = self.root
        self.root.insert_formula(tf)
        self.formulas.insert(index, tf)
        self.formulas_memory.append(tf)
        self.readjust_formula_id()
        return tf



    def readjust_formula_id(self, lowerbound = 1):
        """
        Readjust the formula id of all formulas in self.formulas

        @effect: Make all of the TreeFormula's formula_id match there location in self.formulas
        """
        for i in range(lowerbound, len(self.formulas)):
            if self.formulas[i]:
                self.formulas[i].formula_id = i

    def readjust_node_id(self, lowerbound = 1):
        """
        Readjust the formula id of all nodess in self.nodess

        @effect: Make all of the TreeNode's node_id match there location in self.nodes
        """
        for i in range(lowerbound, len(self.nodes)):
            if self.nodes[i]:
                self.nodes[i].node_id = i


    def delete_formula(self, formula):
        """
        Remove a formula from the tree
        @param: formula is a TruthFormula object
        @effect: Remove formula from self.formulas and adjust formula id's as needed
        @effect: Remove formula from its parent and children
        @effect: Uncheckmark parent if delete_formula is used to checkmark parent
        @effect: Invalidate all children if formula was valid
        """

        # Looking for TreeFormula to remove from node
        f_list = self.node_memory[formula.node.unique_id].formulas
        index = -1
        # Searching for a match
        for i in range(len(f_list)):
            if f_list[i].formula_id == formula.formula_id:
                index = i
                break
        f_list.pop(index)

        # Removing the formula from it's parent and children
        if formula.parent and formula.parent.formula != "PREMISE":
            parent = formula.parent
            formula.remove_parent()
            formula.parent = parent
        for f in formula.children:
            f.parent = None
            f.parent_checkmark = False
        if formula.parent_checkmark:
            formula.parent.checkmarked = False
        formula.mark_child_not_valid()

        # Remove formula from the tree
        self.formulas.pop(formula.formula_id)
        self.readjust_formula_id(formula.formula_id)

    def delete_node(self, u_node_id):
        """
        Delete a node from the tree. Helper function for deleting a branch

        @param: u_node_id is an int corresponding the unique_id of the node to be deleted
        @effect: The node coresponding to u_node_id is deleted and all formulas stored in the node is deleted from the Tree
        """
        node = self.node_memory[u_node_id]

        # Delete the formulas from the tree, but keep the formulas in node for restoration later
        copy = list(node.formulas)
        for f in node.formulas:
            self.delete_formula(f)
        node.formulas = copy

        # Remove node from parent_formula
        parent_formula = node.parent_formula
        parent_formula.node_children.remove(node)

        # Remove the node from parent
        node.parent.children.remove(node)

        # Remove the node from the Tree node list
        self.nodes.pop(node.node_id)
        self.readjust_node_id(node.node_id)

    def readd_node(self, u_node_id):
        """
        Re-add a previously deleted node

        @effect: Restore a node from being delted
        @effect: Add node back to TruthTree
        @effect: Restore the formulas in the node
        """
        child_node = util.return_element_from_list(int(u_node_id), self.node_memory)
        child_node.parent.children.append(child_node)
        self.nodes.insert(child_node.node_id, child_node)
        child_node.parent_formula.node_children.append(child_node)
        print(len(child_node.formulas))
        for f in child_node.formulas:
            self.undelete_formula_helper(f.unique_id)

    def undelete_formula(self, unique_id):
        """
        Function to readd a formula

        @param: unique_id is the id corresponding to the unique id of the formula to be readded
        @effect: The TreeFormula with unique_id is readded to the tree and node that it was deleted from
        @effect: Restore any validity marking and checkmarking from the formula being deleted
        """
        tf = util.return_element_from_list(int(unique_id), self.formulas_memory)
        node = util.return_element_from_list(tf.node.node_id, self.nodes)
        self.undelete_formula_helper(unique_id)
        node.insert_formula(tf)

    def undelete_formula_helper(self, unique_id):
        """
        Helper Function for undelete_formula

        @effect: Add formula with unique_id back into TruthTree
        @effect: Restore all checkmark and valid marking if necessary
        """
        # Find the formula
        tf = util.return_element_from_list(int(unique_id), self.formulas_memory)

        # Insert formula into TruthTree
        self.formulas.insert(int(tf.formula_id), tf)
        self.readjust_formula_id(int(tf.formula_id))

        # Restore parent if needed
        if tf.parent and tf.parent.formula != "PREMISE":
            parent = util.return_element_from_list(tf.parent.formula_id, self.formulas)
            parent.children.append(tf)
        for f in tf.children:
            f.parent = tf

        # Checkmark again and mark valid again if necessary
        if tf.valid:
            tf.mark_child_valid()
        if tf.checkmarked:
            for f in tf.children:
                f.parent_checkmark = True
        if tf.parent_checkmark:
            tf.parent.checkmarked = True

    def branch(self, node, formula = None):
        """
        Branch on a node using a parent formula

        @param: Node is a TreeNode that is being branched on
        @param: formula is the "parent" formula of the branch
        return: true on successful branch
                false on not successful
        """
        print(f"Branching on node {node.node_id}")
        child_node_id1 = len(self.nodes)
        child_node_id2 = len(self.nodes)+1
        child_node1 = node.add_child(child_node_id1, len(self.node_memory))
        child_node2 = node.add_child(child_node_id2, len(self.node_memory)+1)
        print(f"Adding nodes {child_node_id1} and {child_node_id2}")
        self.nodes.append(child_node1)
        self.nodes.append(child_node2)
        self.node_memory.append(child_node1)
        self.node_memory.append(child_node2)
        child_node1.parent_formula = formula
        child_node2.parent_formula = formula
        formula.node_children.append(child_node1)
        formula.node_children.append(child_node2)

# def runner(formulas, goal):
#     """

#     :param formulas:
#     :type formulas: List[string_types]
#     :param goal:
#     :type goal: string_types
#     :return:
#     """

#     if isinstance(formulas, string_types):
#         formulas = [formulas]

#     if not isinstance(goal, string_types):
#         raise TypeError("Expected str for goal, got " + str(type(goal)))

#     parsed_formulas = []
#     for formula in formulas:
#         formula = formula.strip()
#         if len(formula) == 0:
#             continue
#         parsed_formulas.append(forseti.parser.parse(formula))

#     goal = forseti.parser.parse(goal)
#     return TruthTree(parsed_formulas, goal)

# if __name__ == "__main__":
#     PARSER = argparse.ArgumentParser(description="Generate Truth Table for a logical formula")
#     PARSER.add_argument('--formulas', metavar='formula', type=str, nargs="*", help='Logical formula')
#     PARSER.add_argument('--goal', metavar='goal', type=str, help='Goal Formula')
#     PARSER_ARGS = PARSER.parse_args()
#     SHORT_TRUTH_TABLE = runner(PARSER_ARGS.formulas, PARSER_ARGS.goal)
#     if SHORT_TRUTH_TABLE.root.is_closed():
#         print("Argument is valid")
#     else:
#         print("Argument is invalid")
