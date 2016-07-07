from csnake import *

#generate a header file
h = CodeWriter()

HEADER = "_CSNAKE_EXAMPLE_H_"

h.addAutogenComment(source="example.py")
h.addLine()

h.startIfDef(HEADER, invert=True)
h.define(HEADER)
h.addLine()
h.include("<stdint.h>", comment="Include standard types")

h.addLine()
h.addLine(comment="This is a single line comment")
h.addLine()
h.startComment()
h.addLine("multi line comments")
h.addLine("are also supported")
h.endComment()

h.addLine()
h.addLine(comment="Define a structure")

s1 = Struct("DatStructTho", refName="destruct")

v1 = Variable("a", "uint8_t", array=5, comment='Variables can be arrays')
v2 = Variable("b", "uint16_t", qualifiers='volatile', comment='Extra qualifiers can be specified')
v3 = Variable("c", "float", comment='Variables can have associated comments')

s1.addVariable(v1)
s1.addVariable(v2)
s1.addVariable(v3)

s2 = Struct("ParentStruct_t")

s2.addVariable(s1)
s2.addVariable(Variable("x","float"))
s2.addVariable(Variable("y","float"))
s2.addVariable(Variable('z','float'))

#add the two structs to the header file
h.addStruct(s1)
h.addLine()
h.addStruct(s2)
h.addLine()

#and now some enumerations
e = Enum("EnumExample_t",prefix="ENUM_PREFIX_")
e.addValue("A")
e.addValue("B",value=10,comment="Enum values can have comments too")
e.addValue("C")
e.addValue("D")

h.addEnum(e)

#add prototype for the main function
f1 = Function("main", returnType="int")

h.addLine()
h.addFunctionPrototype(f1,comment="main function prototype")
h.addLine()

#now add another function
f2 = Function("doTheNeedful", returnType="void")
f2.addVariable(Variable("need","int"))

h.addFunctionPrototype(f2, comment="Do the Needful")

h.addLine()
h.endIfDef()

h.writeToFile("main.h")

#now define the c file!
c = CodeWriter()
c.addAutogenComment(source="example.py")
c.addLine()
c.include("main.h")

c.addLine()
c.addLine(comment="Main function")
c.addFunctionDefinition(f1)
c.openBrace()
c.addLine("int i = 0;",comment="Iterator")
c.addLine()
c.addLine("for (i=0;i<10;i++)")
c.openBrace()
c.callFunction(f2,"i")
c.closeBrace()
c.addLine()
c.addLine("return 0;")
c.closeBrace()

c.addLine()

c.addLine(comment="do the needful")
c.addFunctionDefinition(f2)
c.openBrace()
c.addLine("need++;")
c.addLine("need--;")
c.closeBrace()
c.addLine()

c.writeToFile("main.c")
