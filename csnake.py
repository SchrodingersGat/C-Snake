from datetime import date

###############################################################################
#                           public helper functions                           #
###############################################################################


def shape(array):
    """Return dimensions (shape) of a multidimensional list"""
    # strings should return nothing
    if isinstance(array, str):
        return ''
    curr = array
    shape = []
    while True:
        try:
            shape.append(len(curr))
            curr = curr[0]
        except TypeError:
            return shape


###############################################################################
#                        classes defining C constructs                        #
###############################################################################


class EnumValue:
    """Singular value of an C-style enumeration"""

    def __init__(self, name, value=None, comment=None):
        self.name = name
        self.value = value
        self.comment = comment


class Enum:
    """c-style enumeration class"""

    def __init__(self, name, prefix=""):

        # enum values
        self.values = []
        self.name = name

        self.prefix = prefix

    def add_value(self, name, value=None, comment=None):
        """assuees that the user adds the values in the correct order"""

        self.values.append(EnumValue(name, value=value, comment=comment))


class Variable:
    """c-style variable"""

    def __init__(self,
                 name,
                 primitive,
                 qualifiers=None,
                 array=None,
                 comment=None,
                 value=None,
                 value_opts=None):
        self.name = name
        self.primitive = primitive
        self.comment = comment
        self.array = array
        self.qualifiers = qualifiers
        self.value = value
        self.value_opts = value_opts

    def declaration(self):
    def __array_dimensions(self):
        if isinstance(self.array, (tuple, list)):
            array = "".join("[{0}]".format(dim) for dim in self.array)
        elif self.array is not None:
            array = "[{dim}]".format(dim=str(self.array))
        elif self.array is None and isinstance(self.value, str):
            array = '[]'
        elif self.array is None and shape(self.value):
            array = "".join("[{0}]".format(dim) for dim in shape(self.value))
        else:
            array = ""
        return array

        """Return a declaration string."""
        if isinstance(self.qualifiers, (list, tuple)):
            qual = " ".join(self.qualifiers) + " "
        elif self.qualifiers is not None:
            qual = str(self.qualifiers) + " "
        else:
            qual = ""

        array = self.__array_dimensions()
        return '{ext}{qual}{prim} {name}{array}'.format(
            ext='extern ' if extern else '',
            qual=qual,
            prim=self.primitive,
            name=self.name,
            array=array)

    def initialization(self, indent):
        """Return an initialization string."""

        def generate_single_var(var_, formatstring=None):
            """generate single variable"""
            if isinstance(var_, str):
                return "\"{val}\"".format(val=var_)
            elif isinstance(var_, (int, float)):
                if formatstring is None:
                    return str(var_)
                return formatstring.format(var_)

        def generate_array(array, indent='    ', formatstring=None):
            """print (multi)dimensional arrays"""

            class OpenBrace:
                """Helper class to identify open braces while printing."""
                pass

            class ClosedBrace:
                """Helper class to identify closed braces while printing"""
                pass

            depth = 0
            stack = []
            stack.append(array)
            output = ''
            leading_comma = False

            while stack:
                top = stack.pop()
                # non-printed tokens
                if isinstance(top, (list, tuple)):
                    stack.append(ClosedBrace())
                    stack.extend(top[::-1])
                    stack.append(OpenBrace())
                    continue
                # non-comma-delimited tokens
                if isinstance(top, ClosedBrace):
                    depth -= 1 if depth > 0 else 0
                    output += '}'
                    if stack:
                        if isinstance(stack[-1], ClosedBrace):
                            output += '\n' + (indent * (depth - 1))
                        else:
                            output += ',\n' + (indent * depth)
                        leading_comma = False
                    continue
                # check the need for leading comma
                if leading_comma:
                    output += ', '
                else:
                    leading_comma = True
                # (potentially) comma delimited tokens
                if isinstance(top, OpenBrace):
                    output += '{'
                    depth += 1
                    if isinstance(stack[-1], (OpenBrace, list, tuple)):
                        output += '\n' + (indent * depth)
                    leading_comma = False
                    continue
                if isinstance(top, (int, float, str)):
                    output += generate_single_var(top, formatstring)
            return output

        # main part: generating initializer
        if isinstance(self.qualifiers, (list, tuple)):
            qual = " ".join(self.qualifiers) + " "
        elif self.qualifiers is not None:
            qual = str(self.qualifiers) + " "
        else:
            qual = ""

        array = self.__array_dimensions()

        if isinstance(self.value, (tuple, list)):
            assignment = '\n' if len(shape(self.value)) > 1 else ''
            assignment += generate_array(self.value, indent, self.value_opts)
        else:
            assignment = generate_single_var(self.value, self.value_opts)

        return '{qual}{prim} {name}{array} = {assignment};'.format(
            qual=qual,
            prim=self.primitive,
            name=self.name,
            array=array,
            assignment=assignment)


class Struct:
    """c-style struct class"""

    def __init__(self, name, ref_name=None, comment=None):
        self.name = name  # definition name of this struct e.g. Struct_t
        self.ref_name = ref_name  # reference name of this struct e.g. the_struct
        self.variables = []
        self.comment = comment

    def add_variable(self, variable):
        """Add another variable to struct"""
        if not isinstance(variable, (Variable, Struct)):
            raise TypeError("variable must be 'Variable' or 'Struct'")

        self.variables.append(variable)

    def declaration(self):
        """Return a declaration string."""
        if self.ref_name is None:
            raise ValueError('no ref_name supplied for Struct "{name}"'.format(
                name=self.name))

        return '{name} {ref};'.format(name=self.name, ref=self.ref_name)


class Function:
    """c-style function"""

    def __init__(self, name, return_type='void'):
        self.name = name
        self.return_type = return_type

        self.variables = []

    def add_argument(self, var):
        """Add an argument to function"""
        if not isinstance(var, Variable):
            raise TypeError("variable must be of type 'Variable'")

        self.variables.append(var)

    def prototype(self):
        """function prototype string"""
        prot = '{ret} {nm}({funcs})'.format(
            ret=self.return_type,
            nm=self.name,
            funcs=', '.join([v.declaration() for v in self.variables])
            if self.variables else 'void')

        return prot

    def call(self, *arg):
        """call a function"""
        if not len(arg) == len(self.variables):
            print(arg)
            raise ValueError(
                "number of arguments must match number of variables")

        call_ = '{name}({args});'.format(
            name=self.name, args=', '.join([str(a) for a in arg]))

        return call_


###############################################################################
#                         Main, file-generating class                         #
###############################################################################


class CodeWriter:
    """Class to describe and generate contents of a .c/.cpp/.h/.hpp file"""

    CPP = "__cplusplus"

    VERSION = "1.1"

    def __init__(self, lf="\n", indent=4):

        self.line_feed = lf
        if isinstance(indent, int):
            self.indent = ' ' * indent
        else:
            self.indent = indent

        # initialize values
        self.commenting = False  # switch for bulk commenting
        self.defs = []  # define levels
        self.switch = []  # switch levels
        self.tabs = 0
        self.text = ''  # code

    def tab_in(self):
        """increase tab level"""
        self.tabs += 1

    def tab_out(self):
        """decrease tab level"""
        if self.tabs > 0:
            self.tabs -= 1

    def reset_tabs(self):
        self.tabs = 0

    def start_comment(self):
        """start a bulk comment"""
        self.add_line('/*')
        self.commenting = True

    def end_comment(self):
        """end a bulk comment"""
        self.commenting = False
        self.add_line('*/')

    def add_autogen_comment(self, source=None):
        """add the auto-gen comment (user can point to the source file if required)"""
        self.start_comment()
        self.add_line(
            "This file was autogenerated using the C-Snake v{version} script".
            format(version=self.VERSION))
        self.add_line(
            "This file should not be edited directly, any changes will be overwritten next time the script is run"
        )
        if source:
            self.add_line(
                "Make any changes to the file '{src}'".format(src=str(source)))
        self.add_line(
            "Source code for C-Snake available at https://github.com/SchrodingersGat/C-Snake"
        )
        self.end_comment()

    def add_license_comment(self, license_, authors, intro=None):
        """Add the license comment."""
        self.start_comment()

        if intro:
            for line in intro.splitlines():
                if line == '':
                    self.add_line()
                else:
                    self.add_line(line)

        year = date.today().year
        if authors:
            for author in authors:
                self.add_line("Copyright © {year} {name}{email}".format(
                    year=year,
                    name=author['name'],
                    email=' <{0}>'.format(author['email']) if author.get(
                        'email', None) else ''))
        self.add_line()

        if not isinstance(license_, str):
            raise TypeError('license_ must be a string.')
        for line in license_.splitlines():
            self.add_line(line)

        self.end_comment()

    def open_brace(self):
        """open-brace and tab"""
        self.add_line('{')
        self.tab_in()

    def close_brace(self, new_line=True):
        """close-brace and tab-out"""
        self.tab_out()
        self.add(self.indent * self.tabs + '}')
        if new_line:
            self.add_line('')

    def define(self, name, value=None, comment=None):
        """add a define"""
        line = "#define " + name
        if value:
            line += ' ' + str(value)

        self.add_line(line, comment=comment, ignore_tabs=True)

    def start_if_def(self, define, invert=False, comment=None):
        """start an #ifdef block (preprocessor)"""
        self.defs.append(define)
        if invert:
            self.add_line(
                "#ifndef " + define, comment=comment, ignore_tabs=True)
        else:
            self.add_line(
                "#ifdef " + define, comment=comment, ignore_tabs=True)

    def end_if_def(self):
        """end an #ifdef block"""

        if self.defs:
            self.add_line("#endif ", comment=self.defs.pop(), ignore_tabs=True)
        else:
            self.add_line("#endif", ignore_tabs=True)

    def cpp_entry(self):
        """add an 'extern' switch for CPP compilers"""
        self.start_if_def(self.CPP, "Play nice with C++ compilers")
        self.add_line('extern "C" {', ignore_tabs=True)
        self.end_if_def()

    def cpp_exit(self):
        self.start_if_def(self.CPP, "Done playing nice with C++ compilers")
        self.add_line('}', ignore_tabs=True)
        self.end_if_def()

    def start_switch(self, switch):
        """start a switch statement"""
        self.switch.append(switch)
        self.add_line('switch ({sw})'.format(sw=switch))
        self.open_brace()

    def end_switch(self):
        """end a switch statement"""
        self.tab_out()
        self.add('}')
        if self.switch:
            self.add(' // ~switch ({sw})'.format(sw=self.switch.pop()))
        self.add_line()

    def add_case(self, case, comment=None):
        """add a case statement"""
        self.add_line('case {case}:'.format(case=case), comment=comment)
        self.tab_in()

    def add_default(self, comment=None):
        """add a default case statement"""
        self.add_line('default:', comment=comment)
        self.tab_in()

    def break_from_case(self):
        """break from a case"""
        self.add_line('break;')
        self.tab_out()

    def return_from_case(self, value=None):
        """return from a case"""
        self.add_line(
            'return{val};'.format(val=' ' + str(value) if value else ''))
        self.tab_out()

    def add(self, text):
        """add raw text"""
        self.text += text

    def add_line(self, text=None, comment=None, ignore_tabs=False):
        """add a line of (formatted) text"""

        # empty line
        if not text and not comment and not self.commenting:
            self.add(self.line_feed)
            return

        if not ignore_tabs and not self.commenting:
            self.add(self.indent * self.tabs)

        if self.commenting:
            self.add("* ")

        # add the text (if appropriate)
        if text:
            self.add(text)
        # add a trailing comment (if appropriate)
        if comment:
            if text:
                self.add(' ')  # add a space after the text
            self.add('//' + comment)

        self.add(self.line_feed)

    def include(self, file, comment=None):
        """add a c-style include"""
        self.add_line(
            "#include {file}".format(file=file),
            comment=comment,
            ignore_tabs=True)

    def add_enum(self, enum):
        """add a constructed enumeration"""
        if not isinstance(enum, Enum):
            raise TypeError('enum must be of type "Enum"')

        self.add_line("typedef enum")
        self.open_brace()

        for i, v in enumerate(enum.values):
            line = enum.prefix + v.name
            if v.value:
                line += " = " + str(v.value)

            if i < (len(enum.values) - 1):
                line += ","

            self.add_line(line, comment=v.comment)

        self.close_brace(new_line=False)
        self.add(' ' + enum.name + ';')
        self.add_line()

    def add_variable_declaration(self, var):
        """add a variable declaration"""
        if not isinstance(var, Variable):
            raise TypeError("variable must be of type 'Variable'")

        self.add_line(var.declaration() + ";", comment=var.comment)

    def add_variable_initialization(self, var):
        """add a variable initialization"""
        if not isinstance(var, Variable):
            raise TypeError("variable must be of type 'Variable'")

        initlines = var.initialization(self.indent).splitlines()
        self.add_line(initlines[0], comment=var.comment)
        if len(initlines) > 1:
            self.tab_in()
            for line in initlines[1:]:
                self.add_line(line)
            self.tab_out()

    def add_struct(self, struct):
        """add a struct"""
        if not isinstance(struct, Struct):
            raise TypeError("struct must be of type 'Struct'")

        self.add_line("typedef struct")
        self.open_brace()

        for var in struct.variables:
            if isinstance(var, Variable):  # variables within the struct
                self.add_variable_declaration(var)
            elif isinstance(var, Struct):  # other structs within the struct
                if var.ref_name is None:
                    raise ValueError('no ref_name provided for struct {name}'.
                                     format(name=var.name))
                self.add_line(var.declaration(), comment=var.comment)

        self.close_brace(new_line=False)
        self.add(' ' + struct.name + ';')
        self.add_line()

    def add_function_prototype(self, func, comment=None):
        """add a function prototype"""
        if not isinstance(func, Function):
            raise TypeError("func must be of type 'Function'")

        self.add_line(func.prototype() + ';', comment=comment)

    def add_function_definition(self, func, comment=None):
        """add a function definition"""
        if not isinstance(func, Function):
            raise TypeError("func must be of type 'Function'")

        self.add_line(func.prototype(), comment=comment)

    def call_function(self, func, *arg):
        """enter a function"""
        if not isinstance(func, Function):
            raise TypeError("func must be of type 'Function'")

        self.add_line(func.call(*arg))

    def write_to_file(self, file):
        """write code to file"""
        with open(file, 'w') as the_file:
            the_file.write(self.text)
