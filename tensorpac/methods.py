"""Main PAC methods.

This file include the following methods :
- Mean Vector Length (Canolty, 2006)
- Kullback Leibler Divergence (Tort, 2010)
- Heights Ratio
- Normalized direct Pac (Ozkurt, 2012)
"""

import numpy as np
from scipy.special import erfinv

__all__ = ['ComputePac']


def ComputePac(pha, amp, idp, nbins, p):
    """Copute real Phase-Amplitude coupling.

    list of the implemented methods :
    - Mean Vector Length
    - Kullback-Leibler Divergence
    - Heights Ratio
    - ndPAC


    Each method take at least a pha and amp array with the respective
    dimensions:
    pha.shape = (npha, ..., npts)
    amp.shape = (namp, ..., npts)
    And each method should return a (namp, npha, ...)
    """
    # Mean Vector Length (Canolty, 2006)
    if idp == 1:
        return MVL(pha, amp)

    # Kullback-Leiber divergence (Tort, 2010)
    elif idp == 2:
        return klDivergence(pha, amp, nbins)

    # Heights ratio
    elif idp == 3:
        return HeightsRatio(pha, amp, nbins)

    # ndPac (Ozkurt, 2012)
    elif idp == 4:
        return ndPac(pha, amp, p)

    else:
        raise ValueError(str(idp) + " is not recognized as a valid pac "
                         "method.")


def MVL(pha, amp):
    """Mean Vector Length (Canolty, 2006).

    Args:
        pha: np.ndarray
            Array of phases of shapes (npha, ..., npts)

        amp: np.ndarra
            Array of amplitudes of shapes (namp, ..., npts)

    Return:
        pac: np.ndarray
            PAC of shape (npha, namp, ...)
    """
    # Number of time points :
    npts = pha.shape[-1]
    return np.abs(np.einsum('i...j, k...j->ik...', amp, np.exp(1j*pha)))/npts


def klDivergence(pha, amp, nbins):
    """Kullback Leibler Divergence (Tort, 2010).

    Args:
        pha: np.ndarray
            Array of phases of shapes (npha, ..., npts)

        amp: np.ndarra
            Array of amplitudes of shapes (namp, ..., npts)

        nbins: int
            Number of bins in which the phase in cut in bins.

    Return:
        pac: np.ndarray
            PAC of shape (npha, namp, ...)
    """
    # Get the phase locked binarized amplitude :
    abin = _kl_hr(pha, amp, nbins)
    # Divide the binned amplitude by the mean over the bins :
    abin = np.divide(abin, np.sum(abin, axis=0))
    abin[abin == 0] = 1
    abin = abin * np.log2(abin)

    return (1 + abin.sum(axis=0)/np.log2(nbins))


def HeightsRatio(pha, amp, nbins):
    """Pac Heights Ratio.

    Args:
        pha: np.ndarray
            Array of phases of shapes (npha, ..., npts)

        amp: np.ndarra
            Array of amplitudes of shapes (namp, ..., npts)

        nbins: int
            Number of bins in which the phase in cut in bins.

    Return:
        pac: np.ndarray
            PAC of shape (npha, namp, ...)
    """
    # Get the phase locked binarized amplitude :
    abin = _kl_hr(pha, amp, nbins)
    M, m = abin.max(axis=0), abin.min(axis=0)
    MDown = M.copy()
    MDown[MDown == 0] = 1

    return (M-m)/MDown


def _kl_hr(pha, amp, nbins):
    """Binarize the amplitude according to phase values.

    This function is shared by the Kullback-Leibler Divergence and the
    Height Ratio.
    """
    # Build the default binned phase vector :
    step = 2*np.pi/nbins
    x = np.arange(-np.pi, np.pi+step, step)
    vecbin = np.c_[x[0:-1], x[1::]]

    abin = []
    for i in vecbin:
        # Find where phase take vecbin values :
        idx = np.logical_and(pha >= i[0], pha < i[1])
        # Take the sum of amplitude inside the bin :
        abin.append(np.einsum('i...j, k...j->ik...', amp, idx))

    return np.array(abin)


def ndPac(pha, amp, p):
    """Normalized direct Pac (Ozkurt, 2012).

    Args:
        pha: np.ndarray
            Array of phases of shapes (npha, ..., npts)

        amp: np.ndarra
            Array of amplitudes of shapes (namp, ..., npts)

    Return:
        pac: np.ndarray
            PAC of shape (npha, namp, ...)
    """
    npts = amp.shape[-1]
    # Normalize amplitude :
    amp = np.divide(amp - np.mean(amp, axis=-1, keepdims=True),
                    np.std(amp, axis=-1, keepdims=True))
    # Compute pac :
    pac = np.abs(np.einsum('i...j, k...j->ik...', amp, np.exp(1j*pha)))/npts
    # Set to zero non-significant values:
    pac[pac < 2 * erfinv(1-p)**2] = 0
    return pac
