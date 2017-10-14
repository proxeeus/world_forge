# spawn_tool (temp name)
Fork of Panda_Zonewalk, the goal is to develop an EQEmu World Editor (spawns, waypoints etc).

The rough idea as of now would be to have a tool capable of:

- opening a zone in a 3D-view
- fetching spawn data from an EQEmu database
- loading spawn data/points into the 3D view as basic shapes
- clicking on those objects would let us manipulate their position in real time and update the coordinates into the db
- waypoints would be governed by the same set of principles
- additionally, this kind of functionality could be extended into a fully-fledged world editor

As of right now, it is possible to load a fully-textured zone and explore it.
Basic 3D objects interaction is currently being worked on (clicking on models, moving them through the zone...)

As soon as this step is completed, work will start on basic GUI elements, and establishing a MySQL connection.