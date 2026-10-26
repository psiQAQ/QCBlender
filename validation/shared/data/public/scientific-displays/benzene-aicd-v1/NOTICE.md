# Original regular-hexagon benzene AICD example

QCBlender contributors created the geometry analytically for this tutorial on 2026-10-26: six carbon atoms on a regular hexagon of radius 1.40 Å and six hydrogens on radial positions at 2.49 Å, all in the XY plane. The geometry was not optimized and is not a structure taken from a third-party example.

The original geometry, inputs, generated numerical data and tutorial documentation are shared under CC-BY-4.0; attribute QCBlender contributors. Existing software notices in the logs retain their original attribution. No software executable or source code is redistributed in this data directory.

## Calculation conditions

Gaussian 16 C.01, closed-shell neutral singlet, RB3LYP/6-31G(d), 6D/7F, NMR=CSGT, SCF=Tight, Integral=UltraFine, 4 threads and 2 GB memory. The all-electron calculation uses IOp(10/93=1). The separate selected-orbital calculation uses IOp(10/93=2) and occupied MOs 17, 20, 21, totaling six electrons. Both finished normally.

Multiwfn 2026.9.20 analyzed the all-electron checkpoint to identify the occupied π orbitals relative to the XY plane. Its command sequence and output are included. Orbital numbers apply only to this wavefunction.

Each tensor dump contains 240630 points. The coordinates, quadrature weights and nine tensor components are preserved byte for byte. Aniso and unit-field current were compared against the published AICD extractor and matrix implementation. The all-electron and π jobs share the same sampling coordinates and weights.

## Included files and provenance

- `original.xyz`: analytically constructed input geometry.
- `all/` and `pi/`: input, formatted checkpoint, complete scientific log, tensor dump and a relative-path `source.json` declaration.
- `pi-orbital-analysis.txt` and `pi-orbital-commands.txt`: wavefunction-based orbital assignment.

Infrastructure-specific installation and scratch paths in the public logs are normalized to `/opt/gaussian/g16/` and `/work/gaussian/scratch/`. Scientific conditions, coordinates, values, calculation boundaries and termination records are unchanged. These path substitutions are disclosed here and are not scientific edits.

The current files and their SHA-256 identities are listed in the tutorial delivery manifest. Original calculation records are retained separately. Neither this example nor a successful import is an independent scientific interpretation of aromaticity.

## Software references

- Gaussian 16, Revision C.01, Gaussian, Inc.: https://gaussian.com/citation/
- Multiwfn: Tian Lu and Feiwu Chen, J. Comput. Chem. 33, 580–592 (2012), https://doi.org/10.1002/jcc.22885
- AICD: D. Geuenich et al., Chem. Rev. 105, 3758–3772 (2005), https://doi.org/10.1021/cr0300901
