import MySQLdb
import globals

class Database:
    host = ""
    user = ""
    password = ""
    port = ""
    db = ""
    conn = None

    lastinsertedspawn2id = 0
    lastinsertedspawngroupid = 0
    lastinsertedgridid = 0

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

    def UpdateDbGridPoint(self, gridpoint):
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        query = """UPDATE grid_entries SET x = %s, y = %s, z = %s, heading = %s WHERE gridid = %s AND zoneid = %s AND number = %s ;"""
        values = (gridpoint.x, gridpoint.y, gridpoint.z, gridpoint.heading, gridpoint.gridid, gridpoint.zoneid, gridpoint.number)

        cursor.execute(query, values)

        print "grid updated!"

    def GetDbGridIdsByZoneId(self, zoneid):
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        query = """SELECT DISTINCT id FROM grid WHERE zoneid=""" + str(zoneid) +";"

        cursor.execute(query)
        return cursor

    def GetDbGridPointsData(self,gridid, zoneid):
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        query = """SELECT * FROM  grid_entries ge WHERE ge.gridid = %s AND ge.zoneid = %s """
        values = (gridid, zoneid)

        cursor.execute(query, values)
        return cursor

    def GetDbGridTypesData(self, gridid, zoneid):
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        query = """SELECT * FROM  grid g WHERE g.gridid = %s AND g.zoneid = %s """
        values = (gridid, zoneid)

        cursor.execute(query, values)
        return cursor

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

    # Gets the next available id value for the Spawn2 table
    def GetNextSpawn2Id(self):
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        query = "SELECT * FROM spawn2 ORDER BY ID DESC LIMIT 1"
        cursor.execute(query)

        row = cursor.fetchone()
        lastId = 0
        if row:
            lastId = row["id"] + 1
        return lastId

    # Gets the next available id value for the Spawngroup table
    def GetNextSpawnGroupId(self):
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        query = "SELECT * FROM spawngroup ORDER BY ID DESC LIMIT 1"
        cursor.execute(query)
        row = cursor.fetchone()
        lastId = 0
        if row:
            lastId = row["id"] + 1
        return lastId

    #Gets the next available Grid id value from the Grids table
    def GetNextGridId(self, zoneid):
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        query = "SELECT * FROM grid WHERE zoneid=" + str(zoneid) +" ORDER BY ID DESC LIMIT 1"
        cursor.execute(query)
        row = cursor.fetchone()
        lastId = 0
        if row:
            lastId = row["id"] + 1
        return lastId

    # Gets the next available Grid 'number' value from the Grid Entries table
    def GetNextGridNumber(self, gridid, zoneid):
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        query = "SELECT * FROM grid_entries WHERE gridid=%s AND zoneid=%s ORDER BY number DESC LIMIT 1"
        values = (gridid, zoneid)
        cursor.execute(query, values)
        row = cursor.fetchone()
        lastId = 0
        if row:
            lastId = row["number"] + 1

        # no grid entry exist yet, but Number cannot be 0, entries start at 1
        if lastId == 0:
            lastId = 1
        return lastId

    # Inserts a new grid
    def InsertNewGrid(self, gridpoint):

        nextgridid = self.GetNextGridId(gridpoint.zoneid)
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        query ="""INSERT INTO grid(id, zoneid, type, type2) VALUES (%s, %s, %s, %s);"""
        values = (nextgridid, gridpoint.zoneid, gridpoint.type, gridpoint.type2)
        cursor.execute(query, values)

        self.conn.commit()

        print("1 grid inserted, ID:", nextgridid)
        self.lastinsertedgridid = nextgridid

    def InsertNewGridEntry(self, gridpoint):
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        query = """INSERT INTO grid_entries(gridid, zoneid,number,x,y,z,heading,pause) VALUES
                    (%s,%s,%s,%s,%s,%s,%s,%s);"""
        nextgridnumber = str(self.GetNextGridNumber(gridpoint.gridid, gridpoint.zoneid))
        values = (gridpoint.gridid, gridpoint.zoneid, nextgridnumber,
                  gridpoint.x, gridpoint.y, gridpoint.z, gridpoint.heading, gridpoint.pause)
        cursor.execute(query, values)

        self.conn.commit()

        print("1 grid entry inserted!"),


    # Gets the name of an NPC based on its ID
    def GetNpcNameById(self, npcid):
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        query = "SELECT name FROM npctypes where id = " + npcid
        cursor.execute(query)
        row = cursor.fetchone()
        name = ""
        if row:
            name = row["name"]
        return name

    # Inserts a new row into the Spawn2 table with the provided Spawn data
    # 1. Insert a new spawngroup entry
    # 2. Insert a new spawn2 entry referencing the previously inserted spawngroupID
    # 3. Inser a new spawnentry referencing both previously inserted spawn IDs
    def InsertNewSpawn(self, spawn):

        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        query = """ INSERT INTO spawngroup(name, spawn_limit, dist, max_x, min_x, max_y, min_y, delay, mindelay, despawn, despawn_timer)
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"""
        values = (spawn.spawngroup_name, spawn.spawngroup_spawnlimit, spawn.spawngroup_dist, spawn.spawngroup_maxx, spawn.spawngroup_minx, spawn.spawngroup_maxy, spawn.spawngroup_miny, spawn.spawngroup_delay, spawn.spawngroup_mindelay, spawn.spawngroup_despawn, spawn.spawngroup_despawntimer)
        cursor.execute(query, values)
        self.conn.commit()
        print("1 spawngroup inserted, ID:", cursor.lastrowid)
        self.lastinsertedspawngroupid = cursor.lastrowid

        query = """INSERT INTO spawn2(spawngroupID,zone, version, x,y,z,heading,respawntime,variance,pathgrid,_condition,cond_value,enabled, 
        animation) VALUES (%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s,%s);"""
        values = (self.lastinsertedspawngroupid, spawn.spawnentry_zone, spawn.spawnentry_version ,spawn.spawnentry_x,spawn.spawnentry_y ,spawn.spawnentry_z , spawn.spawnentry_heading,spawn.spawnentry_respawn ,spawn.spawnentry_variance ,spawn.spawnentry_pathgrid ,spawn.spawnentry_condition ,spawn.spawnentry_condvalue ,spawn.spawnentry_enabled ,spawn.spawnentry_animation )
        cursor.execute(query, values)
        self.conn.commit()
        print("1 record inserted, ID:", cursor.lastrowid)
        self.lastinsertedspawn2id = cursor.lastrowid

        query = "INSERT INTO spawnentry(spawngroupID, npcID, chance) VALUES (%s, %s, %s);"
        values = self.lastinsertedspawngroupid, spawn.spawnentry_npcid, spawn.spawnentry_chance
        cursor.execute(query, values)


    # Update the spawn's db records
    def UpdateSpawn(self, spawn):

        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        query = """UPDATE spawnentry SET chance = %s WHERE spawngroupID = %s AND npcID = %s;"""
        values = (spawn.spawnentry_chance, spawn.spawngroup_id, spawn.spawnentry_npcid)
        cursor.execute(query, values)
        self.conn.commit()
        print("spawnentry updated")

        query = """UPDATE spawn2 SET spawngroupID = %s, zone = %s, version = %s, x = %s, y = %s, z = %s, heading = %s
        , respawntime = %s, variance = %s, pathgrid = %s, _condition = %s, cond_value = %s, enabled = %s, animation = %s
        WHERE id = %s and spawngroupID = %s;"""
        values = (spawn.spawngroup_id, spawn.spawnentry_zone, spawn.spawnentry_version ,spawn.spawnentry_x,spawn.spawnentry_y ,spawn.spawnentry_z , spawn.spawnentry_heading,spawn.spawnentry_respawn ,spawn.spawnentry_variance ,spawn.spawnentry_pathgrid ,spawn.spawnentry_condition ,spawn.spawnentry_condvalue ,spawn.spawnentry_enabled ,spawn.spawnentry_animation, spawn.spawnentry_id, spawn.spawngroup_id )
        cursor.execute(query, values)
        self.conn.commit()
        print ("spawn2 updated")

        query = """UPDATE spawngroup SET name = %s, spawn_limit = %s, dist = %s, max_x = %s, min_x = %s, max_y = %s, min_y = %s, delay = %s, mindelay = %s, despawn = %s, despawn_timer = %s
                WHERE id = %s;"""
        values = (spawn.spawngroup_name, spawn.spawngroup_spawnlimit, spawn.spawngroup_dist, spawn.spawngroup_maxx, spawn.spawngroup_minx, spawn.spawngroup_maxy, spawn.spawngroup_miny, spawn.spawngroup_delay, spawn.spawngroup_mindelay, spawn.spawngroup_despawn, spawn.spawngroup_despawntimer, spawn.spawngroup_id)
        cursor.execute(query, values)
        self.conn.commit()
        print("spawngroup updated")

    # Deletes a complete spawn from the database and all its associated Spawngroup, Spawn2 and Spawnentry entries
    def DeleteSpawn(self, spawn):
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        query = """DELETE FROM spawnentry WHERE spawngroupID = %t and npcID = %t;"""
        values = (spawn.spawngroup_id, spawn.spawnentry_id)
        cursor.execute(query, values)
        self.conn.commit()
        print("Spawn entry deleted successfully.")

        query = """DELETE FROM spawn2 where spawngroupID = %s AND id = %s"""
        values = (spawn.spawngroup_id, spawn.spawnentry_id)
        cursor.execute(query, values)
        self.conn.commit()
        print("Spawn2 deleted successfully.")

        query = """DELETE FROM spawngroup where id = %s"""
        values = (spawn.spawngroup_id)
        cursor.execute(query, values)
        self.conn.commit()
        print ("Spawngroup deleted successfully.")

    def GetNpcNameById(self, npcid):
        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        query = "SELECT name FROM npc_types where id =" + str(npcid) + ";"
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            return row["name"]


