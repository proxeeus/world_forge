# World Forge - an EQEmu 3D Zone Editor
Fork of Panda_Zonewalk, the goal is to develop an EQEmu World Editor (spawns, waypoints etc).

The rough idea as of now would be to have a tool capable of:

- opening a zone in a 3D-view
- fetching spawn data from an EQEmu database
- loading spawn data/points into the 3D view as basic shapes
- clicking on those objects would let us manipulate their position in real time and update the coordinates into the db
- waypoints would be governed by the same set of principles
- additionally, this kind of functionality could be extended into a fully-fledged world editor

As of right now, it is possible to load a fully-textured zone, explore it, and have it populated with spawn data from
the configured EQEmu DB, and add/edit spawns.

Three modes are available:

- Explore mode: lets you freely explore a zone without any ability to alter spawn data
- Edit mode: lets you reposition spawns and change their headings visually by dragging them around
- Insert mode: lets you insert brand new spawns visually into the 3D World view

It is possible to fine-tune stuff by interacting with the various GUI fields, and also
possible to auto-save modifications made while using World Forge's 3D view (this setting is, like many others, configurable via the app's config file).

Waypoints & grids are on the todo list and will most likely follow the same rules.

Installation notes:

- Download Panda3D
- Install wxWidgets (the whl is in the /dependencies/ dir) with the following command 
python -m pip install "path_to_whl"
- Go to where wxWidgets has been installed (python_path\Lib\site-packages\)
- find the folder wx-<version>-msw or similar 
- move the wx folder from the above folder to \site-packages\
- do more or less the same for MySqlPython