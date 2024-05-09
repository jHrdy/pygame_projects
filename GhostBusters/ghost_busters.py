import pygame
from math import sqrt, ceil
from random import randint
import time

width = 800
height = 600
bg_color = (35,35,35)     #'black'
keys = []                 # bude ukládat list se stlačenými klávesy
shots = []                # ukládá existuijící objekty Projectile

norm = sqrt(2)/2

mobWidth = 20
mobHeight = 30

pygame.init()

window = pygame.display.set_mode((width, height))

points = 800
font = pygame.font.SysFont("Arial", 35, bold=True, italic=False)

class Player:
    def __init__(self, xPos, yPos, playerWidth, playerHeight, speed):
        self.xPos = xPos
        self.yPos = yPos
        self.playerWidth = playerWidth
        self.playerHeight = playerHeight
        self.speed = speed
        self.player = pygame.Rect(xPos, yPos, playerWidth, playerHeight)        # vytvoření obdélníku pro hitboxy
        #self.imgLeft = pygame.transform.scale(pygame.image.load("pygame/Ghostbusters/ghostKiller.png"), (self.playerWidth, self.playerHeight)) 
        #self.imgRight = pygame.transform.scale(pygame.image.load("pygame/GhostBusters/ghostKiller_Turn.png"), (self.playerWidth, self.playerHeight))
        self.faceRight = False              # směr obrázku a střelby 
        self.imgs = (pygame.transform.scale(pygame.image.load("ghostKiller.png"), (self.playerWidth, self.playerHeight)), pygame.transform.scale(pygame.image.load("ghostKiller_Turn.png"), (self.playerWidth, self.playerHeight)))

    #get metoda pro 4 rohy obdélníku
    def getBoundaries(self):            
        leftUp = (self.yPos, self.xPos)
        rightUp = (self.yPos, self.xPos + self.playerWidth)
        leftBottom = (self.yPos + self.playerHeight, self.xPos)
        rightBottom = (self.yPos + self.playerHeight, self.xPos + self.playerWidth)

        return (leftUp, rightUp, leftBottom, rightBottom)
    
    # pobyb a prevence vycházení z plochy
    def move(self, keys):
        if keys[pygame.K_UP] and keys[pygame.K_RIGHT] and self.yPos > 1 and self.xPos < width - self.playerWidth:
            self.xPos += self.speed * norm
            self.yPos -= self.speed * norm
            self.faceRight = False
        elif keys[pygame.K_UP] and keys[pygame.K_LEFT] and self.yPos > 1 and self.xPos > 1:
            self.yPos -= self.speed * norm
            self.xPos -= self.speed * norm
            self.faceRight = True
        elif keys[pygame.K_DOWN] and keys[pygame.K_LEFT] and self.yPos < height - self.playerHeight and self.xPos > 1:
            self.yPos += self.speed * norm
            self.xPos -= self.speed * norm
        elif keys[pygame.K_DOWN] and keys[pygame.K_RIGHT] and self.yPos < height - self.playerHeight and self.xPos < width - self.playerWidth:
            self.xPos += self.speed * norm
            self.yPos += self.speed * norm
            self.faceRight = False
        elif keys[pygame.K_UP] and self.yPos > 1:
            self.yPos -= self.speed 
        elif keys[pygame.K_DOWN] and self.yPos < height - self.playerHeight:
            self.yPos += self.speed
        elif keys[pygame.K_LEFT] and self.xPos > 1:
            self.xPos -= self.speed
            self.faceRight = True 
        elif keys[pygame.K_RIGHT] and self.xPos < width - self.playerWidth:
            self.xPos += self.speed
            self.faceRight = False
        self.player = pygame.Rect(self.xPos, self.yPos, self.playerWidth, self.playerHeight)
        #pygame.draw.rect(window, 'white', self.player)
        
        # vykreslení obrázku na základě směru pohledu
        window.blit(self.imgs[self.faceRight], self.player)              # tady je to fakt vyspekulovaný pozor na to
        """if self.faceRight == False:
            window.blit(self.imgLeft, self.player)
        else:
            window.blit(self.imgRight, self.player)"""


class Mob(Player):
    def __init__(self, xPos, yPos, playerWidth, playerHeight, speed, movingDown, sideways):
        super().__init__(xPos, yPos, playerWidth, playerHeight, speed)
        self.mob =  pygame.Rect(xPos, yPos, playerWidth, playerHeight)
        self.movingDown = movingDown            # true pokud se mob začne po spawnu pohybovat dolů
        self.alive = True                   # pokud je False mob se přestane hýbat     
        self.sideways = sideways
        self.img = pygame.transform.scale(pygame.image.load("ghost.png"), (self.playerWidth, self.playerHeight))

    # pohyb Moba pokud je živý 
    # důležitá je logika pro odrážení se od krajů pomocí movingDown
    def movement(self):
        if self.alive == True:
            if self.sideways == 0:
                if self.yPos > 1 and self.movingDown == False:
                    self.yPos -= self.speed  
                elif self.yPos > height - self.playerHeight:
                    self.movingDown = False
                    self.yPos -= self.speed
                elif self.yPos - 2 < 1 or self.movingDown == True:
                    self.yPos += self.speed
                    self.movingDown = True
            else:
                if self.xPos > 1 and self.movingDown == False:
                    self.xPos -= self.speed  
                elif self.xPos > width - self.playerWidth:
                    self.movingDown = False
                    self.xPos -= self.speed
                elif self.xPos - 2 < 1 or self.movingDown == True:
                    self.xPos += self.speed
                    self.movingDown = True

        self.mob = pygame.Rect(self.xPos, self.yPos, self.playerWidth, self.playerHeight)
        window.blit(self.img, self.mob)             # vykresli obrázek ne obdélník
        #pygame.draw.rect(window, 'red', self.mob)
    
    # kolize Projektilu s Mobem 
    def checkCollision(self, Projectile):
        global points
        # následující podmínku lze nahradit vestavěnou funkcí pro pygame.rect -> colliderect()
        if Projectile.xPos < self.xPos + self.playerHeight and self.xPos < Projectile.xPos and Projectile.yPos < self.yPos + self.playerHeight and Projectile.yPos > self.yPos:       
            if self.alive == True:
                points += 100
            self.alive = False
            return True
        else:
            return False

    def lifeStatus(self):
        return self.alive

class Projectile(Player):
    def __init__(self, xPos, yPos, playerWidth, playerHeight, speed, faceRight):
        super().__init__(xPos, yPos, playerWidth, playerHeight, speed)
        self.projectile = pygame.Rect(xPos, yPos, playerWidth, playerHeight)
        self.hit = False        # když trafí moba => True a Projektil zmizí
        if faceRight == True:       # střela poletí vlevo / vpravo 
            self.direction = -1
            self.xPos -= 40
        else:
            self.direction = 1
        self.shift = 0

    # tato metoda nechává 'nábojnici' na zemi aktuálně se v kódu nepoužívá
    def drawForYourself(self):
        self.xPos += self.direction * self.speed
        pygame.draw.rect(window, 'blue', self.projectile)
    
    # logika střílení 
    def shootThem(self):

        if 0 < self.xPos < width and self.hit == False:
            self.xPos += self.direction * self.speed 
            pygame.draw.rect(window, 'blue', (self.xPos - self.shift, self.yPos, self.playerWidth, self.playerHeight))
        else:
            shots.remove(shot)
            del self                    # zmizení a destrukce projektilu

mobs = []       # ukládá všechny aktuální Moby v levelu

# 5 mobů pro první level 
for _ in range(5):
    m = Mob(randint(60, width - mobWidth - 5), randint(100, height - mobHeight - 30), mobWidth, mobHeight, randint(3,8), randint(0,1), sideways=randint(0,1))
    mobs.append(m)

running = True
player = Player(5, height//2 - 60, 40, 60, 6)

    # hlavní GAME LOOP
startTime = time.time()

def ending():
    global running
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    return running

while running:
            newLevel = 1                # hodnota pouze 0 1 jedná se o bool pro změnu levelu je níže důležitá logická funkce 
            window.fill(bg_color)
            score = font.render(f'Your score: {points}', 1, 'white')
            currTime = time.time() - startTime
            timer = ceil(40 - currTime)
            timerDisp = font.render(f'Time left: {timer}s', 1, 'white')
            window.blit(timerDisp, (width - 210, 10))
            window.blit(score, (10,10))
            clock = pygame.time.Clock()
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            keys = pygame.key.get_pressed()
            player.move(keys)

            for mob in mobs:
                mob.movement()
                if mob.alive and mob.mob.colliderect(player.player):       # pro projektil je tato funkce implementována pro moby je importována pro... 
                    points -= 10                                           # ...optimální rychlost kódu
                    continue
            
            if keys[pygame.K_SPACE] and len(shots) < 24:
                shots.append(Projectile(player.xPos+player.playerWidth, player.yPos + 0.5*player.playerHeight -3, 4, 2, 7, player.faceRight))
                points -= 10
            
            for shot in shots:
                shot.shootThem()
                for mob in mobs:
                    if mob.checkCollision(Projectile=shot):
                        shot.hit = True
                    newLevel *= not mob.alive       # logická funkce pro změnu levelu jedná se n-násobnou konjunkci negací mob.alive
                else:
                    # inicializace nového levelu           
                    if newLevel == 1:
                        mobs = []
                        mobcount = randint(4,9)
                        for _ in range(mobcount):
                            m = Mob(randint(60, width - mobWidth - 5), randint(100, height - mobHeight - 25), mobWidth, mobHeight, randint(3,8), randint(0,1), sideways=randint(0,1))
                            mobs.append(m)
            
            pygame.display.flip()

            if points < 0:
                gameOver = font.render(f'GAME OVER! YOU LOST!', 0, 'red')
                window.blit(gameOver, (width//2 - gameOver.get_width()//2, height//2 - gameOver.get_height()))
                while running:
                    running = ending()

            if timer <= 0:
                gameOver = font.render(f'Good game! You scored: {points}', 0, 'red')
                window.blit(gameOver, (width//2 - gameOver.get_width()//2, height//2 - gameOver.get_height()))
                while running:
                    running = ending()
pygame.quit()
