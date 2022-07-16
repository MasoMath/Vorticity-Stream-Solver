'''
Gianluca Gisolo

Vorticity-Stream fxn BVP solver
'''
import numpy as np
# from scipy.integrate import odeint
from scipy.integrate import solve_ivp
import scipy.fft as fft
from scipy import sparse

# Solves non-stiff vorticity pde with FFT and 4,5 solver
def FFTsolver(n, tspan, initial_conditions, endpt=10, custom_initial=False, random_initial=False):
    # declare constants / tolerances
    nu = 0.001
    tol = 1e-6
    
    # domain setup
    xDom = np.linspace(-endpt, endpt, n+1)
    delta = xDom[1]-xDom[0]
    xDom = xDom[0:n]
    [xDom, yDom] = np.meshgrid(xDom,xDom)
    
    # Initial condition setup
    # Repeating pattern from top-down view
    # _eFunc(x,y,[0,0,15,15]) + _eFunc(x,y,[0,0,.5,.5]) - _eFunc(x,y,[-5,0,10,10]) - _eFunc(x,y,[5,0,10,10]) - _eFunc(x,y,[0,5,10,10]) - _eFunc(x,y,[0,-5,10,10]) + _eFunc(x,y,[7.5,7.5,.5,.5]) + _eFunc(x,y,[-7.5,7.5,.5,.5])
    # Valleys
    # eFunc(x,y,[-5,-5,1,7]) - eFunc(x,y,[5,5,7,1]) + eFunc(x,y,[1,1,1,7]) - eFunc(x,y,[-1,-1,7,1]) + eFunc(x,y,[5,0,5,5]) - eFunc(x,y,[-5,0,5,5])
    # 4 Placed vorticities
    # eFunc(x,y,[-2,-2,1,1]) + eFunc(x,y,[2,2,1,1]) - eFunc(x,y,[-2,2,1,1]) - eFunc(x,y,[2,-2,1,1])
    # f = lambda x, y: eFunc(x,y,[-2,-2,5,5]) - eFunc(x,y,[-7,2,3,2]) + eFunc(x,y,[-2,5,1,5]) - eFunc(x,y,[3,-2,4,1])
    # _eFunc(x,y,[5,-3.5,1.5,5]) - _eFunc(x,y,[-7,-2,1.3,2]) + _eFunc(x,y,[0,-1.5,1,5]) - _eFunc(x,y,[3,-2,4,10])
    if custom_initial or random_initial:
        omegaInitial = _constructInitialCon(xDom, yDom, initial_conditions)
    else:
        f = lambda x, y: _eFunc(x,y,[0,2,1,1]) + _eFunc(x,y,[0,4,1,1]) + _eFunc(x,y,[0,6,1,1]) - _eFunc(x,y,[0,-2,1,1]) - _eFunc(x,y,[0,-4,1,1]) - _eFunc(x,y,[0,-6,1,1]) + _eFunc(x,y,[5,0,5,5]) - _eFunc(x,y,[-5,0,5,5])
        omegaInitial = f(xDom, yDom)
    omegaInitial = np.reshape(omegaInitial,(n**2,))
    
    # Finite difference matrix setup
    [xPartial, yPartial, Lap] = periodicDiff(n, delta)
    Lap[0, 0] = -0.5 * Lap[0, 0]
    
    # Setting up kx and ky constants
    # i.e. goes through -n/2 to n/2-1 in steps of 1,
    # but it's shifted so that kx[0] = 0 and kx[n/2] = -n/2
    kx = (np.pi / endpt) * np.roll(np.linspace( -0.5 * n, n * 0.5 - 1, n, dtype=int),
                                                int(0.5 * n))
    kx[0] = tol
    ky = kx
    [kx, ky] = np.meshgrid(kx, ky)
    
    # tolerance contrants for ivp solver
    options = {"rtol": tol, "atol": tol}
    
    # Solving vorticity-stream fxn using fft
    # sol = odeint(vortStreamFFT, omegaInitial, tspan,
    #                    args=(nu, xPartial, yPartial, Lap, n, kx, ky),
    #                   rtol=tol, atol=tol, tfirst=True) #, full_output=1)
    sol = solve_ivp(vortStreamFFT, [tspan[0], tspan[-1]], omegaInitial, t_eval=tspan,
                    args=(nu, xPartial, yPartial, Lap, n, kx, ky),
                    rtol=tol, atol=tol) #, full_output=1)
    return [sol.y.transpose(), xDom, yDom]

# calculates differentials x, y, and Lap
def periodicDiff(n, delta):
    # Calculates x and y partials for X and Y differentials in [psi, omega]
    # Calculates Laplacian operator as Lap
    # Assumes periodic BC
    n2 = n**2
    A_D = -4 * sparse.eye(n2, dtype=int)
    Y = sparse.diags([1, -1, 1, -1],[1-n,-1, 1,n-1],shape=[n,n],dtype=int)
    Y = [Y for i in range(n)]
    Y = sparse.block_diag(Y, dtype=int)
    X = sparse.diags([1, -1, 1, -1], [n-n2, -n, n, n2-n],shape=[n2, n2], dtype=int)
    Lap = A_D + abs(X) + abs(Y)
    
    X = X * 0.5 / delta
    Y = Y * 0.5 / delta
    Lap = Lap / (delta**2)
    return [X, Y, Lap]

# Vorticity-Stream fxn using fft
# returns dOmega i.e. the change in omega
def vortStreamFFT(t, omega, nu, xPartial, yPartial, Lap, n, kx, ky):
    
    # reshaping and fft2
    omegaHat = np.reshape(omega,(n,n))
    omegaHat = fft.fft2(omegaHat)
    
    # ifft2 and reshaping
    phiHat = - omegaHat / ( np.square(kx) + np.square(ky) )
    phi = fft.ifft2(phiHat)
    phi = np.reshape(phi, (n**2,)).real

    block1 = (xPartial @ phi) * (yPartial @ omega)
    block2 = (yPartial @ phi) * (xPartial @ omega)
    phiOmega = block1 - block2

    return (nu * (Lap @ omega)) - phiOmega
    
# function for easily making vorticities
def _eFunc(x,y,para):
    
    xShift = para[0]
    yShift = para[1]
    xScale = para[2]
    yScale = para[3]
    
    return np.exp( (- ( (x - xShift)**2 ) / xScale) - ( ( (y - yShift)**2 ) / yScale) )

def _constructInitialCon(x, y, initial_conditions):
    f = np.zeros(x.shape)
    for con in initial_conditions:
        neg = 0
        if con[2] < 0:
            con[2] = abs(con[2])
            neg += 1
        if con[3] < 0:
            con[3] = abs(con[3])
            neg += 1
        if neg > 0:
            f -= _eFunc(x, y, con)
        else:
            f += _eFunc(x, y, con)
    return f