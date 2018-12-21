def init():
    global spawndialog,griddialog, picker, selectedSpawnXYZ,selectedGridXYZ, selectedSpawnPoint3D,selectedGridPoint3D, spawn_list, hasClickedSpawn, hasClickedGrid, exploreMode, insertMode, editMode, currentZone, database, config, selectedSpawn, selectedGrid, grid_list, zoneid, gridlinks_list
    config, selectedSpawn, spawndialog, griddialog, picker, selectedSpawnXYZ,selectedGridXYZ, selectedSpawnPoint3D,selectedGridPoint3D, spawn_list, database, selectedGrid, grid_list, gridlinks_list = None
    zoneid = 0


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

def getgridfromglobalgridsbyname(gridid, number):
    for x in grid_list:
        if str(x.gridid == gridid) and str(x.number == number):
            return x

def getzoneidbyname(zonename):
    if zonename == 'qeynos':
        return 1
    elif zonename == 'qeynos2':
        return 2
    elif zonename == 'qrg':
        return 3
    elif zonename == 'qeytoqrg':
        return 4
    elif zonename == 'highpass':
        return 5
    elif zonename == 'highkeep':
        return 6
    elif zonename == 'freportn':
        return 8
    elif zonename == 'freportw':
        return 9
    elif zonename == 'freporte':
        return 10
    elif zonename == 'runnyeye':
        return 11
    elif zonename == 'qey2hh1':
        return 12
    elif zonename == 'northkarana':
        return 13
    elif zonename == 'southkarana':
        return 14
    elif zonename == 'eastkarana':
        return 15
    elif zonename == 'beholder':
        return 16
    elif zonename == 'blackburrow':
        return 17
    elif zonename == 'paw':
        return 18
    elif zonename == 'rivervale':
        return 19
    elif zonename == 'kithicor':
        return 20
    elif zonename == 'commons':
        return 21
    elif zonename == 'ecommons':
        return 22
    elif zonename == 'erudnint':
        return 23
    elif zonename == 'erudnext':
        return 24
    elif zonename == 'nektulos':
        return 25
    elif zonename == 'cshome':
        return 26
    elif zonename == 'lavastorm':
        return 27
    elif zonename == 'halas':
        return 29
    elif zonename == 'everfrost':
        return 30
    elif zonename == 'soldunga':
        return 31
    elif zonename == 'soldungb':
        return 32
    elif zonename == 'misty':
        return 33
    elif zonename == 'nro':
        return 34
    elif zonename == 'sro':
        return 35
    elif zonename == 'befallen':
        return 36
    elif zonename == 'oasis':
        return 37
    elif zonename == 'tox':
        return 38
    elif zonename == 'hole':
        return 39
    elif zonename == 'neriaka':
        return 40
    elif zonename == 'neriakb':
        return 41
    elif zonename == 'neriakc':
        return 42
    elif zonename == 'najena':
        return 44
    elif zonename == 'qcat':
        return 45
    elif zonename == 'innothule':
        return 46
    elif zonename == 'feerrott':
        return 47
    elif zonename == 'cazicthule':
        return 48
    elif zonename == 'oggok':
        return 49
    elif zonename == 'rathemtn':
        return 50
    elif zonename == 'lakerathe':
        return 51
    elif zonename == 'grobb':
        return 52
    elif zonename == 'gfaydark':
        return 54
    elif zonename == 'akanon':
        return 55
    elif zonename == 'steamfont':
        return 56
    elif zonename == 'lfaydark':
        return 57
    elif zonename == 'crushbone':
        return 58
    elif zonename == 'mistmoore':
        return 59
    elif zonename == 'kaladima':
        return 60
    elif zonename == 'kaladimb':
        return 67
    elif zonename == 'felwithea':
        return 61
    elif zonename == 'felwitheb':
        return 62
    elif zonename == 'unrest':
        return 63
    elif zonename == 'kedge':
        return 64
    elif zonename == 'guktop':
        return 65
    elif zonename == 'gukbottom':
        return 66
    elif zonename == 'butcher':
        return 68
    elif zonename == 'oot':
        return 69
    elif zonename == 'cauldron':
        return 70
    elif zonename == 'airplane':
        return 71
    elif zonename == 'fearplane':
        return 72
    elif zonename == 'permafrost':
        return 73
    elif zonename == 'kerraridge':
        return 74
    elif zonename == 'paineel':
        return 75
    elif zonename == 'hateplane':
        return 76
    elif zonename == 'arena':
        return 77
    elif zonename == 'fieldofbone':
        return 78
    elif zonename == 'warslikswood':
        return 79
    elif zonename == 'soltemple':
        return 80
    elif zonename == 'droga':
        return 81
    elif zonename == 'cabwest':
        return 82
    elif zonename == 'swampofnohope':
        return 83
    elif zonename == 'firiona':
        return 84
    elif zonename == 'lakeofillomen':
        return 85
    elif zonename == 'dreadlands':
        return 86
    elif zonename == 'burningwood':
        return 87
    elif zonename == 'kaesora':
        return 88
    elif zonename == 'sebilis':
        return 89
    elif zonename == 'citymist':
        return 90
    elif zonename == 'skyfire':
        return 91
    elif zonename == 'frontiermtns':
        return 92
    elif zonename == 'overthere':
        return 93
    elif zonename == 'emeraldjungle':
        return 94
    elif zonename == 'trakanon':
        return 95
    elif zonename == 'timorous':
        return 96
    elif zonename == 'kurn':
        return 97
    elif zonename == 'erudsxing':
        return 98
    elif zonename == 'stonebrunt':
        return 100
    elif zonename == 'warrens':
        return 101
    elif zonename == 'karnor':
        return 102
    elif zonename == 'chardok':
        return 103
    elif zonename == 'dalnir':
        return 104
    elif zonename == 'charasis':
        return 105
    elif zonename == 'cabeast':
        return 106
    elif zonename == 'nurga':
        return 107
    elif zonename == 'veeshan':
        return 108
    elif zonename == 'veksar':
        return 109
    elif zonename == 'iceclad':
        return 110
    elif zonename == 'frozenshadow':
        return 111
    elif zonename == 'velketor':
        return 112
    elif zonename == 'kael':
        return 113
    elif zonename == 'skyshrine':
        return 114
    elif zonename == 'thurgadina':
        return 115
    elif zonename == 'eastwastes':
        return 116
    elif zonename == 'cobaltscar':
        return 117
    elif zonename == 'greatdivide':
        return 118
    elif zonename == 'wakening':
        return 119
    elif zonename == 'westwastes':
        return 120
    elif zonename == 'crystal':
        return 121
    elif zonename == 'necropolis':
        return 123
    elif zonename == 'templeveeshan':
        return 124
    elif zonename == 'sirens':
        return 125
    elif zonename == 'mischiefplane':
        return 126
    elif zonename == 'growthplane':
        return 127
    elif zonename == 'sleeper':
        return 128
    elif zonename == 'thurgadinb':
        return 129