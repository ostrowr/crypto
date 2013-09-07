import math
import itertools
import re
from fractions import Fraction


#does this change the solutions? FM: Test
def fneg(n):
    return -n

def fexp(a, b):
    return Fraction(a ** b)

def ffact(n):
    if n.denominator == 1:
        return Fraction(math.factorial(n.numerator))
    return n

##################################################

def fsqrt(n):
    return Fraction(math.sqrt(n))

def fadd(a, b):
    return a + b

def fsub(a, b):
    return a - b

def fdiv(a, b):
    return a / b

def fmult(a, b):
    return a * b

###################################################

def listFunctionNames(listOfFunctions):
    return [f.__name__ for f in listOfFunctions]
    
def iterableToStrIterable(iterable):
    return [str(i) for i in iterable]

#can I generate these programmatically?
UNARY = [fsqrt]#, ffact]#fneg, fsqrt]#fnull

BINARY = [fadd, fsub, fdiv, fmult]#, fexp]

def genLanguage(fUnary = UNARY, fBinary = BINARY):
    return  {
    'START': ['UNARY', 'BINARY', 'NUM'],
    'UNARY': ['UFUNC(PARAMETER)'],
    'BINARY': ['BFUNC(PARAMETER,PARAMETER)'],
    'PARAMETER': ['UNARY', 'BINARY', 'NUM'],
    'UFUNC': listFunctionNames(fUnary),
    'BFUNC': listFunctionNames(fBinary)
}

dictKeysRegex = r'START|UNARY|BINARY|PARAMETER|UFUNC|BFUNC'

def generateEquations(numList):
    templates = generateTemplates(len(numList))
    groupedByNum = groupList(numList)
    return fillExpressions(templates, groupedByNum)

def fillExpressions(templates, groups):
    intSolutions = {}
    maybeIntSolutions = {}
    for template in templates:
        count = template.count('NUM')
        for group in groups[count]:
            realExpression = replaceWithRealNumbers(template, group)
            result = None
            try:
                result = eval(realExpression)
            except ZeroDivisionError:
                pass
            except ValueError:
                pass
            except OverflowError:
                pass
            if result and result.denominator == 1:
                intSolutions[result.numerator] = realExpression
            elif result:
                limited = result.limit_denominator()
                if limited.denominator == 1:
                    maybeIntSolutions[limited.numerator] = realExpression
                
    return intSolutions, maybeIntSolutions

def replaceWithRealNumbers(template, grouping):
    for group in grouping:
        template = template.replace('NUM', 'Fraction(' + group + ')', 1)
    return template

def resub(match, replace, builtString):
    return builtString[:match.start()] + replace + builtString[match.end():]

def generateTemplates(numParams):
    generated = []
    generateTemplatesR('START', numParams, numParams, generated)
    generated = [s for s in generated if s.count('NUM') <= numParams]
    return generated

def generateTemplatesR(builtString, uLimit, numParameters, generated):
    match = re.search(dictKeysRegex, builtString)
    if not match:
        return builtString
    language = genLanguage()
    if numParameters <= 0:
        language['PARAMETER'] = ['NUM']
    if uLimit <= 0:
        language['UNARY'] = []
    for replacement in language[match.group()]:
        result = None
        if match.group() == 'UNARY':
            result = generateTemplatesR(resub(match, replacement, builtString), uLimit - 1, numParameters, generated)
        elif match.group() == 'PARAMETER':
            result = generateTemplatesR(resub(match, replacement, builtString), uLimit, numParameters - 1, generated)
        elif match.group() == 'NUM':
            result = generateTemplatesR(resub(match, replacement, builtString), uLimit, numParameters, generated)
        else: 
            result = generateTemplatesR(resub(match, replacement, builtString), uLimit, numParameters, generated)
        if result:
            generated.append(result)
    return

# I took this function (slightly modified) from
# http://stackoverflow.com/questions/10035752/elegant-python-code-for-integer-partitioning 
def partitionInt(number):
     answer = set()
     answer.add((number, ))
     for x in range(1, number):
         for y in partitionInt(number - x):
             answer.add(tuple((x, ) + y))
     return answer


def groupList(numList):
    groupedWithLength = {n:[] for n in range(1, len(numList) + 1)}
    numList = iterableToStrIterable(numList)
    partitions = partitionInt(len(numList))
    for permutation in itertools.permutations(numList):
        for partition in partitions:
            g = groupByPattern(permutation, partition)
            groupedWithLength[len(g)].append(g)
    return groupedWithLength 
            

def groupByPattern(numList, pattern):
    grouped = []
    for length in pattern:
        grouped.append(''.join(numList[:length]))
        numList = numList[length:]
    return grouped


