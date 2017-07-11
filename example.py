#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from csnake import *

# generate a header file
h = CodeWriter()

HEADER = "_CSNAKE_EXAMPLE_H_"

h.add_autogen_comment(source="example.py")

intro = "This file is a part of the C-Snake project\nMIT License\n"

mit = """Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""

authors = [{
    'name': 'Oliver',
}, {
    'name': 'Andrej Radovic',
    'email': 'r.andrej@gmail.com'
}]

h.add_license_comment(license_=mit, authors=authors, intro=intro)
h.add_line()

h.start_if_def(HEADER, invert=True)
h.define(HEADER)
h.add_line()
h.include("<stdint.h>", comment="Include standard types")

h.add_line()
h.add_line(comment="This is a single line comment")
h.add_line()
h.start_comment()
h.add_line("multi line comments")
h.add_line("are also supported")
h.end_comment()

h.add_line()
h.add_line(comment="Define a structure")

s1 = Struct("DatStructTho", ref_name="destruct")

v1 = Variable("a", "uint8_t", array=5, comment='Variables can be arrays')
v2 = Variable(
    "b",
    "uint16_t",
    qualifiers='volatile',
    comment='Extra qualifiers can be specified')
v3 = Variable("c", "float", comment='Variables can have associated comments')

s1.add_variable(v1)
s1.add_variable(v2)
s1.add_variable(v3)

s2 = Struct("ParentStruct_t")

s2.add_variable(s1)
s2.add_variable(Variable("x", "float"))
s2.add_variable(Variable("y", "float"))
s2.add_variable(Variable('z', 'float'))

# add the two structs to the header file
h.add_struct(s1)
h.add_line()
h.add_struct(s2)
h.add_line()

# and now some enumerations
e = Enum("EnumExample_t", prefix="ENUM_PREFIX_")
e.add_value("A")
e.add_value("B", value=10, comment="Enum values can have comments too")
e.add_value("C")
e.add_value("D")

h.add_enum(e)

# add prototype for the main function
f1 = Function("main", return_type="int")

h.add_line()
h.add_function_prototype(f1, comment="main function prototype")
h.add_line()

# now add another function
f2 = Function("do_the_needful", return_type="void")
f2.add_argument(Variable("need", "int"))

h.add_function_prototype(f2, comment="Do the Needful")

h.add_line()

# declare some variables extern, to be defined in the .c file
var1 = Variable(
    name='initialized_string',
    primitive='char',
    qualifiers='const',
    array=None,
    comment=None,
    value=("Needs to be an escaped string. Use repr() or "
           "encode('unicode_escape') or escape by hand: \\n."),
    value_opts=None)
var2 = Variable(
    name='initialized_array',
    primitive='uint8_t',
    qualifiers='const',
    array=100,
    comment=None,
    value=[n for n in range(10)],
    value_opts='{0:x}')
var3 = Variable(
    name='multidim_initialized_array',
    primitive='uint8_t',
    qualifiers='const',
    array=None,
    comment=None,
    value=[[0 for _ in range(3)] for _ in range(3)],
    value_opts='{0:x}')

h.add_variable_declaration(var1, extern=True)
h.add_variable_declaration(var2, extern=True)
h.add_variable_declaration(var3, extern=True)

h.end_if_def()

h.write_to_file("main.h")

# now define the c file!
c = CodeWriter()
c.add_autogen_comment(source="example.py")
c.add_line()
c.include("main.h")

c.add_line()

# initialize those declared variables 
c.add_variable_initialization(var1)
c.add_variable_initialization(var2)
c.add_variable_initialization(var3)

c.add_line()
c.add_line(comment="Main function")
c.add_function_definition(f1)
c.open_brace()
c.add_line("int i = 0;", comment="Iterator")
c.add_line()
c.add_line("for (i=0;i<10;i++)")
c.open_brace()
c.call_function(f2, "i")
c.close_brace()
c.add_line()
c.add_line("return 0;")
c.close_brace()

c.add_line()

c.add_line(comment="do the needful")
c.add_function_definition(f2)
c.open_brace()
c.add_line("need++;")
c.add_line("need--;")
c.close_brace()
c.add_line()

c.write_to_file("test.c")
