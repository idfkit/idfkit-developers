# HVAC Topology

EnergyPlus joins HVAC objects through *node names*: a coil's air outlet node and the fan's air inlet
node are the same string. A node name is not a reference, so the
[reference graph](references.md) never sees it, and a mistyped node passes schema validation and
breaks the loop only when EnergyPlus runs.

The `idfkit.hvac` module derives the node graph from the document. `HVACTopology` lists every field
that names each node, with the connection role EnergyPlus gives that field. It walks flow upstream
and downstream from a component, a zone or space, a node or a `NodeList`. A walk can keep only
components of some categories, and it can stay on one fluid instead of crossing from air to water
at a coil. `check_topology()` reports broken connections before a simulation, and `coverage` says
what the view could not see: unexpanded `HVACTemplate` systems, EMS programs and object types
without a rule.

The connection roles come from EnergyPlus's own node connection report for its 26.2 example
files. Each role records where it came from. A finding that rests on a role written from a field's
name, which EnergyPlus never reported, is never an error.

::: idfkit.hvac
