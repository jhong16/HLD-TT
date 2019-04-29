import cmd
import forseti.parser
import shlex

from src import truthtrees

def parse_formula(formula_string):
    """
    Parse a formula string using the forseti parser.

    @param: formula_string is a string that can be 
    @return:
        None and error message if formula can't be parsed 
        Formula and None if formula can be parsed
    """
    formula = None
    try:
        formula = forseti.parser.parse(formula_string)
    except SyntaxError as se:
        print(se)
        return None, se
    return formula, None

def return_element_from_list(i, l):
    """
    Returns an element from the list
    
    @param: i is an integer corresponding to the index of the element in the list
    @param: l is a list of elements
    return:
        element of the list if 0 <= i <= len(l) - 1
        None otherwise
    """
    if(i < 0 or i >= len(l)):
        return None
    else:
        return l[i]

def history_parser(arg):
    """
    @param: arg is a string that contains the words seperated by spaces
    @return: Returns two strings. The first word removed from arg and everything after the space
    """
    v = -1
    try:
        v = arg.index(' ')
    except ValueError:
        return None, None
    first_word = arg[0:v]
    remain = arg[v + 1: len(arg)]
    return first_word, remain

def find_main_connector(arg):
    """
    Find the main_connector of an formula argument and the arguments

    @param: arg is a string that can be parsed by forsetti parser
    """
    arg = argument_parse(arg)
    first_parenthesis_index = arg.find('(')
    if first_parenthesis_index == -1:
        return None, arg
    main_connector = arg[0: first_parenthesis_index].lower()
    arg = arg[first_parenthesis_index + 1: len(arg) - 1]
    return main_connector, arg

def argument_parse(arg):
    """
    Small helper function to get rid of excess parenthesis at the begining and end and any whitespace.

    @param: arg is a string
    @return: arg with the spaces and parenthesis around arg removed
    """
    a = arg.replace(' ','')
    while a[0] == '(' and a[len(arg) - 1] == ')':
        a = a[1 : len(a) - 1]
    return a


def find_seperation(arg):
    """
    Helper Function for decompose
    
    @param: arg is a string corresponding to two function statement sepereated by a comma
            Example: "and(and(a,c),b),or(ab,b)"
    @return:
        return the index of the comma seperating the functions or -1 if no such comma exist
    """
    open_parenthesis = 0 
    for i in range(len(arg)):
        if arg[i] == '(':
            open_parenthesis += 1
        elif arg[i] == ')':
            open_parenthesis -= 1
        elif arg[i] == ',' and open_parenthesis == 0:
            return i
    return -1
