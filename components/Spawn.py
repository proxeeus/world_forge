class Spawn:

    id = 0
    name = ""
    modelname = "models/arrow.egg"
    model = ""

    def __init__(self, dbid, name):
        self.id = dbid
        self.name = name
        #self.model.setScale(50, 50, 50)
        #self.model.setColor(0.6, 0.6, 1.0, 1.0)

    def initmodel(self):
        self.model.setScale(50, 50, 50)
        self.model.setColor(0.6, 0.6, 1.0, 1.0)

    # Initializes the spawn's heading from the EQEmu db value into the 360-based value
    def initheadingfromdb(self, dbheading):
        self.model.setH(dbheading / 512 * 360 - 90)

    def placeintoworld(self, x, y, z):
        self.model.setPos(x, y, z)
