"""
6.101 Lab:
LISP Interpreter Part 2
"""

#!/usr/bin/env python3
import sys
sys.setrecursionlimit(20_000)


#############################
# Scheme-related Exceptions #
#############################

class SchemeError(Exception):
    pass

class SchemeSyntaxError(SchemeError):
    pass

class SchemeNameError(SchemeError):
    pass


class SchemeEvaluationError(SchemeError):
    pass

############################
# Tokenization and Parsing #
############################

def number_or_symbol(value):
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value

def tokenize(source):
    source += " "
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

keywords = {
    "define",
    "lambda",
    "if",
}

def parse(tokens):
    def parse_rec(start, end):
        lpar = 0
        rpar = 0
        for i in range(start, end+1):
            token = tokens[i]
            if token == "(": lpar += 1
            elif token == ")": rpar += 1
            if rpar > lpar: raise SchemeSyntaxError
            if token in keywords and \
                (not start == end) and \
                ((i == start) or (tokens[i-1] != "(")):
                raise SchemeSyntaxError
        if lpar != rpar: raise SchemeSyntaxError

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
    if isNum(variable):
        return variable
    if isExpression(variable) and variable[0] != 'lambda':
        raise SchemeEvaluationError
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

#############################
# Conditionals #
#############################

booleans = {
    "#t": True,
    "#f": False,
}

booleans_rev = {
    True: "#t",
    False: "#f",
}

def evaluate_conditional(pred, true_expr, false_expr, frame):
    if evaluate(pred, frame):
        return evaluate(true_expr, frame)
    return evaluate(false_expr, frame)

def list_compare(func, args):
    n = len(args)
    if n == 1:
        return True
    for i in range(0, n-1):
        if not func(args[i], args[i+1]):
            return False
    return True

def list_iter(crit_bool, args, frame):
    for x in args:
        if evaluate(x, frame) == crit_bool:
            return crit_bool
    return not crit_bool

def negate(*args):
    if len(args) != 1:
        raise SchemeEvaluationError
    return not args[0]

comparison_builtins = {
    "equal?" : lambda *args: list_compare( (lambda x, y: x == y), args),
    ">" : lambda *args: list_compare( (lambda x, y: x > y), args),
    ">=" : lambda *args: list_compare( (lambda x, y: x >= y), args),
    "<" : lambda *args: list_compare( (lambda x, y: x < y), args),
    "<=" : lambda *args: list_compare( (lambda x, y: x <= y), args),
    "and" : lambda args, frame: list_iter(False, args, frame), ##special form
    "or" : lambda args, frame: list_iter(True, args, frame), ##special form
    "not" : negate,
}

#############################
# Lists #
#############################

class Pair:
    EMPTY_LIST = None

    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr

    def __str__(self):
        return f'({self.car}, {self.cdr})'
    
    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.car == other.car and self.cdr == other.cdr

def isCons(obj):
    return isinstance(obj, Pair)

def create_pair(*args):
    if len(args) != 2:
        raise SchemeEvaluationError
    return Pair(args[0], args[1])

def get_pair_elem(elem_num, args):
    if len(args) != 1 or not isCons(args[0]):
        raise SchemeEvaluationError
    if elem_num == 0:
        return args[0].car
    return args[0].cdr

def create_list(*args):
    list = Pair.EMPTY_LIST
    for i in range(len(args)-1, -1, -1):
        list = create_pair(args[i], list)
    return list

def isList(arg):
    if arg is Pair.EMPTY_LIST:
        return True
    return isinstance(arg, Pair) and isList(arg.cdr)

def length_list(arg):
    if arg == Pair.EMPTY_LIST:
        return 0
    if not isinstance(arg, Pair):
        return 1
    return 1 + length_list(arg.cdr)

def get_list_elem(cons, index):
    if not isinstance(cons, Pair):
        raise SchemeEvaluationError
    if index == 0:
        return cons.car
    return get_list_elem(cons.cdr, index-1)

def get_last_pair_list(list):
    if list.cdr is Pair.EMPTY_LIST:
        return list
    return get_last_pair_list(list.cdr)

def extend_list(list, elem):
    list.cdr = create_pair(elem, None)

def append_lists(*args):
    if len(args) == 0:
        return Pair.EMPTY_LIST
    for list in args:
        if not isList(list):
            raise SchemeEvaluationError

    prev = create_pair(None, create_pair(None, None))
    new_list = prev.cdr
    cur = new_list
    for list in args:
        while list is not Pair.EMPTY_LIST:
            cur.car = list.car
            extend_list(cur, None)
            prev, cur, list = prev.cdr, cur.cdr, list.cdr 
    prev.cdr = None
    if new_list.car == None:
        new_list = Pair.EMPTY_LIST
    return new_list

def isListWrapper(*args):
    if len(args) != 1:
        raise SchemeEvaluationError
    return isList(args[0])

def listLengthWrapper(*args):
    if len(args) != 1 or not isList(args[0]):
        raise SchemeEvaluationError
    return length_list(args[0])

def listItemWrapper(*args):
    if len(args) != 2:
        raise SchemeEvaluationError
    cons, index = args
    if not isCons(cons) or not isNum(index) or index < 0:
        raise SchemeEvaluationError
    return get_list_elem(args[0], args[1])


list_builtins = {
    "cons": create_pair,
    "car": lambda *args: get_pair_elem(0, args),
    "cdr": lambda *args: get_pair_elem(1, args),
    "list": create_list,
    "list?": isListWrapper,
    "length": listLengthWrapper,
    "list-ref": listItemWrapper,
    "append": append_lists
    }

#############################
# Reading from Files #
#############################

def evaluate_file(filename: str, frame=None):
    file = open(filename)
    expr = file.read()
    print("expression to evaluate:")
    print(expr)
    return evaluate(parse(tokenize(expr)), frame)

#############################
# Global Variables #
#############################

frame_builtins = {
    "define": lambda: None,
    "lambda": create_function,
    "if": evaluate_conditional,
    "begin": lambda: None,
}

GLOBAL_FRAME = Frame(None, scheme_builtins | comparison_builtins | frame_builtins | list_builtins)

#############################
# Evaluation #
#############################

def isFunc(token):
    return isinstance(token, Function)

def isPair(token):
    return isinstance(token, Pair)

def isNum(token):
    return isinstance(token, int) or isinstance(token, float)

def isBool(token):
    return (isStr(token) and token in booleans)

def isEmptyList(token):
    return token == []

def isStr(token):
    return isinstance(token, str)

def isExpression(token):
    return isinstance(token, list)

def evaluate(tree, frame=None):
    if frame == None:
        frame = make_initial_frame()

    print("tree: " + str(tree))

    if isFunc(tree):
        return tree

    if isPair(tree):
        return tree

    if isNum(tree):
        return tree
    
    if isBool(tree):
        return booleans[tree]
    
    if isEmptyList(tree):
        return Pair.EMPTY_LIST
        
    if isStr(tree):
        return get(tree, frame)
        
    first_elem = tree[0]
    func = evaluate(first_elem, frame)
    if not callable(func):
        raise SchemeEvaluationError
    
    if first_elem == "define":
        if not isExpression(tree[1]):
            name = tree[1]
            value = evaluate(tree[2], frame)
        else: 
            name = tree[1][0]
            value = create_function(tree[1][1:], tree[2], frame)
        return create_variable(name, value, frame)

    if first_elem == "lambda":
        return create_function(tree[1], tree[2], frame)
    
    if first_elem == "if":
        return evaluate_conditional(tree[1], tree[2], tree[3], frame)
    
    if first_elem == "and" or first_elem == "or":
        return comparison_builtins[first_elem]([tree[i] for i in range(1, len(tree))], frame)

    args = []
    for i in range(1, len(tree)):
        args.append(evaluate(tree[i], frame))

    if first_elem == "begin":
        return evaluate(args[-1])

    return func(*tuple(args))



if __name__ == "__main__":
    import os
    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    initial_frame = make_initial_frame()
    for filename in sys.argv:
        if filename != "lab.py":
            evaluate_file(filename, initial_frame)
    import schemerepl
    schemerepl.SchemeREPL(sys.modules[__name__], use_frames=True, verbose=False, repl_frame=initial_frame).cmdloop()
