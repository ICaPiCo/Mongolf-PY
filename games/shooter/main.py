import random
import pyxel
import math

class Game:
    def __init__(self):
        pyxel.init(600, 500, "Top Shooter", display_scale=2, fps=70)
        pyxel.load("my_resource.pyxres")
        self.terrain = Terrain()
        self.enemies = Enemies()
        self.player = Player(self.enemies)
        self.score = 0
        self.game_over = False
        pyxel.run(self.update, self.draw)
    
    def update(self):
        if not self.game_over:
            self.terrain.update()
            self.enemies.update()
            self.player.update()

    def draw(self):
        if not self.game_over:
            pyxel.cls(0)
            self.terrain.draw()
            self.enemies.draw()
            self.player.draw()
    
class Player:
    def __init__(self, enemies):
        self.x = 400
        self.y = 280
        self.bulletSpeed = 20
        self.shots = []
        self.enemies = enemies

    def shootNow(self):
        if pyxel.frame_count % 3 == 0:
            self.shots.append([self.x, self.y, False])

    def checkBulletCollision(self, bullet, enemie):
        distance = math.sqrt((bullet[0] - enemie[0])**2 + (bullet[1] - enemie[1])**2)
        return distance < 24

    def updateBullets(self):
        for shot in self.shots:
            shot[1] -= self.bulletSpeed
            for i in self.enemies.enemies:
                shot[2] = self.checkBulletCollision((shot[0],shot[1]),i)
                if shot[2] == True: 
                    i[2] -= 1
                    break
        self.shots = [shot for shot in self.shots if shot[1] > -10 and shot[2] == False]

    def update(self):
        self.updateBullets()
        if pyxel.btn(pyxel.KEY_UP):
            self.y -= 5
        if pyxel.btn(pyxel.KEY_DOWN):
            self.y += 5
        if pyxel.btn(pyxel.KEY_LEFT):
            self.x -= 6
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x += 6
        if pyxel.btn(pyxel.KEY_SPACE):
            self.shootNow()

    def draw(self):
        for shot in self.shots:
            pyxel.blt(shot[0],shot[1],0,32,0,16,16,colkey=0, scale=2)
        pyxel.blt(self.x, self.y, 0, 0, 0, 16, 16, 0, scale=2)

class Enemies:
    def __init__(self):
        self.enemies = []
        self.enemieSpeed = 1

    def update(self):
        if pyxel.frame_count % 60 == 0:
            x = random.randint(60, pyxel.width-60)
            self.enemies.append([x, -10, 10])        

        for enemie in self.enemies:
            enemie[1] += self.enemieSpeed
            if enemie[2] < 0:
                self.score+=1

        self.enemies = [enemie for enemie in self.enemies if enemie[1] < pyxel.height+10 and enemie[2] > 0]

    def draw(self):
        for enemie in self.enemies:
            pyxel.blt(enemie[0],enemie[1],0,16,0,16,16,colkey=0, scale=2)

class Terrain:
    def __init__(self):
        self.speed = 10
        self.stars = []

    def doStars(self):
        if pyxel.frame_count % 5 == 0:
            x = random.randint(0, pyxel.width)
            self.stars.append([x, -10, random.randint(4,10)])

        for star in self.stars:
            star[1] += star[2]

        self.stars = [star for star in self.stars if star[1] < pyxel.height + 10]

    def update(self):
        self.doStars()
        

    def draw(self):
        for star in self.stars:
            pyxel.circ(star[0], star[1], random.randint(star[2]-5,star[2]-3), random.choice((pyxel.COLOR_WHITE,pyxel.COLOR_ORANGE,pyxel.COLOR_CYAN,pyxel.COLOR_GREEN,pyxel.COLOR_LIGHT_BLUE,pyxel.COLOR_LIME,pyxel.COLOR_PEACH,pyxel.COLOR_PINK, pyxel.COLOR_PURPLE, pyxel.COLOR_RED)))
        
Game()