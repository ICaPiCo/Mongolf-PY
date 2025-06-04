import random
import pyxel
import math

class Shooter:
    def __init__(self):
        pyxel.load("shooter.pyxres")
        self.terrain = Terrain()
        self.enemies = Enemies()
        self.player = Player(self.enemies)
        self.score = 0
        self.game_over = False
    
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
        self.x = pyxel.width//2
        self.y = pyxel.height*2//3
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
                    # Check if enemy has 1 life left before reducing it
                    if i[2] == 1:
                        # Trigger death animation
                        self.enemies.createExplosion(i[0], i[1])
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
                pyxel.circ(random.randint(particle[0]-2,particle[0]+2), random.randint(particle[1]-2,particle[1]+2), random.randint(1, 2), 13)
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
        self.explosions = []
        self.nbTargetOfEnemies = 20

    def enemiesLeftText(self):
        winText = "YOU WIN !!!"
        if self.nbTargetOfEnemies < 0:
            self.nbTargetOfEnemies = 0
        elif self.nbTargetOfEnemies == 0:
            pyxel.text(((pyxel.width-len(winText)*4)/2),50,winText,7)
        else:
            pyxel.text(0,0,f"Enemies left to kill:{self.nbTargetOfEnemies}",7)

    def createExplosion(self, x, y):
        # Create explosion particles at enemy position
        self.nbTargetOfEnemies -= 1
        for _ in range(15):
            particle_x = x + random.randint(-10, 10)
            particle_y = y + random.randint(-10, 10)
            velocity_x = random.uniform(-3, 3)
            velocity_y = random.uniform(-3, 3)
            life = random.randint(20, 40)
            max_life = life  # Store original life for fade calculation
            size = random.randint(2, 6)
            color = random.choice([8, 9, 10, 14])  # Red, orange, yellow colors
            self.explosions.append([particle_x, particle_y, velocity_x, velocity_y, life, size, color, max_life])

    def updateExplosions(self):
        for explosion in self.explosions:
            # Update position
            explosion[0] += explosion[2]  # x += velocity_x
            explosion[1] += explosion[3]  # y += velocity_y
            # Reduce life
            explosion[4] -= 1
            # Reduce size over time
            if explosion[4] < 10:
                explosion[5] = max(1, explosion[5] - 0.2)
        
        # Remove dead explosion particles
        self.explosions = [explosion for explosion in self.explosions if explosion[4] > 0]

    def update(self):
        if pyxel.frame_count % 60 == 0 and self.nbTargetOfEnemies > 0:
            x = random.randint(60, pyxel.width-60)
            self.enemies.append([x, -10, 10])        

        for enemie in self.enemies:
            enemie[1] += self.enemieSpeed

        # Update explosions
        self.updateExplosions()

        # Remove enemies that are off screen or have no life
        self.enemies = [enemie for enemie in self.enemies if enemie[1] < pyxel.height+10 and enemie[2] > 0]

    def draw(self):
        # Draw enemies
        for enemie in self.enemies:
            pyxel.blt(enemie[0],enemie[1],0,16,0,16,16,colkey=0, scale=2)
        
        # Draw explosions with fade effect
        for explosion in self.explosions:
            # Calculate fade based on remaining life (0.0 to 1.0)
            fade_factor = explosion[4] / explosion[7]  # current_life / max_life
            
            # Use dither for transparency effect
            if fade_factor > 0.7:
                # Full opacity - no dither
                pyxel.circ(explosion[0], explosion[1], explosion[5], explosion[6])
            elif fade_factor > 0.4:
                # Medium transparency
                pyxel.dither(0.7)
                pyxel.circ(explosion[0], explosion[1], explosion[5], explosion[6])
                pyxel.dither(1.0)  # Reset dither
            elif fade_factor > 0.2:
                # High transparency
                pyxel.dither(0.4)
                pyxel.circ(explosion[0], explosion[1], explosion[5], explosion[6])
                pyxel.dither(1.0)  # Reset dither
            else:
                # Very high transparency
                pyxel.dither(0.2)
                pyxel.circ(explosion[0], explosion[1], explosion[5], explosion[6])
                pyxel.dither(1.0)  # Reset dither
    
        self.enemiesLeftText()

class Terrain:
    def __init__(self):
        self.speed = 10
        self.earth = False
        self.sea = False
        self.sky = False    
        self.space = True
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
        if self.space:
            for star in self.stars:
                pyxel.circ(star[0], star[1], random.randint(star[2]-5,star[2]-3), pyxel.COLOR_WHITE)