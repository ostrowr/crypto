import math
import itertools
import re
import inspect
from fractions import Fraction

class Crypto:
    def __init__(self):
        self.unary = [fsqrt]
        self.binary = [fadd, fsub, fdiv, fmult]
        self.language = self.genLanguage()
        self.nonterminals = '|'.join(self.language.keys())

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

# def genLanguage(fUnary = UNARY, fBinary = BINARY):
#     return  {
#     'START': ['UNARY', 'BINARY', 'NUM'],
#     'UNARY': ['UFUNC(PARAMETER)'],
#     'BINARY': ['BFUNC(PARAMETER,PARAMETER)'],
#     'PARAMETER': ['UNARY', 'BINARY', 'NUM'],
#     'UFUNC': listFunctionNames(fUnary),
#     'BFUNC': listFunctionNames(fBinary),
#     'NUM': ['TERM', 'TERMNUM'],
#     #'TERMNUM': ['TERMNUM']
#     # define num to concat here
# }

# dictKeysRegex = r'START|NUM|UNARY|BINARY|PARAMETER|UFUNC|BFUNC'

# def generateEquations(numList):
#     templates = generateTemplates(len(numList))
#     groupedByNum = groupList(numList)
#     return fillExpressions(templates, groupedByNum)

# def fillExpressions(templates, groups):
#     intSolutions = {}
#     maybeIntSolutions = {}
#     for template in templates:
#         count = template.count('NUM')
#         for group in groups[count]:
#             realExpression = replaceWithRealNumbers(template, group)
#             result = None
#             try:
#                 result = eval(realExpression)
#             except ZeroDivisionError:
#                 pass
#             except ValueError:
#                 pass
#             except OverflowError:
#                 pass
#             if result and result.denominator == 1:
#                 intSolutions[result.numerator] = realExpression
#             elif result:
#                 limited = result.limit_denominator()
#                 if limited.denominator == 1:
#                     maybeIntSolutions[limited.numerator] = realExpression
#     return intSolutions, maybeIntSolutions

# def replaceWithRealNumbers(template, grouping):
#     for group in grouping:
#         template = template.replace('NUM', 'Fraction(' + group + ')', 1)
#     return template

# def resub(match, replace, builtString):
#     return builtString[:match.start()] + replace + builtString[match.end():]

# def generateTemplates(numParams):
#     generated = []
#     generateTemplatesR('START', numParams, numParams, generated)
#     generated = [s for s in generated if s.count('TERM') == numParams]
#     return generated


# def generateTemplatesR(builtString, uLimit, numParameters, generated):
#     match = re.search(dictKeysRegex, builtString)
#     if not match:
#         return builtString
#     language = genLanguage()
#     if numParameters <= 0:
#         language['PARAMETER'] = ['TERM']
#         language['NUM'] = ['TERM']
#     if uLimit <= 0:
#         language['UNARY'] = []
#     for replacement in language[match.group()]:
#         result = None
#         if match.group() == 'UNARY':
#             result = generateTemplatesR(resub(match, replacement, builtString), uLimit - 1, numParameters, generated)
#         elif match.group() == 'PARAMETER':
#             result = generateTemplatesR(resub(match, replacement, builtString), uLimit, numParameters - 1, generated)
#         elif match.group() == 'NUM' and builtString[match.start() - 4:match.start()] == 'TERM':
#             result = generateTemplatesR(resub(match, replacement, builtString), uLimit, numParameters - 1, generated)
#         else: 
#             result = generateTemplatesR(resub(match, replacement, builtString), uLimit, numParameters, generated)
#         if result:
#             generated.append(result)
#     return

# # I took this function (slightly modified) from
# # http://stackoverflow.com/questions/10035752/elegant-python-code-for-integer-partitioning 
# def partitionInt(number):
#      answer = set()
#      answer.add((number, ))
#      for x in range(1, number):
#          for y in partitionInt(number - x):
#              answer.add(tuple((x, ) + y))
#      return answer


# def groupList(numList):
#     groupedWithLength = {n:[] for n in range(1, len(numList) + 1)}
#     numList = iterableToStrIterable(numList)
#     partitions = partitionInt(len(numList))
#     for permutation in itertools.permutations(numList):
#         for partition in partitions:
#             g = groupByPattern(permutation, partition)
#             groupedWithLength[len(g)].append(g)
#     return groupedWithLength 
            

# def groupByPattern(numList, pattern):
#     grouped = []
#     for length in pattern:
#         grouped.append(''.join(numList[:length]))
#         numList = numList[length:]
#     return grouped


