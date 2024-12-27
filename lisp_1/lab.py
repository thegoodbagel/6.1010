"""
6.101 Lab:
LISP Interpreter Part 1
"""

#!/usr/bin/env python3

# import doctest # optional import
# import typing  # optional import
# import pprint  # optional import

import sys

sys.setrecursionlimit(20_000)

# NO ADDITIONAL IMPORTS!

#############################
# Scheme-related Exceptions #
#############################


class SchemeError(Exception):
    """
    A type of exception to be raised if there is an error with a Scheme
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class SchemeNameError(SchemeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class SchemeEvaluationError(SchemeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SchemeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(value):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Scheme
                      expression
    """
    source += " " ## so we add last real token
    tokens = []
    comment = False
    non_real_tokens = {"(", ")", " ", "\n", ";"}
    real_token = ""

    for char in source:
        if not comment and char not in non_real_tokens:
            real_token += char
        else:
            if real_token: tokens.append(real_token)
            real_token = "" 

            if char == " ": continue
            elif char in {"(", ")"} and not comment: 
                tokens.append(char)
            elif char == ";": comment = True
            elif char == "\n": comment = False
    return tokens


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    
    def parse_rec(start, end):
        if start == end:
            return number_or_symbol(tokens[start])
        
        parsed_tokens = []
        token_index = start+1

        while token_index < end:
            new_start = token_index
            if tokens[token_index] == "(":
                num_lpar = 0
                num_rpar = 0
                while token_index < end:
                    if tokens[token_index] == "(":
                        num_lpar += 1
                    elif tokens[token_index] == ")":
                        num_rpar += 1
                        if num_rpar == num_lpar:
                            break
                    token_index += 1
            new_end = token_index
            parsed_tokens.append(parse_rec(new_start, new_end))
            token_index += 1
        return parsed_tokens

    return parse_rec(0, len(tokens)-1)


######################
# Built-in Functions #
######################

def calc_sub(*args):
    if len(args) == 1:
        return -args[0]
    first_num, *rest_nums = args
    return first_num - scheme_builtins['+'](*rest_nums)

def calc_mult(*args):
    product = 1
    for i in args:
        product *= i
    return product

def calc_div(*args):
    if len(args) == 1:
        return 1 / args[0]
    first_num, *rest_nums = args
    return first_num / scheme_builtins['*'](*rest_nums)

scheme_builtins = {
    "+": lambda *args: sum(args),
    "-": calc_sub,
    "*": calc_mult,
    "/": calc_div,
}

#############################
# Frames and Variables #
#############################

    
class Frame:
    def __init__(self, parent=None, namespace=None):
        self.parent = parent
        self.namespace = namespace
        if namespace == None:
            self.namespace = dict()

    def __str__(self):
        return f'namespace: {str([x for x in self.namespace])}'

def make_initial_frame():   
    return Frame(GLOBAL_FRAME)

def create_variable(variable, value, frame):
    frame.namespace[variable] = value
    return value

def get(variable, frame):
    while frame:
        if variable in frame.namespace:
            return frame.namespace[variable]
        frame = frame.parent
    raise SchemeNameError

#############################
# Functions #
#############################

class Function:
    def __init__(self, param_list, expr, enclosing_frame):
        self.param = tuple(param_list)
        self.expr = expr
        self.frame = enclosing_frame

    def __call__(self, *args):
        if len(args) != len(self.param):
            raise SchemeEvaluationError
        new_frame = Frame(self.frame)
        for (param, val) in zip(self.param, args):
            new_frame.namespace[param] = val
        return evaluate(self.expr, new_frame)
    
    def __str__(self):
        return "a function"

def create_function(arg, expr, frame):
    new_func = Function(arg, expr, frame)
    return new_func

frame_builtins = {
    "define": create_variable,
    "lambda": create_function,
}

GLOBAL_FRAME = Frame(None, scheme_builtins | frame_builtins)

##############
# Evaluation #
##############

def isNum(token):
    return isinstance(token, int) or isinstance(token, float)

def isStr(token):
    return isinstance(token, str)

def evaluate(tree, frame=None):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """

    if frame == None:
        frame = make_initial_frame()

    if isNum(tree):
        return tree
        
    if isStr(tree):
        return get(tree, frame)
    
    print("tree: " + str(tree))
    print("frame: " + str(frame))
    
    first_elem = tree[0]
    func = evaluate(first_elem, frame)
    if not callable(func):
        raise SchemeEvaluationError
    
    if first_elem == "define":
        return create_variable(tree[1], evaluate(tree[2], frame), frame)
    
    if first_elem == "lambda":
        return create_function(tree[1], tree[2], frame)

    args = []
    for i in range(1, len(tree)):
        args.append(evaluate(tree[i], frame))
    return func(*tuple(args))


if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)
    import os
    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    import schemerepl
    schemerepl.SchemeREPL(sys.modules[__name__], use_frames=False, verbose=False).cmdloop()
