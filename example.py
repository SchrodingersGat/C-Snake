from csnake import *

# generate a header file
h = CodeWriter()

HEADER = "_CSNAKE_EXAMPLE_H_"

h.add_autogen_comment(source="example.py")
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
v2 = Variable("b", "uint16_t", qualifiers='volatile',
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
f2.add_variable(Variable("need", "int"))

h.add_function_prototype(f2, comment="Do the Needful")

h.add_line()
h.end_if_def()

h.write_to_file("main.h")

# now define the c file!
c = CodeWriter()
c.add_autogen_comment(source="example.py")
c.add_line()
c.include("main.h")

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
