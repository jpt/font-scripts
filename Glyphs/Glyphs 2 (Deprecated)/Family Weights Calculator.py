#MenuTitle: Family Weights Calculator
# -*- coding: utf-8 -*-

__doc__="""
Calculate and apply stem weights to your font family.
"""

import vanilla

class FamilySteps( object ):
	def __init__( self ):
		
		windowWidth  = 306
		windowHeight = 372
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), 
			"Family Weights Calculator",
		)

		linePos, inset, lineHeight = 12, 15, 22

		self.w.numStepsText = vanilla.TextBox( (inset, linePos+2, 110, 17), "Number of steps:", sizeStyle='small')

		self.w.numSteps = vanilla.EditText( (inset+110, linePos, 32, 20), int(self.numInstances()), sizeStyle = 'small')

		linePos += lineHeight


		self.w.minStemText = vanilla.TextBox( (inset, linePos+2, 110, 17), "Thin stem width:", sizeStyle='small')
		self.w.minStem = vanilla.EditText( (inset+110, linePos, 32, 20), int(self.minMax()[0]), sizeStyle = 'small')
		
		linePos += lineHeight

		self.w.maxStemText = vanilla.TextBox( (inset, linePos+2, 110, 17), "Black stem width:", sizeStyle='small')
		self.w.maxStem = vanilla.EditText( (inset+110, linePos, 32, 20), int(self.minMax()[1]), sizeStyle = 'small')
		
		linePos += lineHeight+8

		self.w.calcButton = vanilla.Button((inset,linePos, 120, 17), "Calculate", sizeStyle='small', callback=self.calculate)
		self.w.setDefaultButton( self.w.calcButton )


		linePos += lineHeight+6

		self.w.equalColumn = vanilla.TextBox( (inset, linePos+2, 70, 17), "Equal", sizeStyle='small')
		self.w.lucasColumn = vanilla.TextBox( (inset+72, linePos+2, 70, 17), "Luc(as)", sizeStyle='small')
		self.w.impallariColumn = vanilla.TextBox( (inset+144, linePos+2, 70, 17), "Impallari", sizeStyle='small')
		self.w.abrahamColumn = vanilla.TextBox( (inset+216, linePos+2, 70, 17), "Abraham", sizeStyle='small')


		linePos += lineHeight

		self.w.equalList = vanilla.List( (inset, linePos+2, 60, (17*(self.numInstances()+1))+8), self.equalWeights(self.minMax()[0],self.minMax()[1],self.numInstances()))
		self.w.lucasList = vanilla.List( (inset+72, linePos+2, 60, (17*(self.numInstances()+1))+8), self.lucasWeights(self.minMax()[0],self.minMax()[1],self.numInstances()))
		self.w.impallariList = vanilla.List( (inset+144, linePos+2, 60, (17*(self.numInstances()+1))+8), self.impallariWeights(self.minMax()[0],self.minMax()[1],self.numInstances()))
		self.w.abrahamList = vanilla.List( (inset+216, linePos+2, 60, (17*(self.numInstances()+1))+8), self.abrahamWeights(self.minMax()[0],self.minMax()[1],self.numInstances()))
		
		linePos += lineHeight*9 -8

		self.w.applyEqual = vanilla.Button((inset,linePos, 60, 17), "Apply", sizeStyle='small', callback=self.apply)
		self.w.applyLucas = vanilla.Button((inset+72,linePos, 60, 17), "Apply", sizeStyle='small', callback=self.apply)
		self.w.applyImpallari = vanilla.Button((inset+144,linePos, 60, 17), "Apply", sizeStyle='small', callback=self.apply)
		self.w.applyAbraham = vanilla.Button((inset+216,linePos, 60, 17), "Apply", sizeStyle='small', callback=self.apply)
		

		self.w.open()
		

	def calculate(self,sender):
		steps, min, max = float(self.w.numSteps.get()), float(self.w.minStem.get()), float(self.w.maxStem.get())

		equalWeights = self.equalWeights(min,max,steps)
		lucasWeights = self.lucasWeights(min,max,steps)
		impallariWeights = self.impallariWeights(min,max,steps)
		abrahamWeights = self.abrahamWeights(min,max,steps)

		self.w.equalList.set(equalWeights)
		self.w.lucasList.set(lucasWeights)
		self.w.impallariList.set(impallariWeights)
		self.w.abrahamList.set(abrahamWeights)


	def apply( self, sender ):
		steps = self.w.numSteps.get()
		existingSteps = len(Glyphs.font.instances)
		equalSteps, lucasSteps, impallariSteps, abrahamSteps = self.w.equalList.get(), self.w.lucasList.get(), self.w.impallariList.get(), self.w.abrahamList.get()

		if(int(steps) != int(existingSteps)):
			Message(title="Cannot Apply Instances", message="You do not have the same number of instances in the calculator as the font. Please add/remove instances in Font Info->Instances.", OKButton=None)
			return
		else:
			if(sender == self.w.applyEqual):
				for i, instance in enumerate(Glyphs.font.instances):
					instance.weightValue = equalSteps[i]
			elif(sender == self.w.applyLucas):
				for i, instance in enumerate(Glyphs.font.instances):
					instance.weightValue = lucasSteps[i]
			elif(sender == self.w.applyImpallari):
				for i, instance in enumerate(Glyphs.font.instances):
					instance.weightValue = impallariSteps[i]
			elif(sender == self.w.applyAbraham):
				for i, instance in enumerate(Glyphs.font.instances):
					instance.weightValue = abrahamSteps[i]

	def numInstances( self ):
		try:
			if(self.w.numSteps.get() > 0):
				return float(self.w.numSteps.get())
			else:
				return 9.0
		except:
			numInstances = len(Glyphs.font.instances)
			if(numInstances>2):
				return numInstances
			else:
				return 9.0

	def equalWeights( self, min, max, steps ):
		equalWeights = []
		for x in range(1,int(steps)+1):
			equalWeights.append(int(round(self.equalSteps(float(x),min,max,steps))))
		return equalWeights

	def impallariWeights( self, min, max, steps ):
		impallariWeights = []
		for x in range(1,int(steps)+1):
			impallariWeights.append(int(round(self.impallariSteps(float(x),min,max,steps))))
		return impallariWeights

	def lucasWeights( self, min, max, steps ):
		lucasWeights = []
		for x in range(1,int(steps)+1):
			lucasWeights.append(int(round(self.lucasSteps(float(x),min,max,steps))))
		return lucasWeights

	def abrahamWeights( self, min, max, steps ):
		abrahamWeights = []
		for x in range(1,int(steps)+1):
			abrahamWeights.append(int(round(self.abrahamSteps(float(x),min,max,steps))))
		return abrahamWeights


	def minMax( self ):

		try:
			if(self.w.minStem.get() > 0 and self.w.maxStem.get() > 0):
				return [float(self.w.minStem.get()), float(self.w.maxStem.get())]
		except:
			min = 0
			max = 0
			if(len(Glyphs.font.masters) > 1):
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
				return [float(round(min)),float(round(max))]
			else:
				return [20.0, 200.0]

	def equalSteps(self,x,min,max,steps):
		return (max-min)/(steps-1)*(x-1)+min

	def lucasSteps(self,x,min,max,steps):
	    return min*pow(max/min,(x-1)/(steps-1))

	def impallariSteps(self,x,min,max,steps):
		return (x-1)/(steps-1)*self.equalSteps(x,min,max,steps)+(steps-x)/(steps-1)*self.lucasSteps(x,min,max,steps)

	def abrahamSteps(self,x,min,max,steps):
		return (1-pow((x-1)/(steps-1),1.25))*self.equalSteps(x,min,max,steps)+pow((x-1)/(steps-1),1.25)*self.lucasSteps(x,min,max,steps)

FamilySteps()
