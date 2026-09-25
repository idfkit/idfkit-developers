# Scene

Resolving a model's geometry into one frame, without changing the model.

`get_scene(doc)` returns every surface it could place, in world coordinates with
the building rotation applied, alongside what it could not place and what it did
not attempt. It reads; it does not author, validate or mutate. Writing the
document before and after yields the same bytes.

The resolution it applies was measured against EnergyPlus's own surface vertex
report rather than reasoned from the input reference, which is why
[`translate_to_world`][idfkit.geometry.translate_to_world] now agrees with it.

::: idfkit.scene
