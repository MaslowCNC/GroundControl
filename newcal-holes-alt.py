import math
import random

def CalculateMaximumError(error):
	if (math.fabs(error) < 0.3):
		errorReturn = 0.3*0.3
	else:
		errorReturn = error*error
	return errorReturn


def CalculateChainLengths(leftMotorX, leftMotorY, rightMotorX, rightMotorY, targetX, targetY, chainOverSprocket, rotationRadius, chainSagCorrection, leftChainTolerance, rightChainTolerance, oldSag, dX, dY):
	# dX = AH1x-H1x, dY = AH1y-H1y
	leftMotorDistanceTarget = math.sqrt(math.pow(leftMotorX - targetX,2) + math.pow(leftMotorY - targetY ,2))
	rightMotorDistanceTarget = math.sqrt(math.pow(rightMotorX - targetX,2) + math.pow(rightMotorY - targetY ,2))
	#Calculate the chain angles from horizontal, based on if the chain connects to the sled from the top or bottom of the sprocket
	if chainOverSprocket == 1:
		leftChainAngleTarget = (math.asin((leftMotorY - targetY) / leftMotorDistanceTarget) + math.asin(sprocketRadius/leftMotorDistanceTarget))
		rightChainAngleTarget = (math.asin((rightMotorY - targetY) / rightMotorDistanceTarget) + math.asin(sprocketRadius/rightMotorDistanceTarget))

		leftChainAroundSprocketTarget = sprocketRadius * leftChainAngleTarget
		rightChainAroundSprocketTarget = sprocketRadius * rightChainAngleTarget

	else:
		leftChainAngleTarget = (math.asin((leftMotorY - targetY) / leftMotorDistanceTarget) - math.asin(sprocketRadius/leftMotorDistanceTarget))
		rightChainAngleTarget = (math.asin((rightMotorY - targetY) / rightMotorDistanceTarget) - math.asin(sprocketRadius/rightMotorDistanceTarget))

		leftChainAroundSprocketTarget = sprocketRadius * (3.14159 - leftChainAngleTarget)
		rightChainAroundSprocketTarget = sprocketRadius * (3.14159 - rightChainAngleTarget)

	#Calculate the straight chain length from the sprocket to the bit
	leftChainStraightTarget = math.sqrt(math.pow(leftMotorDistanceTarget,2) - math.pow(sprocketRadius,2))
	rightChainStraightTarget = math.sqrt(math.pow(rightMotorDistanceTarget,2) - math.pow(sprocketRadius,2))

	#Correct the straight chain lengths to account for chain sag
	if (oldSag == False):
		leftChainSag = (1 + ((chainSagCorrection / 1000000000000) * math.pow(math.cos(leftChainAngleTarget),2) * math.pow(leftChainStraightTarget,2) * math.pow((math.tan(rightChainAngleTarget) * math.cos(leftChainAngleTarget)) + math.sin(leftChainAngleTarget),2)))
		rightChainSag = (1 + ((chainSagCorrection / 1000000000000) * math.pow(math.cos(rightChainAngleTarget),2) * math.pow(rightChainStraightTarget,2) * math.pow((math.tan(leftChainAngleTarget) * math.cos(rightChainAngleTarget)) + math.sin(rightChainAngleTarget),2)))
	else:
		leftForceMultiplier = 1.0 / ((targetX-leftMotorX)/(leftMotorY-targetY)+(rightMotorX-targetX)/(rightMotorY-targetY))*math.sqrt(math.pow(((rightMotorX-targetX)/(rightMotorY-targetY)),2)*math.pow(((targetX-leftMotorX)/(leftMotorY-targetY)),2)+math.pow(((rightMotorX-targetX)/(rightMotorY-targetY)),2))
		rightForceMultiplier = 1.0 / ((targetX-leftMotorX)/(leftMotorY-targetY)+(rightMotorX-targetX)/(rightMotorY-targetY))*math.sqrt(math.pow(((rightMotorX-targetX)/(rightMotorY-targetY)),2)*math.pow(((targetX-leftMotorX)/(leftMotorY-targetY)),2)+math.pow(((targetX-leftMotorX)/(leftMotorY-targetY)),2))
		leftChainSag = 1.0 + leftChainStraightTarget/(chainSagCorrection*100000.0 * math.cos(leftChainAngleTarget)*leftForceMultiplier)
		rightChainSag = 1.0 + rightChainStraightTarget/(chainSagCorrection*100000.0 * math.cos(rightChainAngleTarget)*rightForceMultiplier)

	#Calculate total chain lengths accounting for sprocket geometry and chain sag
	LChainLengthTarget = (leftChainAroundSprocketTarget + leftChainStraightTarget*leftChainSag*leftChainTolerance)-rotationRadius
	RChainLengthTarget = (rightChainAroundSprocketTarget + rightChainStraightTarget*rightChainSag*rightChainTolerance)-rotationRadius



	return LChainLengthTarget, RChainLengthTarget

def CalculateCoordinates(dH0H1, dH0H2, dH0H3, dH0H4, dH1H2, dH1H4, dH2H3, dH3H4, dH0M5, dH2M5 ):
	#Calculate x,y coordinates for each hole
	H0x = 0
	H0y = 0
	M5x = 0
	M5y = dH0M5
	H2y = (dH0M5*dH0M5+dH0H2*dH0H2-dH2M5*dH2M5)/(2*dH0M5)*-1.0
	H2x = math.sqrt( (dH0M5+dH0H2+dH2M5) * (dH0M5+dH0H2-dH2M5) * (dH0M5-dH0H2+dH2M5) * (-dH0M5+dH0H2+dH2M5) )/(2*dH0M5)*-1.0
	#print "H2x:"+str(H2x)+", H2y:"+str(H2y)

	H3y = (dH0M5*dH0M5+dH0H3*dH0H3-(dH2H3-dH2M5)*(dH2H3-dH2M5))/(2*dH0M5)*-1.0
	H3x = math.sqrt( (dH0M5+dH0H3+(dH2H3-dH2M5)) * (dH0M5+dH0H3-(dH2H3-dH2M5)) * (dH0M5-dH0H3+(dH2H3-dH2M5)) * (-dH0M5+dH0H3+(dH2H3-dH2M5)) )/(2*dH0M5)
	#print "H3x:"+str(H3x)+", H3y:"+str(H3y)

	theta = math.atan2(H3y,H3x*-1.0)
	#print "Theta:"+str(theta)
	rH4x = (dH0H3*dH0H3-dH3H4*dH3H4+dH0H4*dH0H4)/(2*dH0H3)
	rH4y = math.sqrt( (dH0H3+dH3H4+dH0H4) * (dH0H3+dH3H4-dH0H4) *(dH0H3-dH3H4+dH0H4) * (-dH0H3+dH3H4+dH0H4) )/(2*dH0H3)
	#print "rH4x:"+str(rH4x)+", rH4y:"+str(rH4y)

	H4x = ((rH4x*math.cos(-theta))-(rH4y*math.sin(-theta)))*-1.0
	H4y = ((rH4x*math.sin(-theta))+(rH4y*math.cos(-theta)))*-1.0
	#print "H4x:"+str(H4x)+", H4y:"+str(H4y)
	# Calculate the actual chain lengths for each cut location

	theta = math.atan2(H2y,H2x)
	#print "Theta:"+str(theta)
	rH1x = (dH0H2*dH0H2-dH1H2*dH1H2+dH0H1*dH0H1)/(2*dH0H2)
	rH1y = math.sqrt( (dH0H2+dH1H2+dH0H1) * (dH0H2+dH1H2-dH0H1) *(dH0H2-dH1H2+dH0H1) * (-dH0H2+dH1H2+dH0H1) )/(2*dH0H2)
	#print "rH1x:"+str(rH1x)+", rH1y:"+str(rH1y)

	H1x = ((rH1x*math.cos(-theta))-(rH1y*math.sin(-theta)))
	H1y = ((rH1x*math.sin(-theta))+(rH1y*math.cos(-theta)))*-1.0
	return H0x, H0y, H1x, H1y, H2x, H2y, H3x, H3y, H4x, H4y

# adjust based upon machine settings
workspaceHeight = 1219.2
workspaceWidth = 2438.4
gearTeeth = 10
chainPitch = 6.35
holePattern = 3 # 0 = wide holes, 1 = 12-foot holes
# adjust in the event the hole pattern is changed
if (holePattern == 0):
	aH1x = (workspaceWidth/2.0-254.0)*-1.0
	aH1y = (workspaceHeight/2.0-254.0)
	aH2x = aH1x
	aH2y = aH1y*-1.0
	aH3x = aH1x*-1.0
	aH3y = aH2y
	aH4x = aH3x
	aH4y = aH1y
if (holePattern == 1):
	aH1x = -304.8
	aH1y = 304.8
	aH2x = aH1x
	aH2y = aH1y*-1.0
	aH3x = aH1x*-1.0
	aH3y = aH2y
	aH4x = aH3x
	aH4y = aH1y
if (holePattern == 3):
	aH1x = (workspaceWidth/2.0-254.0)*-1.0
	aH1y = (workspaceHeight/2.0-254.0)
	aH2x = aH1x
	aH2y = aH1y*-1.0
	aH3x = aH1x*-1.0
	aH3y = aH2y
	aH4x = aH3x
	aH4y = aH1y
	aH5x = -304.8
	aH5y = 304.8
	aH6x = aH5x
	aH6y = aH5y*-1.0
	aH7x = aH5x*-1.0
	aH7y = aH6y
	aH8x = aH7x
	aH8y = aH5y

#measured distances of hole pattern
##---CHANGE THESE TO WHAT YOU MEASURED---##
##---USE MILLIMETERS ONLY---##
##---My tape measure was off by 101 mm so the -101.0 adjust for it---##
##---CHANGE IT BECAUSE YOURS IS LIKELY DIFFERENT---###
dH0H1 = 1069.0-40.0
dH0H2 = 1069.0-40.0
dH0H3 = 1070.0-40.0
dH0H4 = 1069.0-40.0
dH1H2 = 753.0-40.0
dH1H4 = 1971.0-40.0
dH2H3 = 1971.0-40.0
dH3H4 = 751.5-40.0
dH0M5 = 590.0-40.0
dH2M5 = 1004.75-40.0 #1013.0-40.0

dH0H5 = 471.0-40.0
dH0H6 = 471.0-40.0
dH0H7 = 470.0-40.0
dH0H8 = 470.0-40.0
dH5H6 = 649.0-40.0
dH5H8 = 650.0-40.0
dH6H7 = 650.0-40.0
dH7H8 = 647.0-40.0
dH0M9 = 590.0-40.0 #350.0-40.0
dH6M9 = 342.75-40.0

if (holePattern==1):
	dH0H1 = dH0H5
	dH0H2 = dH0H6
	dH0H3 = dH0H7
	dH0H4 = dH0H8
	dH1H2 = dH5H6
	dH1H4 = dH5H8
	dH2H3 = dH6H7
	dH3H4 = dH7H8
	dH0M5 = dH0M9
	dH2M5 = dH6M9

#optimization parameters.. this really does affect how well you can arrive at a solution and how good of a solution it is
acceptableTolerance = .05
numberOfIterations = 100000000  # reduced number of iterations
motorYcoordCorrectionScale = 0.01
motorXcoordCorrectionScale = 0.05
chainSagCorrectionCorrectionScale = 0.01
motorSpacingCorrectionScale = 0.001
rotationRadiusCorrectionScale = 0.01
chainCompensationCorrectionScale = 0.01

#optional adjustments
adjustMotorYcoord = True  # this allows raising lowering of top beam
adjustMotorTilt = True  # this allows tilting of top beam
adjustMotorXcoord = False  # this allows shifting of top beam
adjustMotorSpacingInterval = 100 #0 means never, 1 means always, 100 means every 100 times there's no improvement
adjustRotationalRadiusInterval = 100 #0 means never, 1 means always, 100 means every 100 times there's no improvement
adjustChainCompensationInterval = 10 #0 means never, 1 means always, 100 means every 100 times there's no improvement
adjustChainSag = True

#parameters used during calibration cut.. currently assumes motors are level and 0,0 is centered
##---CHANGE THESE TO MATCH YOUR MACHINE WHEN YOU RAN THE HOLE PATTERN---##
motorSpacing = 3602.98
desiredMotorSpacing = motorSpacing #this allows you to change from motor spacing you cut with and make it a fixed value
motorYoffset = 475.57
motorTilt = -0.3583
rotationRadius = 137.8601
chainSagCorrection = 31.039523
chainOverSprocket = 1
leftChainTolerance = 1.0-(0.09636/100.0) # can't use current values .. value must be less than or equal to 1
rightChainTolerance =1.0-(0.25666/100.0) # can't use current values .. value must be less than or equal to 1
desiredRotationalRadius = 140.0 #rotationRadius #this allows you to change from rotation radius you cut with and make it a fixed value

# Gather current machine parameters
sprocketRadius = (gearTeeth*chainPitch / 2.0 / 3.14159) # + chainPitch/math.sin(3.14159 / gearTeeth)/2.0)/2.0 # new way to calculate.. needs validation
leftMotorX = math.cos(motorTilt*3.141592/180.0)*motorSpacing/-2.0
leftMotorY = math.sin(motorTilt*3.141592/180.0)*motorSpacing/-2.0 + motorYoffset+workspaceHeight/2.0
rightMotorX = math.cos(motorTilt*3.141592/180.0)*motorSpacing+leftMotorX
rightMotorY = math.sin(motorTilt*3.141592/180.0)*motorSpacing/2.0 + motorYoffset +workspaceHeight/2.0

leftMotorXEst = -1801.39470025#desiredMotorSpacing/-2.0#leftMotorX-(desiredMotorSpacing-motorSpacing)/2.0 #adjusts motor x based upon change in motor spacing
leftMotorYEst = 1099.1285#leftMotorY+(rightMotorY-leftMotorY)/2.0
rightMotorXEst = 1801.49051#desiredMotorSpacing/2.0#rightMotorX+(desiredMotorSpacing-motorSpacing)/2.0
rightMotorYEst = 1075.7175#rightMotorY-(rightMotorY-leftMotorY)/2.0#rightMotorY
leftChainToleranceEst = 1.0#leftChainTolerance
rightChainToleranceEst = 1-0.1747015/100.0#1.0#rightChainTolerance
rotationRadiusEst = 140.041#desiredRotationalRadius  # Not affected by chain compensation
chainSagCorrectionEst= 28.140215#chainSagCorrection

iterativeSolvedH0M5= True

#calculate coordinates of the holes based upon distance measurements
if (iterativeSolvedH0M5):
	errorMagnitude = 999999
	errorImprovementInterval = 0.0
	previousErrorMagnitude = 0.0
	while (math.fabs(errorMagnitude) > 0.1):
		dH0M5 += errorImprovementInterval
		H0x, H0y, H1x, H1y, H2x, H2y, H3x, H3y, H4x, H4y = CalculateCoordinates(dH0H1, dH0H2, dH0H3, dH0H4, dH1H2, dH1H4, dH2H3, dH3H4, dH0M5, dH2M5)
		errorMagnitude = dH1H4 - math.sqrt( math.pow(H1x-H4x,2)+math.pow(H1y-H4y,2))
		#print str(previousErrorMagnitude)+", "+str(errorMagnitude)+", "+str(dH0M5)
		#x=raw_input()
		if (errorImprovementInterval!=0 and math.fabs(previousErrorMagnitude) < math.fabs(errorMagnitude)):
			break;
		previousErrorMagnitude = errorMagnitude
		errorImprovementInterval = errorMagnitude*0.01
	print str(dH0M5)
	if (holePattern == 3):
		print ("Inner Holes:")
		errorMagnitude = 999999
		previousErrorMagnitude = 0.0
		errorImprovementInterval = 0.0
		while (math.fabs(errorMagnitude) > 0.1):
			dH0M9 += errorImprovementInterval
			H0x, H0y, H5x, H5y, H6x, H6y, H7x, H7y, H8x, H8y = CalculateCoordinates(dH0H5, dH0H6, dH0H7, dH0H8, dH5H6, dH5H8, dH6H7, dH7H8, dH0M9, dH6M9)
			errorMagnitude = dH5H8 - math.sqrt( math.pow(H5x-H8x,2)+math.pow(H5y-H8y,2))
			#print str(previousErrorMagnitude)+", "+str(errorMagnitude)+", "+str(dH0M5)
			#x=raw_input()
			if (errorImprovementInterval!=0 and math.fabs(previousErrorMagnitude) < math.fabs(errorMagnitude)):
				break;
			previousErrorMagnitude = errorMagnitude
			errorImprovementInterval = errorMagnitude*0.01
else:
	H0x, H0y, H1x, H1y, H2x, H2y, H3x, H3y, H4x, H4y = CalculateCoordinates(dH0H1, dH0H2, dH0H3, dH0H4, dH1H2, dH1H4, dH2H3, dH3H4, dH0M5, dH2M5)
	if (holePattern == 3):
		H0x, H0y, H5x, H5y, H6x, H6y, H7x, H7y, H8x, H8y = CalculateCoordinates(dH0H5, dH0H6, dH0H7, dH0H8, dH5H6, dH5H8, dH6H7, dH7H8, dH0M9, dH6M9)

print "Desired:"
print "aH1x:"+str(aH1x)+", aH1y:"+str(aH1y)
print "aH2x:"+str(aH2x)+", aH2y:"+str(aH2y)
print "aH3x:"+str(aH3x)+", aH3y:"+str(aH3y)
print "aH4x:"+str(aH4x)+", aH4y:"+str(aH4y)
if (holePattern == 3):
	print "aH5x:"+str(aH5x)+", aH5y:"+str(aH5y)
	print "aH6x:"+str(aH6x)+", aH6y:"+str(aH6y)
	print "aH7x:"+str(aH7x)+", aH7y:"+str(aH7y)
	print "aH8x:"+str(aH8x)+", aH8y:"+str(aH8y)
print "Actual:"
print "H1x:"+str(H1x)+", H1y:"+str(H1y)
print "H2x:"+str(H2x)+", H2y:"+str(H2y)
print "H3x:"+str(H3x)+", H3y:"+str(H3y)
print "H4x:"+str(H4x)+", H4y:"+str(H4y)
if (holePattern == 3):
	print "H5x:"+str(H5x)+", H5y:"+str(H5y)
	print "H6x:"+str(H6x)+", H6y:"+str(H6y)
	print "H7x:"+str(H7x)+", H7y:"+str(H7y)
	print "H8x:"+str(H8x)+", H8y:"+str(H8y)
print "Delta:"
print "H1x:"+str(aH1x-H1x)+", H1y:"+str(aH1y-H1y)
print "H2x:"+str(aH2x-H2x)+", H2y:"+str(aH2y-H2y)
print "H3x:"+str(aH3x-H3x)+", H3y:"+str(aH3y-H3y)
print "H4x:"+str(aH4x-H4x)+", H4y:"+str(aH4y-H4y)
if (holePattern == 3):
	print "H5x:"+str(aH5x-H5x)+", H5y:"+str(aH5y-H5y)
	print "H6x:"+str(aH6x-H6x)+", H6y:"+str(aH6y-H6y)
	print "H7x:"+str(aH7x-H7x)+", H7y:"+str(aH7y-H7y)
	print "H8x:"+str(aH8x-H8x)+", H8y:"+str(aH8y-H8y)

x=raw_input("") #pause for review

# Calculate the chain lengths for each hole location based upon inputted model

LChainLengthHole1, RChainLengthHole1 = CalculateChainLengths(leftMotorX, leftMotorY, rightMotorX, rightMotorY, aH1x, aH1y, chainOverSprocket, rotationRadius, chainSagCorrection, leftChainTolerance, rightChainTolerance, False, aH1x-H1x, aH1y-H1y)
LChainLengthHole2, RChainLengthHole2 = CalculateChainLengths(leftMotorX, leftMotorY, rightMotorX, rightMotorY, aH2x, aH2y, chainOverSprocket, rotationRadius, chainSagCorrection, leftChainTolerance, rightChainTolerance, False, aH1x-H1x, aH1y-H1y)
LChainLengthHole3, RChainLengthHole3 = CalculateChainLengths(leftMotorX, leftMotorY, rightMotorX, rightMotorY, aH3x, aH3y, chainOverSprocket, rotationRadius, chainSagCorrection, leftChainTolerance, rightChainTolerance, False, aH1x-H1x, aH1y-H1y)
LChainLengthHole4, RChainLengthHole4 = CalculateChainLengths(leftMotorX, leftMotorY, rightMotorX, rightMotorY, aH4x, aH4y, chainOverSprocket, rotationRadius, chainSagCorrection, leftChainTolerance, rightChainTolerance, False, aH1x-H1x, aH1y-H1y)
if (holePattern == 3):
	LChainLengthHole5, RChainLengthHole5 = CalculateChainLengths(leftMotorX, leftMotorY, rightMotorX, rightMotorY, aH5x, aH5y, chainOverSprocket, rotationRadius, chainSagCorrection, leftChainTolerance, rightChainTolerance, False, aH1x-H1x, aH1y-H1y)
	LChainLengthHole6, RChainLengthHole6 = CalculateChainLengths(leftMotorX, leftMotorY, rightMotorX, rightMotorY, aH6x, aH6y, chainOverSprocket, rotationRadius, chainSagCorrection, leftChainTolerance, rightChainTolerance, False, aH1x-H1x, aH1y-H1y)
	LChainLengthHole7, RChainLengthHole7 = CalculateChainLengths(leftMotorX, leftMotorY, rightMotorX, rightMotorY, aH7x, aH7y, chainOverSprocket, rotationRadius, chainSagCorrection, leftChainTolerance, rightChainTolerance, False, aH1x-H1x, aH1y-H1y)
	LChainLengthHole8, RChainLengthHole8 = CalculateChainLengths(leftMotorX, leftMotorY, rightMotorX, rightMotorY, aH8x, aH8y, chainOverSprocket, rotationRadius, chainSagCorrection, leftChainTolerance, rightChainTolerance, False, aH1x-H1x, aH1y-H1y)

eLChainLengthHole1, eRChainLengthHole1 = CalculateChainLengths(leftMotorX, leftMotorY, rightMotorX, rightMotorY, H1x, H1y, chainOverSprocket, rotationRadius, chainSagCorrection, leftChainTolerance, rightChainTolerance, False, aH1x-H1x, aH1y-H1y)
eLChainLengthHole2, eRChainLengthHole2 = CalculateChainLengths(leftMotorX, leftMotorY, rightMotorX, rightMotorY, H2x, H2y, chainOverSprocket, rotationRadius, chainSagCorrection, leftChainTolerance, rightChainTolerance, False, aH1x-H1x, aH1y-H1y)
eLChainLengthHole3, eRChainLengthHole3 = CalculateChainLengths(leftMotorX, leftMotorY, rightMotorX, rightMotorY, H3x, H3y, chainOverSprocket, rotationRadius, chainSagCorrection, leftChainTolerance, rightChainTolerance, False, aH1x-H1x, aH1y-H1y)
eLChainLengthHole4, eRChainLengthHole4 = CalculateChainLengths(leftMotorX, leftMotorY, rightMotorX, rightMotorY, H4x, H4y, chainOverSprocket, rotationRadius, chainSagCorrection, leftChainTolerance, rightChainTolerance, False, aH1x-H1x, aH1y-H1y)
if (holePattern == 3):
	eLChainLengthHole5, eRChainLengthHole5 = CalculateChainLengths(leftMotorX, leftMotorY, rightMotorX, rightMotorY, H5x, H5y, chainOverSprocket, rotationRadius, chainSagCorrection, leftChainTolerance, rightChainTolerance, False, aH1x-H1x, aH1y-H1y)
	eLChainLengthHole6, eRChainLengthHole6 = CalculateChainLengths(leftMotorX, leftMotorY, rightMotorX, rightMotorY, H6x, H6y, chainOverSprocket, rotationRadius, chainSagCorrection, leftChainTolerance, rightChainTolerance, False, aH1x-H1x, aH1y-H1y)
	eLChainLengthHole7, eRChainLengthHole7 = CalculateChainLengths(leftMotorX, leftMotorY, rightMotorX, rightMotorY, H7x, H7y, chainOverSprocket, rotationRadius, chainSagCorrection, leftChainTolerance, rightChainTolerance, False, aH1x-H1x, aH1y-H1y)
	eLChainLengthHole8, eRChainLengthHole8 = CalculateChainLengths(leftMotorX, leftMotorY, rightMotorX, rightMotorY, H8x, H8y, chainOverSprocket, rotationRadius, chainSagCorrection, leftChainTolerance, rightChainTolerance, False, aH1x-H1x, aH1y-H1y)

errorLH1 = LChainLengthHole1-eLChainLengthHole1;
errorLH2 = LChainLengthHole2-eLChainLengthHole2;
errorLH3 = LChainLengthHole3-eLChainLengthHole3;
errorLH4 = LChainLengthHole4-eLChainLengthHole4;
errorRH1 = RChainLengthHole1-eRChainLengthHole1;
errorRH2 = RChainLengthHole2-eRChainLengthHole2;
errorRH3 = RChainLengthHole3-eRChainLengthHole3;
errorRH4 = RChainLengthHole4-eRChainLengthHole4;
if (holePattern == 3):
	errorLH5 = LChainLengthHole5-eLChainLengthHole5;
	errorLH6 = LChainLengthHole6-eLChainLengthHole6;
	errorLH7 = LChainLengthHole7-eLChainLengthHole7;
	errorLH8 = LChainLengthHole8-eLChainLengthHole8;
	errorRH5 = RChainLengthHole5-eRChainLengthHole5;
	errorRH6 = RChainLengthHole6-eRChainLengthHole6;
	errorRH7 = RChainLengthHole7-eRChainLengthHole7;
	errorRH8 = RChainLengthHole8-eRChainLengthHole8;

#print "errorLH1:"+str(errorLH1)

print "Machine parameters:"
print "Rotation Disk Radius: " + str(rotationRadius) + ", Chain Sag Correction Value: " + str(chainSagCorrection)
print "leftMotorX: "+str(leftMotorX) + ", leftMotorY: "+str(leftMotorY)+", rightMotorX: "+str(rightMotorX)+", rightMotorY:"+str(rightMotorY)
print "LHole1: "+str(LChainLengthHole1)+", RHole1: "+str(RChainLengthHole1)
print "LHole2: "+str(LChainLengthHole2)+", RHole2: "+str(RChainLengthHole2)
print "LHole3: "+str(LChainLengthHole3)+", RHole3: "+str(RChainLengthHole3)
print "LHole4: "+str(LChainLengthHole4)+", RHole4: "+str(RChainLengthHole4)
if (holePattern == 3):
	print "LHole5: "+str(LChainLengthHole5)+", RHole5: "+str(RChainLengthHole5)
	print "LHole6: "+str(LChainLengthHole6)+", RHole6: "+str(RChainLengthHole6)
	print "LHole7: "+str(LChainLengthHole7)+", RHole7: "+str(RChainLengthHole7)
	print "LHole8: "+str(LChainLengthHole8)+", RHole8: "+str(RChainLengthHole8)

x=raw_input("") #pause for review



LChainErrorHole1 = acceptableTolerance #this just makes it a float really
LChainErrorHole2 = acceptableTolerance
LChainErrorHole3 = acceptableTolerance
LChainErrorHole4 = acceptableTolerance
RChainErrorHole1 = acceptableTolerance
RChainErrorHole2 = acceptableTolerance
RChainErrorHole3 = acceptableTolerance
RChainErrorHole4 = acceptableTolerance
if (holePattern == 3):
	LChainErrorHole5 = acceptableTolerance #this just makes it a float really
	LChainErrorHole6 = acceptableTolerance
	LChainErrorHole7 = acceptableTolerance
	LChainErrorHole8 = acceptableTolerance
	RChainErrorHole5 = acceptableTolerance
	RChainErrorHole6 = acceptableTolerance
	RChainErrorHole7 = acceptableTolerance
	RChainErrorHole8 = acceptableTolerance


previousErrorMagnitude = 99999999999999.9

bestErrorMagnitude = 99999999.9
reportCounter = 999
adjustMotorSpacingCounter = 0
adjustRotationalRadiusCounter = 0
adjustChainCompensationCounter = 0
adjustMotorSpacing = False # just initializing these variables
adjustRotationalRadius = False # just initializing these variables
adjustChainCompensation = False # just initializing these variables
scaleMultiplier = 1.0
n = 0
print "Iterating for new machine parameters"

# Iterate until error tolerance is achieved or maximum number of iterations occurs
errorMagnitude = 999999.9
previousErrorMagnitude = 9999999.9
bestErrorMagnitude = 9999999.9
while(errorMagnitude > acceptableTolerance and n < numberOfIterations):
	n += 1

	# calculate chain lengths based upon estimated parameters and actual hole locations
	LChainLengthHole1Est, RChainLengthHole1Est = CalculateChainLengths(leftMotorXEst, leftMotorYEst, rightMotorXEst, rightMotorYEst, aH1x, aH1y, chainOverSprocket, rotationRadiusEst, chainSagCorrectionEst, leftChainToleranceEst, rightChainToleranceEst, False, 0.0, 0.0)
	LChainLengthHole2Est, RChainLengthHole2Est = CalculateChainLengths(leftMotorXEst, leftMotorYEst, rightMotorXEst, rightMotorYEst, aH2x, aH2y, chainOverSprocket, rotationRadiusEst, chainSagCorrectionEst, leftChainToleranceEst, rightChainToleranceEst, False, 0.0, 0.0)
	LChainLengthHole3Est, RChainLengthHole3Est = CalculateChainLengths(leftMotorXEst, leftMotorYEst, rightMotorXEst, rightMotorYEst, aH3x, aH3y, chainOverSprocket, rotationRadiusEst, chainSagCorrectionEst, leftChainToleranceEst, rightChainToleranceEst, False, 0.0, 0.0)
	LChainLengthHole4Est, RChainLengthHole4Est = CalculateChainLengths(leftMotorXEst, leftMotorYEst, rightMotorXEst, rightMotorYEst, aH4x, aH4y, chainOverSprocket, rotationRadiusEst, chainSagCorrectionEst, leftChainToleranceEst, rightChainToleranceEst, False, 0.0, 0.0)
	if (holePattern == 3):
		LChainLengthHole5Est, RChainLengthHole5Est = CalculateChainLengths(leftMotorXEst, leftMotorYEst, rightMotorXEst, rightMotorYEst, aH5x, aH5y, chainOverSprocket, rotationRadiusEst, chainSagCorrectionEst, leftChainToleranceEst, rightChainToleranceEst, False, 0.0, 0.0)
		LChainLengthHole6Est, RChainLengthHole6Est = CalculateChainLengths(leftMotorXEst, leftMotorYEst, rightMotorXEst, rightMotorYEst, aH6x, aH6y, chainOverSprocket, rotationRadiusEst, chainSagCorrectionEst, leftChainToleranceEst, rightChainToleranceEst, False, 0.0, 0.0)
		LChainLengthHole7Est, RChainLengthHole7Est = CalculateChainLengths(leftMotorXEst, leftMotorYEst, rightMotorXEst, rightMotorYEst, aH7x, aH7y, chainOverSprocket, rotationRadiusEst, chainSagCorrectionEst, leftChainToleranceEst, rightChainToleranceEst, False, 0.0, 0.0)
		LChainLengthHole8Est, RChainLengthHole8Est = CalculateChainLengths(leftMotorXEst, leftMotorYEst, rightMotorXEst, rightMotorYEst, aH8x, aH8y, chainOverSprocket, rotationRadiusEst, chainSagCorrectionEst, leftChainToleranceEst, rightChainToleranceEst, False, 0.0, 0.0)

	# Determine chain length errors for current estimated machine parameters versus the measured parameters
	LChainErrorHole1 = LChainLengthHole1Est - LChainLengthHole1 + errorLH1#
	LChainErrorHole2 = LChainLengthHole2Est - LChainLengthHole2 + errorLH2#
	LChainErrorHole3 = LChainLengthHole3Est - LChainLengthHole3 + errorLH3#
	LChainErrorHole4 = LChainLengthHole4Est - LChainLengthHole4 + errorLH4#
	RChainErrorHole1 = RChainLengthHole1Est - RChainLengthHole1 + errorRH1#
	RChainErrorHole2 = RChainLengthHole2Est - RChainLengthHole2 + errorRH2#
	RChainErrorHole3 = RChainLengthHole3Est - RChainLengthHole3 + errorRH3#
	RChainErrorHole4 = RChainLengthHole4Est - RChainLengthHole4 + errorRH4#
	if (holePattern == 3):
		LChainErrorHole5 = LChainLengthHole5Est - LChainLengthHole5 + errorLH5#
		LChainErrorHole6 = LChainLengthHole6Est - LChainLengthHole6 + errorLH6#
		LChainErrorHole7 = LChainLengthHole7Est - LChainLengthHole7 + errorLH7#
		LChainErrorHole8 = LChainLengthHole8Est - LChainLengthHole8 + errorLH8#
		RChainErrorHole5 = RChainLengthHole5Est - RChainLengthHole5 + errorRH5#
		RChainErrorHole6 = RChainLengthHole6Est - RChainLengthHole6 + errorRH6#
		RChainErrorHole7 = RChainLengthHole7Est - RChainLengthHole7 + errorRH7#
		RChainErrorHole8 = RChainLengthHole8Est - RChainLengthHole8 + errorRH8#


#	errorMagnitude = math.sqrt( (LChainErrorHole1*LChainErrorHole1 + LChainErrorHole2*LChainErrorHole2 + LChainErrorHole3*LChainErrorHole3 + LChainErrorHole4*LChainErrorHole4 + RChainErrorHole1*RChainErrorHole1 + RChainErrorHole2*RChainErrorHole2 + RChainErrorHole3*RChainErrorHole3 + RChainErrorHole4*RChainErrorHole4) / 8.0)
#	if (holePattern == 3):
#		errorMagnitude = math.sqrt( (LChainErrorHole1*LChainErrorHole1 + LChainErrorHole2*LChainErrorHole2 + LChainErrorHole3*LChainErrorHole3 + LChainErrorHole4*LChainErrorHole4 +  LChainErrorHole5*LChainErrorHole5 + LChainErrorHole6*LChainErrorHole6 + LChainErrorHole7*LChainErrorHole7 + LChainErrorHole8*LChainErrorHole8 + RChainErrorHole1*RChainErrorHole1 + RChainErrorHole2*RChainErrorHole2 + RChainErrorHole3*RChainErrorHole3 + RChainErrorHole4*RChainErrorHole4 +  RChainErrorHole5*RChainErrorHole5 + RChainErrorHole6*RChainErrorHole6 + RChainErrorHole7*RChainErrorHole7 + RChainErrorHole8*RChainErrorHole8) / 16.0)

	errorMagnitude = 0.0
	errorMagnitude += CalculateMaximumError(LChainErrorHole1)
	errorMagnitude += CalculateMaximumError(LChainErrorHole2)
	errorMagnitude += CalculateMaximumError(LChainErrorHole3)
	errorMagnitude += CalculateMaximumError(LChainErrorHole4)
	errorMagnitude += CalculateMaximumError(RChainErrorHole1)
	errorMagnitude += CalculateMaximumError(RChainErrorHole2)
	errorMagnitude += CalculateMaximumError(RChainErrorHole3)
	errorMagnitude += CalculateMaximumError(RChainErrorHole4)
	if (holePattern == 3):
		errorMagnitude += CalculateMaximumError(LChainErrorHole5)
		errorMagnitude += CalculateMaximumError(LChainErrorHole6)
		errorMagnitude += CalculateMaximumError(LChainErrorHole7)
		errorMagnitude += CalculateMaximumError(LChainErrorHole8)
		errorMagnitude += CalculateMaximumError(RChainErrorHole5)
		errorMagnitude += CalculateMaximumError(RChainErrorHole6)
		errorMagnitude += CalculateMaximumError(RChainErrorHole7)
		errorMagnitude += CalculateMaximumError(RChainErrorHole8)
		errorMagnitude = math.sqrt(errorMagnitude/16.0)
	else:
		errorMagnitude = math.sqrt(errorMagnitude/8.0)

	if (errorMagnitude >= previousErrorMagnitude):
		leftMotorXEst = previousleftMotorXEst
		leftMotorYEst = previousleftMotorYEst
		rightMotorXEst = previousrightMotorXEst
		rightMotorYEst = previousrightMotorYEst
		rotationRadiusEst = previousrotationRadiusEst
		chainSagCorrectionEst = previouschainSagCorrectionEst
		leftChainToleranceEst = previousleftChainToleranceEst
		rightChainToleranceEst = previousrightChainToleranceEst
		adjustMotorSpacingCounter +=1
		if (adjustMotorSpacingCounter == adjustMotorSpacingInterval):
			adjustMotorSpacingCounter = 0
			adjustMotorSpacing = True
		adjustRotationalRadiusCounter +=1
		if (adjustRotationalRadiusCounter == adjustRotationalRadiusInterval):
			adjustRotationalRadiusCounter = 0
			adjustRotationalRadius = True
		adjustChainCompensationCounter +=1
		if (adjustChainCompensationCounter == adjustChainCompensationInterval):
			adjustChainCompensationCounter = 0
			adjustChainCompensation = True
	else:
		adjustMotorSpacingCounter = 0
		adjustRotationalRadiusCounter = 0
		adjustChainCompensationCounter = 0
		previousErrorMagnitude = errorMagnitude
		previousrotationRadiusEst = rotationRadiusEst
		previouschainSagCorrectionEst = chainSagCorrectionEst
		previousleftChainToleranceEst = leftChainToleranceEst
		previousrightChainToleranceEst = rightChainToleranceEst
		previousleftMotorXEst = leftMotorXEst
		previousleftMotorYEst = leftMotorYEst
		previousrightMotorXEst = rightMotorXEst
		previousrightMotorYEst = rightMotorYEst
		if (errorMagnitude < bestErrorMagnitude):
			bestErrorMagnitude = errorMagnitude
			bestrotationRadiusEst = rotationRadiusEst
			bestchainSagCorrectionEst = chainSagCorrectionEst
			bestleftChainToleranceEst = leftChainToleranceEst
			bestrightChainToleranceEst = rightChainToleranceEst
			bestleftMotorXEst = leftMotorXEst
			bestleftMotorYEst = leftMotorYEst
			bestrightMotorXEst = rightMotorXEst
			bestrightMotorYEst = rightMotorYEst
			bestLChainErrorHole1 = LChainErrorHole1
			bestLChainErrorHole2 = LChainErrorHole2
			bestLChainErrorHole3 = LChainErrorHole3
			bestLChainErrorHole4 = LChainErrorHole4
			bestRChainErrorHole1 = RChainErrorHole1
			bestRChainErrorHole2 = RChainErrorHole2
			bestRChainErrorHole3 = RChainErrorHole3
			bestRChainErrorHole4 = RChainErrorHole4
			if (holePattern ==3):
				bestLChainErrorHole5 = LChainErrorHole5
				bestLChainErrorHole6 = LChainErrorHole6
				bestLChainErrorHole7 = LChainErrorHole7
				bestLChainErrorHole8 = LChainErrorHole8
				bestRChainErrorHole5 = RChainErrorHole5
				bestRChainErrorHole6 = RChainErrorHole6
				bestRChainErrorHole7 = RChainErrorHole7
				bestRChainErrorHole8 = RChainErrorHole8

			#report better findings
			reportCounter += 1
			if (reportCounter == 1000):
				reportCounter = 0
				distBetweenMotors = math.sqrt( math.pow(bestleftMotorXEst-bestrightMotorXEst,2)+math.pow(bestleftMotorYEst-bestrightMotorYEst,2))
				motorTilt = math.atan((bestrightMotorYEst-bestleftMotorYEst)/(bestrightMotorXEst-bestleftMotorXEst))*180.0/3.141592
				print "---------------------------------------------------------------------------------------------"
				print "Best so far at N: " + str(n) + ", Error Magnitude: " + str(round(bestErrorMagnitude, 3))
				print "Motor Spacing: "+str(distBetweenMotors) + ", Motor Elevation: "+str(((bestleftMotorYEst+(bestrightMotorYEst-bestleftMotorYEst)/2.0))-workspaceHeight/2.0)+", Top Beam Tilt: "+str(motorTilt) +" degrees"
				tleftMotorX = math.cos(motorTilt*3.141592/180.0)*distBetweenMotors/-2.0 + (bestrightMotorXEst+bestleftMotorXEst)/2.0
				tleftMotorY = math.sin(motorTilt*3.141592/180.0)*distBetweenMotors/-2.0 + bestleftMotorYEst + (bestrightMotorYEst-bestleftMotorYEst)/2.0
				trightMotorX = math.cos(motorTilt*3.141592/180.0)*distBetweenMotors+tleftMotorX
				trightMotorY = math.sin(motorTilt*3.141592/180.0)*distBetweenMotors/2.0 + bestleftMotorYEst + (bestrightMotorYEst-bestleftMotorYEst)/2.0
				print "tleftMotorX: "+str(tleftMotorX) + ", tleftMotorY: "+str(tleftMotorY)
				print "trightMotorX: "+str(trightMotorX)+", trightMotorY:"+str(trightMotorY)
				print "tmotorspacing: "+str(math.sqrt( math.pow(tleftMotorX-trightMotorX,2)+math.pow(tleftMotorY-trightMotorY,2)))

				print "Rotation Disk Radius: " + str(round(bestrotationRadiusEst, 3)) + ", Chain Sag Correction Value: " + str(round(bestchainSagCorrectionEst, 6)) + ", Left Chain:"+str(round((1.0-bestleftChainToleranceEst)*100,7))+", Right Chain:"+str(round((1.0-bestrightChainToleranceEst)*100,7))
				print "leftMotorX: "+str(bestleftMotorXEst) + ", leftMotorY: "+str(bestleftMotorYEst)
				print "rightMotorX: "+str(bestrightMotorXEst)+", rightMotorY:"+str(bestrightMotorYEst)
				print "  LChain Error Hole 1: " + str(round(bestLChainErrorHole1,4)) + ", LChain Error Hole 2: " + str(round(bestLChainErrorHole2,4)) + ", LChain Error Hole 3: " + str(round(bestLChainErrorHole3,4)) + ", LChain Error Hole 4: " + str(round(bestLChainErrorHole4,4))
				print "  RChain Error Hole 1: " + str(round(bestRChainErrorHole1,4)) + ", RChain Error Hole 2: " + str(round(bestRChainErrorHole2,4)) + ", RChain Error Hole 3: " + str(round(bestRChainErrorHole3,4)) + ", RChain Error Hole 4: " + str(round(bestRChainErrorHole4,4))
				if (holePattern ==3):
					print "  LChain Error Hole 5: " + str(round(bestLChainErrorHole5,4)) + ", LChain Error Hole 6: " + str(round(bestLChainErrorHole6,4)) + ", LChain Error Hole 7: " + str(round(bestLChainErrorHole7,4)) + ", LChain Error Hole 8: " + str(round(bestLChainErrorHole8,4))
					print "  RChain Error Hole 5: " + str(round(bestRChainErrorHole5,4)) + ", RChain Error Hole 6: " + str(round(bestRChainErrorHole6,4)) + ", RChain Error Hole 7: " + str(round(bestRChainErrorHole7,4)) + ", RChain Error Hole 8: " + str(round(bestRChainErrorHole8,4))
				print "  RMS Error Hole 1: "+str(round(math.sqrt(math.pow(bestLChainErrorHole1,2)+math.pow(bestRChainErrorHole1,2)),4))
				print "  RMS Error Hole 2: "+str(round(math.sqrt(math.pow(bestLChainErrorHole2,2)+math.pow(bestRChainErrorHole2,2)),4))
				print "  RMS Error Hole 3: "+str(round(math.sqrt(math.pow(bestLChainErrorHole3,2)+math.pow(bestRChainErrorHole3,2)),4))
				print "  RMS Error Hole 4: "+str(round(math.sqrt(math.pow(bestLChainErrorHole4,2)+math.pow(bestRChainErrorHole4,2)),4))
				if (holePattern == 3):
					print "  RMS Error Hole 5: "+str(round(math.sqrt(math.pow(bestLChainErrorHole5,2)+math.pow(bestRChainErrorHole5,2)),4))
					print "  RMS Error Hole 6: "+str(round(math.sqrt(math.pow(bestLChainErrorHole6,2)+math.pow(bestRChainErrorHole6,2)),4))
					print "  RMS Error Hole 7: "+str(round(math.sqrt(math.pow(bestLChainErrorHole7,2)+math.pow(bestRChainErrorHole7,2)),4))
					print "  RMS Error Hole 8: "+str(round(math.sqrt(math.pow(bestLChainErrorHole8,2)+math.pow(bestRChainErrorHole8,2)),4))
				#x = raw_input("")

	#pick a random variable to adjust
	#direction = random.randint(0,1)  # determine if its an increase or decrease
	adjustValue = random.randint(-100, 100)
	Completed = False # trick value to enter while
	while (Completed == False):
		picked = random.randint(1,6)
		tscaleMultiplier = scaleMultiplier * float(adjustValue)/100.0 #avoid altering scaleMultiplier
		if (picked == 1):
			motor = random.randint(0,3) #pick which motor (or both) to adjust
			if (motor == 0 and adjustMotorTilt): #tilt left motor up or down
				leftMotorYEst += motorYcoordCorrectionScale*tscaleMultiplier
				# because left motor moved, change x coordinate of right motor to keep distance between motors fixed
				rightMotorXEst = leftMotorXEst + math.sqrt(math.pow(desiredMotorSpacing,2) - math.pow((leftMotorYEst-rightMotorYEst),2))
				Completed = True
				#print "1 "+str(leftMotorXEst)+", "+str(rightMotorXEst)+", "+str(desiredMotorSpacing)
			if (motor == 1 and adjustMotorTilt ): #tilt right motor up or down
				rightMotorYEst += motorYcoordCorrectionScale*tscaleMultiplier
				# because right motor mover, change x coordinate of left motor to keep distance between motors fixed
				leftMotorXEst = rightMotorXEst - math.sqrt(math.pow(desiredMotorSpacing,2) - math.pow((rightMotorYEst-leftMotorYEst),2))
				Completed = True
				#print "2"+str(leftMotorXEst)+", "+str(rightMotorXEst)+", "+str(desiredMotorSpacing)
			if (motor ==2 and adjustMotorYcoord): # moves both motors up or down in unison
				leftMotorYEst += motorYcoordCorrectionScale*tscaleMultiplier
				rightMotorYEst += motorYcoordCorrectionScale*tscaleMultiplier
				Completed = True
				#print "3"
			if (motor ==3 and adjustMotorSpacing):
				desiredMotorSpacing += motorSpacingCorrectionScale*tscaleMultiplier
				adjustMotorSpacing=False
				motor = random.randint(0,1)
				if (motor == 0):
					leftMotorXEst = rightMotorXEst - math.sqrt(math.pow(desiredMotorSpacing,2) - math.pow((rightMotorYEst-leftMotorYEst),2))
				else:
					rightMotorXEst = leftMotorXEst + math.sqrt(math.pow(desiredMotorSpacing,2) - math.pow((leftMotorYEst-rightMotorYEst),2))
				Completed = True
		if (picked == 2 and adjustMotorXcoord): #all x moves are in unison to keep distance between motors fixed
			leftMotorXEst += errorMagnitude*motorXcoordCorrectionScale*tscaleMultiplier
			rightMotorXEst += errorMagnitude*motorXcoordCorrectionScale*tscaleMultiplier
			Completed = True
			#print "6"
		if (picked == 3 and adjustChainSag):
			chainSagCorrectionEst += errorMagnitude*chainSagCorrectionCorrectionScale*tscaleMultiplier
			if (chainSagCorrectionEst < -99999):
				chainSagCorrectionEst = 20.0
			if (chainSagCorrectionEst > 99999):
				chainSagCorrectionEst = 40.0
			Completed = True
			#print "7"
		if (picked == 4 and adjustRotationalRadius): #recommend against this one if at all possible
			rotationRadiusEst -= errorMagnitude*rotationRadiusCorrectionScale*tscaleMultiplier
			adjustRotationalRadius = False
			Completed = True
			#print "8"
		if (picked == 5 and adjustChainCompensation):
			leftChainToleranceEst += errorMagnitude*chainCompensationCorrectionScale*tscaleMultiplier
			#rotationRadiusEst -= errorMagnitude*rotationRadiusCorrectionScale*tscaleMultiplier
			#make sure chain tolerance doesn't go over 1 (i.e., chain is shorter than should be.. this can cause optimization to go bonkers)
			if (leftChainToleranceEst>= 1.0):
				leftChainToleranceEst = 1.0
			adjustChainCompensation = False
			Completed = True
			#print "9"
		if (picked == 6 and adjustChainCompensation):
			rightChainToleranceEst += errorMagnitude*chainCompensationCorrectionScale*tscaleMultiplier
			#rotationRadiusEst -= errorMagnitude*rotationRadiusCorrectionScale*tscaleMultiplier #counteract chain tolerance some
			#make sure chain tolerance doesn't go over 1 (i.e., chain is shorter than should be.. this can cause optimization to go bonkers)
			if (rightChainToleranceEst>= 1.0):
				rightChainToleranceEst = 1.0
			adjustChainCompensation = False
			Completed = True
			#print "10"

	#make sure values aren't too far out of whack.
	if (False): # will never be run if False
		if (rotationRadiusEst<desiredRotationalRadius-2):
			rotationRadiusEst = desiredRotationalRadius-2
		if (rotationRadiusEst>desiredRotationalRadius+2):
			rotationRadiusEst = desiredRotationalRadius+2
		if (chainSagCorrectionEst < 10):
			chainSagCorrectionEst = 10
		if (chainSagCorrectionEst > 60):
			chainSagCorrectionEst = 60


print "---------------------------------------------------------------------------------------------"
if n == numberOfIterations:
	print "Machine parameters could no solve to your desired tolerance, but hopefully it got close."
else:
	print "Solved!"

print "Parameters for new GC"
print "--Maslow Settings Tab--"
distBetweenMotors = math.sqrt( math.pow(bestleftMotorXEst-bestrightMotorXEst,2)+math.pow(bestleftMotorYEst-bestrightMotorYEst,2))
print "Distance Between Motors: "+str(distBetweenMotors)
print "Motor Offset Height in mm: "+str(((bestleftMotorYEst+(bestrightMotorYEst-bestleftMotorYEst)/2.0))-workspaceHeight/2.0)
print "--Advanced Settings Tab--"
print "Chain Tolerance, Left Chain: "+str(round((1.0-bestleftChainToleranceEst)*100,7))
print "Chain Tolerance, Right Chain: "+str(round((1.0-bestrightChainToleranceEst)*100,7))
motorTilt = math.atan((bestrightMotorYEst-bestleftMotorYEst)/(bestrightMotorXEst-bestleftMotorXEst))*180.0/3.141592
print "Top Beam Tilt: "+str(round(motorTilt,7))
print "Rotation Radius for Triangular Kinematics: " + str(round(bestrotationRadiusEst, 4))
print "Chain Sag Correction Value for Triangular Kinematics: " + str(round(bestchainSagCorrectionEst, 6))
print "---------------------------------------------------------------------------------------------"
print "Error Magnitude: " + str(round(bestErrorMagnitude, 3))
print "  LChain Error Hole 1: " + str(round(bestLChainErrorHole1,4)) + ", LChain Error Hole 2: " + str(round(bestLChainErrorHole2,4)) + ", LChain Error Hole 3: " + str(round(bestLChainErrorHole3,4)) + ", LChain Error Hole 4: " + str(round(bestLChainErrorHole4,4))
print "  RChain Error Hole 1: " + str(round(bestRChainErrorHole1,4)) + ", RChain Error Hole 2: " + str(round(bestRChainErrorHole2,4)) + ", RChain Error Hole 3: " + str(round(bestRChainErrorHole3,4)) + ", RChain Error Hole 4: " + str(round(bestRChainErrorHole4,4))
if (holePattern ==3):
	print "  LChain Error Hole 5: " + str(round(bestLChainErrorHole5,4)) + ", LChain Error Hole 6: " + str(round(bestLChainErrorHole6,4)) + ", LChain Error Hole 7: " + str(round(bestLChainErrorHole7,4)) + ", LChain Error Hole 8: " + str(round(bestLChainErrorHole8,4))
	print "  RChain Error Hole 5: " + str(round(bestRChainErrorHole5,4)) + ", RChain Error Hole 6: " + str(round(bestRChainErrorHole6,4)) + ", RChain Error Hole 7: " + str(round(bestRChainErrorHole7,4)) + ", RChain Error Hole 8: " + str(round(bestRChainErrorHole8,4))
print "  RMS Error Hole 1: "+str(round(math.sqrt(math.pow(bestLChainErrorHole1,2)+math.pow(bestRChainErrorHole1,2)),4))
print "  RMS Error Hole 2: "+str(round(math.sqrt(math.pow(bestLChainErrorHole2,2)+math.pow(bestRChainErrorHole2,2)),4))
print "  RMS Error Hole 3: "+str(round(math.sqrt(math.pow(bestLChainErrorHole3,2)+math.pow(bestRChainErrorHole3,2)),4))
print "  RMS Error Hole 4: "+str(round(math.sqrt(math.pow(bestLChainErrorHole4,2)+math.pow(bestRChainErrorHole4,2)),4))
if (holePattern == 3):
	print "  RMS Error Hole 5: "+str(round(math.sqrt(math.pow(bestLChainErrorHole5,2)+math.pow(bestRChainErrorHole5,2)),4))
	print "  RMS Error Hole 6: "+str(round(math.sqrt(math.pow(bestLChainErrorHole6,2)+math.pow(bestRChainErrorHole6,2)),4))
	print "  RMS Error Hole 7: "+str(round(math.sqrt(math.pow(bestLChainErrorHole7,2)+math.pow(bestRChainErrorHole7,2)),4))
	print "  RMS Error Hole 8: "+str(round(math.sqrt(math.pow(bestLChainErrorHole8,2)+math.pow(bestRChainErrorHole8,2)),4))


x="n"
while (x<>"x"):
   x = raw_input ("Press 'x' to exit")


#this was here for testing.  typed a lot so I'm saving it.
#print "leftMotorDistanceHole1: "+str(leftMotorDistanceHole1)+", leftMotorDistanceHole2: "+str(leftMotorDistanceHole2)+", leftMotorDistanceHole3: "+str(leftMotorDistanceHole3)+", leftMotorDistanceHole4: "+str(leftMotorDistanceHole4)
#print "rightMotorDistanceHole1: "+str(rightMotorDistanceHole1)+", rightMotorDistanceHole2: "+str(rightMotorDistanceHole2)+", rightMotorDistanceHole3: "+str(rightMotorDistanceHole3)+", leftMotorDistanceHole4: "+str(rightMotorDistanceHole4)
#print "leftChainAngleHole1: "+str(leftChainAngleHole1)+", leftChainAngleHole2: "+str(leftChainAngleHole2)+", leftChainAngleHole3: "+str(leftChainAngleHole3)+", leftChainAngleHole4: "+str(leftChainAngleHole4)
#print "rightChainAngleHole1: "+str(rightChainAngleHole1)+", rightChainAngleHole2: "+str(rightChainAngleHole2)+", rightChainAngleHole3: "+str(rightChainAngleHole3)+", rightChainAngleHole4: "+str(rightChainAngleHole4)
#print "leftChainSag1: "+str(leftChainSag1)+", leftChainSag2: "+str(leftChainSag2)+", leftChainSag3: "+str(leftChainSag3)+", leftChainSag4: "+str(leftChainSag4)
#print "rightChainSag1: "+str(rightChainSag1)+", rightChainSag2: "+str(rightChainSag2)+", rightChainSag3: "+str(rightChainSag3)+", rightChainSag4: "+str(rightChainSag4)
