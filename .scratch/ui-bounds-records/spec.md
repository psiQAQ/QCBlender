# Record and bound atom-view selection ranges

Limit existing per-object record row selectors to their display layer's current
record count; normalize stored values without changing scientific source numbers.
Empty record tables expose disabled controls. Mayer atom selectors use source atom
count and retain the existing pair membership check. Bound atom-view First/Last
Atom sockets use source atom count, preserving Last Atom's 0 = all value. Style
sockets use 0..2. Unbound reusable assets retain their generic contracts.

Validation seam: `refresh_record_ranges(obj, meta)` with a controlled Blender
custom-property boundary. Native Blender UI, undo and persistence are validated by
the coordinating agent; this task does not start or connect to Blender.
