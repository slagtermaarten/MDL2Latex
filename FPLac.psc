Modelname: FP + lac_stochastic
Description: Fusion protein + Stamatakis and Mantzaris (2009) Lac operon, propensities as in original paper

#UnitSubstance: mole, 1, 0, 1
#UnitVolume: litre, 1, 0, 1
#UnitTime: second, 1, 0, 1
#UnitLength: metre, 1, 0, 1
#UnitArea: metre, 1, 0, 2

# Reactions
R1:
    $pool > MR
    VEcoli * Na * ksMR

R2:
    MR > MR + R
    ksR * MR

R3:
    {2}R > R2
    (k2R)/(VEcoli * Na) * R * (R-1)
    
R4:
    R2 > {2}R
    k2Rb * R2

R5:
    R2 + O > R2O
    (kr)/(VEcoli * Na) * R2 * O

R6:
    R2O > {2}R+O
    krb * R2O

R7:
    {2}I + R2> I2R2
    (kdr1)/(VEcoli * Na * VEcoli * Na) * R2 * I * (I-1)

R8:
    I2R2 + O > {2}I + R2O
    kdr1b * I2R2

R9:
    {2}I + R2O > I2R2 + O
    (kdr2)/(VEcoli * Na * VEcoli * Na) * R2O * I * (I-1)
    
R10:
    I2R2 + O > {2}I + R2O
    (kdr2b)/(VEcoli * Na) * I2R2 *O

R11:
    O > O + MY
    ks1MY * O

R12:
    R2O > R2O + MY
    ks0MY * R2O
# Mistake in the original paper? TURNS OUT YES!
R13:
    MY > MY + Y
    ksY * MY

R14:
    Y + Iex > YIex
    kp * Iex * Y

R15:
    YIex > Y + Iex
    kpb * YIex
 
R16:
    YIex > Y + I
    kft * YIex

R17:
    Iex > I
    VEcoli * Na * kt * Iex

R18:
    I > Iex
    kt * I

R19:
    MR > $pool
    lMR * MR

R20:
    MY > $pool
    lMY * MY

R21:
    R > $pool
    lR * R

R22:
    R2 > $pool
    lR2 * R2

R23:
    Y > $pool
    lY * Y

R24:
    YIex > I
    lYIex * YIex

R25:
    I2R2 > {2}I
    lI2R2 * I2R2

R26:
    O > O + MFP
    ks1MFP * O

R27:
    R2O > R2O + MFP
    ks0MFP * R2O

R28:
    MFP > MFP + FP
    ksFP * MFP

R29:
    FP + Bu > FP + Bm
    (kcFP)/(Na * VEcoli) * FP * Bu

R30:
    FP > $pool
    lFP * FP

R31:
    MFP > $pool
    lMFP * MFP

# Parameters
Na        = 6.0221367e14
VEcoli    = 8e-16
# OT       = 1
ksMR      = 0.23
ksR       = 15
k2R       = 50
k2Rb      = 10e-3
kr        = 960
krb       = 2.4
kdr1      = 3e-7
kdr1b     = 12
kdr2      = 3e-7
kdr2b     = 4.8e3
ks1MY     = 0.5
ks0MY     = 0.01
ksY       = 30
kp        = 0.12
kpb       = 0.1
kft       = 6e4
kt        = 0.92
lMR       = 0.462
lMY       = 0.462
lR        = 0.2
lR2       = 0.2
lY        = 0.2
lYIex     = 0.2
lI2R2     = 0.2         
kcFP      = 0.5 # Check/recompute this value
ks1MFP    = 0.5
ks0MFP    = 0.0
ksFP      = 30
lMFP      = 0.462
lFP       = 0.2

# Initial values
MR        =  0
R         =  40
MY        =  0
R2        =  0
R2O       =  0
Iex       =  0
I         =  0
I2R2      =  0
Y         =  0
YIex      =  0
O         =  20
MFP       =  0
FP        =  0
Bu        =  20
Bm        =  0
