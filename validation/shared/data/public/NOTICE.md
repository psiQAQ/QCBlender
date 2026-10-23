# Public tutorial samples

Current dataset: Gaussian-v1. Owned calculation data: CC BY 4.0; attribution QCBlender contributors. P01/P03/P05 are optimized structures at the original methods/bases; P02 is an owned two-job water optimization/frequency/NBO output. P04 contains a first-order saddle and a complete bidirectional geomeTRIC 1.1.1 IRC driven by real Gaussian energies and gradients, with Gaussian endpoint frequency checks; Gaussian built-in IRC attempts were not accepted as complete. P05 fragments retain their geometries in the optimized complex. P06 contains coordinate-only XYZ derivatives. Native FCHK files are produced by Gaussian formchk.

Gaussian 16 Revision C.01 is the wavefunction producer. Multiwfn 2026.9.20 produces IGMH/IRI, ESP/AIM and NOCV analyses. Cite Tian Lu, Feiwu Chen, J. Comput. Chem. 33, 580 (2012), DOI:10.1002/jcc.22885; Tian Lu, J. Chem. Phys. 161, 082503 (2024), DOI:10.1063/5.0216272.

IRC integration and endpoint relaxation use geomeTRIC 1.1.1; cite L.-P. Wang and C. Song, J. Chem. Phys. 144, 214108 (2016), DOI:10.1063/1.4952956.

NOCV energies use the actual complex KS reconstruction and retain the Multiwfn approximation; they are not evaluated using F_TS. No basis-set or scientific grid-convergence claim is made. QCBlender display grids default to 0.2 angstrom; externally generated analysis grids are recorded separately in the current manifest. Original program outputs retain their scientific values; public copies omit machine execution details.

Legacy-v2 inputs and their frozen manifest remain historical data. Their previous scientific and GUI evidence does not qualify this dataset. The old restricted P02 input is not included.
