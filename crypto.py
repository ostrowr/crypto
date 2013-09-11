import math
import itertools
import re
import inspect
from fractions import Fraction

class Crypto:
    def __init__(self):
        self.unary = [Fsqrt]
        self.binary = [Fadd, Fsub, Fdiv, Fmult]
        self.language = self.genLanguage()
        self.nonterminals = '|'.join(self.language.keys())
        self.funcNames = '|'.join(listFunctionNames(self.unary + self.binary))

    def addFunction(self):
        pass
        # inspect.getargspec(<function>).args

    def genLanguage(self):
        return  {
        'START': ['UNARY', 'BINARY', 'NUM'],
        'UNARY': ['UFUNC(PARAMETER)'],
        'BINARY': ['BFUNC(PARAMETER,PARAMETER)'],
        'PARAMETER': ['UNARY', 'BINARY', 'NUM'],
        'UFUNC': listFunctionNames(self.unary),
        'BFUNC': listFunctionNames(self.binary),
        'NUM': ['TERM', 'TERMNUM'],
        #'TERMNUM': ['TERMNUM']
        # define num to concat here
    }

    def generateTemplates(self, numParams):
        generated = []
        self.__generateTemplatesR('START', numParams, numParams, generated)
        generated = [s for s in generated if s.count('TERM') == numParams]
        self.templates = generated
        return self.templates


    def __generateTemplatesR(self, builtString, uLimit, numParameters, generated):
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
                result = self.__generateTemplatesR(self.resub(match, replacement, builtString), uLimit - 1, numParameters, generated)
            elif match.group() == 'PARAMETER':
                result = self.__generateTemplatesR(self.resub(match, replacement, builtString), uLimit, numParameters - 1, generated)
            elif match.group() == 'NUM' and builtString[match.start() - 4:match.start()] == 'TERM':
                result = self.__generateTemplatesR(self.resub(match, replacement, builtString), uLimit, numParameters - 1, generated)
            else: 
                result = self.__generateTemplatesR(self.resub(match, replacement, builtString), uLimit, numParameters, generated)
            if result:
                generated.append(result)
        return


    def generateEquations(self, numList, templates=None):
        equations = []
        if templates is None:
            return self.generateEquations(numList, self.generateTemplates(len(numList)))
        for template in templates:
            for permutation in itertools.permutations(iterableToStrIterable(numList)):
                equation = template
                for num in permutation:
                    equation = equation.replace('TERM', num, 1)
                equations.append(equation)
        self.equations = equations
        return self.equations


    def solveCrypto(self, numList, equations=None, templates=None):
        if equations is None:
            return self.solveCrypto(numList, self.generateEquations(numList, templates), templates)
        solutions = {}
        imprecise = {}
        invalid = {}
        for equation in equations:
            impreciseFlag = False
            errorFlag = False
            try:
                result = eval(equation)
            except ZeroDivisionError:
                errorFlag = True
                result = "Zero Division Error"
            except OverflowError:
                errorFlag = True
                result = "Overflow Error"
            except ValueError:
                errorFlag = True
                result = "Math Domain Error"
            except exception as e:
                errorFlag = True
                result = e
            if errorFlag:
                appendIntoDict(invalid, result, equation)
                continue
            if result.denominator != 1:
                newResult = result.limit_denominator()
                if newResult != result:
                    result = float(result)
                    impreciseFlag = True
            if impreciseFlag:
                appendIntoDict(imprecise, result, equation)
            else:
                appendIntoDict(solutions, result, equation)
        self.precise_solutions = solutions
        self.imprecise_solutions = imprecise #mostly not imprecise
        self.invalid_solutions = invalid
        return self.precise_solutions, self.imprecise_solutions

    @staticmethod
    def resub(match, replace, builtString):
        return builtString[:match.start()] + replace + builtString[match.end():]

    def prettyPrintWithKeyCondition(self, condition):
        print "Precise Solutions:"
        for sol in sorted(self.precise_solutions.keys()):
            if condition(sol):
                print "\t", sol, shortest(self.precise_solutions[sol]) #shortest isn't working!
        print "\nImprecise Solutions:"
        for sol in sorted(self.imprecise_solutions.keys()):
            if condition(sol):
                print "\t", sol, shortest(self.imprecise_solutions[sol])
        print

    @staticmethod
    def isCloseToInt(n):
        a = int(n + .1)
        if abs(a - n) <= .00001:
            return True
        return False 



    def solveCrypto1(self, numList, equations=None, templates=None):
        if equations is None:
            return self.solveCrypto1(numList, self.generateEquations(numList, templates), templates)

        for equation in equations:
            expression, solution, precision = evalExpression(equation)


    def evalFromRight(self, expression):
        readableExpression = expression
        result = None
        pattern = re.compile('(' + self.funcNames + ')\((\d+)(?:,(\d+)|\))')
        match = pattern.search(expression)
        operator = match.group(1)
        arg1 = match.group(2)
        arg2 = match.group(3)
        if arg2 is None:
            result = globals()[operator](Fraction(arg1))
        else:
            result = globals()[operator](Fraction(arg1), Fraction(arg2))
        print result
        #readableExpression = self.resub(match, "hello!", readableExpression)
        #print readableExpression

Fmult(4,Fsub(Fsqrt(Fmult(4, 4)),4))


#This isn't working!! fix.
def appendIntoDict(dictionary, key, val):
    if dictionary.get(key) is None:
        dictionary[key] = [val]
    else:
        dictionary[key].append(val)

def shortest(iterator):
    minL = iterator[0]
    shortest = iterator[0]
    for i in iterator:
        length = len(i)
        if length < minL:
            minL = length
            shortest = i
    return i


class Operator:
    pass




class Fneg(Operator):
    def __init__(self, a):
        self.val = -a
    def __str__(self):
        return '(-' + str(a) + ')'
    def __name__(self):
        return 'Fneg'

class Fsqrt(Operator):
    def __init__(self, a):
        self.val = Fraction(math.sqrt(n))
    def __str__(self):
        return '(sqrt(' + str(a) + '))'
    def __name__(self):
        return 'Fsqrt'

class Ffact(Operator):
    def __init__(self, a):
        if n.denominator == 1:
            self.val = math.factorial(n.numerator)
        self.val = n
    def __str__(self):
        return '(' + str(a) + '!)'
    def __name__(self):
        return 'Ffact'



class Fadd(Operator):
    def __init__(self, a, b):
        self.val = a + b
    def __str__(self):
        return '(' + str(a) + '+' + str(b) + ')'
    def __name__(self):
        return 'Fadd'


class Fsub(Operator):
    def __init__(self, a, b):
        self.val = a - b
    def __str__(self):
        return '(' + str(a) + '-' + str(b) + ')'
    def __name__(self):
        return 'Fsub'


class Fdiv(Operator):
    def __init__(self, a, b):
        self.val = Fraction(a) / Fraction(b)
    def __str__(self):
        return '(' + str(a) + '/' + str(b) + ')'
    def __name__(self):
        return 'Fdiv'


class Fmult(Operator):
    def __init__(self, a, b):
        self.val = a * b
    def __str__(self):
        return '(' + str(a) + '*' + str(b) + ')'
    def __name__(self):
        return 'Fmult'



#does this change the solutions? FM: Test
def fneg(n):
    return -n

def fexp(a, b):
    return Fraction(a ** b)

def ffact(n):
    if n.denominator == 1:
        return math.factorial(n.numerator)
    return n

##################################################

def fsqrt(n):
    return Fraction(math.sqrt(n))

def fadd(a, b):
    return a + b

def fsub(a, b):
    return a - b

def fdiv(a, b):
    return Fraction(a) / Fraction(b)

def fmult(a, b):
    return a * b


###################################################

def listFunctionNames(listOfFunctions):
    return [f.__name__ for f in listOfFunctions]
    
def iterableToStrIterable(iterable):
    return [str(i) for i in iterable]

#can I generate these programmatically?
UNARY = []#fsqrt]#, ffact]#fneg, fsqrt]#fnull

BINARY = [fadd, fsub, fdiv, fmult]#, fexp] # add a concat function instead
#of looping through all partitions?



