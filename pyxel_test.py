import pyxel

screen_x,screen_y = 192, 120

class Balloon:
    xAxis=0
    yAxis=2
    rotation=0
    scale=0

    def __init__(self, name):
        self.name = name        

    def update(self):
        if self.rotation >= 360:
            self.rotation = 0

        if pyxel.btn(pyxel.KEY_Z):
            self.yAxis-=0.1
        elif pyxel.btn(pyxel.KEY_S):
            self.yAxis+=0.1
        elif pyxel.btn(pyxel.KEY_Q):
            self.xAxis+=0.1
        elif pyxel.btn(pyxel.KEY_D):
            self.xAxis-=0.1
        elif pyxel.btn(pyxel.KEY_A):
            self.rotation+=1
        elif pyxel.btn(pyxel.KEY_E):
            self.rotation-=1
        elif pyxel.btn(pyxel.KEY_UP):
            self.scale+=0.1
        elif pyxel.btn(pyxel.KEY_DOWN):
            self.scale-=0.1
        else:
            pass
        
    def draw(self):
        pyxel.cls(0)
        imgX, imgY = self.getSpriteCenter()
        imgY+=10
        pyxel.blt(imgX, imgY, (0), 0, 0, 8, 8, colkey=0, scale=self.scale+1, rotate=self.rotation)

        for i in range(3):
            pyxel.blt(imgX, (imgY), (0), 8, 0, 8, 8, colkey=0, scale=self.scale+1, rotate=self.rotation)
            imgY-=self.yAxis
            imgX-=self.xAxis

        pyxel.blt(imgX, imgY, (0), 0, 8, 8, 8, colkey=0, scale=self.scale+1, rotate=self.rotation)
        imgY-=self.yAxis
        imgX-=self.xAxis
        
        for i in range(3):
            pyxel.blt(imgX, (imgY), (0), 8, 8, 8, 8, colkey=0, scale=self.scale+1, rotate=self.rotation)
            imgY-=self.yAxis
            imgX-=self.xAxis

        pyxel.blt(imgX, imgY, (0), 16, 8, 8, 8, colkey=0, scale=self.scale+1, rotate=self.rotation)
        imgY-=self.yAxis
        imgX-=self.xAxis

        pyxel.blt(imgX, imgY, (0), 24, 0, 8, 8, colkey=0, scale=self.scale+3, rotate=self.rotation)
        imgY-=self.yAxis
        imgX-=self.xAxis

        pyxel.blt(imgX, imgY, (0), 24, 8, 8, 8, colkey=0, scale=self.scale+3, rotate=self.rotation)
        imgY-=self.yAxis
        imgX-=self.xAxis

        pyxel.blt(imgX, imgY, (0), 32, 0, 8, 8, colkey=0, scale=self.scale+3, rotate=self.rotation)
        imgY-=self.yAxis
        imgX-=self.xAxis

        pyxel.blt(imgX, imgY, (0), 24, 8, 8, 8, colkey=0, scale=self.scale+3, rotate=self.rotation)
        imgY-=self.yAxis
        imgX-=self.xAxis

        pyxel.blt(imgX, imgY, (0), 24, 0, 8, 8, colkey=0, scale=self.scale+3, rotate=self.rotation)
        imgY-=self.yAxis
        imgX-=self.xAxis

        pyxel.blt(imgX, imgY, (0), 16, 8, 8, 8, colkey=0, scale=self.scale+3, rotate=self.rotation)
        imgY-=self.yAxis
        imgX-=self.xAxis

        pyxel.text(0, 0, self.name, 7)

    def getTextSize(self, text):
        return len(text)*4, 8

    def getTextCenter(self, text):
        text_width, text_height = self.getTextSize(text)
        return (screen_x - text_width) / 2, (screen_y - text_height) / 2

    def getSpriteCenter(self):
        return (screen_x - 4) / 2, (screen_y - 4) / 2

mongol = Balloon("mongol")

pyxel.init(screen_x, screen_y, title="Balloon", display_scale=9)
pyxel.load("my_resource.pyxres")
pyxel.run(mongol.update,mongol.draw)