import numpy as np
import matplotlib.pyplot as plt

from tensorpac.spectral import spectral
from tensorpac.utils import PacSignals
from tensorpac.pac import Pac

from brainpipe.feature import pac


x = PacSignals(fpha=12, famp=100, ndatasets=30, tmax=1, noise=1, chi=0.1, dpha=0, damp=0)[0]
# x = np.squeeze(x)
print('DATASET :', x.shape)


# TENSORPAC :
p = Pac(1024, idpac=(1, 1, 3), fpha=(1, 30, 2, 2), famp=(60, 160, 10, 10), dcomplex='hilbert')
xpac, spac = p.fit(x, x, axis=1, nperm=50, traxis=0, njobs=-1)



# BRAINPIPE :
fpha = np.ndarray.tolist(p.fpha)
famp = np.ndarray.tolist(p.famp)
P = pac(1024, 1024, Id='113', pha_f=fpha, amp_f=famp)
XPAC = np.squeeze(P.get(x.T, x.T, n_perm=50, matricial=True)[0])
print(XPAC.shape)



plt.figure(1)

plt.subplot(1, 2, 1)
plt.pcolormesh(p.xvec, p.yvec, xpac.mean(2))
plt.axis('tight')

plt.subplot(1, 2, 2)
plt.pcolormesh(p.xvec, p.yvec, XPAC.mean(2))
plt.axis('tight')

plt.show()