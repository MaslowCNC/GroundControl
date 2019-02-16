import kinematics as kinematics
import math
from scipy.optimize import least_squares
import numpy
class HoleyCalibration():
    SP_D=3601.2
    SP_motorOffsetY=468.4
    SP_rotationDiskRadius=139.1
    SP_leftChainTolerance=0
    SP_rightChainTolerance=0
    SP_sledWeight=22
    SP_chainOverSprocket=False
    
    Opt_D=3601.2
    Opt_motorOffsetY=468.4
    Opt_rotationDiskRadius=139.1
    Opt_leftChainTolerance=0
    Opt_rightChainTolerance=0
    Opt_sledWeight=22
    
    #Chain lengths @ each hole
    ChainLengths=[]
    MeasurementMap=[
            (1,2),
            (2,3),
            (4,5),
            (5,6),
            (1,4),
            (2,5),
            (3,6),
            (2,4),
            (1,5),
            (3,5),
            (2,6)]
    
    IdealLengthArray=0
    MeasuredLengthArray=0
    DesiredLengthDeltaArray=0
    
    OptimizationOutput=0
    
    kin=kinematics.Kinematics()
    #Define function with input of (ideal lengths and) machine parameters (delta) and output of length error
    def LengthDeltaFromIdeal(self,DeltaArray):
        self.kin.D=self.SP_D+DeltaArray[0]
        self.kin.motorOffsetY=self.SP_motorOffsetY+DeltaArray[1]
        self.kin.leftChainTolerance=self.SP_leftChainTolerance+DeltaArray[2]
        self.kin.rightChainTolerance=self.SP_rightChainTolerance+DeltaArray[3]
        self.kin.recomputeGeometry()
        #import pdb; pdb.set_trace()
        CalculatedPositions=[]
        for LeftChainLength,RightChainLength in self.ChainLengths:
            CalculatedPositions.append(self.kin.forward(LeftChainLength,RightChainLength))
        
        return self.MeasuredLengthArray-self.CalculateMeasurements(CalculatedPositions)
    
    def InitialMeasurementError(self,Meas,idx): #For validating in GUI
        Ideal=self.IdealLengthArray[idx]
        return Ideal-Meas
    def ValidateMeasurement(self,Meas,idx):
        if idx<12:
            Ideal=self.IdealLengthArray[idx]
            return 0.1>abs((Ideal-Meas)/Ideal)
        else:
            return Meas>0.0
        
    def CalculateMeasurements(self,HolePositions):
#        aH1x,aH1y,aH2x,aH2y,aH3x,aH3y,aH4x,aH4y,aH5x,aH5y,aH6x,aH6y
        Measurements=[]
        for StartHoleIdx,EndHoleIdx in self.MeasurementMap:
            x1,y1=HolePositions[StartHoleIdx-1]
            x2,y2=HolePositions[EndHoleIdx-1]
            Measurements.append(GeometricLength(x1,y1,x2,y2))
        ToTopHole=1
        Measurements.append(GeometricLength(HolePositions[ToTopHole][0],HolePositions[ToTopHole][1],HolePositions[ToTopHole][0],self.kin.machineHeight/2))
        
        return numpy.array(Measurements)
    
    def InitializeIdealXyCoordinates(self):
        
        workspaceHeight = self.kin.machineHeight
        workspaceWidth = self.kin.machineWidth
        aH1x = -(workspaceWidth/2.0-254.0)
        aH1y = (workspaceHeight/2.0-254.0)
        aH2x = 0
        IdealCoordinates=[
                (aH1x,aH1y),
                (aH2x,aH1y),
                (-aH1x,aH1y),
                (aH1x,-aH1y),
                (aH2x,-aH1y),
                (-aH1x,-aH1y)]
        self.kin.D=self.SP_D
        self.kin.motorOffsetY=self.SP_motorOffsetY
        self.kin.rotationDiskRadius=self.SP_rotationDiskRadius
        self.kin.sledWeight=self.SP_sledWeight
        self.kin.leftChainTolerance=self.SP_leftChainTolerance
        self.kin.rightChainTolerance=self.SP_rightChainTolerance
        self.kin.chainOverSprocket=self.SP_chainOverSprocket
        self.kin.recomputeGeometry()
        self.IdealLengthArray=self.CalculateMeasurements(IdealCoordinates)
        
        self.ChainLengths=[]
        for x,y in IdealCoordinates:
            self.ChainLengths.append(self.kin.inverse(x,y))
        return self.IdealLengthArray
    
    def SetMeasurements(self,Measurements):
        self.MeasuredLengthArray=numpy.array(Measurements)
    
    def Calibrate(self):
        self.OptimizationOutput=least_squares(self.LengthDeltaFromIdeal,numpy.array([0,0,0,0]),jac='2-point',diff_step=.1,ftol=1e-11)
        Deltas=self.OptimizationOutput.x
        self.Opt_D=Deltas[0]+self.SP_D
        self.Opt_motorOffsetY=Deltas[1]+self.SP_motorOffsetY
        self.Opt_leftChainTolerance=Deltas[2]+self.SP_leftChainTolerance
        self.Opt_rightChainTolerance=Deltas[3]+self.SP_rightChainTolerance
        self.kin.D=self.Opt_D
        self.kin.motorOffsetY=self.Opt_motorOffsetY
        self.kin.leftChainTolerance=self.Opt_leftChainTolerance
        self.kin.rightChainTolerance=self.Opt_rightChainTolerance
        self.kin.recomputeGeometry()
    def ReportCalibration(self):
        print('Optimized Errors')
        for idx,pts,ms,cal,er in zip(
                range(self.MeasuredLengthArray.size),
                self.MeasurementMap,
                self.MeasuredLengthArray,
                self.CalibratedLengths(),
                self.CalibratedLengthError()):
            print(('\tIndex                : {}'+
                   '\n\t\tPoints Span        : {} to {}'+
                   '\n\t\tMeasured Distance  : {}'+
                   '\n\t\tCalibrated Distance: {}'+
                   '\n\t\tDistance Error     : {}').format(
                           idx,pts[0],pts[1],ms,cal,er))
        print("")
        print("Distance Between Motors:")
        print(self.Opt_D)
        print("")
        print("Motor Y Offset:")
        print(self.Opt_motorOffsetY)
        print("")
        print("Left Chain Tolerance:")
        print(self.Opt_leftChainTolerance)
        print("")
        print("Right Chain Tolerance:")
        print(self.Opt_rightChainTolerance)
    def CalibratedLengths(self):
        return self.MeasuredLengthArray-self.OptimizationOutput.fun
    def CalibratedLengthError(self):
        #import pdb; pdb.set_trace()
        return self.OptimizationOutput.fun
    def HolePositionsFromChainLengths(self):
        HolePositions=[]
        for LeftChainLength,RightChainLength in self.ChainLengths:
            HolePositions.append(self.kin.forward(LeftChainLength,RightChainLength))
        return HolePositions
    
    def SimulateMeasurement(self,D,motorOffsetY,leftChainTolerance,rightChainTolerance):
        #Simulate Measurement.  Modify machine parameters, use kin.forward to determine x,y coordinates. Return machine parameters to original
        self.kin.D=D
        self.kin.motorOffsetY=motorOffsetY
        self.kin.leftChainTolerance=leftChainTolerance
        self.kin.rightChainTolerance=rightChainTolerance
        self.kin.recomputeGeometry()
        
        HolePositions=self.HolePositionsFromChainLengths()
        
        self.kin.D=self.SP_D
        self.kin.motorOffsetY=self.SP_motorOffsetY
        self.kin.rotationDiskRadius=self.SP_rotationDiskRadius
        self.kin.sledWeight=self.SP_sledWeight
        self.kin.leftChainTolerance=self.SP_leftChainTolerance
        self.kin.rightChainTolerance=self.SP_rightChainTolerance
        self.kin.recomputeGeometry()
        
        Measurements=self.CalculateMeasurements(HolePositions)
        
        self.SetMeasurements(Measurements)

def GeometricLength(x1,y1,x2,y2):
    return math.sqrt(math.pow(x1-x2,2) + math.pow(y1-y2,2))
    