# Conditional C1 horizon-entropy mapping

This is a derivation under explicit assumptions, not a new black-hole solution or a parameter constraint. The source is [EFMW-Lagrangian candidate C1, commit 83f9d2ec03e055c6cd09aa6359189161ad1571f6](https://github.com/enuminous/EFMW-Lagrangian/blob/83f9d2ec03e055c6cd09aa6359189161ad1571f6/candidate/CANDIDATE.md), inspected through public access. A source snapshot is in `sources/EFMW-C1-CANDIDATE.md`.

## Restriction and coefficient

Set the gauge fields and all their associated couplings to zero. Keep the metric and canonical scalars. C1 is linear in the curvature scalar R in this restriction:

\[
\mathcal L=\frac{M_{\rm Pl}^2}{2}F(\varphi)R
-\frac12\sum_a(\nabla\varphi_a)^2-V(\varphi),
\qquad M_{\rm Pl}^2=(8\pi G)^{-1}.
\]

Extracting the curvature terms in the candidate potential gives

\[
F=1-\frac{1}{M_{\rm Pl}^2}\left[
\sum_a\xi_a\varphi_a^2+2\sum_a g_{Ea}\varphi_a
+2\sum_{a<b}h_{Eab}\varphi_a\varphi_b\right]
=1-\frac{2\mathcal U_R}{M_{\rm Pl}^2}.
\]

Couplings carry the dimensions specified by the action, so each subtracted term is dimensionless. Require F>0 throughout the region under consideration. This is not sufficient by itself for stability, a regular horizon, or existence of a merger solution.

## Stationary Wald entropy

For a regular stationary bifurcate Killing horizon, diffeomorphism-invariant local action and binormal normalization epsilon_ab epsilon^ab=-2, the Wald expression is

\[
S_W=-2\pi\int_H\frac{\partial\mathcal L}{\partial R_{abcd}}
\epsilon_{ab}\epsilon_{cd}\,dA
=2\pi M_{\rm Pl}^2\int_H F\,dA
=\frac{1}{4G}\int_H F\,dA.
\]

Units here are hbar=c=k_B=1. This uses the scalar Lagrangian rather than the density in the derivative and the horizon measure separately. For F=1 it reduces to the usual area entropy. If F is not constant over a horizon, use its area-weighted average; do not insert an arbitrary point value.

For widely separated initial stationary horizons, define

\[
\bar F_i=\frac{\bar F_1 A_1+\bar F_2 A_2}{A_1+A_2},\quad
R=\frac{A_f}{A_1+A_2},\quad
\frac{S_f}{S_1+S_2}=\frac{\bar F_f}{\bar F_i}R=\eta R.
\]

Thus the entropy-growth condition is eta*R >= 1. If the same constant F applies to all three horizons, it cancels. This endpoint identity does **not** prove a dynamical second law for C1. Energy/regularity assumptions and dynamical entropy ambiguities require separate analysis. No claim is made about a nonstationary horizon slice.

## What the lab can and cannot evaluate

The lab's eta sweep evaluates the algebraic sensitivity of a Kerr-derived ratio. It does not replace the Kerr metric by a C1 solution. In a real modified-gravity model, both the horizon geometry and the inference likelihood could change. Consequently no interval on eta, xi, g or h follows from this sweep. The QNM frequency-scale deformation is an independent phenomenological construction; no equation identifies it with a C1 coefficient or with eta.

Required next steps:

1. Specify a scalar potential, couplings, asymptotic vacuum, matter/frame convention, and a regular stationary black-hole branch. Determine whether the branch has nonconstant scalar fields at all; a constant-field Kerr branch may leave the proposed effect absent.
2. Solve the linear perturbation problem with ingoing horizon/outgoing infinity conditions, establish stability, and derive at least two mode frequencies and damping times. Compute the horizon integral of F on the same solutions.
3. Model source excitation and premerger dynamics, then fit independent pre/post data with the resulting waveform and likelihood. Demonstrate uncertainty calibration with injections before interpreting a recovered entropy or area difference.

## Novelty and evidence status

The Kerr area relation, single-mode mass degeneracy and Wald functional are established constructions. Applying them to this C1 restriction is a conditional correspondence calculation, not a new entropy law. C1 physical validity, non-Kerr waveform prediction and an observational EFMW bound are **UNRESOLVED**. No Lean verification or full Zoo certification is claimed.

Reference: R. M. Wald, *Black hole entropy is the Noether charge*, Physical Review D 48, R3427–R3431 (15 October 1993), [doi:10.1103/PhysRevD.48.R3427](https://doi.org/10.1103/PhysRevD.48.R3427); [original preprint](https://arxiv.org/abs/gr-qc/9307038). Peer-reviewed foundational result; not evidence for EFMW.
