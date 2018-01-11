from   kivy.uix.widget                    import   Widget
from   kivy.properties                    import   ObjectProperty
from   UIElements.touchNumberInput        import   TouchNumberInput
from   kivy.uix.popup                     import   Popup
import global_variables
import math

class TriangularCalibration(Widget):
    '''
    
    Provides a standard interface for running the calibration test pattern for triangular kinematics 
    
    '''
    data                         =  ObjectProperty(None) #linked externally
    numberOfTimesTestCutRun      = -2
    
    def cutTestPaternTriangular(self):

        workspaceHeight = float(self.data.config.get('Maslow Settings', 'bedHeight'))
        workspaceWidth = float(self.data.config.get('Maslow Settings', 'bedWidth'))

        self.data.units = "MM"
        self.data.gcode_queue.put("G21 ")
        self.data.gcode_queue.put("G90  ") #Switch to absolute mode
        self.data.gcode_queue.put("G40 ")

        self.data.gcode_queue.put("G0 Z5 ")
        self.data.gcode_queue.put("G0 X0 Y0  ")
        self.data.gcode_queue.put("G17 ")

        self.data.gcode_queue.put("G91 ")   #Switch to relative mode

        self.data.gcode_queue.put("G0 X12.7 Y" + str(workspaceHeight/4) + "  ")  # Move up 25% the workspace to first cut point
        self.data.gcode_queue.put("G1 Z-7 F500 ")
        self.data.gcode_queue.put("G1 X-25.4 ") # Cut 25.4mm horizontal mark
        self.data.gcode_queue.put("G1 Z7 ")
        self.data.gcode_queue.put("G0 Y-" + str(workspaceHeight/2) + "  ")  # Move down 50% the workspace to second cut point
        self.data.gcode_queue.put("G1 Z-7 ")
        self.data.gcode_queue.put("G1 X25.4 ") # Cut 25.4mm horizontal mark
        self.data.gcode_queue.put("G1 Z7 ")

        self.data.gcode_queue.put("G0 X" + str((workspaceWidth/8)-12.7) + " Y" + str(workspaceHeight/4) + "  ")  # Move up 25% the workspace and to the side to allow measurement of the cuts

        self.data.gcode_queue.put("G90  ") #Switch back to absolute mode

        self.cutBtnT.text = "Re-Cut Test\nPattern"
        self.vertMeasureT1.disabled = False
        self.vertMeasureT2.disabled = False
        self.enterValuesT.disabled = False

    def enterTestPaternValuesTriangular(self):
        '''

        Takes the measured distance and uses it to iteratively calculate the rotationDiskRadius and yMotorOffset

        '''

        # Validate user inputs

        workspaceHeight = float(self.data.config.get('Maslow Settings', 'bedHeight'))

        try:
            distBetweenCuts = float(self.vertMeasureT1.text)
        except:
            self.data.message_queue.put("Message: Please enter a number for the distance between cuts.")
            return

        try:
            distWorkareaTopToCut = float(self.vertMeasureT2.text)
        except:
            self.data.message_queue.put("Message: Please enter a number for the distance between the top of the work area and the top cut.")
            return

        try:
            bitDiameter = float(self.bitDiameterT.text)
        except:
            self.data.message_queue.put("Message: Please enter a number for the bit diameter.")
            return

        if self.unitsBtnT.text == 'Units: inches':
            if (((distBetweenCuts*25.4) > workspaceHeight) or ((distBetweenCuts*25.4) < (workspaceHeight / 10))):
                self.data.message_queue.put('Message: The measurement between cuts of ' + str(distBetweenCuts) + ' inches seems wrong.\n\nPlease check the number and enter it again.')
                return
            if (((distWorkareaTopToCut*25.4) > (workspaceHeight / 2)) or (distWorkareaTopToCut < 0)):
                self.data.message_queue.put('Message: The measurement between the top edge of the work area and the top cut of ' + str(distWorkareaTopToCut) + ' inches seems wrong.\n\nPlease check the number and enter it again.')
                return
            if ((bitDiameter > 1) or (bitDiameter < 0)):
                self.data.message_queue.put('Message: The bit diameter value of ' + str(bitDiameter) + ' inches seems wrong.\n\nPlease check the number and enter it again.')
                return
            distBetweenCuts *= 25.4
            distWorkareaTopToCut *= 25.4
            bitDiameter *= 25.4
        else:
            if ((distBetweenCuts > workspaceHeight) or (distBetweenCuts < (workspaceHeight / 10))):
                self.data.message_queue.put('Message: The measurement between cuts of ' + str(distBetweenCuts) + ' mm seems wrong.\n\nPlease check the number and enter it again.')
                return
            if ((distWorkareaTopToCut > (workspaceHeight / 2)) or (distWorkareaTopToCut < 0)):
                self.data.message_queue.put('Message: The measurement between the top edge of the work area and the top cut of ' + str(distWorkareaTopToCut) + ' mm seems wrong.\n\nPlease check the number and enter it again.')
                return
            if ((bitDiameter > 25.4) or (bitDiameter < 0)):
                self.data.message_queue.put('Message: The bit diameter value of ' + str(bitDiameter) + ' mm seems wrong.\n\nPlease check the number and enter it again.')
                return

        # Configure iteration parameters

        acceptableTolerance = .001
        numberOfIterations = 5000
        motorYcoordCorrectionScale = 0.5
        rotationRadiusCorrectionScale = 0.5

        # Gather current machine parameters

        motorSpacing = float(self.data.config.get('Maslow Settings', 'motorSpacingX'))
        motorXcoord = motorSpacing/2
        motorYoffsetEst = float(self.data.config.get('Maslow Settings', 'motorOffsetY'))
        motorYcoordEst = (workspaceHeight/2) + motorYoffsetEst
        rotationRadiusEst = float(self.data.config.get('Advanced Settings', 'rotationRadius'))
        gearTeeth = float(self.data.config.get('Advanced Settings', 'gearTeeth'))
        chainPitch = float(self.data.config.get('Advanced Settings', 'chainPitch'))
        motorSprocketRadius = (gearTeeth*chainPitch)/(2*3.14159)

        # Calculate the actual chain lengths for each cut location

        MotorDistanceCut1 = math.sqrt(math.pow(motorXcoord,2)+math.pow(motorYcoordEst - (workspaceHeight/4),2))
        MotorDistanceCut2 = math.sqrt(math.pow(motorXcoord,2)+math.pow(motorYcoordEst + (workspaceHeight/4),2))

        ChainLengthCut1 = (motorSprocketRadius * (3.14159 - math.acos(motorSprocketRadius / MotorDistanceCut1) - math.acos((motorYcoordEst - (workspaceHeight/4)) / MotorDistanceCut1))) + math.sqrt(math.pow(MotorDistanceCut1,2) - math.pow(motorSprocketRadius,2)) - rotationRadiusEst
        ChainLengthCut2 = (motorSprocketRadius * (3.14159 - math.acos(motorSprocketRadius / MotorDistanceCut2) - math.acos((motorYcoordEst + (workspaceHeight/4)) / MotorDistanceCut2))) + math.sqrt(math.pow(MotorDistanceCut2,2) - math.pow(motorSprocketRadius,2)) - rotationRadiusEst

        # Set up the iterative algorithm

        print "Previous machine parameters:"
        print "Motor Spacing: " + str(motorSpacing) + ", Motor Y Offset: " + str(motorYoffsetEst) + ", Rotation Disk Radius: " + str(rotationRadiusEst)

        motorYcoordEst = distWorkareaTopToCut + (bitDiameter / 2)
        rotationRadiusEst = 0
        ChainErrorCut1 = acceptableTolerance
        ChainErrorCut2 = acceptableTolerance
        n = 0

        self.vertMeasureT1.disabled = True
        self.vertMeasureT2.disabled = True
        self.enterValuesT.disabled = True

        print "Iterating for new machine parameters"

        # Iterate until error tolerance is achieved or maximum number of iterations occurs

        while (((abs(ChainErrorCut1) >= acceptableTolerance ) or (abs(ChainErrorCut2) >= acceptableTolerance)) and (n < numberOfIterations)):
            n += 1

            # Calculate chain lengths for current estimated parameters

            MotorDistanceCut1Est = math.sqrt(math.pow(motorXcoord,2)+math.pow(motorYcoordEst,2))
            MotorDistanceCut2Est = math.sqrt(math.pow(motorXcoord,2)+math.pow(motorYcoordEst + distBetweenCuts,2))

            ChainLengthCut1Est = (motorSprocketRadius * (3.14159 - math.acos(motorSprocketRadius / MotorDistanceCut1Est) - math.acos((motorYcoordEst) / MotorDistanceCut1Est))) + math.sqrt(math.pow(MotorDistanceCut1Est,2) - math.pow(motorSprocketRadius,2)) - rotationRadiusEst
            ChainLengthCut2Est = (motorSprocketRadius * (3.14159 - math.acos(motorSprocketRadius / MotorDistanceCut2Est) - math.acos((motorYcoordEst + distBetweenCuts) / MotorDistanceCut2Est))) + math.sqrt(math.pow(MotorDistanceCut2Est,2) - math.pow(motorSprocketRadius,2)) - rotationRadiusEst

            # Determine chain length errors for current estimated machine parameters versus the measured parameters

            ChainErrorCut1 = ChainLengthCut1Est - ChainLengthCut1
            ChainErrorCut2 = ChainLengthCut2Est - ChainLengthCut2

            # Develop a printable motor Y offset value to update the user

            motorYoffsetEstPrint = motorYcoordEst - distWorkareaTopToCut - (bitDiameter / 2)

            print "N: " + str(n) + ", Motor Spacing: " + str(round(motorSpacing, 3)) + ", Motor Y Offset: " + str(round(motorYoffsetEstPrint, 3)) + ", Rotation Disk Radius: " + str(round(rotationRadiusEst, 3)) + ", Chain Error Cut 1: " + str(round(ChainErrorCut1,3)) + ", Chain Error Cut 2: " + str(round(ChainErrorCut2,3))

            # Update the machine parameters based on the current chain length errors

            if ((ChainErrorCut1 < 0 and ChainErrorCut2 < 0) or (ChainErrorCut1 > 0 and ChainErrorCut2 > 0)):
                motorYcoordEst -= ((ChainErrorCut1 + ChainErrorCut2) / 2) * motorYcoordCorrectionScale
            else:
                rotationRadiusEst += ((ChainErrorCut1 - ChainErrorCut2) / 2) * rotationRadiusCorrectionScale
                if (rotationRadiusEst < 0):
                    rotationRadiusEst = 0

            # If we get unrealistic values, reset and try again with smaller steps

            if (motorYcoordEst < -(workspaceHeight/4) or motorYcoordEst > (2*workspaceHeight) or rotationRadiusEst > workspaceHeight):
                    motorYcoordEst = distWorkareaTopToCut + (bitDiameter / 2)
                    rotationRadiusEst = 0
                    motorYcoordCorrectionScale = float(motorYcoordCorrectionScale/2)
                    rotationRadiusCorrectionScale = float(rotationRadiusCorrectionScale/2)
                    print "Estimated values out of range, trying again with smaller steps"

        if n == numberOfIterations:
            self.data.message_queue.put('Message: The machine was not able to be calibrated. Please ensure the work area dimensions are correct and try again.')
            print "Machine parameters could not be determined"

            # Return sled to workspace center

            self.data.gcode_queue.put("G21 ")
            self.data.gcode_queue.put("G90 ")
            self.data.gcode_queue.put("G40 ")
            self.data.gcode_queue.put("G0 X0 Y0 ")
            
            return

        print "Machine parameters found:"

        motorYoffsetEst = motorYcoordEst - distWorkareaTopToCut - (bitDiameter / 2)

        motorYoffsetEst = round(motorYoffsetEst, 1)
        rotationRadiusEst = round(rotationRadiusEst, 1)

        print "Motor Spacing: " + str(motorSpacing) + ", Motor Y Offset: " + str(motorYoffsetEst) + ", Rotation Disk Radius: " + str(rotationRadiusEst)

        # Update machine parameters

        self.data.config.set('Maslow Settings', 'motorOffsetY', str(motorYoffsetEst))
        self.data.config.set('Advanced Settings', 'rotationRadius', str(rotationRadiusEst))
        self.data.config.write()
        self.data.pushSettings()

        # With new calibration parameters return sled to workspace center

        self.data.gcode_queue.put("G21 ")
        self.data.gcode_queue.put("G90 ")
        self.data.gcode_queue.put("G40 ")
        self.data.gcode_queue.put("G0 X0 Y0 ")

        self.carousel.load_slide(self.carousel.slides[11])

    def stopCut(self):
        self.data.quick_queue.put("!") 
        with self.data.gcode_queue.mutex:
            self.data.gcode_queue.queue.clear()
        
        self.cutBtnT.disabled = False

    def switchUnitsT(self):
        if self.unitsBtnT.text == 'Units: mm':
            self.unitsBtnT.text = 'Units: inches'
        else:
            self.unitsBtnT.text = 'Units: mm'
