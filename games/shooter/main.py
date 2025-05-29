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
        self.smokeSpeed = 2
        self.shots = []
        self.particles = []
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

    def getDistance(self, object1, object2):
        return math.sqrt((object1[0] - object2[0])**2 + (object1[1] - object2[1])**2)

    def powerSmoke(self):
        if pyxel.frame_count % 2 == 0:
            self.particles.append([self.x+8, self.y+14, False])

        for particle in self.particles:
            particle[1] += self.smokeSpeed

        self.particles = [particle for particle in self.particles if particle[1] < pyxel.width+20 and particle[2] == False]

        for particle in self.particles:
            particleDistance = self.getDistance((particle[0], particle[1]), (self.x+8, self.y+14))
            if  particleDistance < 10:
                pyxel.circ(particle[0], particle[1], random.randint(1,3), 7)
            elif particleDistance < 15:
                pyxel.circ(particle[0], particle[1], random.randint(4, 6), 8)
            elif particleDistance < 25:
                pyxel.circ(particle[0], particle[1], random.randint(7, 9), 9)
            elif particleDistance < 35:
                pyxel.circ(particle[0], particle[1], random.randint(3, 5), 10)
            elif particleDistance < 60:
                pyxel.dither(random.randint(5, 10) / 10)
                pyxel.circ(random.randint(particle[0]-5,particle[0]+5), random.randint(particle[1]-5,particle[1]+5), random.randint(2, 4), 13)
                pyxel.dither(1)
            elif particleDistance < 65:
                pyxel.dither(random.randint(0, 5) / 10)
                pyxel.circ(random.randint(particle[0]-2,particle[0]+2), random.randint(particle[1]-2,particle[1]+2), random.randint(2, 4), 13)
                pyxel.dither(1)
            else:
                particle[2] = True

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
        self.powerSmoke()
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
            pyxel.circ(star[0], star[1], random.randint(star[2]-5,star[2]-3), pyxel.COLOR_WHITE)
        
Game()