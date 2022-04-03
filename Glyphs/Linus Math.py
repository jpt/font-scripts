# import vanilla todo - axis mappings etc built into glyphs
from math import exp, log

# python 3 + 2
try:
    xrange
except NameError:
    xrange = range

# https://bugs.python.org/msg59137

def signum(x):
	return (x > 0) - (x < 0)

# begin linus romer / lucas de groot stuff - https://github.com/linusromer/stepinterpolation

def expo(x, xa, ya, xb, yb):
	return ya*pow(ya/yb,((x-xa)/(xa-xb)))

def expoSquare(x, k):
	if (k == 0):
		return x
	else:
		return (exp(k*x)-1)/(exp(k)-1)

def expoRect(x, k, xa, ya, xb, yb):
	return (yb-ya)*expoSquare((x-xa)/(xb-xa),k)+ya

def findK(xa, ya, xb, yb, xc, yc):
	ka = -99.0
	kb = 100.0
	k = 1.0
	for i in xrange(0,100):
		k = (ka+kb)/2;
		if(expoRect(xc,k,xa,ya,xb,yb)*signum(yb-ya) > yc*signum(yb-ya)):
			ka = k
		else:
			kb = k
	return k

def getLucasSteps(stepA,valueA,stepB,valueB,stepC,valueC,stepWidth,decimals,numberOfSteps,leastStepNumber):
	if (valueA == 0):
	    k = 1.0
	else:
	    k = float(log(valueB/valueA))
	values = []
	for i in xrange(0,int(numberOfSteps)):
		x = leastStepNumber + i * stepWidth
		if(stepC is False or valueC is False):
			if (valueA*valueB == 0):
				y = expoRect(x,stepA,valueA,stepB,valueB)
			else:
				y = expo(x,stepA,valueA,stepB,valueB)
		else:
			k = findK(stepA,valueA,stepB,valueB,stepC,valueC)
			y = expoRect(x,k,stepA,valueA,stepB,valueB)
		values.append(otRound(y,decimals))
	return values

# end linus/lucas stuff

def getEqualSteps(valueA,valueB,numberOfSteps,decimals):
	def equalSteps(x,valueA,valueB,numberOfSteps):
		return (valueB-valueA)/(numberOfSteps-1)*(x-1)+valueA
	values = []
	for x in xrange(1,int(numberOfSteps)+1):
		value = equalSteps(x,valueA,valueB,numberOfSteps)
		values.append(otRound(value,decimals))
	return values

def transformToRange(c,d,arr,decimals):
	values = []
	a = arr[0]
	b = arr[len(arr)-1]
	
	def affine(x,a,b,c,d): # x, minInput, maxInput, minOutput, maxOutput -- see https://math.stackexchange.com/q/377169
		return otRound(((x-a)*((d-c)/(b-a))+c), decimals)
		
	for x in range(0,len(arr)):
		values.append(affine(arr[x],a,b,c,d))
	return values

def otRound(num,decimals=5):
	num = round(num,decimals)
	if(num.is_integer()):
		num = int(num)
	return num
	
				
def main():
	
	# these will be inputs, values are just for demonstration
	
	stepA = 1.0
	valueA = 20.0
	stepB = 9.0
	valueB = 111.0
	stepC = 4
	valueC = 90	
	leastStepNumber = stepA
	greatestStepNumber = stepB 
	stepWidth = 1
	decimals = 5  #  not implemented yet, because todo:  default to be as specific as the spec will allow (aka todo: look into it). 
	numberOfSteps = (greatestStepNumber-leastStepNumber+1)/stepWidth

	
	# get the values & print
	
	lucasSteps = getLucasSteps(stepA,valueA,stepB,valueB,stepC,valueC,stepWidth,decimals,numberOfSteps,leastStepNumber)
	equalSteps = getEqualSteps(valueA,valueB,numberOfSteps,decimals)
	
	print(lucasSteps)
	print(equalSteps)
	
	varSteps = transformToRange(0,1000,lucasSteps,decimals) # just for for example, a weight axis from 0-1000, but other axes will need other values. I will bake those values into the logic if there is an axis tag. todo. 
	varEqualSteps = transformToRange(0,1000,equalSteps,decimals)

	
	
	print(varSteps)
	print(varEqualSteps)
		
	###
	
	### again, this time lets say targeting WOFF/CSS 
		
	stepA = 1.0
	valueA = 100.0
	stepB = 9.0
	valueB = 900.0
	stepC = False
	valueC = False	
	leastStepNumber = stepA
	greatestStepNumber = stepB 
	stepWidth = 1
	decimals = 5  #  not implemented yet, because todo:  default to be as specific as the spec will allow (aka todo: look into it). 

	
	# get the values & print
	
	lucasSteps = getLucasSteps(stepA,valueA,stepB,valueB,stepC,valueC,stepWidth,decimals,numberOfSteps,leastStepNumber)
	equalSteps = getEqualSteps(valueA,valueB,numberOfSteps,decimals)
	
	print(lucasSteps)
	print(equalSteps)
	
	varSteps = transformToRange(0,1000,lucasSteps,decimals) # just for for example, a weight axis from 0-1000, but other axes will need other values. I will bake those values into the logic if there is an axis tag. todo. 
	varEqualSteps = transformToRange(100,900,equalSteps,decimals) 
	
	print(varSteps)
	print(varEqualSteps)

main()

