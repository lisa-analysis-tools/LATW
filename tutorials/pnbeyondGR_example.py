# we need elliptic integrals
import numpy as np
from mpmath import *
from mpmath import mp

# base class: in few >= 2.0, a custom trajectory is written as an ODE class
# that is plugged into the EMRIInspiral integrator (via inspiral_kwargs["func"]).
from few.trajectory.ode.base import ODEBase

# settings for elliptic integrals
mp.dps = 25
mp.pretty = True

# constants from our package
from few.utils.constants import MTSUN_SI, YRSID_SI, PI


# for common interface with C/mathematica
def Power(x, n):
    return x**n


def Sqrt(x):
    return np.sqrt(x)


# This is the actual class that implements a modified PN trajectory.
# In few >= 2.0 the integrator (DOPR853 inside EMRIInspiral) drives the
# integration, so we only provide the right-hand side of the ODE here.
# (The pre-2.0 version of this example subclassed TrajectoryBase and
# integrated the ODE by hand with scipy's DOP853.)
class ModifiedPnTrajectory(ODEBase):
    # tell the integrator about this model
    @property
    def background(self):
        return "Schwarzschild"

    @property
    def equatorial(self):
        return True

    @property
    def separatrix_buffer_dist(self):
        # terminate the inspiral at p = p_sep + 0.1
        return 0.1

    def evaluate_rhs(self, y):
        # extract the three orbital elements (the integrator handles phases)
        p, e, x = y[:3]

        # any extra parameters (after m1, m2, a, p0, e0, x0) show up here
        modification = self.additional_args[0]

        # guard against bad integration steps
        if e >= 1.0 or e < 1e-2 or p < 6.0 or (p - 6 - 2 * e) < 0.1:
            return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        # perform elliptic calculations
        EllipE = ellipe(4 * e / (p - 6.0 + 2 * e))
        EllipK = ellipk(4 * e / (p - 6.0 + 2 * e))
        EllipPi1 = ellippi(
            16 * e / (12.0 + 8 * e - 4 * e * e - 8 * p + p * p),
            4 * e / (p - 6.0 + 2 * e),
        )
        EllipPi2 = ellippi(
            2 * e * (p - 4) / ((1.0 + e) * (p - 6.0 + 2 * e)), 4 * e / (p - 6.0 + 2 * e)
        )

        # Azimuthal frequency
        Omega_phi = (2 * Power(p, 1.5)) / (
            Sqrt(-4 * Power(e, 2) + Power(-2 + p, 2))
            * (
                8
                + (
                    (
                        -2
                        * EllipPi2
                        * (6 + 2 * e - p)
                        * (3 + Power(e, 2) - p)
                        * Power(p, 2)
                    )
                    / ((-1 + e) * Power(1 + e, 2))
                    - (EllipE * (-4 + p) * Power(p, 2) * (-6 + 2 * e + p))
                    / (-1 + Power(e, 2))
                    + (
                        EllipK
                        * Power(p, 2)
                        * (28 + 4 * Power(e, 2) - 12 * p + Power(p, 2))
                    )
                    / (-1 + Power(e, 2))
                    + (
                        4
                        * (-4 + p)
                        * p
                        * (2 * (1 + e) * EllipK + EllipPi2 * (-6 - 2 * e + p))
                    )
                    / (1 + e)
                    + 2
                    * Power(-4 + p, 2)
                    * (
                        EllipK * (-4 + p)
                        + (EllipPi1 * p * (-6 - 2 * e + p)) / (2 + 2 * e - p)
                    )
                )
                / (EllipK * Power(-4 + p, 2))
            )
        )

        # Post-Newtonian calculations
        yPN = pow(Omega_phi, 2.0 / 3.0)

        EdotPN = (
            (96 + 292 * Power(e, 2) + 37 * Power(e, 4))
            / (15.0 * Power(1 - Power(e, 2), 3.5))
            * pow(yPN, 5)
        )
        LdotPN = (
            (4 * (8 + 7 * Power(e, 2)))
            / (5.0 * Power(-1 + Power(e, 2), 2))
            * pow(yPN, 7.0 / 2.0)
        )

        # flux
        # NOTE (few >= 2.0): the right-hand side is given per unit mass ratio;
        # the integrator applies the mass-ratio scaling internally, so there is
        # no epsilon factor here (the pre-2.0 version of this example
        # multiplied the fluxes by epsilon).
        Edot = -EdotPN
        Ldot = -LdotPN

        # time derivatives
        pdot = (
            -2
            * (
                Edot
                * Sqrt((4 * Power(e, 2) - Power(-2 + p, 2)) / (3 + Power(e, 2) - p))
                * (3 + Power(e, 2) - p)
                * Power(p, 1.5)
                + Ldot * Power(-4 + p, 2) * Sqrt(-3 - Power(e, 2) + p)
            )
        ) / (4 * Power(e, 2) - Power(-6 + p, 2))

        edot = -(
            (
                Edot
                * Sqrt((4 * Power(e, 2) - Power(-2 + p, 2)) / (3 + Power(e, 2) - p))
                * Power(p, 1.5)
                * (
                    18
                    + 2 * Power(e, 4)
                    - 3 * Power(e, 2) * (-4 + p)
                    - 9 * p
                    + Power(p, 2)
                )
                + (-1 + Power(e, 2))
                * Ldot
                * Sqrt(-3 - Power(e, 2) + p)
                * (12 + 4 * Power(e, 2) - 8 * p + Power(p, 2))
            )
            / (e * (4 * Power(e, 2) - Power(-6 + p, 2)) * p)
        )

        Phi_phi_dot = Omega_phi

        # by construction (equatorial orbit)
        Phi_theta_dot = Omega_phi

        Phi_r_dot = (
            p * Sqrt((-6 + 2 * e + p) / (-4 * Power(e, 2) + Power(-2 + p, 2))) * PI
        ) / (
            8 * EllipK
            + (
                (-2 * EllipPi2 * (6 + 2 * e - p) * (3 + Power(e, 2) - p) * Power(p, 2))
                / ((-1 + e) * Power(1 + e, 2))
                - (EllipE * (-4 + p) * Power(p, 2) * (-6 + 2 * e + p))
                / (-1 + Power(e, 2))
                + (EllipK * Power(p, 2) * (28 + 4 * Power(e, 2) - 12 * p + Power(p, 2)))
                / (-1 + Power(e, 2))
                + (
                    4
                    * (-4 + p)
                    * p
                    * (2 * (1 + e) * EllipK + EllipPi2 * (-6 - 2 * e + p))
                )
                / (1 + e)
                + 2
                * Power(-4 + p, 2)
                * (
                    EllipK * (-4 + p)
                    + (EllipPi1 * p * (-6 - 2 * e + p)) / (2 + 2 * e - p)
                )
            )
            / Power(-4 + p, 2)
        )

        # this is the (beyond-GR / environmental) modification
        pdot *= 1 + modification
        edot *= 1 + modification
        # read out data. It must return the 6 derivatives
        # (pdot, edot, xdot, Phi_phi_dot, Phi_theta_dot, Phi_r_dot)
        return [
            float(pdot),
            float(edot),
            0.0,
            float(Phi_phi_dot),
            float(Phi_theta_dot),
            float(Phi_r_dot),
        ]
