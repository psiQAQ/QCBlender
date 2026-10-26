# Owned water-dimer surface projection

Copyright 2026 QCBlender contributors. The original calculation data and derived
scientific data in this directory are distributed under CC BY 4.0; see LICENSE.
Retain this notice and cite the software used to produce an analysis.

The molecular geometry is the project's owned Gaussian-v2 P03 water dimer,
copied from gaussian-v2/P06/water-dimer.xyz. It is rotated by +90 degrees about Y
and centered along X: x_new=z_old-1.4822284968169446, y_new=y_old, z_new=-x_old.
input.gjf and reference.xyz retain the same coordinates rounded to 12 decimals.
The Gaussian route in input.gjf is only a geometry container; no Gaussian job
is run for this projection. No official Multiwfn example geometry is used.

Multiwfn 2026.9.20 generates the unscaled vdW union-of-spheres projection with
H=1.20 A, O=1.52 A and radius scale 1. The grid is 61 by 41, X=-4..4 A,
Y=-3..3 A, Zstart=4 A, Zend=-4 A, Zstep=0.05 A. Settings use isilent=1,
4 threads and the default vdwrfile=none. mwfn_commands.txt and mwfn_log.txt
retain the actual interactive command sequence and output.

distmap.txt uses coordinates relative to the lower X/Y limits and reports
z_hit-z_start. The validity mask is derived independently from open ray/sphere
chords and the discrete Z sampling: 849 sampled hits, 1652 missed samples.
One continuous ray intersects a thin chord between Z samples and is therefore
marked missed. This is a finite-step projection, not an exact continuous surface.
All 2501 depths agree with the independent discrete reference within 5.01e-9 A;
the maximum XY text-rounding error is below 5.01e-7 A.

Multiwfn citations: Tian Lu and Feiwu Chen, J. Comput. Chem. 33, 580 (2012),
DOI:10.1002/jcc.22885; Tian Lu, J. Chem. Phys. 161, 082503 (2024),
DOI:10.1063/5.0216272. Program website: http://sobereva.com/multiwfn/.
The program itself and third-party example inputs are not distributed here.
