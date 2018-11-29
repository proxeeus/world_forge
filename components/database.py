import MySQLdb
import globals

class Database:
    host = ""
    user = ""
    password = ""
    port = ""
    db = ""
    conn = None

    def __init__(self, host, user, password, port, db):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.db = db

    # Establishes a connection to the EQEmu database
    def ConnectToDatabase(self):
        self.conn = MySQLdb.Connection(
            self.host,
            self.user,
            self.password,
            self.db)

        return self.conn

    # Queries the Database in order to get spawn data
    # (this should be refactored at some point)
    def GetDbSpawnData(self):
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        query = """SELECT nt.name as NpcName, nt.id as NpcId, s2.id as Spawn2Id, s2.zone as Spawn2Zone, s2.x as Spawn2X, s2.y as Spawn2Y, s2.z as Spawn2Z, 
                s2.heading as Spawn2Heading, s2.respawntime as Spawn2Respawn, s2.variance as Spawn2Variance, s2._condition as Spawn2Condition,
                s2.cond_value as Spawn2CondValue, s2.pathgrid as Spawn2Grid, s2.enabled as Spawn2Enabled,
                s2.version as Spawn2Version, s2.animation as Spawn2Animation,
                sg.name as spawngroup_name,sg.id as Spawngroup_id, sg.min_x as Spawngroup_minX, sg.max_x as Spawngroup_maxX,
                sg.min_y as Spawngroup_minY, sg.max_y as Spawngroup_maxY, sg.dist as Spawngroup_dist, sg.mindelay as Spawngroup_mindelay,
                sg.delay as Spawngroup_delay, sg.despawn_timer as Spawngroup_despawntimer,
                sg.spawn_limit as Spawngroup_spawnlimit, se.chance as Spawnentry_chance FROM spawn2 s2
                JOIN spawngroup sg ON sg.id = s2.spawngroupid
                JOIN spawnentry se
                ON se.spawngroupid = sg.id
                JOIN npc_types nt
                ON nt.id = se.npcid
                WHERE s2.zone = '""" + globals.currentZone + "'"
        cursor.execute(query)
        return cursor