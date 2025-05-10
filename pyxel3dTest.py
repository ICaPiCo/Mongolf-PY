import pyxel
from math import *

screen_x,screen_y = int(1920/4), int(1200/4)

class Balloon:
    xAxis=0
    yAxis=2
    rotation=0
    scale=0
    letterSize=16
    big=3
    medium=2

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
            self.xAxis-=0.1
        elif pyxel.btn(pyxel.KEY_D):
            self.xAxis+=0.1
        elif pyxel.btn(pyxel.KEY_A):
            self.rotation-=1
        elif pyxel.btn(pyxel.KEY_E):
            self.rotation+=1
        elif pyxel.btn(pyxel.KEY_UP):
            self.scale+=0.1
        elif pyxel.btn(pyxel.KEY_DOWN):
            self.scale-=0.1
        else:
            pass
        
    def draw(self):
        pyxel.cls(0)
        pyxel.blt(0, 0, (1), 0, 0, 256, 256, colkey=0, scale=self.scale+1)
        imgX, imgY = self.getSpriteCenter()
        imgY+=10
        pyxel.blt(imgX, imgY, (0), 0, 0, 8, 8, colkey=0, scale=self.scale+1, rotate=self.rotation)

        for i in range(3*self.big):
            pyxel.blt(imgX, (imgY), (0), 8, 0, 8, 8, colkey=0, scale=self.scale+1, rotate=self.rotation)
            imgY-=self.yAxis/self.big
            imgX-=self.xAxis/self.big

        pyxel.blt(imgX, imgY, (0), 0, 8, 8, 8, colkey=0, scale=self.scale+1, rotate=self.rotation)
        imgY-=self.yAxis
        imgX-=self.xAxis
        
        for i in range(3*self.big):
            pyxel.blt(imgX, (imgY), (0), 8, 8, 8, 8, colkey=0, scale=self.scale+1, rotate=self.rotation)
            imgY-=self.yAxis/self.big
            imgX-=self.xAxis/self.big

        pyxel.blt(imgX, imgY, (0), 16, 8, 8, 8, colkey=0, scale=self.scale+1, rotate=self.rotation)
        imgY-=self.yAxis
        imgX-=self.xAxis

        pyxel.blt(imgX, imgY, (0), 24, 0, 8, 8, colkey=0, scale=self.scale+6, rotate=self.rotation)
        imgY-=self.yAxis
        imgX-=self.xAxis

        pyxel.blt(imgX, imgY, (0), 24, 8, 8, 8, colkey=0, scale=self.scale+6, rotate=self.rotation)
        imgY-=self.yAxis
        imgX-=self.xAxis

        pyxel.blt(imgX, imgY, (0), 32, 0, 8, 8, colkey=0, scale=self.scale+6, rotate=self.rotation)
        imgY-=self.yAxis
        imgX-=self.xAxis

        pyxel.blt(imgX, imgY, (0), 24, 8, 8, 8, colkey=0, scale=self.scale+6, rotate=self.rotation)
        imgY-=self.yAxis
        imgX-=self.xAxis

        pyxel.blt(imgX, imgY, (0), 24, 0, 8, 8, colkey=0, scale=self.scale+6, rotate=self.rotation)
        imgY-=self.yAxis
        imgX-=self.xAxis

        pyxel.blt(imgX, imgY, (0), 16, 8, 8, 8, colkey=0, scale=self.scale+6, rotate=self.rotation)
        imgY-=self.yAxis
        imgX-=self.xAxis

        textRealScale=0.5

        pyxel.blt(self.letterSize*0.5, self.letterSize*0.5, (0), 0, 16, 16, 16, colkey=0, scale=textRealScale, rotate=self.rotation)
        pyxel.blt(self.letterSize*0.5*2, self.letterSize*0.5, (0), 16, 16, 16, 16, colkey=0, scale=textRealScale, rotate=self.rotation)
        pyxel.blt(self.letterSize*0.5*3, self.letterSize*0.5, (0), 32, 16, 16, 16, colkey=0, scale=textRealScale, rotate=self.rotation)
        pyxel.blt(self.letterSize*0.5*4, self.letterSize*0.5, (0), 48, 16, 16, 16, colkey=0, scale=textRealScale, rotate=self.rotation)
        pyxel.blt(self.letterSize*0.5*5, self.letterSize*0.5, (0), 64, 16, 16, 16, colkey=0, scale=textRealScale, rotate=self.rotation)

        pyxel.text(0,0,f"xAxis: {(trunc(self.xAxis*10))/10}, yAxis: {(trunc(self.yAxis*10))/10}, rotation: {self.rotation}, scale: {(trunc(self.scale*10))/10}",7)

    def getTextSize(self, text):
        return len(text)*4, 8

    def getTextCenter(self, text):
        text_width, text_height = self.getTextSize(text)
        return (screen_x - text_width) / 2, (screen_y - text_height) / 2

    def getSpriteCenter(self):
        return (screen_x - 4) / 2, (screen_y - 4) / 2

mongol = Balloon("mongol")

pyxel.init(screen_x, screen_y, title="MONGO", display_scale=3)
pyxel.load("my_resource.pyxres")
pyxel.run(mongol.update,mongol.draw)