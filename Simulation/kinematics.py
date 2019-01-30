import math

class Kinematics():


    '''
    The Kinematics module relates the lengths of the chains to the position of the cutting head
    in X-Y space.
    '''

    l             = 310.0                               #horizontal distance between sled attach points
    s             = 139.0                               #vertical distance between sled attach points and bit
    h             = math.sqrt((l/2)*(l/2) + s * s)           #distance between sled attach point and bit
    h3            = 79.0                                #distance from bit to sled center of mass
    D             = 2978.4                              #distance between sprocket centers
    R             = 10.2                                #sprocket radius
    machineHeight = 1219.2                              #this is 4 feet in mm
    machineWidth  = 2438.4                              #this is 8 feet in mm
    motorOffsetY  = 463.0                               #vertical distance from the corner of the work area to the sprocket center
    chain1Offset  = 0                                   #number of links +,- that have slipped
    chain2Offset  = 0                                   #number of links +,- that have slipped

    x = 2708.4
    y = 270

    #utility variables
    DegPerRad = 360/(4 * math.atan(1))
    Time = 0
    Mirror = 0

    # Definition of angles
    # Gamma, angle of left chain
    # Lamda, angle of right chain
    # Phi, tilt of sled
    # Theta, angle between chains and bit (corners of triangle formed by l, s, h)

    #Calculation tolerances
    MaxError = 0.01
    MaxTries = 10
    DeltaPhi = 0.01
    DeltaY = 0.01

    #Criterion Computation Variables
    Phi = -0.2
    TanGamma = 0
    TanLambda= 0
    Y1Plus = 0
    Y2Plus = 0
    if (l < 1.0):
        Theta = 0
    else:
        Theta = math.atan(2*s/l)
    Psi1 = Theta - Phi
    Psi2 = Theta + Phi
    Tries = 0
    Jac=[0,0,0,0,0,0,0,0,0,0]
    Solution=[0,0,0]
    Crit=[0,0,0]
    #Offsetx1 = 0
    #Offsetx2 = 0
    #Offsety1 = 0
    #Offsety2 = 0
    #SinPsi1 = 0
    #CosPsi1 = 0
    #SinPsi2 = 0
    #CosPsi2 = 0
    #SinPsi1D = 0
    #CosPsi1D = 0
    #SinPsi2D = 0
    #CosPsi2D = 0
    #MySinPhi = 0
    #MySinPhiDelta = 0

    #intermediate output
    Lambda = 0
    Gamma = 0

    # Motor axes length to the bit for triangular kinematics
    Motor1Distance = 0#left motor axis distance to sled
    Motor2Distance = 0#right motor axis distance to sled

    # output = chain lengths measured from 12 o'clock
    Chain1  = 0#left chain length
    Chain2  = 0#right chain length
    
    leftChainTolerance=0
    rightChainTolerance=0
    chainWeight=.09/304.8
    chainElasticity=.000023
    sledWeight=22

    i = 0
    
    rotationDiskRadius = 100
    chainSagCorrection = 0
    chainOverSprocket = 1
    _xCordOfMotor = D/2
    _yCordOfMotor = machineHeight/2 + motorOffsetY
    isQuadKinematics    = True

    def _verifyValidTarget(self, xTarget, yTarget):
        #If the target point is beyond one of the edges of the board, the machine stops at the edge

        if (xTarget < -self.machineWidth/2):
            xTarget = -self.machineWidth/2

        elif (xTarget >  self.machineWidth/2):
            xTarget =  self.machineWidth/2

        elif (yTarget >  self.machineHeight/2):
            yTarget =  self.machineHeight/2

        elif (yTarget <  -self.machineHeight/2):
            yTarget =  -self.machineHeight/2

    def recomputeGeometry(self):
        '''
        Some variables are computed on class creation for the geometry of the machine to reduce overhead,
        calling this function regenerates those values.
        '''
        self.h = math.sqrt((self.l/2)*(self.l/2) + self.s * self.s)
        self.Theta = math.atan(2*self.s/self.l)
        self.Psi1 = self.Theta - self.Phi
        self.Psi2 = self.Theta + self.Phi
        
        self._xCordOfMotor = self.D/2
        self._yCordOfMotor = self.machineHeight/2 + self.motorOffsetY

    def inverse(self, xTarget, yTarget):
        '''
        
        Compute the lengths of chain needed to reach a target XY position
        
        '''
        if self.isQuadKinematics:
            return self.quadrilateralInverse(xTarget, yTarget)
        else:
            return self.triangularInverse(xTarget, yTarget)
    
    def triangularInverse(self, xTarget, yTarget):
        '''
    
        The inverse kinematics (relating an xy coordinate pair to the required chain lengths to hit that point)
        function for a triangular set up where the chains meet at a point, or are arranged so that they simulate 
        meeting at a point.
        
        '''
    
        #Confirm that the coordinates are on the wood
        self._verifyValidTarget(xTarget, yTarget)
        
        Motor1Distance = math.sqrt(math.pow((-1*self._xCordOfMotor - xTarget),2)+math.pow((self._yCordOfMotor - yTarget),2))
        Motor2Distance = math.sqrt(math.pow((self._xCordOfMotor - xTarget),2)+math.pow((self._yCordOfMotor - yTarget),2))

        #Calculate the chain angles from horizontal, based on if the chain connects to the sled from the top or bottom of the sprocket
        if self.chainOverSprocket == 1:
            Chain1Angle = math.asin((self._yCordOfMotor - yTarget)/Motor1Distance) + math.asin(self.R/Motor1Distance)
            Chain2Angle = math.asin((self._yCordOfMotor - yTarget)/Motor2Distance) + math.asin(self.R/Motor2Distance)

            Chain1AroundSprocket = self.R * Chain1Angle
            Chain2AroundSprocket = self.R * Chain2Angle
            
            xTangent1=-self._xCordOfMotor+self.R*math.sin(Chain1Angle)
            yTangent1=self._yCordOfMotor+self.R*math.cos(Chain1Angle)
            
            xTangent2=self._xCordOfMotor-self.R*math.sin(Chain2Angle)
            yTangent2=self._yCordOfMotor+self.R*math.cos(Chain2Angle)
        else:
            Chain1Angle = math.asin((self._yCordOfMotor - yTarget)/Motor1Distance) - math.asin(self.R/Motor1Distance)
            Chain2Angle = math.asin((self._yCordOfMotor - yTarget)/Motor2Distance) - math.asin(self.R/Motor2Distance)

            Chain1AroundSprocket = self.R * (3.14159 - Chain1Angle)
            Chain2AroundSprocket = self.R * (3.14159 - Chain2Angle)
            
            xTangent1=-self._xCordOfMotor-self.R*math.sin(Chain1Angle)
            yTangent1=self._yCordOfMotor-self.R*math.cos(Chain1Angle)
            
            xTangent2=self._xCordOfMotor+self.R*math.sin(Chain2Angle)
            yTangent2=self._yCordOfMotor-self.R*math.cos(Chain2Angle)
        
        #Calculate the straight chain length from the sprocket to the bit
        Chain1Straight = math.sqrt(math.pow(Motor1Distance,2)-math.pow(self.R,2))
        Chain2Straight = math.sqrt(math.pow(Motor2Distance,2)-math.pow(self.R,2))
        
        #TensionDenominator=(x_l       y_r-      x_r       y_l-      x_l       y_t     +x_t    y_l      +x_r       y_t    -x_t     y_r)
        TensionDenominator= (xTangent1*yTangent2-xTangent2*yTangent1-xTangent1*yTarget+xTarget*yTangent1+xTangent2*yTarget-xTarget*yTangent2)
        
        #Total vertical force is sled weight, plus half the two chain weights
        TotalWeight=self.sledWeight+0.5*self.chainWeight*(Chain1Straight+Chain2Straight)
        
        #T_l     = -(    w                *sqrt(     pow(x_l      -x_t    ,2.0)+pow(     y_l      -y_t    ,2.0))  (x_r      -x_t))    /TensionDenominator
        Tension1 = - (TotalWeight*math.sqrt(math.pow(xTangent1-xTarget,2)+math.pow(yTangent1-yTarget,2))*(xTangent2-xTarget))/TensionDenominator
        
        #T_r     = (   w                *sqrt(     pow(x_r      -x_t    ,2.0)+pow(     y_r      -y_t    ,2.0))  (x_l      -x_t))/(x_ly_r-x_ry_l-x_ly_t+x_ty_l+x_ry_t-x_ty_r)
        Tension2 = (TotalWeight*math.sqrt(math.pow(xTangent2-xTarget,2)+math.pow(yTangent2-yTarget,2))*(xTangent1-xTarget))/TensionDenominator
        
        HorizontalTension=Tension1*(xTarget-xTangent1)/Chain1Straight
        
        #Calculation of horizontal component of tension for two chains should be equal, as validation step
        #HorizontalTension1=Tension1*(xTarget-xTangent1)/Chain1Straight
        #HorizontalTension2=Tension2*(xTangent2-xTarget)/Chain2Straight
        
        #Calculation of vertical force due to tension, to validate tension calculation
        #VerticalForce=Tension1*(yTangent1-yTarget)/Chain1Straight+Tension2*(yTangent2-yTarget)/Chain2Straight
        
        a1=HorizontalTension/self.chainWeight
        a2=HorizontalTension/self.chainWeight
        # print("Horizontal Tension ",HorizontalTension)
        
        #Catenary Equation
        Chain1=math.sqrt(math.pow(2*a1*math.sinh((xTarget-xTangent1)/(2*a1)),2)+math.pow(yTangent1-yTarget,2))
        Chain2=math.sqrt(math.pow(2*a2*math.sinh((xTangent2-xTarget)/(2*a2)),2)+math.pow(yTangent2-yTarget,2))
        CatenaryDelta1=Chain1-Chain1Straight
        CatenaryDelta2=Chain2-Chain2Straight
        # print("Catenary Delta 1 ",CatenaryDelta1)
        # print("Catenary Delta 2 ",CatenaryDelta2)
        
        #Calculate total chain lengths accounting for sprocket geometry and chain sag
        Chain1ElasticityDelta=Chain1-Chain1/(1+Tension1*self.chainElasticity)
        Chain2ElasticityDelta=Chain2-Chain2/(1+Tension2*self.chainElasticity)
        #print("Chain1 Elasticity Delta ",Chain1ElasticityDelta)
        #print("Chain2 Elasticity Delta ",Chain2ElasticityDelta)
        
        Chain1 = Chain1AroundSprocket + Chain1/(1.0+self.leftChainTolerance/100.0)/(1+Tension1*self.chainElasticity)
        Chain2 = Chain2AroundSprocket + Chain2/(1.0+self.rightChainTolerance/100.0)/(1+Tension2*self.chainElasticity)

        #Subtract of the virtual length which is added to the chain by the rotation mechanism
        Chain1 = Chain1 - self.rotationDiskRadius
        Chain2 = Chain2 - self.rotationDiskRadius
        
        return Chain1, Chain2
    
    def quadrilateralInverse(self, xTarget, yTarget):

        '''

        Take the XY position and return chain lengths.

        '''

        #Confirm that the coordinates are on the wood
        self._verifyValidTarget(xTarget, yTarget)

        #coordinate shift to put (0,0) in the center of the plywood from the left sprocket
        self.x = (self.D/2.0) + xTarget
        self.y = (self.machineHeight/2.0) + self.motorOffsetY  - yTarget

        #Coordinates definition:
        #         x -->, y |
        #                  v
        # (0,0) at center of left sprocket
        # upper left corner of plywood (270, 270)

        Tries = 0                                  #initialize
        if(self.x > self.D/2.0):                              #the right half of the board mirrors the left half so all computations are done  using left half coordinates.
          self.x = self.D-self.x                                  #Chain lengths are swapped at exit if the x,y is on the right half
          self.Mirror = True

        else:
            self.Mirror = False

        self.TanGamma = self.y/self.x
        self.TanLambda = self.y/(self.D-self.x)
        self.Y1Plus = self.R * math.sqrt(1 + self.TanGamma * self.TanGamma)
        self.Y2Plus = self.R * math.sqrt(1 + self.TanLambda * self.TanLambda)

        self._MyTrig()
        #self.Psi1 = self.Theta - self.Phi
        #self.Psi2 = self.Theta + self.Phi
                                                 #These criteria will be zero when the correct values are reached
                                                 #They are negated here as a numerical efficiency expedient

        self.Crit[0] = - self._moment(self.Y1Plus, self.Y2Plus, self.Phi, self.MySinPhi, self.SinPsi1, self.CosPsi1, self.SinPsi2, self.CosPsi2)
        self.Crit[1] = - self._YOffsetEqn(self.Y1Plus, self.x - self.h * self.CosPsi1, self.SinPsi1)
        self.Crit[2] = - self._YOffsetEqn(self.Y2Plus, self.D - (self.x + self.h * self.CosPsi2), self.SinPsi2)

        while (Tries <= self.MaxTries):
            if (abs(self.Crit[0]) < self.MaxError):
                if (abs(self.Crit[1]) < self.MaxError):
                    if (abs(self.Crit[2]) < self.MaxError):
                        break

                       #estimate the tilt angle that results in zero net _moment about the pen
                       #and refine the estimate until the error is acceptable or time runs out

                              #Estimate the Jacobian components

            self.Jac[0] = (self._moment( self.Y1Plus, self.Y2Plus,self.Phi + self.DeltaPhi, self.MySinPhiDelta, self.SinPsi1D, self.CosPsi1D, self.SinPsi2D, self.CosPsi2D) + self.Crit[0])/self.DeltaPhi
            self.Jac[1] = (self._moment( self.Y1Plus + self.DeltaY, self.Y2Plus, self.Phi, self.MySinPhi, self.SinPsi1, self.CosPsi1, self.SinPsi2, self.CosPsi2) + self.Crit[0])/self.DeltaY
            self.Jac[2] = (self._moment(self.Y1Plus, self.Y2Plus + self.DeltaY,  self.Phi, self.MySinPhi, self.SinPsi1, self.CosPsi1, self.SinPsi2, self.CosPsi2) + self.Crit[0])/self.DeltaY
            self.Jac[3] = (self._YOffsetEqn(self.Y1Plus, self.x - self.h * self.CosPsi1D, self.SinPsi1D) + self.Crit[1])/self.DeltaPhi
            self.Jac[4] = (self._YOffsetEqn(self.Y1Plus + self.DeltaY, self.x - self.h * self.CosPsi1,self.SinPsi1) + self.Crit[1])/self.DeltaY
            self.Jac[5] = 0.0
            self.Jac[6] = (self._YOffsetEqn(self.Y2Plus, self.D - (self.x + self.h * self.CosPsi2D), self.SinPsi2D) + self.Crit[2])/self.DeltaPhi
            self.Jac[7] = 0.0
            self.Jac[8] = (self._YOffsetEqn(self.Y2Plus + self.DeltaY, self.D - (self.x + self.h * self.CosPsi2D), self.SinPsi2) + self.Crit[2])/self.DeltaY


            #solve for the next guess

            buildOutJac  =  self._moment( self.Y1Plus + self.DeltaY, self.Y2Plus, self.Phi, self.MySinPhi, self.SinPsi1, self.CosPsi1, self.SinPsi2, self.CosPsi2) + self.Crit[0]


            self._MatSolv()     # solves the matrix equation Jx=-Criterion

            # update the variables with the new estimate


            self.Phi = self.Phi + self.Solution[0]
            self.Y1Plus = self.Y1Plus + self.Solution[1]                         #don't allow the anchor points to be inside a sprocket
            if (self.Y1Plus < self.R):
                self.Y1Plus = self.R

            self.Y2Plus = self.Y2Plus + self.Solution[2]                         #don't allow the anchor points to be inside a sprocke
            if (self.Y2Plus < self.R):
                self.Y2Plus = self.R


            self.Psi1 = self.Theta - self.Phi
            self.Psi2 = self.Theta + self.Phi

                                                                 #evaluate the
                                                                 #three criterion equations
            self._MyTrig()

            self.Crit[0] = - self._moment(self.Y1Plus, self.Y2Plus, self.Phi, self.MySinPhi, self.SinPsi1, self.CosPsi1, self.SinPsi2, self.CosPsi2)
            self.Crit[1] = - self._YOffsetEqn(self.Y1Plus, self.x - self.h * self.CosPsi1, self.SinPsi1)
            self.Crit[2] = - self._YOffsetEqn(self.Y2Plus, self.D - (self.x + self.h * self.CosPsi2), self.SinPsi2)
            Tries = Tries + 1                                       # increment itteration count


        if (Tries > self.MaxTries):
            print "unable to calculate chain lengths"

        #Variables are within accuracy limits
        #  perform output computation

        self.Offsetx1 = self.h * self.CosPsi1
        self.Offsetx2 = self.h * self.CosPsi2
        self.Offsety1 = self.h *  self.SinPsi1
        self.Offsety2 = self.h * self.SinPsi2
        self.TanGamma = (self.y - self.Offsety1 + self.Y1Plus)/(self.x - self.Offsetx1)
        self.TanLambda = (self.y - self.Offsety2 + self.Y2Plus)/(self.D -(self.x + self.Offsetx2))
        self.Gamma  = math.atan(self.TanGamma)
        self.Lambda = math.atan(self.TanLambda)

        #compute the chain lengths

        if(self.Mirror):
            Chain2 = math.sqrt((self.x - self.Offsetx1)*(self.x - self.Offsetx1) + (self.y + self.Y1Plus - self.Offsety1)*(self.y + self.Y1Plus - self.Offsety1)) - self.R * self.TanGamma + self.R * self.Gamma   #right chain length
            Chain1 = math.sqrt((self.D - (self.x + self.Offsetx2))*(self.D - (self.x + self.Offsetx2))+(self.y + self.Y2Plus - self.Offsety2)*(self.y + self.Y2Plus - self.Offsety2)) - self.R * self.TanLambda + self.R * self.Lambda   #left chain length
        else:
            Chain1 = math.sqrt((self.x - self.Offsetx1)*(self.x - self.Offsetx1) + (self.y + self.Y1Plus - self.Offsety1)*(self.y + self.Y1Plus - self.Offsety1)) - self.R * self.TanGamma + self.R * self.Gamma   #left chain length
            Chain2 = math.sqrt((self.D - (self.x + self.Offsetx2))*(self.D - (self.x + self.Offsetx2))+(self.y + self.Y2Plus - self.Offsety2)*(self.y + self.Y2Plus - self.Offsety2)) - self.R * self.TanLambda + self.R * self.Lambda   #right chain length



        aChainLength = Chain1
        bChainLength = Chain2
        #print 'target ({:.2f},{:.2f}) chains {:.3f},{:.3f} chain diff {:.3f} sled angle {:.4f} (degrees{:.4f})'.format(xTarget,yTarget,aChainLength, bChainLength, aChainLength - bChainLength, self.Phi, self.Phi*3.14159)

        return aChainLength, bChainLength

    def forward(self, chainALength, chainBLength):
        '''

        Take the chain lengths and return an XY position

        '''
        #print("Chain Sag Correction:")
        #print(self.chainSagCorrection)
        #print("")
        # apply any offsets for slipped links
        chainALength = chainALength + (self.chain1Offset * self.R)
        chainBLength = chainBLength + (self.chain2Offset * self.R)

        xGuess = -10
        yGuess = 10

        guessCount = 0

        while(1):


            #check our guess
            guessLengthA, guessLengthB = self.inverse(xGuess, yGuess)

            aChainError = chainALength - guessLengthA
            bChainError = chainBLength - guessLengthB

            #print 'guess {:7.3f} {:7.3f} error {:7.3f} {:7.3f} guesslength {:7.3f} {:7.3f} '.format(xGuess,yGuess,aChainError,bChainError,guessLengthA, guessLengthB)

            #if we've converged on the point...or it's time to give up, exit the loop
            if((abs(aChainError) < .000000001 and abs(bChainError) < .000000001) or guessCount > 5000):
                if(guessCount > 5000):
                    print "Message: Unable to find valid machine position. Please calibrate chain lengths.",aChainError,bChainError,xGuess,yGuess
                    return xGuess, yGuess
                else:
                    return xGuess, yGuess
            else:
                #adjust the guess based on the result
                xGuess = xGuess + .1*aChainError - .1*bChainError
                yGuess = yGuess - .1*aChainError - .1*bChainError
                guessCount = guessCount + 1

    def _MatSolv(self):
        Sum = 0
        NN = 0
        i = 0
        ii = 0
        J = 0
        JJ = 0
        K = 0
        KK = 0
        L = 0
        M = 0
        N = 0

        fact = 0

        b = 0
        while b < 5 :
            b = b + 1

        # gaus elimination, no pivot


        N = 3
        NN = N-1
        i = 1
        while (i<=NN):
            J = (N+1-i)
            JJ = (J-1) * N-1
            L = J-1
            KK = -1
            K = 0
            while (K<L):
                fact = self.Jac[KK+J]/self.Jac[JJ+J];
                M = 1
                while (M<=J):
                    self.Jac[KK + M]= self.Jac[KK + M] -fact * self.Jac[JJ+M]
                    M = M + 1
                KK = KK + N;
                self.Crit[K] = self.Crit[K] - fact * self.Crit[J-1];
                K = K + 1
            i = i + 1

    #Lower triangular matrix solver

        self.Solution[0] =  self.Crit[0]/self.Jac[0]
        ii = N-1

        i = 2
        while (i<=N):
            M = i -1;
            Sum = self.Crit[i-1];

            J = 1
            while (J<=M):
                Sum = Sum-self.Jac[ii+J]*self.Solution[J-1];
                J = J + 1

            self.Solution[i-1] = Sum/self.Jac[ii+i];
            ii = ii + N;

            i = i + 1

    def _moment(self, Y1Plus, Y2Plus, Phi, MSinPhi, MSinPsi1, MCosPsi1, MSinPsi2, MCosPsi2):   #computes net moment about center of mass
        '''Temp
        Offsetx1
        Offsetx2
        Offsety1
        Offsety2
        Psi1
        Psi2
        TanGamma
        TanLambda'''


        self.Psi1 = self.Theta - Phi
        self.Psi2 = self.Theta + Phi


        self.Offsetx1 = self.h * MCosPsi1
        self.Offsetx2 = self.h * MCosPsi2
        self.Offsety1 = self.h * MSinPsi1
        self.Offsety2 = self.h * MSinPsi2
        self.TanGamma = (self.y - self.Offsety1 + Y1Plus)/(self.x - self.Offsetx1)
        self.TanLambda = (self.y - self.Offsety2 + Y2Plus)/(self.D -(self.x + self.Offsetx2))

        return self.h3*MSinPhi + (self.h/(self.TanLambda+self.TanGamma))*(MSinPsi2 - MSinPsi1 + (self.TanGamma*MCosPsi1 - self.TanLambda * MCosPsi2))

    def _MyTrig(self):

        Phisq = self.Phi * self.Phi
        Phicu = self.Phi * Phisq
        Phidel = self.Phi + self.DeltaPhi
        Phidelsq = Phidel * Phidel
        Phidelcu = Phidel * Phidelsq
        Psi1sq = self.Psi1 * self.Psi1
        Psi1cu = Psi1sq * self.Psi1
        Psi2sq = self.Psi2 * self.Psi2
        Psi2cu = self.Psi2 * Psi2sq
        Psi1del = self.Psi1 - self.DeltaPhi
        Psi1delsq = Psi1del * Psi1del
        Psi1delcu = Psi1del * Psi1delsq
        Psi2del = self.Psi2 + self.DeltaPhi
        Psi2delsq = Psi2del * Psi2del
        Psi2delcu = Psi2del * Psi2delsq

        self.MySinPhi = -0.1616*Phicu - 0.0021*Phisq + 1.0002*self.Phi
        self.MySinPhiDelta = -0.1616*Phidelcu - 0.0021*Phidelsq + 1.0002*Phidel

        self.SinPsi1 = -0.0942*Psi1cu - 0.1368*Psi1sq + 1.0965*self.Psi1 - 0.0241#sinPsi1
        self.CosPsi1 = 0.1369*Psi1cu - 0.6799*Psi1sq + 0.1077*self.Psi1 + 0.9756#cosPsi1
        self.SinPsi2 = -0.1460*Psi2cu - 0.0197*Psi2sq + 1.0068*self.Psi2 - 0.0008#sinPsi2
        self.CosPsi2 = 0.0792*Psi2cu - 0.5559*Psi2sq + 0.0171*self.Psi2 + 0.9981#cosPsi2

        self.SinPsi1D = -0.0942*Psi1delcu - 0.1368*Psi1delsq + 1.0965*Psi1del - 0.0241#sinPsi1
        self.CosPsi1D = 0.1369*Psi1delcu - 0.6799*Psi1delsq + 0.1077*Psi1del + 0.9756#cosPsi1
        self.SinPsi2D = -0.1460*Psi2delcu - 0.0197*Psi2delsq + 1.0068*Psi2del - 0.0008#sinPsi2
        self.CosPsi2D = 0.0792*Psi2delcu - 0.5559*Psi2delsq + 0.0171*Psi2del +0.9981#cosPsi2

    def _YOffsetEqn(self, YPlus, Denominator, Psi):

        Temp = ((math.sqrt(YPlus * YPlus - self.R * self.R)/self.R) - (self.y + YPlus - self.h * math.sin(Psi))/Denominator)
        return Temp



