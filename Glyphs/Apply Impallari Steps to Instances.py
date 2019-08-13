#MenuTitle: Apply Impallari Steps to Instances
# -*- coding: utf-8 -*-

__doc__="""
Applies Impallari Steps to available instances. Make sure your instances are ordered from thinnest at top to thickest at bottom. 
"""

steps = len(Glyphs.font.instances)

min = 0
max = 0

for master in Glyphs.font.masters:
	weight = master.weightValue

	if min == 0:
		min = weight
	if max == 0:
		max = weight
	
	if weight > max:
		max = weight
	if weight < max:
		min = weight
		
def equalSteps(x):
    return (max-min)/(steps-1)*(x-1)+min

def lucasSteps(x):
    return min*pow(float(max)/min,float(x-1)/(steps-1))

def impallariSteps(x):
	return float(x-1)/(steps-1)*equalSteps(x)+float(steps-x)/(steps-1)*lucasSteps(x)

weights = []

for x in range(1,steps+1):
	weights.append(round(impallariSteps(x)))
	
for i, instance in enumerate(Glyphs.font.instances):
	instance.weightValue = weights[i]