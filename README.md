# QCBlender

English | [简体中文](README_zh.md)

QCBlender displays existing quantum chemistry results in Blender and generates orbital, density, and electrostatic potential grids from supported HF/DFT wavefunctions. Structures, isosurfaces, materials, and vibrations can be adjusted through native Geometry Nodes. Scientific data retain their provenance, units, and calculation conditions.

**QCBlender 0.1.0 Alpha Preview** targets Windows x64 and Blender 5.1.1. Availability and exact assets are shown on [GitHub Releases](https://github.com/psiQAQ/QCBlender/releases/tag/v0.1.0). Candidate checks, Agent installation verification and independent human/scientific acceptance are recorded separately; preparing a candidate does not mean it has been published.

## What you can do

| Task | Input | Result |
| --- | --- | --- |
| Visualize orbitals and electron distributions | Gaussian `.fchk/.fch` with a complete basis set and MOs, or existing `.cube/.cub` files | Isosurface and volume displays of positive/negative MO phases and total/alpha/beta/spin densities |
| Inspect electrostatic potential | Supported FCHK, or existing density/ESP Cube files | Density surfaces colored by ESP, fixed color scales, slices, point values, and line profiles |
| Inspect molecular properties and vibrations | Gaussian `.log/.out`, or FCHK containing the relevant properties | Structures, method-specific energies, charges, and dipoles; vibration display when normal modes are available, and export of original IR frequencies/intensities |
| Browse geometry changes | Gaussian optimization logs, ordered IRC FCHK lists, or standard XYZ | Stepwise optimization/IRC geometries and records; discrete viewing of XYZ frames with the same atom order |
| Display existing external analyses | Paired Cube files, point/path files, or result tables | IGMH/IRI, ESP extrema/areas, NBO/E(2), AIM, Mayer, and ETS-NOCV/NOCV results; see the [import guide](docs/EXTERNAL_ANALYSIS_IMPORT.md) for file requirements |

External analyses must first be performed with the corresponding software. QCBlender reads and displays their results. Its built-in evaluation does not run new SCF calculations.

## Compatibility and installation

The documented validation was performed on **Windows x64 with Blender 5.1.1**. The extension manifest declares a minimum Blender version of 5.1.1 and an upper version boundary of 5.2.0. Other versions and platforms were not covered by that validation.

Built-in evaluation is limited to nonperiodic, real-valued, all-electron HF/DFT wavefunctions. See [support and validation status](docs/VALIDATION.md) for the specific basis sets, methods, and sample coverage. The extension includes the required scientific libraries; no separate Python environment is needed at runtime.

Choose either installation method after the preview is available on [GitHub Releases](https://github.com/psiQAQ/QCBlender/releases/tag/v0.1.0).

### Install from a ZIP

1. **Download the extension**: obtain `qcblender-0.1.0.zip` and compare its SHA-256 with `SHA256SUMS.txt` from the same Release. The repository's source ZIP cannot be installed directly as a Blender extension.
2. **Install the extension**: in Blender, open **Edit → Preferences → Get Extensions → top-right menu → Install from Disk**, then select the extension ZIP.
3. **Enable it and check the runtime**: select **Add-ons** in the Preferences sidebar, search for **QCBlender**, and confirm that it is enabled. Expand its preferences and click **Check Scientific Runtime**. Continue to orbital generation after all module checks pass.

### Install from the remote repository

1. Open **Edit → Preferences → System → Network** and enable **Allow Online Access**.
2. Open **Get Extensions → Repositories → ＋ → Add Remote Repository**. Paste the complete URL `https://notes.psiqaq.cn/QCBlender/index.json` and add the repository.
3. Sync the repository, search for **QCBlender**, and install it. Confirm that it is enabled under **Add-ons**, then run **Check Scientific Runtime** as above.

The same Release provides `qcblender-tutorial-0.1.0.zip`: the Chinese SOP, all topics, screenshots, renders, required inputs and source/license notices. Extract it without changing the relative locations of `human/` and `shared/`. The tutorial bundle does not duplicate the extension installer. If the repository cannot sync, check online access and the complete URL, or use the ZIP method.

## Create your first orbital image

After installation and the runtime check, prepare an FCHK containing a complete basis set and molecular orbitals (MOs), such as the [P01 oxygen molecule example](validation/shared/data/public/gaussian-v2/P01/o2-uhf.fchk). For a detailed parameter checklist and expected results, follow the [orbital workflow in the user tutorial](validation/human/SOP.md#orbital).

1. **Import the FCHK**: in the **3D Viewport**, press **N** and open **QCBlender → Import and Export → Import → Import Gaussian / Cube / XYZ**, then select the FCHK.
2. **Open the atom view settings**: select the atom object created by the import. Under **N sidebar → Current QC Object → Open Object Properties**, check the target object name and open its settings.
3. **Generate the orbital field**: under **Object Properties → Create Views and Tools → Compute**, click **Generate Quantum Field**. Wait for the independent scientific preflight to pass. In the parameter dialog, select **Molecular orbital**, check the spin channel, and choose an orbital by its source orbital number or HOMO/LUMO. Check the grid parameters, click **OK**, and wait for generation to finish.
4. **Adjust the orbital display**: select the new field object and click **Open Object Properties** again. Under **Geometry Representation**, adjust the isovalue and positive/negative phase display. Adjust colors in **Material Properties** in the Properties editor.

   > Positive and negative orbital surfaces represent orbital phase.

5. **Save the project**: use **N sidebar → Project and Maintenance → Save and Archive → Save Self-Contained Project**. This should create a `.blend` file and a `.qcdata/` directory with the same base name. Move both together when relocating the project.
6. **Render the image**: set up the camera and lights, then render with Blender's native renderer.

<details>
<summary>Default grid parameters and defaults for new views</summary>

- Initial grid settings: spacing **0.2 Å**, margin **3 Å**, and memory budget **512 MiB**.
- The outer parameter for a new atom view is `Quality=3`; a new slice has **201** points per axis.
- The nine public node assets retain their original defaults.

</details>

<details>
<summary>Export data and parameter summaries, and set an output directory</summary>

To export data, select the QC object containing the target records and use **N sidebar → Import and Export → Export → Export Data and Parameter Summary**. This explicitly saves original IR, optimization/convergence, IRC, Mayer, sampled line-profile, paired-field voxel, and ESP area records as UTF-8 CSV files and `metadata.json`. See [parameter summaries](validation/human/SOP.md#export) and [profile CSV export](validation/human/topics/04-spatial-tools.md) for instructions.

Each export creates a uniquely named result subdirectory. If no export directory is set, saved projects use the directory containing the `.blend` file; unsaved projects use the system Documents directory. Set **Data Export Directory** in the add-on preferences to an absolute path for use across projects, or override it for an individual export.

</details>

For the full workflow, start with installation in the [user tutorial](validation/human/SOP.md), then choose topics as needed. The [validation directory](validation/README.md) brings together tutorials, screenshots, installation packages, and data, and explains how to package the materials after manual completion. See the [Agent workflow](validation/agent/README.md) for technical checks.

The [data directory](validation/shared/data/README.md) manages public, local-only, and regression inputs. Public P01/P03/P04/P05/P06 data use CC BY 4.0. P02 is restricted to local use; redistribution permission has not been confirmed.

## Saving projects and scientific limitations

The `.blend` file stores nodes, materials, and layouts; `.qcdata/` stores scientific arrays, provenance, and display caches. Save the latest project state before packaging it. Surface meshes alone cannot recover missing scientific arrays. Keep the original calculation outputs separately.

Binary `.chk` files must first be converted to FCHK with `formchk` from an existing Gaussian installation. The physical quantity and units of an ordinary Cube file may be unknown and must be explicitly declared based on how it was generated. Declaring them does not convert the values. ECP, complex orbitals, periodic systems, native ORCA formats, and `.mwfn` are not currently supported.

Standard XYZ supports element symbols/atomic numbers and three finite coordinates in Å. Multiple frames with the same atom count and element order can be viewed discretely. Extended properties, unit cells/PBC, interpolation, and playback are outside XYZ support. Linking scientific sources to multi-frame XYZ is explicitly rejected; single-frame XYZ is checked against the actual geometry.

Connections between atoms are inferred from distances and do not represent calculated bond orders. Vibration playback speed is a display parameter; it does not turn static orbitals or densities into time-dependent wavefunctions. For scientific figures, record the method, basis set, provenance summary, physical quantity/units, grid, isovalue, and color-scale range.

## Developer documentation

See the [documentation index](docs/README.md) for the full classification, with separate entry points for current guidance, research evidence, and historical acceptance records.

| Category | Documents and purpose |
| --- | --- |
| Building and validation | [Development guide](docs/DEVELOPMENT.md): environment, building, and verification of the same candidate; [validation status](docs/VALIDATION.md): exact candidates and Passed / Not Run results |
| Architecture and data | [Architecture](docs/QCBLENDER_V1_DESIGN.md), [data contract](docs/specs/qc-data-contract.md), [node contract](docs/specs/geometry-nodes.md), and [single-extension ADR](docs/adr/0001-self-contained-extension.md) |
| Scientific basis | [Domain vocabulary](CONTEXT.md), [input format research](docs/research/gaussian-inputs.md), and [Gaussian energy semantics](docs/research/gaussian-energy-semantics.md) |
| Samples and reproduction | [Data directory](validation/shared/data/README.md), [user tutorial](validation/human/SOP.md), and [complex example parameters and reconstruction](docs/COMPLEX_EXAMPLES.md) |
| Development conventions and issues | [AGENTS](AGENTS.md), [local task rules](docs/agents/issue-tracker.md), and [development issue records](docs/DEVELOPMENT_PITFALLS.md) |
| Licenses and history | [LICENSE](LICENSE), [third-party materials](THIRD_PARTY.md), and [CHANGELOG](docs/CHANGELOG.md) |

For your first Alpha session, follow the [P01/MO9 workflow](validation/human/SOP.md). Under **Import and Export → Export → Export Data and Parameter Summary**, select **Current View Parameter Summary** to save Chinese Markdown and JSON. See the [GitHub release study](docs/research/github-release-workflow.md) for the release process and gates.
