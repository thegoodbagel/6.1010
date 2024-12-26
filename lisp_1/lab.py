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



##############
# Evaluation #
##############


def evaluate(tree):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    if isinstance(tree, str):
        if tree in scheme_builtins:
            return scheme_builtins[tree]
        raise SchemeNameError
    if isinstance(tree, int) or isinstance(tree, float):
        return tree
    ## tree is S-expression (list)
    operation = evaluate(tree[0])
    if not callable(operation):
        raise SchemeEvaluationError
    args = []
    for i in range(1, len(tree)):
        args.append(evaluate(tree[i]))
    return operation(*tuple(args))


if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)
    import os
    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    import schemerepl
    schemerepl.SchemeREPL(sys.modules[__name__], use_frames=False, verbose=False).cmdloop()
