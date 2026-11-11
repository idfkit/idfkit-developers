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

## Loops

`loops()` lists every `AirLoopHVAC`, `PlantLoop` and `CondenserLoop`, air loops first.
`memberships(obj)` says which loops a component sits on and where, as `LoopMembership` records: a
component listed on a branch reports the branch and its 0-based position; one on an air loop's path
but on no branch, such as an outdoor-air mixer or a terminal unit, reports the side alone; zone
equipment reports its `ZoneHVAC:EquipmentConnections`. A water coil sits on an air loop and on the
demand side of a water loop, so it reports both.

`chain(loop, side)` gives one side of a loop in flow order. A plant or condenser loop, and an air
loop's supply side, give one list per branch. An air loop's demand side gives one list per path
from a demand inlet to a zone, then one per path from a zone to the demand outlet.
`zones_served(air_loop)` lists the zones or spaces an air loop's demand side reaches.

## Findings

`check_topology()` reports each node once, under the most specific code that fits it.

| Code | Check | Severity |
|---|---|---|
| T001 | A component inlet nothing supplies, not a loop inlet and not outdoor air | warning |
| T002 | A zone inlet nothing supplies | warning |
| T003 | A zone exhaust nothing draws from | warning |
| T004 | A node only setpoint managers, sensors, controllers or actuators name | warning |
| T010 | A branch lists nodes the component does not have | error |
| T011 | Consecutive branch components do not connect | error |
| T030 | An outlet a branch carries that nothing takes | warning |
| T090 | An object type with node fields but no connection rule | info |
| T091 | A template system is present; its topology is not covered | info |

An outlet that nothing takes is legal off a branch: exhaust fans, air-cooled condensers and relief
streams vent outdoors, and an unused zone return is valid too. T010 and T011 are errors only when
they rest on roles EnergyPlus reported; otherwise they are warnings. A clean result does not mean
a model simulates.

## Renaming a node

Node names are strings, so `IDFDocument.rename()` never reaches them.
`IDFDocument.rename_node(old, new)` rewrites every node field naming `old`, matched without regard
to case, and every `NodeList` entry, through the normal field write, so the document's revision moves and cached views are
rebuilt. A field that names a `NodeList` keeps naming the list. Output variable keys and other
free text that happen to spell the node are left alone. It refuses a new name that is already a
node of the model, so two nodes are never merged, and if any write fails it undoes the writes
already made. It raises `KeyError` when no field names `old`, and returns a `NodeRenameResult`:
the fields and `NodeList` entries rewritten, and each changed object once.

::: idfkit.document.IDFDocument.rename_node

::: idfkit.hvac
