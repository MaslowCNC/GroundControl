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
        self.h = math.sqrt((self.l/2)*(self.l/2) + self.s * self.s)
        self.Theta = math.atan(2*self.s/self.l)
        self.Psi1 = self.Theta - self.Phi
        self.Psi2 = self.Theta + self.Phi
    
    def inverse(self, xTarget, yTarget):
        
        '''
        
        Take the XY position and return chain lengths.
        
        '''
        
        #Confirm that the coordinates are on the wood
        self._verifyValidTarget(xTarget, yTarget)
        
        #coordinate shift to put (0,0) in the center of the plywood from the left sprocket
        self.x = (self.D/2.0) + xTarget
        self.y = (self.machineHeight/2.0) + self.motorOffsetY  - yTarget
        
        #print "begin inverse: "
        #print "x: " + str(self.x)
        #print "y: " + str(self.y)
        
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
        
        #print "after mirror: "
        #print "Mirror: " + str(self.Mirror)
        #print "x: " + str(self.x)
        
        self.TanGamma = self.y/self.x
        self.TanLambda = self.y/(self.D-self.x)
        self.Y1Plus = self.R * math.sqrt(1 + self.TanGamma * self.TanGamma)
        self.Y2Plus = self.R * math.sqrt(1 + self.TanLambda * self.TanLambda)
        #self.Phi = -0.2 * (-8.202e-4 * x + 1.22) - 0.03
        
        #print "after TanGamma thing: "
        #print "self.TanGamma " + str(self.TanGamma)
        #print "self.TanLambda " + str(self.TanLambda)
        #print "self.Y1Plus " + str(self.Y1Plus)
        #print "self.Y2Plus " + str(self.Y2Plus)
        
        self._MyTrig()
        #self.Psi1 = self.Theta - self.Phi
        #self.Psi2 = self.Theta + self.Phi
                                                 #These criteria will be zero when the correct values are reached 
                                                 #They are negated here as a numerical efficiency expedient
                                                 
        self.Crit[0] = - self._moment(self.Y1Plus, self.Y2Plus, self.Phi, self.MySinPhi, self.SinPsi1, self.CosPsi1, self.SinPsi2, self.CosPsi2)
        self.Crit[1] = - self._YOffsetEqn(self.Y1Plus, self.x - self.h * self.CosPsi1, self.SinPsi1)
        self.Crit[2] = - self._YOffsetEqn(self.Y2Plus, self.D - (self.x + self.h * self.CosPsi2), self.SinPsi2)
        
        
        #print "\n\n block zebra: "
        #print "self.Crit[0] " + str(self.Crit[0]*1000)
        #print "self.Crit[1] " + str(self.Crit[1]*1000)
        #print "self.Crit[2] " + str(self.Crit[2]*1000)
      
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
            
            #print "\n\n++++++++++++++++++++++++++++++++++"
            #print "build out Jac[1]: " + str(buildOutJac*1000.0)
            #print "Crit[0] " + str(self.Crit[0]*1000)
            #print "self.Jac[0] " + str(self.Jac[0]*1000.0)
            #print "self.Jac[1] " + str(self.Jac[1]*1000.0)
            #print "self.Jac[2] " + str(self.Jac[2]*1000.0)
            #print "self.Jac[3] " + str(self.Jac[3]*1000.0)
            #print "self.Jac[4] " + str(self.Jac[4]*1000.0)
            #print "self.Jac[5] " + str(self.Jac[5]*1000.0)
            #print "self.Jac[6] " + str(self.Jac[6]*1000.0)
            #print "self.Jac[7] " + str(self.Jac[7]*1000.0)
            #print "self.Jac[8] " + str(self.Jac[8]*1000.0)
            
            self._MatSolv()     # solves the matrix equation Jx=-Criterion                                                     
                       
            # update the variables with the new estimate
            
            #print "\n\n@@@@@@@@@@@@@@@@@@@@@"
            
            self.Phi = self.Phi + self.Solution[0]
            self.Y1Plus = self.Y1Plus + self.Solution[1]                         #don't allow the anchor points to be inside a sprocket
            if (self.Y1Plus < self.R):
                self.Y1Plus = self.R                               
            
            self.Y2Plus = self.Y2Plus + self.Solution[2]                         #don't allow the anchor points to be inside a sprocke
            if (self.Y2Plus < self.R):
                self.Y2Plus = self.R
            

            self.Psi1 = self.Theta - self.Phi
            self.Psi2 = self.Theta + self.Phi
            
            #print "self.Phi " + str(self.Phi*1000.0)
            #print "self.Y1Plus " + str(self.Y1Plus*1000.0)
            #print "self.Y2Plus " + str(self.Y2Plus*1000.0)
            #print "self.Psi1 " + str(self.Psi1*1000.0)
            #print "self.Psi2 " + str(self.Psi2*1000.0)
                                                                 #evaluate the
                                                                 #three criterion equations
            self._MyTrig()
            
            self.Crit[0] = - self._moment(self.Y1Plus, self.Y2Plus, self.Phi, self.MySinPhi, self.SinPsi1, self.CosPsi1, self.SinPsi2, self.CosPsi2)
            self.Crit[1] = - self._YOffsetEqn(self.Y1Plus, self.x - self.h * self.CosPsi1, self.SinPsi1)
            self.Crit[2] = - self._YOffsetEqn(self.Y2Plus, self.D - (self.x + self.h * self.CosPsi2), self.SinPsi2)
            Tries = Tries + 1                                       # increment itteration count

          
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
            
            
            print "\n\n++++++++++++++"
            print "Returning Lengths: "
            print "Chain1: " + str(Chain1)
            print "Chain2: " + str(Chain2)
            print "self.Gamma: " + str(self.Gamma)
            print "self.Lambda: " + str(self.Lambda)
            
            aChainLength = Chain1
            bChainLength = Chain2
            
            return aChainLength, bChainLength

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
                    print "Message: Unable to find valid machine position. Please calibrate chain lengths."
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
        
        #print "test loop"
        b = 0
        while b < 5 :
            #print b
            b = b + 1
        #print b
        
        # gaus elimination, no pivot
        
        #print "\n\ngaus elimination"
        #print "Jac: "
        #print self.Jac[0]
        
        #print("Crits at begin: ")
        #print "self.Crit[0] " + str(self.Crit[0]*1000)
        #print "self.Crit[1] " + str(self.Crit[1]*1000)
        #print "self.Crit[2] " + str(self.Crit[2]*1000)
        
        N = 3
        NN = N-1
        i = 1
        while (i<=NN):
            #print "for loop #1";
            #print "i = " + str(i)
            J = (N+1-i)
            JJ = (J-1) * N-1
            L = J-1
            KK = -1
            K = 0
            while (K<L):
                #print "for loop #2"
                #print "K = " + str(K)
                fact = self.Jac[KK+J]/self.Jac[JJ+J];
                M = 1
                while (M<=J):
                    #print "for loop #3"
                    #print "M = " + str(M)
                    self.Jac[KK + M]= self.Jac[KK + M] -fact * self.Jac[JJ+M]
                    M = M + 1
                KK = KK + N;
                self.Crit[K] = self.Crit[K] - fact * self.Crit[J-1];
                K = K + 1
            i = i + 1

    #Lower triangular matrix solver
        
        #print "\n\nLower triangular matrix solver";
        
        self.Solution[0] =  self.Crit[0]/self.Jac[0]
        ii = N-1
        
        #print "self.Solution[0] " + str(self.Solution[0]*1000)
        #print "self.Crit[0] " + str(self.Crit[0]*1000)
        #print "self.Crit[1] " + str(self.Crit[1]*1000)
        #print "self.Crit[2] " + str(self.Crit[2]*1000)
        #print "ii " + str(ii)
        #print "N " + str(N)
        
        i = 2
        while (i<=N):
            #print "Loop #1"
            #print "i = " + str(i)
            M = i -1;
            Sum = self.Crit[i-1];
            
            J = 1
            while (J<=M):
                #print "loop #2"
                #print "J = " + str(J)
                Sum = Sum-self.Jac[ii+J]*self.Solution[J-1];
                #print "Sum = " + str(Sum*1000)
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
        
        #print "\n begin _moment"
        
        #print "Called with:"
        #print "Y1Plus " + str(Y1Plus*1000)
        #print "Y2Plus " + str(Y2Plus*1000)
        #print "Phi " + str(Phi*1000)
        #print "MSinPhi " + str(MSinPhi*1000)
        #print "MSinPsi1 " + str(MSinPsi1*1000)
        #print "MCosPsi1 " + str(MCosPsi1*1000)
        #print "MSinPsi2 " + str(MSinPsi2*1000)
        #print "MCosPsi2 " + str(MCosPsi2*1000)
        
        self.Psi1 = self.Theta - Phi
        self.Psi2 = self.Theta + Phi
        
        #print "internal variables"
        #print "self.Psi1 " + str(self.Psi1*1000)
        #print "self.Psi2 " + str(self.Psi2*1000)
        
        
        #print "--->Y1Plus " + str(Y1Plus*1000)
        
        self.Offsetx1 = self.h * MCosPsi1
        self.Offsetx2 = self.h * MCosPsi2
        self.Offsety1 = self.h * MSinPsi1
        self.Offsety2 = self.h * MSinPsi2
        self.TanGamma = (self.y - self.Offsety1 + Y1Plus)/(self.x - self.Offsetx1)
        self.TanLambda = (self.y - self.Offsety2 + Y2Plus)/(self.D -(self.x + self.Offsetx2))
        
        #print "--->Y1Plus " + str(Y1Plus*1000)
        
        #print "self.x " + str(self.x)
        #print "self.y " + str(self.y)
        #print "--->Y1Plus " + str(Y1Plus*1000)
        #print "Y1Plus " + str(Y1Plus*1000)
        
        #print "self.Offsetx1 " + str(self.Offsetx1*1000)
        #print "self.Offsetx2 " + str(self.Offsetx2*1000)
        #print "self.Offsety1 " + str(self.Offsety1*1000)
        #print "self.Offsety2 " + str(self.Offsety2*1000)
        #print "TanGamma " + str(self.TanGamma*1000)
        #print "TanLambda " + str(self.TanLambda*1000)
        
        #print "\n\n\n moment buildout:"
        #print (self.h3*MSinPhi)*1000 #(MSinPsi2 - MSinPsi1 +(self.TanGamma*MCosPsi1 - self.TanLambda * MCosPsi2))*10000.0
        
        #print "Moment returns: "
        #print (self.h3*MSinPhi + (self.h/(self.TanLambda+self.TanGamma))*(MSinPsi2 - MSinPsi1 + (self.TanGamma*MCosPsi1 - self.TanLambda * MCosPsi2)))*1000.0
        
        return self.h3*MSinPhi + (self.h/(self.TanLambda+self.TanGamma))*(MSinPsi2 - MSinPsi1 + (self.TanGamma*MCosPsi1 - self.TanLambda * MCosPsi2))   

    def _MyTrig(self):
        
        #print "\n\nbegin my trig: "
        
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
        
        #print "Phisq " + str(Phisq*1000.0)
        #print "Phicu " + str(Phicu*1000.0)
        #print "Phidel " + str(Phidel*1000.0)
        #print "Phidelsq " + str(Phidelsq*1000.0)
        #print "Phidelcu " + str(Phidelcu*1000.0)
        #print "Psi1sq " + str(Psi1sq*1000.0)
        #print "Psi1cu " + str(Psi1cu*1000.0)
        #print "Psi2sq " + str(Psi2sq*1000.0)
        #print "Psi2cu " + str(Psi2cu*1000.0)
        #print "Psi1del " + str(Psi1del*1000.0)
        #print "Psi1delsq " + str(Psi1delsq*1000.0)
        #print "Psi1delcu " + str(Psi1delcu*1000.0)
        #print "Psi2del " + str(Psi2del*1000.0)
        #print "Psi2delsq " + str(Psi2delsq*1000.0)
        #print "Psi2delcu " + str(Psi2delcu*1000.0)
        #print "\n\n\n"
        
        # Phirange is 0 to -27 degrees
        # sin -0.1616   -0.0021    1.0002   -0.0000 (error < 6e-6) 
        # cos(phi): 0.0388   -0.5117    0.0012    1.0000 (error < 3e-5)
        # Psi1 range is 42 to  69 degrees, 
        # sin(Psi1):  -0.0942   -0.1368    1.0965   -0.0241 (error < 2.5 e-5)
        # cos(Psi1):  0.1369   -0.6799    0.1077    0.9756  (error < 1.75e-5)
        # Psi2 range is 15 to 42 degrees 
        # sin(Psi2): -0.1460   -0.0197    1.0068   -0.0008 (error < 1.5e-5)
        # cos(Psi2):  0.0792   -0.5559    0.0171    0.9981 (error < 2.5e-5)

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
        
        #print "block 2"
        #print "self.MySinPhi " + str(self.MySinPhi*1000)
        #print "self.MySinPhiDelta " + str(self.MySinPhiDelta*1000)
        #print "self.SinPsi1 " + str(self.SinPsi1*1000)
        #print "self.CosPsi1 " + str(self.CosPsi1*1000)
        #print "self.SinPsi2 " + str(self.SinPsi2*1000)
        #print "self.CosPsi2 " + str(self.CosPsi2*1000)
        #print "self.SinPsi1D " + str(self.SinPsi1D*1000)
        #print "self.CosPsi1D " + str(self.CosPsi1D*1000)
        #print "self.SinPsi2D " + str(self.SinPsi2D*1000)
        #print "self.CosPsi2D " + str(self.CosPsi2D*1000)
        
    def _YOffsetEqn(self, YPlus, Denominator, Psi):
        
        Temp = ((math.sqrt(YPlus * YPlus - self.R * self.R)/self.R) - (self.y + YPlus - self.h * math.sin(Psi))/Denominator)
        return Temp

    