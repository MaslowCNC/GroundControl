class Kinematics():
    
    
    '''
    The Kinematics module relates the lengths of the chains to the position of the cutting head
    in X-Y space.
    '''
    
    
    
    def _verifyValidTarget(xTarget, yTarget):
        #If the target point is beyond one of the edges of the board, the machine stops at the edge
        
        if (xTarget < -machineWidth/2):
            xTarget = -machineWidth/2
        
        elif (xTarget >  machineWidth/2):
            xTarget =  machineWidth/2
        
        elif (yTarget >  machineHeight/2):
            yTarget =  machineHeight/2
        
        elif (yTarget <  -machineHeight/2):
            yTarget =  -machineHeight/2
    
    

'''
void Kinematics::recomputeGeometry(){
    /*
    Some variables are computed on class creation for the geometry of the machine to reduce overhead,
    calling this function regenerates those values.
    */
    h = sqrt((l/2)*(l/2) + s * s);
    Theta = atan(2*s/l);
    Psi1 = Theta - Phi;
    Psi2 = Theta + Phi;
}

void  Kinematics::inverse(float xTarget,float yTarget, float* aChainLength, float* bChainLength){
    
    //Confirm that the coordinates are on the wood
    _verifyValidTarget(&xTarget, &yTarget);
    
    //coordinate shift to put (0,0) in the center of the plywood from the left sprocket
    x = (D/2.0) + xTarget;
    y = (machineHeight/2.0) + motorOffsetY  - yTarget;
    
    //Coordinates definition:
    //         x -->, y |
    //                  v
    // (0,0) at center of left sprocket
    // upper left corner of plywood (270, 270)
    
    Tries = 0;                                  //initialize                   
    if(x > D/2.0){                              //the right half of the board mirrors the left half so all computations are done  using left half coordinates.
      x = D-x;                                  //Chain lengths are swapped at exit if the x,y is on the right half
      Mirror = true;
    }
    else{
        Mirror = false;
    }
    
    TanGamma = y/x;
    TanLambda = y/(D-x);
    Y1Plus = R * sqrt(1 + TanGamma * TanGamma);
    Y2Plus = R * sqrt(1 + TanLambda * TanLambda);
    Phi = -0.2 * (-8.202e-4 * x + 1.22) - 0.03;
  
    _MyTrig();
    Psi1 = Theta - Phi;
    Psi2 = Theta + Phi;
                                             //These criteria will be zero when the correct values are reached 
                                             //They are negated here as a numerical efficiency expedient
                                             
    Crit[0]=  - _moment(Y1Plus, Y2Plus, Phi, MySinPhi, SinPsi1, CosPsi1, SinPsi2, CosPsi2);
    Crit[1] = - _YOffsetEqn(Y1Plus, x - h * CosPsi1, SinPsi1);
    Crit[2] = - _YOffsetEqn(Y2Plus, D - (x + h * CosPsi2), SinPsi2);

  
    while (Tries <= MaxTries) {
        if (abs(Crit[0]) < MaxError) {
            if (abs(Crit[1]) < MaxError) {
                if (abs(Crit[2]) < MaxError){
                    break;
                }
            }
        } 
                  
                   //estimate the tilt angle that results in zero net _moment about the pen
                   //and refine the estimate until the error is acceptable or time runs out
    
                          //Estimate the Jacobian components 
                                                       
        Jac[0] = (_moment( Y1Plus, Y2Plus,Phi + DeltaPhi, MySinPhiDelta, SinPsi1D, CosPsi1D, SinPsi2D, CosPsi2D) + Crit[0])/DeltaPhi;
        Jac[1] = (_moment( Y1Plus + DeltaY, Y2Plus, Phi, MySinPhi, SinPsi1, CosPsi1, SinPsi2, CosPsi2) + Crit[0])/DeltaY;  
        Jac[2] = (_moment(Y1Plus, Y2Plus + DeltaY,  Phi, MySinPhi, SinPsi1, CosPsi1, SinPsi2, CosPsi2) + Crit[0])/DeltaY;
        Jac[3] = (_YOffsetEqn(Y1Plus, x - h * CosPsi1D, SinPsi1D) + Crit[1])/DeltaPhi;
        Jac[4] = (_YOffsetEqn(Y1Plus + DeltaY, x - h * CosPsi1,SinPsi1) + Crit[1])/DeltaY;
        Jac[5] = 0.0;
        Jac[6] = (_YOffsetEqn(Y2Plus, D - (x + h * CosPsi2D), SinPsi2D) + Crit[2])/DeltaPhi;
        Jac[7] = 0.0;
        Jac[8] = (_YOffsetEqn(Y2Plus + DeltaY, D - (x + h * CosPsi2D), SinPsi2) + Crit[2])/DeltaY;


        //solve for the next guess
        _MatSolv();     // solves the matrix equation Jx=-Criterion                                                     
                   
        // update the variables with the new estimate

        Phi = Phi + Solution[0];
        Y1Plus = Y1Plus + Solution[1];                         //don't allow the anchor points to be inside a sprocket
        if (Y1Plus < R){
            Y1Plus = R;                               
        }
        Y2Plus = Y2Plus + Solution[2];                         //don't allow the anchor points to be inside a sprocke
        if (Y2Plus < R){
            Y2Plus = R;
        }

        Psi1 = Theta - Phi;
        Psi2 = Theta + Phi;   
                                                             //evaluate the
                                                             //three criterion equations
    _MyTrig();
    
    Crit[0] = - _moment(Y1Plus, Y2Plus, Phi, MySinPhi, SinPsi1, CosPsi1, SinPsi2, CosPsi2);
    Crit[1] = - _YOffsetEqn(Y1Plus, x - h * CosPsi1, SinPsi1);
    Crit[2] = - _YOffsetEqn(Y2Plus, D - (x + h * CosPsi2), SinPsi2);
    Tries = Tries + 1;                                       // increment itteration count

    }                                       
  
    //Variables are within accuracy limits
    //  perform output computation

    Offsetx1 = h * CosPsi1;
    Offsetx2 = h * CosPsi2;
    Offsety1 = h *  SinPsi1;
    Offsety2 = h * SinPsi2;
    TanGamma = (y - Offsety1 + Y1Plus)/(x - Offsetx1);
    TanLambda = (y - Offsety2 + Y2Plus)/(D -(x + Offsetx2));
    Gamma = atan(TanGamma);
    Lambda =atan(TanLambda);

    //compute the chain lengths

    if(Mirror){
        Chain2 = sqrt((x - Offsetx1)*(x - Offsetx1) + (y + Y1Plus - Offsety1)*(y + Y1Plus - Offsety1)) - R * TanGamma + R * Gamma;   //right chain length                       
        Chain1 = sqrt((D - (x + Offsetx2))*(D - (x + Offsetx2))+(y + Y2Plus - Offsety2)*(y + Y2Plus - Offsety2)) - R * TanLambda + R * Lambda;   //left chain length
    }
    else{
        Chain1 = sqrt((x - Offsetx1)*(x - Offsetx1) + (y + Y1Plus - Offsety1)*(y + Y1Plus - Offsety1)) - R * TanGamma + R * Gamma;   //left chain length                       
        Chain2 = sqrt((D - (x + Offsetx2))*(D - (x + Offsetx2))+(y + Y2Plus - Offsety2)*(y + Y2Plus - Offsety2)) - R * TanLambda + R * Lambda;   //right chain length
    }
    
    *aChainLength = Chain1;
    *bChainLength = Chain2;

}

void  Kinematics::forward(float chainALength, float chainBLength, float* xPos, float* yPos){
    
    float xGuess = 0;
    float yGuess = 0;
    
    float guessLengthA;
    float guessLengthB;
    
    int guessCount = 0;
    
    while(1){
        
        
        //check our guess
        inverse(xGuess, yGuess, &guessLengthA, &guessLengthB);
        
        float aChainError = chainALength - guessLengthA;
        float bChainError = chainBLength - guessLengthB;
        
        
        //adjust the guess based on the result
        xGuess = xGuess + .1*aChainError - .1*bChainError;
        yGuess = yGuess - .1*aChainError - .1*bChainError;
        
        guessCount++;
        
        //Prevent the connection from timing out
        Serial.print("[PosError:");
        Serial.print(aChainError);
        Serial.print(',');
        Serial.print(bChainError);
        Serial.print(',');
        Serial.print('0');
        Serial.println("]");
        
        //if we've converged on the point...or it's time to give up, exit the loop
        if((abs(aChainError) < .1 && abs(bChainError) < .1) or guessCount > 100){
            if(guessCount > 100){
                Serial.println("Message: Unable to find valid machine position. Please calibrate chain lengths.");
                *xPos = 0;
                *yPos = 0;
            }
            else{
                *xPos = xGuess;
                *yPos = yGuess;
            }
            break;
        }
    }
}

void  Kinematics::_MatSolv(){
    float Sum;
    int NN;
    int i;
    int ii;
    int J;
    int JJ;
    int K;
    int KK;
    int L;
    int M;
    int N;

    float fact;

    // gaus elimination, no pivot

    N = 3;
    NN = N-1;
    for (i=1;i<=NN;i++){
        J = (N+1-i);
        JJ = (J-1) * N-1;
        L = J-1;
        KK = -1;
        for (K=0;K<L;K++){
            fact = Jac[KK+J]/Jac[JJ+J];
            for (M=1;M<=J;M++){
                Jac[KK + M]= Jac[KK + M] -fact * Jac[JJ+M];
            }
        KK = KK + N;      
        Crit[K] = Crit[K] - fact * Crit[J-1];
        }
    }

#Lower triangular matrix solver

    Solution[0] =  Crit[0]/Jac[0];
    ii = N-1;
    for (i=2;i<=N;i++){
        M = i -1;
        Sum = Crit[i-1];
        for (J=1;J<=M;J++){
            Sum = Sum-Jac[ii+J]*Solution[J-1]; 
        }
    Solution[i-1] = Sum/Jac[ii+i];
    ii = ii + N;
    }
}

float Kinematics::_moment(float Y1Plus, float Y2Plus, float Phi, float MSinPhi, float MSinPsi1, float MCosPsi1, float MSinPsi2, float MCosPsi2){   //computes net moment about center of mass
    float Temp;
    float Offsetx1;
    float Offsetx2;
    float Offsety1;
    float Offsety2;
    float Psi1;
    float Psi2;
    float TanGamma;
    float TanLambda;

    Psi1 = Theta - Phi;
    Psi2 = Theta + Phi;
    
    Offsetx1 = h * MCosPsi1;
    Offsetx2 = h * MCosPsi2;
    Offsety1 = h * MSinPsi1;
    Offsety2 = h * MSinPsi2;
    TanGamma = (y - Offsety1 + Y1Plus)/(x - Offsetx1);
    TanLambda = (y - Offsety2 + Y2Plus)/(D -(x + Offsetx2));
    
    return h3*MSinPhi + (h/(TanLambda+TanGamma))*(MSinPsi2 - MSinPsi1 + (TanGamma*MCosPsi1 - TanLambda * MCosPsi2));   
}

void Kinematics::_MyTrig(){
    float Phisq = Phi * Phi;
    float Phicu = Phi * Phisq;
    float Phidel = Phi + DeltaPhi;
    float Phidelsq = Phidel * Phidel;
    float Phidelcu = Phidel * Phidelsq;
    float Psi1sq = Psi1 * Psi1;
    float Psi1cu = Psi1sq * Psi1;
    float Psi2sq = Psi2 * Psi2;
    float Psi2cu = Psi2 * Psi2sq;
    float Psi1del = Psi1 - DeltaPhi;
    float Psi1delsq = Psi1del * Psi1del;
    float Psi1delcu = Psi1del * Psi1delsq;
    float Psi2del = Psi2 + DeltaPhi;
    float Psi2delsq = Psi2del * Psi2del;
    float Psi2delcu = Psi2del * Psi2delsq;
  
    // Phirange is 0 to -27 degrees
    // sin -0.1616   -0.0021    1.0002   -0.0000 (error < 6e-6) 
    // cos(phi): 0.0388   -0.5117    0.0012    1.0000 (error < 3e-5)
    // Psi1 range is 42 to  69 degrees, 
    // sin(Psi1):  -0.0942   -0.1368    1.0965   -0.0241 (error < 2.5 e-5)
    // cos(Psi1):  0.1369   -0.6799    0.1077    0.9756  (error < 1.75e-5)
    // Psi2 range is 15 to 42 degrees 
    // sin(Psi2): -0.1460   -0.0197    1.0068   -0.0008 (error < 1.5e-5)
    // cos(Psi2):  0.0792   -0.5559    0.0171    0.9981 (error < 2.5e-5)

    MySinPhi = -0.1616*Phicu - 0.0021*Phisq + 1.0002*Phi;
    MySinPhiDelta = -0.1616*Phidelcu - 0.0021*Phidelsq + 1.0002*Phidel;

    SinPsi1 = -0.0942*Psi1cu - 0.1368*Psi1sq + 1.0965*Psi1 - 0.0241;//sinPsi1
    CosPsi1 = 0.1369*Psi1cu - 0.6799*Psi1sq + 0.1077*Psi1 + 0.9756;//cosPsi1
    SinPsi2 = -0.1460*Psi2cu - 0.0197*Psi2sq + 1.0068*Psi2 - 0.0008;//sinPsi2
    CosPsi2 = 0.0792*Psi2cu - 0.5559*Psi2sq + 0.0171*Psi2 + 0.9981;//cosPsi2

    SinPsi1D = -0.0942*Psi1delcu - 0.1368*Psi1delsq + 1.0965*Psi1del - 0.0241;//sinPsi1
    CosPsi1D = 0.1369*Psi1delcu - 0.6799*Psi1delsq + 0.1077*Psi1del + 0.9756;//cosPsi1
    SinPsi2D = -0.1460*Psi2delcu - 0.0197*Psi2delsq + 1.0068*Psi2del - 0.0008;//sinPsi2
    CosPsi2D = 0.0792*Psi2delcu - 0.5559*Psi2delsq + 0.0171*Psi2del +0.9981;//cosPsi2

}

def_YOffsetEqn(YPlus, float Denominator, float Psi):
    float Temp;
    Temp = ((sqrt(YPlus * YPlus - R * R)/R) - (y + YPlus - h * sin(Psi))/Denominator);
    return Temp;

'''