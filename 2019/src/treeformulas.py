# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import argparse
from forseti.formula import Formula, Predicate, Symbol, Not, And, Or, If, Iff
import forseti.parser
from six import string_types
from src import util

"""
TreeFormula is an object used to represent a boolean expression in predicate logic.

TreeFormula is used in TruthTree class.

Currently, TreeFormula can be decomposed, check for equality, and can check
if another TreeFormula is in it's decomposition.
"""

def pretty_print(formula):
    """
    :param formula:
    :return:
    """
    if isinstance(formula, Symbol) or isinstance(formula, Predicate):
        text = str(formula)
    elif isinstance(formula, Not):
        text = "¬" + pretty_print(formula.args[0])
    else:
        temp = []
        for arg in formula.args:
            temp.append(pretty_print(arg))
        if isinstance(formula, And):
            text = " ∧ ".join(temp)
        elif isinstance(formula, Or):
            text = " ∨ ".join(temp)
        elif isinstance(formula, If):
            text = " → ".join(temp)
        elif isinstance(formula, Iff):
            text = " ↔ ".join(temp)
        else:
            raise TypeError("Invalid Formula Type: " + str(type(formula)))
        text = "(" + text + ")"
    return text.strip()

class TreeFormula(object):
    def __init__(self, arg, formula = None, vis_id = None, mem_id = None):
        """
        @param: arg is a forsetti parseable formula
        @param: formula is the the string corresponding to what forsetti parses arg to
        @param: vis_id is the id corresponding to the id that is printed in the truth tree
        @param: mem_id is the unique id of the formula object
        @effect: Create the TreeFormula of the description above
        """
        if formula is None:
            formula = util.parse_formula(arg)
        self.formula = formula
        self.node = None
        self.arg = arg
        self.formula_id = vis_id
        self.checkmarked = False
        self.closed = False
        self.valid = False
        self.parent = None
        self.children = list()
        self.unique_id = mem_id
        self.node_children = list()
        self.parent_checkmark = False

    def checkmark(self):
        """
        Checkmark the current formula 

        @effect: self.checkmark becomes True
        @effect: All of the children of self parent_checkmark paremeter is marked True
        """
        self.checkmarked = True
        for tf in self.children:
            tf.parent_checkmark = True

    def uncheckmark(self):
        """
        Uncheckmark the current formula

        @effect: self.checkmark becomes False
        @effect: All of the children of self parent_checkmark paremeter is marked False
        """
        self.checkmarked = False
        for tf in self.children:
            tf.parent_checkmark = False

    def remove_parent(self):
        """
        Remove the parent from self

        @effect: self is removed from self.parent's children
        @effect: self.parent is set to None
        """
        if self.parent:
            if self.parent.formula != "PREMISE":
                self.parent.children.remove(self)
                if self.parent.valid:
                    self.valid = False
                    self.mark_child_not_valid()
        self.parent = None

    def verify(self):
        """
        Returns if a formula is valid

        Formula is valid if:
            1) It is a premise
            2) Its parent is valid

        @return: True if formula is valid. False elsewise.
        """
        if self.valid:
            return True
        if self.parent:
            if self.parent.formula == "PREMISE":
                return True
            else:
                return self.parent.verify()
        return False

    def decompose(self):
        """
        Decompose the current formula into its decomposition

        @return:
            Return up to two sets of formula where each set is a possible decompositon and a main connector
            Return the main connector of the decomposition (Either or, and, iff, None)
            Return two formula that are decomposition of the formula using arguments returned from decompose_formula_argument
        """
        main_connector, decom1, decom2 = decompose_formula_argument(self.arg)
        return main_connector, TreeFormula(decom1, "Dummy"), TreeFormula(decom2, "Dummy")

    def __repr__(self):
        return f"{self.formula_id}: {self.formula}"

    def __eq__(self, other):
        if (self is None and other is None):
            return True
        if (self is None):
            return False
        if (other is None):
            return False
        if (self.arg == other.arg):
            return True

        # Finding the main connector of the formulas
        original_connector1, v = util.find_main_connector(self.arg)
        original_connector2, v = util.find_main_connector(other.arg)

        # Checking the decomposition of both formulas
        main_connector1, other_decom1, other_decom2 = self.decompose()
        main_connector2, form2_decom1, form2_decom2 = other.decompose()

        #Converting iff to either its or counter-part or it and counter-part
        if main_connector1 == "iff" and main_connector2 == "or":
            main_connector1 = "or"
        if main_connector2 == "iff" and main_connector1 == "or":
            main_connector2 = "or"
        if main_connector1 == "iff" and main_connector2 == "and":
            main_connector1 = "and"
            v1, v2 = decompose_iff_into_if(self.arg)
            other_decom1 = TreeFormula(v1, "Dummy")
            other_decom2 = TreeFormula(v2, "Dummy")
        if main_connector2 == "iff" and main_connector1 == "and":
            main_connector2 = "and"
            v1, v2 = decompose_iff_into_if(other.arg)
            form2_decom1 = TreeFormula(v1, "Dummy")
            form2_decom2 = TreeFormula(v2, "Dummy")
        
        #If main connector is different
        if (main_connector1 != main_connector2):
            return False

        # Comparing literals
        if main_connector1 is None:
            return other_decom1.arg == form2_decom1.arg

        #If decompositions are the same
        if (other_decom1 == form2_decom1 and other_decom2 == form2_decom2) or (other_decom1 == form2_decom2 and other_decom2 == form2_decom1):
            return True

        #Try decomposing more
        if (original_connector1 == "and" and original_connector2 == "and"):
            return other.in_decomposition_lte(self) and self.in_decomposition_lte(other)
        if (original_connector1 == "or" and original_connector2 == "or"):
            return other.in_decomposition_lte(self) and self.in_decomposition_lte(other)

        #Not equal
        return False
    
    def in_decomposition(self, other):
        """
        Check to see if other is in self's decomposition

        @return: 
            True if other is in decomposition of self.
            Also return True if self == other
        """
        if other == self:
            return True
        return self.in_decomposition_lte(other)

    def in_decomposition_lte(self, other):
        """
        Helper Function for in_decomposition. Checks if other is actuallly in self decomposition
        
        @return: True if other is in self decomposition
                 False elsewise
        """
        # Decomposing self
        dummy, self_decom1, self_decom2 = self.decompose()
        original_connector, dummy = util.find_main_connector(self.arg) 

        # Testing if other is equal to decom 1 or 2
        if other == self_decom1:
            return True
        # self is a literal and cannot be decomposed
        if self_decom2.arg is None:
            return False
        if other == self_decom2:
            return True

        # Attempt to see if other is in self decomposition's decomposition 
        original_connector1, dummy = util.find_main_connector(self_decom1.arg) 
        original_connector2, dummy = util.find_main_connector(self_decom2.arg) 
        f1_in_decom1 = False
        f1_in_decom2 = False
        if original_connector1 == original_connector:
            f1_in_decom1 = self_decom1.in_decomposition(other)
        if original_connector2 == original_connector and not f1_in_decom1:
            f1_in_decom2 = self_decom2.in_decomposition(other)   
        
        # Success
        if f1_in_decom1 or f1_in_decom2:
            return True

        # Attempting to see if other decomposition's are in self decompositions (only if original connectors are the same)
        f1_original_connector1, dummy = util.find_main_connector(other.arg) 
        if f1_original_connector1 == original_connector:
            dummy, other_decom1, other_decom2 = other.decompose()
            return self.in_decomposition(other_decom1) and self.in_decomposition(other_decom2)

        # The two decompositions of iff
        if original_connector == "iff":
            a1, a2 = decompose_iff_into_if(self.arg)
            return TreeFormula(a1, "Dummy").in_decomposition(other) or TreeFormula(a2, "Dummy").in_decomposition(other) 
        if f1_original_connector1 == "iff":
            dummy, a1, a2 = decompose_formula_argument(other.arg)
            return self.in_decomposition(TreeFormula(a1, "Dummy")) and self.in_decomposition(TreeFormula(a2, "Dummy"),)

        return False
 
    def mark_child_not_valid(self):
        """
        Mark the children of self as not being valid

        @effect: Mark children formula of self (and their children) as being invalid
        """
        for f in self.children:
            f.valid = False
            f.mark_child_not_valid()

    def mark_child_valid(self):
        """
        Mark the children of self as being valid

        @effect: Mark children formula of self (and their children) as being valid
        """
        for f in self.children:
            f.valid = True
            f.mark_child_valid()

    def add_formula_children(self, child_formula):
        """
        Add child_formula as a child of self

        @param: child_formula is the formula to be added to self
        @effect: child_formula is added to self.children and mark validity as necessary
        """
        if child_formula.parent:
                child_formula.remove_parent()
        child_formula.parent = self
        self.children.append(child_formula) 
        child_formula.valid = child_formula.verify()
        if child_formula.valid:
            child_formula.mark_child_valid()

def decompose_formula_argument(arg):
    """
    @param: arg is a string contained in TreeFormula's arg parameter
    @return:
        Return three strings
        First string corresponds to the main connector (and, or, iff, None)
        The two remaining strings are the decomposition arguments for TreeFormula 
        Return None, None, None if arg is not supported
    """
    arg = util.argument_parse(arg)
    main_connector, arg = util.find_main_connector(arg)

    # arg is a literal
    if main_connector is None:
        return None, arg, None
    
    if main_connector == "not":
        arg = util.argument_parse(arg)
        inner_parenthesis_index = arg.find('(')
        if(inner_parenthesis_index == -1):
            return None, f"not({arg})", None
        else:
            inner_connector = arg[0: inner_parenthesis_index].lower()
            arg = arg[inner_parenthesis_index + 1: len(arg) - 1]
            if inner_connector == "and":
                seperator = util.find_seperation(arg)
                return "or", f"not({arg[0: seperator]})", f"not({arg[seperator+1: len(arg)]})"
            if inner_connector == "or":
                seperator = util.find_seperation(arg)
                return "and", f"not({arg[0: seperator]})", f"not({arg[seperator+1: len(arg)]})"
            if inner_connector == "not":
                return None, arg, None
            if inner_connector == "if":
                seperator = util.find_seperation(arg)
                return "and", arg[0: seperator], f"not({arg[seperator+1 : len(arg)]})"
            if inner_connector == "iff":
                seperator = util.find_seperation(arg)
                return "iff", f"and(not({arg[0: seperator]}),{arg[seperator+1 : len(arg)]})", f"and({arg[0: seperator]},not({arg[seperator+1 : len(arg)]}))"
            return None, None, None
    if main_connector == "and":
        seperator = util.find_seperation(arg)
        return main_connector, arg[0: seperator], arg[seperator+1: len(arg)]
    if main_connector == "or":
        seperator = util.find_seperation(arg)
        return main_connector, arg[0: seperator], arg[seperator+1: len(arg)]
    if main_connector == "if":
        seperator = util.find_seperation(arg)
        return "or", f"not({arg[0:seperator]})", arg[seperator+1: len(arg)]
    if main_connector == "iff":
        seperator = util.find_seperation(arg)
        return "iff", f"and({arg[0: seperator]},{arg[seperator+1: len(arg)]})", f"and(not({arg[0: seperator]}),not({arg[seperator+1: len(arg)]}))"
    return None, None, None

def decompose_iff_into_if(arg):
    """
    Returns if form of iff

    @param: arg is a string in the form iff(a,b)
    @return:
        Return two string:
            or(not(a),b) 
            or(a,not(b))
    """
    arg = util.argument_parse(arg)
    first_parenthesis_index = arg.find('(')

    # Seperating the main connector and it's arguments
    main_connector = arg[0: first_parenthesis_index].lower()
    arg = arg[first_parenthesis_index + 1: len(arg) - 1]
    seperator = util.find_seperation(arg)
    return f"or(not({arg[0: seperator]}),{arg[seperator+1: len(arg)]})", f"or({arg[0: seperator]},not({arg[seperator+1: len(arg)]}))"

