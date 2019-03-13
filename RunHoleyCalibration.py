import CalibrationWidgets.HoleyCalibration as HoleyCalibration

cal=HoleyCalibration.HoleyCalibration()

# Starting machine calibration
cal.kin.isQuadKinematics=False
cal.SP_D=3629.025
cal.SP_motorOffsetY=503.4 #539.7
cal.SP_rotationDiskRadius=138.1
cal.SP_sledWeight=109.47 #N
cal.SP_leftChainTolerance=0
cal.SP_rightChainTolerance=0
cal.SP_chainOverSprocket=0


IdealLengthArray=cal.InitializeIdealXyCoordinates()

#RealMachineParameters={
#        'D':3630,
#        'motorOffsetY':700,
#        'leftChainTolerance':.5,
#        'rightChainTolerance':.5}
#cal.SimulateMeasurement(**RealMachineParameters)
Measurements=[
            (47.+5./8.)-(9.+11./16.),
            (85.+9./16.)-(47.+5./8.),
            (47.+5./8.)-(9.+23./32.),
            (48.+1./4.)-(10.+3./8.),
            (37.+1./2.)-(9.+1./2.),
            (37.+1./2.)-(9.+1./2.),
            (37.+11./16.)-(9.+5./8.),
            (60.+19./32.)-(13.+15./32.),
            (61.+1./2.)-(14.+11./32.),
            61.-(13+7./8.),
            (61.+15./32.)-(14.+5./16.),
            9.+3./8.]
Measurements=[Measurement*25.4 for Measurement in Measurements]
cal.SetMeasurements(Measurements)
cal.Calibrate()
cal.ReportCalibration()
