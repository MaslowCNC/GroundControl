#!/usr/bin/env python3

import math

import numpy

from groundcontrol.refine_calibration_parameters.kinematics import Kinematics, Calibration

####################################################################################################################
#	globals

#	conversion factor to convert chain sag correction parameter to solvable parameter
ChainSagParameterMultiplier = 1e6

#	epsilon used for calculating partials of all parameters
PartialEpsilon = 1e-2

####################################################################################################################
#	function bodies

def sqrDistance( p0, p1 ):
	return (p0[0]-p1[0])**2 + (p0[1]-p1[1])**2

def sqrHypot( p ):
	return p[0]**2 + p[1]**2

def distance( p0, p1 ):
	return math.hypot( p0[0]-p1[0], p0[1]-p1[1] )

def vectorDifference( a, b ):
	''' compute the 2D offset a-b '''

	return [ ai-bi for ai,bi in zip(a,b) ]

def flatten( l ):
	return list( sum( l, () ) )

def convertChainSagCorrectionToParameter( chainSagCorrection ):
	return chainSagCorrection * ChainSagParameterMultiplier
def convertParameterToChainSagCorrection( parameter ):
	return parameter / ChainSagParameterMultiplier

def constructKinematicsCalibrationObject( settings ):
	'''	given a set of settings from a .ini file (all values will be strings), construct the kinematics calibration 
		object
	'''
	
	#	construct calibration object
	cal = Calibration()

	#	set the values from settings
	cal.h3 = float( settings['sledcg'] )
	cal.D = float( settings['motorspacingx'] )
	
	sprocketCircumference = float( settings['gearteeth'] ) * float( settings['chainpitch'] ) 
	cal.R = sprocketCircumference / math.pi
	
	cal.machineHeight = float( settings['bedheight'] )
	cal.machineWidth = float( settings['bedwidth'] )
	cal.motorOffsetY = float( settings['motoroffsety'] )
	
	cal.chain1Offset = 0
	cal.chain2Offset = 0
	cal.rotationDiskRadius = float( settings['rotationradius'] )
	cal.chainSagCorrection = float( settings['chainsagcorrection'] )
	cal.chainOverSprocket = 1 if settings['chainoversprocket'] == 'Top' else 0 
	cal.isQuadKinematics = 0 if settings['kinematicstype'].lower().startswith( 'tri' ) else 1
	
	#	return cal
	return cal

def updateSettingsFromKinematicsCalibrationObject( calibration, maslowSettings, advancedSettings ):
	'''	given a set of settings from a .ini file (all values will be strings), and a kinematics calibration 
		object, update the appropriate settings in $settings
	'''
	cal = calibration

	#	set the values from settings
	maslowSettings['sledcg'] = '{:.02f}'.format( cal.h3 )
	maslowSettings['motorspacingx'] = '{:.02f}'.format( cal.D )

	sprocketCircumference = cal.R * math.pi
	gearteeth = float( advancedSettings['gearteeth'] )
	chainpitch = sprocketCircumference / gearteeth
	advancedSettings['chainpitch'] = '{:.02f}'.format( chainpitch )
	
	maslowSettings['bedheight'] = '{:.02f}'.format( cal.machineHeight )
	maslowSettings['bedwidth'] = '{:.02f}'.format( cal.machineWidth )
	maslowSettings['motoroffsety'] = '{:.02f}'.format( cal.motorOffsetY )
	advancedSettings['rotationradius'] = '{:.02f}'.format( cal.rotationDiskRadius )
	advancedSettings['chainsagcorrection'] = '{:.02f}'.format( cal.chainSagCorrection )

	advancedSettings['chainoversprocket'] = 'Top' if cal.chainOverSprocket != 0 else 'Bottom'
	advancedSettings['kinematicstype'] = 'Triangular' if cal.isQuadKinematics == 0 else 'Quadrilateral'

class CalibrationMeasurements:
	'''	these measurements include the target and actual positions for a set of calibrations points '''
	
	def __init__( self, config ):
		'''	read measurements from config .ini file '''

		#	flatten config file
		settingsList = []
		for section in config.sections():
			settingsList += list( config[section].items() )
		settings = dict( settingsList )
		#print( 'Measurements = {!r}'.format( settings ) )
		
		#	get number of positions
		numPositions = int( settings['numpositions'] )
		
		#	get actual values from settings
		self.actualPositions = [ ( float( settings['x{}'.format(i)] ), float( settings['y{}'.format(i)] ) ) for i in range( numPositions ) ]

		#	get target values from settings
		self.targetPositions = [ ( float( settings['tx{}'.format(i)] ), float( settings['ty{}'.format(i)] ) ) for i in range( numPositions ) ]

	def getNumPositions( self  ):
		numPositions = len(self.actualPositions)
		assert( numPositions == len(self.targetPositions) )
		return numPositions

class CalibrationCostFunction:
	'''	this cost function contains the overall residual cost between actual and target positions to be minimized '''
	
	def	__init__( self, calibration, measurements, doCalibrateChainPitch = False ):
		'''	construct from previous calibration parameters and observed measurements 
			These should be of type Calibration and CalibrationMeasurements
		'''
		
		#	should we calibrate chain pitch?
		self.doCalibrateChainPitch = doCalibrateChainPitch

		self.calibration = calibration
		#self.measurements = measurements
		
		self.initializeMeasurements( measurements, calibration )
		
		#	remember the scalar for updating parameters
		self.updateParametersScalar = 1

	@staticmethod
	def computeChainLength( position, kinematics ):
		'''	return (leftChainLength,rightChainLength) from given target position for given kinematics object '''
		return kinematics.inverse( *position )
		
	@staticmethod 
	def computePosition( leftChainLength, rightChainLength, kinematics ):
		'''	return position from chain length '''
		return kinematics.forward( leftChainLength, rightChainLength )
	
	@staticmethod
	def convertMeasurementToBedPosition( position, calibration ):
		'''	given a point in measurement coords ( (0,0) is upper left, and right/down is positive )
			convert to kinematics coords ( (0,0) is center of bed, and right/up is positive )
		'''
		return ( position[0] - calibration.machineWidth/2.0, calibration.machineHeight/2.0 - position[1] )
	
	def getNumPositions( self ):
		'''	get number of calibration positions '''
		numPositions = len(self.actualPositions)
		assert numPositions == len(self.chainLengths)
		return numPositions
		
	def getNumResidualPairs( self ):
		'''	there is one residual pair (x,y) for each position '''
		return self.getNumPositions()
		
	#def getNumResidualRows( self ):
	#	'''	there are two residual rows for each (x,y) pair '''
	#	return 2*self.getNumResidualPairs()
	
	@staticmethod
	def constructKinematics( calibration ):
		'''	construct kinematics from calibration object '''
		return Kinematics( calibration )

	def initializeMeasurements( self, measurements, calibration ):
		'''	initialize measurements related member values '''
		
		#	remember the actual positions
		self.actualPositions = [ self.convertMeasurementToBedPosition( position, calibration ) 
										for position in measurements.actualPositions ]
		
		#	compute the target positions
		targetPositions = [ self.convertMeasurementToBedPosition( position, calibration ) 
										for position in measurements.targetPositions ]
										
		#	create kinematics to calculate chain lengths
		kinematics = Kinematics( calibration )
		
		#	calculate the chain lengths that were generated from the target positions
		#	These would have actually been sent to the machine as the target when the actual positions occurred
		self.chainLengths = [ self.computeChainLength( targetPosition, kinematics ) 
										for targetPosition in targetPositions ]
	
		#	make sure we have a chain length for each actual position
		if len(self.actualPositions) != len(self.chainLengths):
			raise ValueError( 'number of target positions and actual positions must match!' )

	def computeResidualPair( self, i, kinematics ):
		'''	compute the i'th (x,y) residual pair from given kinematics object
			NOTE that $i must be in [0,len(self.actualPositions)-1]
		'''
		
		#	calculate position from chainLengths[i]
		leftChainLength, rightChainLength = self.chainLengths[i]
		position = self.computePosition( leftChainLength, rightChainLength, kinematics )
		
		#	return square distance from position to actualPosition
		return tuple( vectorDifference( self.actualPositions[i], position ) )
		
	def computeVectorOfResiduals( self, kin ):
		'''	compute the vector of residuals '''

		#	get list of x,y residual pairs
		residualPairs = [ self.computeResidualPair( residualIndex, kin ) for residualIndex in range( self.getNumResidualPairs() ) ]

		#	return flattend list of residuals
		return flatten( residualPairs )

	def computeCost( self, calibration ):
		'''	given a new set of calibration parameters, compute the cost function roughly equating to 
			"how far off are the self.actualPositions from the positions computed from self.chainLengths?"
		'''

		##	cache the number of residual functions
		#numResidualPairs = self.getNumResidualPairs()

		#	create kinematics to calculate positions from chain lengths
		kinematics = Kinematics( calibration )
		
		#	compute residuals
		residuals = self.computeVectorOfResiduals( kinematics )
		sqrResiduals = [ x*x for x in residuals ]
		
		#	return sum of the residuals
		return sum( sqrResiduals )
		
	def getParametersFromCalibration( self, calibration ):
		'''	return initial solvable parameter set from initial calibration object
		'''
		cal = calibration
		parameters = [ cal.D, cal.motorOffsetY, 
						cal.rotationDiskRadius, 
						convertChainSagCorrectionToParameter( cal.chainSagCorrection ),
						cal.motorOffsetX, cal.rightMotorDeltaY ]
		if self.doCalibrateChainPitch:
			parameters.append( cal.R )
		return parameters
				
	def setCalibrationFromParameters( self, parameters, calibration ):
		'''	set the values in calibration from parameters
			NOTE that the number of parameters must be the same as returned by
				getParametersFromCalibration()
		'''
		cal = calibration
		i = 0
		cal.D = parameters[i]
		i += 1
		cal.motorOffsetY = parameters[i]
		i += 1
		cal.rotationDiskRadius = parameters[i]
		i += 1
		cal.chainSagCorrection = convertParameterToChainSagCorrection( parameters[i] )
		i += 1
		cal.motorOffsetX = parameters[i]
		i += 1
		cal.rightMotorDeltaY = parameters[i]
		i += 1
		if self.doCalibrateChainPitch:
			cal.R = parameters[i]
			i += 1

		assert( i == len(parameters) )

	# ##################################
	# # warning REMOVE_ THE FOLLOWING TWO FUNCTIONS

	# @staticmethod
	# def getParametersFromCalibration( calibration ):
	# 	'''	return initial solvable parameter set from initial calibration object
	# 	'''
	# 	cal = calibration
	# 	parameters = [ cal.motorOffsetY ]
	# 	return parameters
				
	# @staticmethod
	# def setCalibrationFromParameters( parameters, calibration ):
	# 	'''	set the values in calibration from parameters
	# 		NOTE that the number of parameters must be the same as returned by
	# 			getParametersFromCalibration()
	# 	'''
	# 	cal = calibration
	# 	i = 0
	# 	cal.motorOffsetY = parameters[i]
	
	# # up to here
	# ##################################
	
	def computeJacobianOfResiduals( self, parameters ):
		'''	given a set of solvable parameters, compute the Jacobian matrix of the residuals '''
		
		#	cache the number of residual functions
		numResidualPairs = self.getNumResidualPairs()
		
#		#	set calibration from parameters
#		self.setCalibrationFromParameters( parameters, self.calibration )
		
		#	loop over each parameter and calculate a column of the jacobian
		jacobianColumns = []
		for parameterIndex in range(len(parameters)):
		#	calculate the partial of each residual with respect to this parameter
			#	make a copy of parameters
			parametersCopy = parameters[:]
			
			#	offset this parameter to the left by epsilon, construct kinematics, and compute left values for all residuals
			parametersCopy[parameterIndex] = parameters[parameterIndex]-PartialEpsilon
			self.setCalibrationFromParameters( parametersCopy, self.calibration )
			kinematics = Kinematics( self.calibration )
			#leftValueVector = flatten( [ self.computeResidualPair( residualIndex, kin ) for residualIndex in range( numResidualPairs ) ] )
			leftValueVector = self.computeVectorOfResiduals( kinematics )
		
			#	offset this parameter to the right by epsilon, construct kinematics, and compute right values for all residuals
			parametersCopy[parameterIndex] = parameters[parameterIndex]+PartialEpsilon
			self.setCalibrationFromParameters( parametersCopy, self.calibration )
			kinematics = Kinematics( self.calibration )
			#rightValueVector = flatten( [ self.computeResidualPair( residualIndex, kin ) for residualIndex in range( numResidualPairs ) ] )
			rightValueVector = self.computeVectorOfResiduals( kinematics )
			
			#	compute slope between left and right values to get jacobian column vector
			column = [ (rightValue-leftValue)/(2*PartialEpsilon) for leftValue,rightValue in zip( leftValueVector, rightValueVector ) ]
			
			#	append to jacobian columns
			jacobianColumns.append( column )
			
		#	construct jacobian
		jacobian = numpy.array( jacobianColumns ).T
		
		#	return 
		return jacobian

	def updateParametersUsingGaussNewton( self, parameters ):
		'''	given a set of parameters, return ( newParameters, oldCost ) by doing a single
				Gauss-Newton iteration
		'''
		
		#	cache the number of residual functions
		numResidualPairs = self.getNumResidualPairs()

		#	compute the vector of residuals 
		self.setCalibrationFromParameters( parameters, self.calibration )
		kinematics = Kinematics( self.calibration )
		#residuals = flatten( [ self.computeResidualPair( i, kin ) for i in range( numResidualPairs ) ] )
		residuals = self.computeVectorOfResiduals( kinematics )

#		#	log residuals
#		logging.getLogger( name='main' ).debug( '    residuals = {!r}'.format( residuals ) )

		#	calculate the Jacobian of the residuals
		jacobian = self.computeJacobianOfResiduals( parameters )
		
		#	calculate Moore-Penrose pseudoinverse of the jacobian
		jacobianInv = numpy.linalg.pinv( jacobian )
		
		#	calculate new parameters using Gauss-Newton step:
		#		newParms = oldParms + jacobianInv @ residuals
#warning WHY  DOES THIS ONLY WORK WITH A MINUS NOT A PLUS?
		newParameters = parameters - self.updateParametersScalar * jacobianInv @ residuals
		
		#	compute old cost function
		oldCost = sum( [ residual**2 for residual in residuals ] )
		
		#	return
		return newParameters, oldCost

