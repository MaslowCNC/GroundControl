#!/usr/bin/env python3

import sys

import argparse
import configparser
import logging

import math

import calibration_helpers

##################################
#	globals

#	logger
root = logging.getLogger()
root.setLevel( logging.DEBUG )
logHandler = logging.StreamHandler(sys.stdout)
logHandler.setFormatter( logging.Formatter( '{levelname}:{name}:{message}', style='{' ) )
logHandler.setLevel( logging.DEBUG )
root.addHandler( logHandler )
logger = logging.getLogger( name='main' )

#	stopping criteria
StopAtNegLogConvergence = 10
StopAtCost = 1e-4

#	should we do chain pitch calibration?
DoCalibrateChainPitch = False

#	setup parser
parser = argparse.ArgumentParser( description='Read Maslow CNC calibration parameters and actual measured cuts and write new parameters' )
parser.add_argument( 'inputConfigFileName', metavar='INPUT_CONFIG_INI', type=str, nargs='+',
                    help='input config file in .ini format' )
parser.add_argument( 'inputMeasurementsFileName', metavar='INPUT_MEASUREMENT_FILE', type=str, nargs='+',
                    help='input measurements file in .ini format (see example file)' )
parser.add_argument( 'outputConfigFileName', metavar='OUTPUT_CONFIG_INI', type=str, nargs='+',
                    help='output config file in .ini format' )
#parser.add_argument('--sum', dest='accumulate', action='store_const',
#                    const=sum, default=max,
#                    help='sum the integers (default: find the max)')

args = parser.parse_args()

#	parse args
inputConfigFileName, = args.inputConfigFileName
outputConfigFileName, = args.outputConfigFileName
inputMeasurementsFileName, = args.inputMeasurementsFileName

#	read the input config file
config = configparser.ConfigParser()
config.read( inputConfigFileName )
logging.info( 'inputConfig[{!r}] read with sections = {!r}'.format( inputConfigFileName, config.sections() ) )

#	get config sections
maslowSettings = config['Maslow Settings']
advancedSettings = config['Advanced Settings']
settings = dict( list( maslowSettings.items() ) + list( advancedSettings.items() ) )
logger.debug( 'settings = {!r}'.format( settings ) )

#	construct the kinematics calibration object from input settings
calibration = calibration_helpers.constructKinematicsCalibrationObject( settings )

#	print initial calibration values
print( 'Initial D = {:.03f}'.format( calibration.D ) )
print( 'Initial R = {:.03f}'.format( calibration.R ) )
print( 'Initial motorOffsetY = {:.03f}'.format( calibration.motorOffsetY ) )
print( 'Initial rotationDiskRadius = {:.03f}'.format( calibration.rotationDiskRadius ) )
print( 'Initial chainSagCorrection = {:.03f}'.format( calibration.chainSagCorrection ) )
print( 'Initial motorOffsetX = {:.03f}'.format( calibration.motorOffsetX ) )
print( 'Initial rightMotorDeltaY = {:.03f}'.format( calibration.rightMotorDeltaY ) )
print( '\n\n\n' )

#	read the measurements .ini file
measurementsConfig = configparser.ConfigParser()
measurementsConfig.read( inputMeasurementsFileName )
measurements = calibration_helpers.CalibrationMeasurements( measurementsConfig )

#	construct calibration cost function
costFunction = calibration_helpers.CalibrationCostFunction( calibration, measurements,
													doCalibrateChainPitch = DoCalibrateChainPitch )

#	get initial parameters
parameters = costFunction.getParametersFromCalibration( calibration )
cost = None

#	log initial cost
logger.info( 'Initial cost = {!r}'.format( costFunction.computeCost( calibration ) ) )
logger.debug( 'Initial parameters = {!r}\n'.format( parameters ) )

#	log initial residuals
kinematics = costFunction.constructKinematics( calibration )
logger.debug( 'Initial residuals = {!r}\n'.format( [ costFunction.computeResidualPair( i, kinematics ) for i in range( costFunction.getNumResidualPairs() ) ] ) )

#	loop until convergence
def computeConvergence( newError, oldError ):
	return abs( oldError - newError ) / ( abs(oldError) + abs(newError) )
def computeNegLogConvergence( newError, oldError ):
	convergence = computeConvergence( newError, oldError )
	if convergence < 1e-100:
		return 100
	else:
		return -math.log10( convergence )
		
iterationCount = 0
while True:
	#	take the step
	newParameters, oldCost = costFunction.updateParametersUsingGaussNewton( parameters )
	
	#	log
	logger.debug( 'Iter[{}] cost = {!r}'.format( iterationCount, oldCost ) )
	logger.debug( '    parameters = {!r}\n'.format( list(parameters) ) )

	#	compute convergence
	if cost != None:
		negLogConvergence = computeNegLogConvergence( oldCost, cost )
		logger.debug( '  convergence = {:.04f}'.format( negLogConvergence ) )
		if negLogConvergence >= StopAtNegLogConvergence or oldCost <= StopAtCost:
			break

		#	check if cost went up
		if oldCost > cost:
			#	update parameters in a smaller step size
			costFunction.updateParametersScalar /= 2
			logger.debug( '    updateParametersScalar is down to {!r}'.format( costFunction.updateParametersScalar ) )
		else:
			#	increase stepsize just a little bit
			costFunction.updateParametersScalar = min( 1, costFunction.updateParametersScalar * 2**.1 )
			logger.debug( '    updateParametersScalar is up to {!r}'.format( costFunction.updateParametersScalar ) )

	#	update cost and parameters
	parameters = newParameters
	cost = oldCost

	print( 'Iteration count = {!r}'.format( iterationCount ) )

	#	increment iteration count
	iterationCount += 1

#	update calibration object from final parameters
costFunction.setCalibrationFromParameters( parameters, calibration )

#	print out the final calibration
print( 'Final D = {:.03f}'.format( calibration.D ) )
print( 'Final R = {:.03f}'.format( calibration.R ) )
print( 'Final motorOffsetY = {:.03f}'.format( calibration.motorOffsetY ) )
print( 'Final rotationDiskRadius = {:.03f}'.format( calibration.rotationDiskRadius ) )
print( 'Final chainSagCorrection = {:.03f}'.format( calibration.chainSagCorrection ) )
print( 'Final motorOffsetX = {:.03f}'.format( calibration.motorOffsetX ) )
print( 'Final rightMotorDeltaY = {:.03f}'.format( calibration.rightMotorDeltaY ) )

#	log final residuals
kinematics = costFunction.constructKinematics( calibration )
logger.debug( 'Final residuals = {!r}\n'.format( [ costFunction.computeResidualPair( i, kinematics ) for i in range( costFunction.getNumResidualPairs() ) ] ) )

#	transfer new values from calibration object to settings
calibration_helpers.updateSettingsFromKinematicsCalibrationObject( calibration, maslowSettings, advancedSettings )

#	write to output .ini file
with open( outputConfigFileName, 'w' ) as configFile:
  config.write( configFile )