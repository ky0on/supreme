"""RANdom SAmple Consensus

Martin A. Fischler and Robert C. Bolles,
"Random sample consensus: a paradigm for model fitting with applications to
image analysis and automated cartography",
Communications of the ACM, 1981

"""

__all__ = ['IModel','RANSAC']

import numpy as N
from numpy.testing import set_local_path, restore_path

set_local_path('../..')
from supreme.lib.zope import interface as zi
restore_path()

class IModel(zi.Interface):
    parameters = zi.Attribute("Model parameters")
    ndp = zi.Attribute("Number of defining points, i.e. the model parameters "
                       "can be estimated from a minimum of ndp points.")

    def __call__(data,confidence=0):
        """Evaluate data fit.

        :Parameters:
            data : array
                Data points as row vectors.
            confidence : float
                Value between 0 and 1 indicating how well a point must
                fit the model to be considered an inlier.  A value of
                zero implies almost any data point is considered
                fitting the model.

        :Returns:
            score : array of float
                Fit of data points to model.
            inlier : array of bool
                Whether a data point is an inlier or not.

        """

    def estimate(data):
        """Estimate model parameters from data.

        :Parameters:
            data : array
                Data points as row vectors.

        :Returns:
            parameters:
               Model parameters in any format the model can interpret.
            residual : float
               Measure of data fit.

        """

class RANSAC(object):
    """RANdom SAmple Consensus"""

    def __init__(self,model=None,p_inlier=None):
        """
        :Parameters:
            model : Model
                Model describing inlier data.
            p_inlier : float (0..1)
                Probability that any data point is an inlier.

        """
        for param in [model,p_inlier]:
            assert param is not None

        assert IModel.providedBy(model)
        self.model = model
        self.p_inlier = p_inlier

    def __call__(self,data=None,inliers_required=None,confidence=None):
        """Execute RANSAC.

        :Parameters:
            data : MxN array
                M data points as row features.
            inliers_required : int
                Number of inliers (in addition to those randomly chosen)
                needed to successfully terminate RANSAC.
            confidence : float (0..1)
                How well a point must fit the model to be considered
                an inlier.  A value of zero implies almost any data
                point fits the model, while one implies that it must
                lie exactly on the model prediction.

        """
        for param in [data,inliers_required,confidence]:
            assert param is not None

        model = self.model

        max_iter = 3*N.ceil(self.p_inlier ** (-model.ndp)).astype(int)
        #print "Maximum number of RANSAC iterations:", max_iter

        success = False
        for i in range(max_iter):
            rand_idx = N.floor(N.random.random(model.ndp)*len(data)).astype(int)
            model.parameters,res = model.estimate(data[rand_idx,...])
            score,inliers = model(data,confidence)
            if N.sum(inliers) >= inliers_required:
                success = True
                break
        if success:
            pass
            #print "RANSAC successfully converged after %s iterations." % i
        else:
            raise Exception("RANSAC failed to converge.")

        inliers[rand_idx] = True
        data = data[inliers,...]
        return model.estimate(data)