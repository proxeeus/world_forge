def init():
    global spawndialog, selectedSpawnXYZ, selectedSpawnPoint3D, spawn_list, hasClickedSpawn, exploreMode, insertMode, editMode, currentZone, database, config, selectedSpawn
    config, selectedSpawn, spawndialog, selectedSpawnXYZ, selectedSpawnPoint3D, spawn_list, database = None


def addspawntolist(spawn):
    spawn_list.append(spawn)

def getspawnfromglobalspawnsbyname(spawn2Id):
    for x in spawn_list:
        if str(x.spawnentry_id) == str(spawn2Id):
            return x

def deletespawnfromglobalspawnsbyid(spawn2Id):
    for x in spawn_list:
        if str(x.spawnentry_id) == spawn2Id:
            spawn = x
            spawn_list.remove(spawn)
