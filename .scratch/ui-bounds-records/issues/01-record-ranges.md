Triage: ready-for-agent
Status: resolved

# Bound record and source atom selectors

Implement the approved record range scope in `record_ranges.py`,
`external_results.py`, `nbo.py`, `irc.py`, and `views.py`.

## Comments

- Source atom count is cache-only `_atom_count` metadata populated from loaded
  arrays during bind and from manifest array descriptors during source refresh.
- Follow test-first slices at `refresh_record_ranges(obj, meta)`; Python boundary
  tests do not establish native Blender UI behavior.

## Answer

- Existing record row properties now use per-object hard and soft ranges and
  normalize stored values to their role-specific row count. NBO and E(2) use
  independent counts; empty tables have disabled or hidden selectors.
- Mayer atom selectors use cached source atom count; the existing exact atom-pair
  membership check remains. IRC navigation disables its endpoint buttons.
- Bound atom and field view sockets expose valid source atom/style ranges. Source
  refresh upgrades outer view graphs; a shared outer graph is copied first, and
  reusable unbound assets are not changed.
- `views.bind` adds `_atom_count` to a copy of cached metadata, leaving scientific
  metadata unchanged. The coordinating task supplies manifest-based cache counts
  and per-object refresh calls in `source_browser.py`.
- Passed: six `tests.test_record_ranges` boundary tests; AST parsing of five
  changed Blender modules; `git diff --check`.
- Failed: initial attempt to load `tests.test_science_result_filters` with the
  base Miniforge interpreter because NumPy is unavailable. No dependencies were
  installed. Scientific filter tests have not executed with that interpreter.
- Not Run: native Blender controls, undo/redo, saved-project reopen and integrated
  extension validation. These are assigned to the coordinating task.
