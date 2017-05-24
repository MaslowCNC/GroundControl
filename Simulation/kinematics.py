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
    
    x = 2708.4
    y = 270

    #utility variables
    DegPerRad = 360/(4 * math.atan(1))
    Time = 0
    Mirror = 0

    #Calculation tolerances
    MaxError = 0.001
    MaxTries = 10
    DeltaPhi = 0.001
    DeltaY = 0.01

    #Criterion Computation Variables
    Phi = -0.2
    TanGamma = 0
    TanLambda= 0
    Y1Plus = 0
    Y2Plus = 0
    Theta = math.atan(2*s/l)
    Psi1 = Theta - Phi
    Psi2 = Theta + Phi
    Tries = 0
    Jac=[0,0,0,0,0,0,0,0,0,0]
    Solution=[]
    Crit=[0,0,0]
    Offsetx1 = 0
    Offsetx2 = 0
    Offsety1 = 0
    Offsety2 = 0
    SinPsi1 = 0
    CosPsi1 = 0
    SinPsi2 = 0
    CosPsi2 = 0
    SinPsi1D = 0
    CosPsi1D = 0
    SinPsi2D = 0
    CosPsi2D = 0
    MySinPhi = 0
    MySinPhiDelta = 0

    #intermediate output
    Lambda = 0
    Gamma = 0

    # output = chain lengths measured from 12 o'clock
    Chain1  = 0#left chain length 
    Chain2  = 0#right chain length

    i = 0
    
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
        h = sqrt((l/2)*(l/2) + s * s)
        Theta = atan(2*s/l)
        Psi1 = Theta - Phi
        Psi2 = Theta + Phi
    
    def inverse(self, xTarget, yTarget):
        
        '''
        
        Take the XY position and return chain lengths.
        
        '''
        
        #Confirm that the coordinates are on the wood
        self._verifyValidTarget(xTarget, yTarget)
        
        #coordinate shift to put (0,0) in the center of the plywood from the left sprocket
        x = (self.D/2.0) + xTarget
        y = (self.machineHeight/2.0) + self.motorOffsetY  - yTarget
        
        #Coordinates definition:
        #         x -->, y |
        #                  v
        # (0,0) at center of left sprocket
        # upper left corner of plywood (270, 270)
        
        Tries = 0                                  #initialize                   
        if(x > self.D/2.0):                              #the right half of the board mirrors the left half so all computations are done  using left half coordinates.
          x = self.D-x                                  #Chain lengths are swapped at exit if the x,y is on the right half
          self.Mirror = True
        
        else:
            self.Mirror = False
        
        
        self.TanGamma = y/x
        self.TanLambda = y/(self.D-x)
        self.Y1Plus = self.R * math.sqrt(1 + self.TanGamma * self.TanGamma)
        self.Y2Plus = self.R * math.sqrt(1 + self.TanLambda * self.TanLambda)
        self.Phi = -0.2 * (-8.202e-4 * x + 1.22) - 0.03
      
        self._MyTrig()
        self.Psi1 = self.Theta - self.Phi
        self.Psi2 = self.Theta + self.Phi
                                                 #These criteria will be zero when the correct values are reached 
                                                 #They are negated here as a numerical efficiency expedient
                                                 
        self.Crit[0] = - self._moment(self.Y1Plus, self.Y2Plus, self.Phi, self.MySinPhi, self.SinPsi1, self.CosPsi1, self.SinPsi2, self.CosPsi2)
        self.Crit[1] = - self._YOffsetEqn(self.Y1Plus, x - self.h * self.CosPsi1, self.SinPsi1)
        self.Crit[2] = - self._YOffsetEqn(self.Y2Plus, self.D - (x + self.h * self.CosPsi2), self.SinPsi2)

      
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
        
        Crit[0] = - _moment(Y1Plus, Y2Plus, Phi, MySinPhi, SinPsi1, CosPsi1, SinPsi2, CosPsi2)
        Crit[1] = - _YOffsetEqn(Y1Plus, x - h * CosPsi1, SinPsi1)
        Crit[2] = - _YOffsetEqn(Y2Plus, D - (x + h * CosPsi2), SinPsi2)
        Tries = Tries + 1                                       # increment itteration count

      
        #Variables are within accuracy limits
        #  perform output computation

        self.Offsetx1 = self.h * self.CosPsi1
        self.Offsetx2 = self.h * self.CosPsi2
        self.Offsety1 = self.h *  self.SinPsi1
        self.Offsety2 = self.h * self.SinPsi2
        self.TanGamma = (y - Offsety1 + Y1Plus)/(x - Offsetx1)
        self.TanLambda = (y - Offsety2 + Y2Plus)/(D -(x + Offsetx2))
        self.Gamma = atan(TanGamma)
        self.Lambda =atan(TanLambda)

        #compute the chain lengths

        if(Mirror):
            Chain2 = sqrt((x - Offsetx1)*(x - Offsetx1) + (y + Y1Plus - Offsety1)*(y + Y1Plus - Offsety1)) - R * TanGamma + R * Gamma   #right chain length                       
            Chain1 = sqrt((D - (x + Offsetx2))*(D - (x + Offsetx2))+(y + Y2Plus - Offsety2)*(y + Y2Plus - Offsety2)) - R * TanLambda + R * Lambda   #left chain length
        else:
            Chain1 = sqrt((x - Offsetx1)*(x - Offsetx1) + (y + Y1Plus - Offsety1)*(y + Y1Plus - Offsety1)) - R * TanGamma + R * Gamma   #left chain length                       
            Chain2 = sqrt((D - (x + Offsetx2))*(D - (x + Offsetx2))+(y + Y2Plus - Offsety2)*(y + Y2Plus - Offsety2)) - R * TanLambda + R * Lambda   #right chain length
        
        
        aChainLength = Chain1
        bChainLength = Chain2

    def forward(self, chainALength, chainBLength):
        '''
        
        Take the chain lengths and return an XY position
        
        '''
        xGuess = 0
        yGuess = 0
        
        guessLengthA
        guessLengthB
        
        guessCount = 0
        
        while(1):
            
            
            #check our guess
            inverse(xGuess, yGuess, guessLengthA, guessLengthB)
            
            aChainError = chainALength - guessLengthA
            bChainError = chainBLength - guessLengthB
            
            
            #adjust the guess based on the result
            xGuess = xGuess + .1*aChainError - .1*bChainError
            yGuess = yGuess - .1*aChainError - .1*bChainError
            
            guessCount = guessCount + 1
            
            
            #if we've converged on the point...or it's time to give up, exit the loop
            if((abs(aChainError) < .1 and abs(bChainError) < .1) or guessCount > 100):
                if(guessCount > 100):
                    Serial.println("Message: Unable to find valid machine position. Please calibrate chain lengths.")
                    xPos = 0
                    yPos = 0
                else:
                    xPos = xGuess
                    yPos = yGuess
                break

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

        # gaus elimination, no pivot

        N = 3
        NN = N-1
        i=1
        while (i<=NN):
            J = (N+1-i)
            JJ = (J-1) * N-1
            L = J-1
            KK = -1
            K=0
            while (K<L):
                fact = self.Jac[KK+J]/self.Jac[JJ+J]
                M = 1
                while (M<=J):
                    self.Jac[KK + M]= self.Jac[KK + M] -fact * self.Jac[JJ+M]
                    M = M + 1
                K = K + 1
            KK = KK + N      
            self.Crit[K] = self.Crit[K] - fact * self.Crit[J-1]
            i = i + 1

    #Lower triangular matrix solver

        Solution[0] =  self.Crit[0]/self.Jac[0]
        ii = N-1
        i=2
        while (i<=N):
            M = i -1
            Sum = Crit[i-1]
            J=1
            while (J<=M):
                Sum = Sum-Jac[ii+J]*Solution[J-1]
                J = J + 1
            i = i + 1
        Solution[i-1] = Sum/self.Jac[ii+i]
        ii = ii + N
    
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

        self.Psi1 = self.Theta - self.Phi
        self.Psi2 = self.Theta + self.Phi
        
        self.Offsetx1 = self.h * MCosPsi1
        self.Offsetx2 = self.h * MCosPsi2
        self.Offsety1 = self.h * MSinPsi1
        self.Offsety2 = self.h * MSinPsi2
        TanGamma = (self.y - self.Offsety1 + self.Y1Plus)/(self.x - self.Offsetx1)
        TanLambda = (self.y - self.Offsety2 + self.Y2Plus)/(self.D -(self.x + self.Offsetx2))
        
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
      
        # Phirange is 0 to -27 degrees
        # sin -0.1616   -0.0021    1.0002   -0.0000 (error < 6e-6) 
        # cos(phi): 0.0388   -0.5117    0.0012    1.0000 (error < 3e-5)
        # Psi1 range is 42 to  69 degrees, 
        # sin(Psi1):  -0.0942   -0.1368    1.0965   -0.0241 (error < 2.5 e-5)
        # cos(Psi1):  0.1369   -0.6799    0.1077    0.9756  (error < 1.75e-5)
        # Psi2 range is 15 to 42 degrees 
        # sin(Psi2): -0.1460   -0.0197    1.0068   -0.0008 (error < 1.5e-5)
        # cos(Psi2):  0.0792   -0.5559    0.0171    0.9981 (error < 2.5e-5)

        MySinPhi = -0.1616*Phicu - 0.0021*Phisq + 1.0002*self.Phi
        MySinPhiDelta = -0.1616*Phidelcu - 0.0021*Phidelsq + 1.0002*Phidel

        SinPsi1 = -0.0942*Psi1cu - 0.1368*Psi1sq + 1.0965*self.Psi1 - 0.0241#sinPsi1
        CosPsi1 = 0.1369*Psi1cu - 0.6799*Psi1sq + 0.1077*self.Psi1 + 0.9756#cosPsi1
        SinPsi2 = -0.1460*Psi2cu - 0.0197*Psi2sq + 1.0068*self.Psi2 - 0.0008#sinPsi2
        CosPsi2 = 0.0792*Psi2cu - 0.5559*Psi2sq + 0.0171*self.Psi2 + 0.9981#cosPsi2

        SinPsi1D = -0.0942*Psi1delcu - 0.1368*Psi1delsq + 1.0965*Psi1del - 0.0241#sinPsi1
        CosPsi1D = 0.1369*Psi1delcu - 0.6799*Psi1delsq + 0.1077*Psi1del + 0.9756#cosPsi1
        SinPsi2D = -0.1460*Psi2delcu - 0.0197*Psi2delsq + 1.0068*Psi2del - 0.0008#sinPsi2
        CosPsi2D = 0.0792*Psi2delcu - 0.5559*Psi2delsq + 0.0171*Psi2del +0.9981#cosPsi2

    def _YOffsetEqn(self, YPlus, Denominator, Psi):
        
        Temp = ((math.sqrt(YPlus * YPlus - self.R * self.R)/self.R) - (self.y + YPlus - self.h * math.sin(Psi))/Denominator)
        return Temp

    