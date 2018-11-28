def init():
    global spawndialog, selectedSpawnXYZ, selectedSpawnPoint3D, spawn_list, hasClickedSpawn, exploreMode, insertMode, editMode, currentZone
    spawndialog, selectedSpawnXYZ, selectedSpawnPoint3D, spawn_list = None


def addspawntolist(spawn):
    spawn_list.append(spawn)

def getspawnfromglobalspawnsbyname(spawn2Id):
    for x in spawn_list:
        if str(x.spawnentry_id) == spawn2Id:
            return x
