# Copyright (c) 2012, James Hensman and Ricardo Andrade
# Licensed under the BSD 3-clause license (see LICENSE.txt)

from kernpart import kernpart
import numpy as np
from GPy.util.linalg import mdot, pdinv

class coregionalise(kernpart):
    """
    Kernel for Intrisec Corregionalization Models
    """
    def __init__(self,Nout,R=1, W=None, kappa=None):
        self.D = 1
        self.name = 'coregion'
        self.Nout = Nout
        self.R = R
        if W is None:
            self.W = np.ones((self.Nout,self.R))
        else:
            assert W.shape==(self.Nout,self.R)
            self.W = W
        if kappa is None:
            kappa = np.ones(self.Nout)
        else:
            assert kappa.shape==(self.Nout,)
        self.kappa = kappa
        self.Nparam = self.Nout*(self.R + 1)
        self._set_params(np.hstack([self.W.flatten(),self.kappa]))

    def _get_params(self):
        return np.hstack([self.W.flatten(),self.kappa])

    def _set_params(self,x):
        assert x.size == self.Nparam
        self.kappa = x[-self.Nout:]
        self.W = x[:-self.Nout].reshape(self.Nout,self.R)
        self.B = np.dot(self.W,self.W.T) + np.diag(self.kappa)

    def _get_param_names(self):

        return sum([['W%i_%i'%(i,j) for j in range(self.R)] for i in range(self.Nout)],[]) + ['kappa_%i'%i for i in range(self.Nout)]

    def K(self,index,index2,target):
        index = np.asarray(index,dtype=np.int)
        if index2 is None:
            index2 = index
        else:
            index2 = np.asarray(index2,dtype=np.int)
        ii,jj = np.meshgrid(index,index2)
        target += self.B[ii,jj].T

    def Kdiag(self,index,target):
        target += np.diag(self.B)[np.asarray(index,dtype=np.int).flatten()]

    def dK_dtheta(self,partial,index,index2,target):
        index = np.asarray(index,dtype=np.int)
        if index2 is None:
            index2 = index
        else:
            index2 = np.asarray(index2,dtype=np.int)
        ii,jj = np.meshgrid(index,index2)
        PK = np.zeros((self.R,self.R))
        dkappa = np.zeros(self.Nout)
        partial_small = np.zeros_like(self.B)
        for i in range(self.Nout):
            for j in range(self.Nout):
                partial_small[j,i] = np.sum(partial[(ii==i)*(jj==j)])
        #print partial_small
        dkappa = np.diag(partial_small)

        ##target += (((X2[:, None, :] * self.variances)) * partial[:,:, None]).sum(0)
        dW = 2.*(self.W[:,None,:]*partial_small[:,:,None]).sum(0)

        target += np.hstack([dW.flatten(),dkappa])

    def dKdiag_dtheta(self,partial,index,target):
        raise NotImplementedError

    def dK_dX(self,partial,X,X2,target):
        pass



