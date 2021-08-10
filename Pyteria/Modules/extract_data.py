import ast
import hashlib
from collections import Counter


class ImportStatement():
    def __init__(self, name):
        self.name = name
        self.alias = []
        self.children = []

    def add_alias(self, value):
        self.alias.append(value)

    def add_child(self, value):
        self.children.append(value)

# code adapted from Haney, A (2021). python-morgue retrieved from: github.com/adamhaney/python-morgue/blob/master/morgue.py on 4/16/2021
class ImportFromStatement(ImportStatement):
    def __init__(self, name, parent_module):
        self.parent_module = parent_module
        super().__init__(name)


class MethodCallNodes(ast.NodeVisitor):
    # code adapted from https://suhas.org/function-call-ast-python/
    def __init__(self):
        self.func_name = []

    @property
    def name(self):
        self.func_name.reverse()
        # return '.'.join(self.func_name)
        # print(self.func_name)
        return self.func_name

    def visit_Name(self, node):
        self.func_name.append(node.id)

    def visit_Attribute(self, node):
        self.func_name.append(node.attr)

        if isinstance(node.value, ast.Attribute):
            # Recursion magic is hype!
            self.visit(node.value)

        elif isinstance(node.value, ast.Name):
            self.func_name.append(node.value.id)


class MethodCall():
    def __init__(self, name):
        self.name = name
        self.children = []
        self.full_call = ""
        self.count = 0
        # self.parent = None

    def add_child(self, child):
        self.children.append(child)

    def add_parent(self, parent):
        self.parent = parent

    def get_parent_tree(self):
        if self.parent != None:
            # print("DEBUG -- "self.parent.name)
            # self.parent.get_parent_tree()
            return self.parent

    def increment_count(self):
        self.count += 1


class MethodCallChild(MethodCall):
    def __init__(self, name, parent_call):
        self.name = name
        self.parent_call = parent_call
        super().__init__(name)
        self.parent_call.add_child(self)


class Constant():
    def __init__(self, value, kind):
        self.value = str(value)
        self.kind = kind

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value
        self.__sha256 = hashlib.sha256(self.__value.encode()).hexdigest()

    @property
    def sha256(self):
        return self.__sha256


def generate_tree(file_path):
    """
    Name: generate_tree
    Purpose: generates a code object ast module can parse
    Arguments: file_path, file path
    Returns: code object
    """
    try:
        with open(file_path, 'r') as source:
            ast_tree = ast.parse(source.read())
    except Exception as e:
        print('ERROR: CANNOT OPEN FILE OR GENERATE AST TREE. DOES THE PROGRAM CONTAIN SYNTAX ERRORS?\n\tINFO:', e)
        exit()

    return ast_tree


def get_imports(tree):
    """
    Name: get_imports
    Purpose: Get import data from an ast node
    Arguments: tree, ast node
    Returns: list of ImportStatement and ImportFromStatement objects
    """

    module_objects = []
    # Tab, tab, tab. Tabs for days! Try to simplify this.
    # Walk through the node tree.
    for node in ast.walk(tree):
        # Is this node an 'import' statement?
        if isinstance(node, ast.Import):
            # Pull all module names.
            for name in node.names:
                module = ImportStatement(name.name)

                # Does this function have an alias?
                if name.asname:
                    module.add_alias(name.asname)

            module_objects.append(module)

        # Is this node an 'import from' statement?
        elif isinstance(node, ast.ImportFrom):
            # Pull the module name.
            module = ImportStatement(node.module)

            # Pull the all imported functions from the module.
            for name in node.names:
                # Pull the module name.
                child_class = ImportFromStatement(name.name, module)

                # Does this function have an alias?
                if name.asname:
                    child_class.add_alias(name.asname)

                # Associate child with parent.
                module.add_child(child_class)

            module_objects.append(module)

    return module_objects


def format_imports(import_obj_list):
    """
    Name: format_imports
    Purpose: Formats import object list into json style dictionary
    Arguments: import_obj_list, ImportStatement
    Returns: dict
    """

    formated_modules = {}

    for mod in import_obj_list:
        child_list = []

        for child in mod.children:
            formated_modules[child.name] = {
                "type": "import", "value": child.name, "aliases": child.alias}
            child_list.append(child.name)

        formated_modules[mod.name] = {
            "type": "import", "value": mod.name, "aliases": mod.alias, "children": child_list}

    return formated_modules


def get_method_calls(tree):
    """
    Name: get_method_calls
    Purpose: Get method call data from an ast node
    Arguments: tree, ast node
    Returns: List of MethodCall and MethodCallChildren objects
    """
    method_calls = []

    for node in ast.walk(tree):
        # Is this node a method call?
        if isinstance(node, ast.Call):
            curr_func = MethodCallNodes()
            # Visit function called changes depending on node type
            # Check visit_<Type>() in MethodCallNodes class for more info
            curr_func.visit(node.func)
            method_calls.append(curr_func.name)

    method_objects = []
    # SOO many for loops. This probably needs to be refactored.
    for call_list in method_calls:
        i = 0
        # print(call_list)
        for call in call_list:
            if i == 0:
                parent_method = MethodCall(call)
                curr_method = parent_method
            else:
                curr_method = MethodCallChild(call, parent_method)
            i += 1
            method_objects.append(curr_method)

    return method_objects


def format_calls(call_obj_list):
    """
    Name: format_calls
    Purpose: Formats method call object list into json style dictionary
    Arguments: call_obj_list, MethodCall
    Returns: dict
    """
    all_calls = []
    for call in call_obj_list:
        # print(isinstance(call, MethodCall))
        if not isinstance(call, MethodCallChild):
            full_call = ""
            full_call = call.name
            for child in call.children:
                # print(child.name, ',', child)
                full_call = full_call + '.' + child.name
            call.full_call = full_call
            all_calls.append(call.full_call)
    occurences = Counter(all_calls)
    calls_list = {}
    for call_data in occurences:
        # print("DEBUG --", call_data, ":", occurences.get(call_data))
        calls_list[call_data] = {
            "type": "method_call", "value": call_data, "count": occurences.get(call_data)}
    return calls_list


def import_test():
    """
    Name: import_test
    Purpose: Creates test output to show import extraction functions are working
    Arguments: None
    Returns: None
    """
    print("Running test output...")
    test_dir = './Test Files'
    test_file = 'test_cases.py'
    # Pretty sure I know how this is working... But I shoud come back and verify that.
    test_full_path = abspath(
        join(dirname(__file__), test_dir + '/' + test_file))
    # print("DEBUG:",test_file)
    try:
        with open(test_full_path, 'r') as source:
            ast_tree = ast.parse(source.read())
    except Exception as err:
        print("Cannot open file:", err)

    modules = get_imports(ast_tree)
    print(format_imports(modules))
    """
    for mod in modules:
        print("Module: ", mod.name, ', Aliases: ',
              mod.alias, ", obj ref: ", mod, sep="")
        print(" Children Classes:")
        for child in mod.children:
            print("     | ", child.name, ", Aliases:", child.alias, ", parent obj ref:",
                  child.parent_module, sep="")
    """


def method_call_test():
    """
    Name: method_call_test
    Purpose: Creates test output to show method call extract functions are working
    Arguments: None
    Returns: None
    """
    test_dir = 'Test Files'
    test_file = 'test_cases.py'

    test_full_path = abspath(
        join(dirname(__file__), test_dir + '/' + test_file))
    # print("DEBUG:",test_file)
    ast_tree = generate_tree(test_full_path)
    calls = get_method_calls(ast_tree)

    print(format_calls(calls))


def get_constants(tree):
    """
    Name: get_constants
    Purpose: Creates test output to show method call extract functions are working
    Arguments: tree, ast.NodeTree
    Returns: list
    """
    constant_objects = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant):
            constant = Constant(node.value, node.kind)
            constant_objects.append(constant)

    return constant_objects


def format_constants(constant_obj_list):
    """
    Name: format_constants
    Purpose: Formats constant object list into json style dictionary
    Arguments: constant_obj_list, Constant
    Returns: dict
    """
    formatted_constants = {}
    for constant in constant_obj_list:
        new_entry = {"type": "constant",
                     "value": constant.value, "kind": constant.kind, "SHA256": constant.sha256}
        formatted_constants[constant.sha256] = new_entry
    return formatted_constants


def constant_test():
    """
    Name: constant_test
    Purpose: Creates test output to show constant extract functions are working
    Arguments: None
    Returns: None
    """
    test_dir = 'Test Files'
    test_file = 'test_cases.py'

    test_full_path = abspath(
        join(dirname(__file__), test_dir + '/' + test_file))
    # print("DEBUG:",test_file)

    ast_tree = generate_tree(test_full_path)
    constants_data = get_constants(ast_tree)
    formated_constant_data = format_constants(constants_data)
    print(formated_constant_data)


if __name__ == '__main__':
    from os.path import abspath, dirname, join
    print("Running tests...\n")
    print("---IMPORT TEST---")
    import_test()
    print("-"*20+"\n")

    print("---METHOD CALL TEST---")
    method_call_test()
    print("-"*20+"\n")

    print("---CONSTANT TEST---")
    constant_test()
