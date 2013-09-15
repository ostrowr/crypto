import math
import itertools
import re
#import inspect
import unittest
import sys
import argparse
from fractions import Fraction


class Crypto:
    """Solves 'Crypto' for arbitrary functions.

    Traditionally, 'Crypto' a game with the goal:
    "given five numbers, create an expression with
    the first 4 numbers and the arithmetic operators
    such that its evaluation is equal to the fifth number." 
    This class extends that concept and allows crypto 
    to be extended to n numbers and arbitrary functions.

    Attributes:
        unary: a list of functions that take one value.
        binary: a list of functions that take two values.
        language: a CFG that defines function composition
        nonterminals: a string with all of the nonterminals in 
            the language, seperated by `|`
        funcNames: a string with all of the function names
            available, seperated by `|`
        ulimit: the number of unary functions allowed in an expression
        templates: a list of expression templates with placeholder
            values in place of real numbers.
            e.g. `Fmult(Fsum(TERM, TERM), TERM)
        equations: a list of expressions in function format.
            e.g. `Fmult(Fsum(32, 6), 9)
        solutions: a dictionary containing the shortest expression
            that give each result.
            e.g. {'1': '(3-2)/1', '2': '3-2+1'...}
    """


    def __init__(self):
        """
        Inits Crypto with default values.
        """
        self.unary = [Fsqrt]
        self.binary = [Fadd, Fsub, Fdiv, Fmult]
        self.language = self.genLanguage()
        self.nonterminals = '|'.join(self.language.keys())
        self.funcNames = '|'.join(listFunctionNames(self.unary + self.binary))
        self.ulimit = 4
        self.templates = None
        self.equations = None
        self.solutions = None

    def addFunction(self):
        pass
        # inspect.getargspec(<function>).args


    def genLanguage(self):
        """
        Returns the language that generates all 
        possible function compositions of self.unary
        and self.binary.
        """
        return  {
        'START': ['UNARY', 'BINARY', 'NUM'],
        'UNARY': ['UFUNC(PARAMETER)'],
        'BINARY': ['BFUNC(PARAMETER,PARAMETER)'],
        'PARAMETER': ['UNARY', 'BINARY', 'NUM'],
        'UFUNC': listFunctionNames(self.unary),
        'BFUNC': listFunctionNames(self.binary),
        'NUM': ['TERM', 'TERMNUM'],
    }


    def generateTemplates(self, numParams):
        """
        Generates all templates for expressions.

        Args:
            numParams: The number of terminals (numbers)
                that are allowed in each template.

        Returns:
            A list containing all legal templates.
        """
        generated = []
        self.__generateTemplatesR('START', self.ulimit, numParams, generated)
        generated = [s for s in generated if s.count('TERM') == numParams]
        self.templates = generated
        return self.templates


    def __generateTemplatesR(self, builtString, uLimit, numParameters, generated):
        """
        Recursive function to generate templates.

        Args:
            builtString: Template string that is recursively built.
            uLimit: Maximum number of unary functions allowed in the template.
            numParameters: The number of parameters for the template.
            generated: A list of templates that this function populates.
        
        Returns:
            None
        """
        match = re.search(self.nonterminals, builtString)
        if not match:
            return builtString
        language = self.genLanguage()
        if numParameters <= 0:
            language['PARAMETER'] = ['TERM']
            language['NUM'] = ['TERM']
        if uLimit <= 0:
            language['UNARY'] = []
        for replacement in language[match.group()]:
            result = None
            if match.group() == 'UNARY':
                result = self.__generateTemplatesR(
                        self.resub(match, replacement, builtString), 
                        uLimit - 1, 
                        numParameters, 
                        generated
                        )
            elif match.group() == 'PARAMETER':
                result = self.__generateTemplatesR(
                        self.resub(match, replacement, builtString), 
                        uLimit, 
                        numParameters - 1, 
                        generated
                        )
            elif match.group() == 'NUM' \
                    and builtString[match.start() - 4:match.start()] == 'TERM':
                result = self.__generateTemplatesR(
                        self.resub(match, replacement, builtString), 
                        uLimit, 
                        numParameters - 1, 
                        generated
                        )
            else: 
                result = self.__generateTemplatesR(
                        self.resub(match, replacement, builtString), 
                        uLimit, 
                        numParameters, 
                        generated
                        )
            if result:
                generated.append(result)
        return


    def generateEquations(self, numList, templates=None):
        """
        Generates a list of legal expressions.

        Args:
            numList: A list of numbers (string or numeric)
                with which expressions can be generated.
            templates: A list of templates to be filled with
                the numbers in numList. If None, is automatically
                filled.

        Returns:
            A list of expressions that contain all of the numbers
            in numList.
        """
        equations = []
        if templates is None:
            return self.generateEquations(
                    numList, 
                    self.generateTemplates(len(numList))
                    )
        for template in templates:
            for permutation in itertools.permutations(
                        iterableToStrIterable(numList)
                        ):
                equation = template
                for num in permutation:
                    equation = equation.replace('TERM', num, 1)
                equations.append(equation)
        self.equations = equations
        return self.equations


    @staticmethod
    def resub(match, replace, builtString):
        """ 
        given an re.matchObject, replaces the match in builtString with
        replace. Assumes that the match object comes from builtString.
        """ 
        return builtString[:match.start()] + replace + builtString[match.end():]


    # def prettyPrintWithKeyCondition(self, condition):
    #     print "Precise Solutions:"
    #     for sol in sorted(self.precise_solutions.keys()):
    #         if condition(sol):
    #             print "\t", sol, shortest(self.precise_solutions[sol]) #shortest isn't working!
    #     print "\nImprecise Solutions:"
    #     for sol in sorted(self.imprecise_solutions.keys()):
    #         if condition(sol):
    #             print "\t", sol, shortest(self.imprecise_solutions[sol])
    #     print

    # @staticmethod
    # def isCloseToInt(n):
    #     a = int(n + .1)
    #     if abs(a - n) <= .00001:
    #         return True
    #     return False 



    def solveCrypto(self, numList, equations=None, templates=None):
        """
        Finds all solutions to Crypto!

        Args:
            numList: List of numbers (string or numeric) to solve for.
            equations: a list of equations generated by numList.
                if None, automatically generated.
            templates: templates for len(numList) params.
                if None, automatically generated.

        Returns:
            a dict containing the shortest expression for each solution.
        """
        if equations is None:
            return self.solveCrypto(
                    numList, 
                    self.generateEquations(numList, templates), 
                    templates
                    )
        solutions = {}
        for equation in equations:
            expression = self.convertToReadable(equation)
            try:
                value = self.evalExpression(equation)
            except Exception as e:
                value = str(e)
            curr = solutions.get(value)
            if not curr or len(expression) < len(curr):
                solutions[value] = expression
                # only one solution per value
        self.solutions = solutions
        return solutions


    @staticmethod
    def stripParens(expression):
        if expression[0] == '(' and expression[-1] == ')':
            return expression[1:-1]
        return expression


    def printIntegralSolutions(self):
        integral = {int(k): v for (k, v) in self.solutions.items() if not re.search('^[a-zF]|/', k)}
        fractional = {Fraction(k): v for (k, v) in self.solutions.items() if re.search('/', k)}
        for i in sorted(integral.keys()):
            print i, self.stripParens(integral[i])


    def convertToReadable(self, expression):
        operator, paramList, start, end = self.getLastFunction(expression)
        while operator:
            result = globals()[operator](*paramList)
            expression = expression[:start] + str(result) + expression[end+1:] #here
            operator, paramList, start, end = self.getLastFunction(expression)
        return expression


    def evalExpression(self, expression):
        operator, paramList, start, end = self.getLastFunction(expression)
        while operator:
            result = globals()[operator](*[Fraction(i) for i in paramList])
            expression = expression[:start] + str(result.getVal()) + expression[end+1:]
            operator, paramList, start, end = self.getLastFunction(expression)
        return expression


    def getLastFunction(self, expression):
        pattern = re.compile('(?:.*)(' + self.funcNames + ')\(')
        match = pattern.search(expression)
        if not match:
            return None, None, None, None
        operator = match.group(1)
        start = match.start(1)
        paramStart = match.end(1)
        numParens = 1
        pos = paramStart + 1
        while numParens:
            if expression[pos] == ')':
                numParens -= 1
            elif expression[pos] == '(':
                numParens += 1
            pos += 1
        return operator, expression[paramStart+1:pos-1].split(','), start, pos - 1



# def appendIntoDict(dictionary, key, val):
#     if dictionary.get(key) is None:
#         dictionary[key] = [val]
#     else:
#         dictionary[key].append(val)

# def shortest(iterator):
#     minL = iterator[0]
#     shortest = iterator[0]
#     for i in iterator:
#         length = len(i)
#         if length < minL:
#             minL = length
#             shortest = i
#     return i


class Operator:
    pass


class Fneg(Operator):
    def __init__(self, a):
        self.a = a
    def __str__(self):
        return '(-' + str(self.a) + ')'
    def __name__(self):
        return 'Fneg'
    def getVal(self):
        return -self.a


class Fsqrt(Operator):
    def __init__(self, a):
        self.a = a
    def __str__(self):
        return 'sqrt(' + str(self.a) + ')'
    def __name__(self):
        return 'Fsqrt'
    def getVal(self):
        return Fraction(math.sqrt(self.a))


class Ffact(Operator):
    def __init__(self, a):
        self.a = a
    def __str__(self):
        return '(' + str(self.a) + '!)'
    def __name__(self):
        return 'Ffact'
    def getVal(self):
        if self.a.denominator == 1:
            return math.factorial(a)
        return a


class Fadd(Operator):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __str__(self):
        return '(' + str(self.a) + '+' + str(self.b) + ')'
    def __name__(self):
        return 'Fadd'
    def getVal(self):
        return self.a + self.b


class Fsub(Operator):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __str__(self):
        return '(' + str(self.a) + '-' + str(self.b) + ')'
    def __name__(self):
        return 'Fsub'
    def getVal(self):
        return self.a - self.b


class Fdiv(Operator):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __str__(self):
        return '(' + str(self.a) + '/' + str(self.b) + ')'
    def __name__(self):
        return 'Fdiv'
    def getVal(self):
        return Fraction(self.a) / Fraction(self.b)


class Fmult(Operator):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __str__(self):
        return '(' + str(self.a) + '*' + str(self.b) + ')'
    def __name__(self):
        return 'Fmult'
    def getVal(self):
        return self.a * self.b



# #does this change the solutions? FM: Test
# def fneg(n):
#     return -n

# def fexp(a, b):
#     return Fraction(a ** b)

# def ffact(n):
#     if n.denominator == 1:
#         return math.factorial(n.numerator)
#     return n

# ##################################################

# def fsqrt(n):
#     return Fraction(math.sqrt(n))

# def fadd(a, b):
#     return a + b

# def fsub(a, b):
#     return a - b

# def fdiv(a, b):
#     return Fraction(a) / Fraction(b)

# def fmult(a, b):
#     return a * b


###################################################


def listFunctionNames(listOfFunctions):
    return [f.__name__ for f in listOfFunctions]
    

def iterableToStrIterable(iterable):
    return [str(i) for i in iterable]


def main():
    #USE ARGPARSE!
    # pCount = raw_input('\nThis program gives all integral solutions to Crypto.\n\n Enter the number of parameters: ')
    # c = Crypto()
    # templates = c.generateTemplates(int(pCount))
    # params = raw_input('\n Enter ' + pCount + ' numbers to solve Crypto, or press [enter] to quit. ')
    # params = params.split(' ')
    # if not params:
    #     return
    # print params
    # solutions = c.solveCrypto(sys.argv[1:])
    # c.printIntegralSolutions()


if __name__ == '__main__':
    main()
