import numpy as np
import pygame
import time
import pickle
import os
import matplotlib.pyplot as plt


rewardList = {}
maxScore = 0
class blocks:
    
    def __init__(self,safe,displayWidth=600,displayHeight = 400,x_begin=0,y_begin=1,fall = 3,gapBetweenBlocks=2):
        self.x_begin = x_begin
        self.y_begin = y_begin
        self.x_len = displayWidth // 5
        self.y_len = displayHeight // 8
        self.safe = safe
        self.fall = fall
        self.gapBetweenBlocks = gapBetweenBlocks
        self.blocksCords = self.buildBlocks()



    
    def buildBlocks(self):
        cords = [[self.x_begin,self.y_begin,self.x_len,self.y_len]]
        for i in range(1,5):
            cords.append( [ cords[i-1][0]+self.x_len+self.gapBetweenBlocks, self.y_begin, self.x_len, self.y_len] )
        return cords

    def moveDown(self):
        for hurdle in self.blocksCords:
            hurdle[1] += self.fall

    def displayBlocks(self,game = None, dcolor = (0, 0, 0), scolor = (255, 255, 255)):
        if game == None:
            raise Exception('Game is not Defined.!')
            quit()
        for idx, cord in enumerate(self.blocksCords):
            if idx == self.safe: pygame.draw.rect(game, scolor, cord)
            else: pygame.draw.rect(game, dcolor, cord)

            
class snake:
    
    def __init__(self, xloc, x_boundaryLow, x_boundaryHigh, boundary_offset, color = (255, 255, 255),size = 8,xspeed = 3,yspeed = 3):
        self.size = size
        self.x = xloc
        self.y = 560
        self.color = color
        self.xspeed = boundary_offset
        self.xrangeHigh = x_boundaryHigh
        self.xrangeLow = x_boundaryLow
        self.Qtable = np.zeros([25,3])
        if os.path.isfile('Table.pickle'):
            pickel_in = open('Table.pickle','rb')
            self.Qtable = pickle.load(pickel_in)
        #print(self.Qtable)
        self.learningRate = .7
        self.yeild = .99

    def remember(self):
        pickle_out = open('Table.pickle','wb')
        pickle.dump(self.Qtable, pickle_out)
        pickle_out.close()
            
    def moveRight(self):
        self.x+=self.xspeed
        if self.x-self.size >= self.xrangeHigh:
            self.x = self.xrangeLow + self.size

    def moveLeft(self):
        self.x-=self.xspeed
        if self.x+self.size <= self.xrangeLow:
            self.x = self.xrangeHigh-self.size

    def showSnake(self,game = None,color = (0, 0, 255)):
        if game == None:
            raise Exception('Game is not Defined.!')
            quit()
        pygame.draw.circle(game, color, (self.x, self.y), self.size)


class Snake_and_Blocks:

    def __init__(self,gameWindowWidth = 600,gameWindowHeight = 400):
        self.PlayerDead = False
        self.gameWidth = gameWindowWidth 
        self.gameHeight = gameWindowHeight
        self.score = 0
        self.gameDisplay = pygame.display.set_mode((self.gameWidth,self.gameHeight)) 
        pygame.display.set_caption('Snakes and Blocks(Quality implementation)')
        self.hurdle = blocks(safe = np.random.randint(5), displayWidth = self.gameWidth // 2, displayHeight = self.gameHeight)
        # (self.hurdle.blocksCords[0][0] + self.hurdle.blocksCords[0][2] // 2)+ np.random.randint(0,4) * self.hurdle.blocksCords[0][2]
        self.player = snake(xloc = ((self.hurdle.blocksCords[0][0] + self.hurdle.blocksCords[0][2] // 2) + (self.hurdle.blocksCords[-1][0] + self.hurdle.blocksCords[0][2] // 2)) // 2,
                            x_boundaryLow = self.hurdle.blocksCords[0][0] + self.hurdle.blocksCords[0][2] // 2,
                            x_boundaryHigh = self.hurdle.blocksCords[-1][0] + self.hurdle.blocksCords[0][2] // 2,
                            boundary_offset = self.hurdle.blocksCords[0][2])
        

    def makeMsgObject(self,msg, fontDefination,color):
        surface = fontDefination.render(msg, True, color)
        return surface, surface.get_rect()

    def state(self):
        for i in range(5):
            if self.hurdle.blocksCords[i][0] < self.player.x < self.hurdle.blocksCords[i][0] + self.hurdle.blocksCords[i][2]:
                return i*5 + self.hurdle.safe
        
    def step(self, move):
        if move == 0: self.player.moveLeft()
        elif move == 1: self.player.moveRight()
        else: pass
        return self.state()
        

    def sayMessage(self, msg,fontType = 'freesansbold.ttf', fontSize = 22, xpos = 410, ypos = 10, color = (255, 255, 255)):
        fontDefination = pygame.font.Font(fontType,fontSize)
        msgSurface, messageRectangle = self.makeMsgObject(msg, fontDefination, color)
        messageRectangle = (xpos, ypos)
        self.gameDisplay.blit(msgSurface, messageRectangle)

    def showScore(self):
        self.sayMessage(''.join(['score : ', str(self.score)]))

    def checkCollision(self):
        if self.player.y - self.player.size >= self.hurdle.blocksCords[self.hurdle.safe][1] + self.hurdle.blocksCords[self.hurdle.safe][3] or\
           self.player.y + self.player.size <= self.hurdle.blocksCords[self.hurdle.safe][1]: return 0
        
        if self.player.x + self.player.size >= self.hurdle.blocksCords[self.hurdle.safe][0] and\
           self.player.x - self.player.size <= self.hurdle.blocksCords[self.hurdle.safe][0] + self.hurdle.blocksCords[self.hurdle.safe][2] and\
           self.player.y + self.player.size >= self.hurdle.blocksCords[self.hurdle.safe][1] and\
           self.player.y - self.player.size <= self.hurdle.blocksCords[self.hurdle.safe][1] + self.hurdle.blocksCords[self.hurdle.safe][3]: return 0.5
        else:
            self.PlayerDead = True
            return -0.005



    def showState(self):
        table = self.player.Qtable
        xpos, ypos = 480, 120
        colours = [[255,0,0],[0,255,0],[0,0,255]]
        self.sayMessage('*  LEFT  RIGHT  STAY',xpos = xpos,ypos = ypos)
        ypos += 40
        xpos = 520
        for row in table:
            for val in row:
                if val < 0:
                    pygame.draw.rect(self.gameDisplay, colours[0], (xpos, ypos, 10, 5))
                elif val == 0:
                    pygame.draw.rect(self.gameDisplay, colours[1], (xpos, ypos, 10, 5))
                elif val > 0:
                    pygame.draw.rect(self.gameDisplay, colours[2], (xpos, ypos, 10, 5))
                xpos += 80
            ypos += 10
            xpos = 520
        self.sayMessage('Green = Zero ',xpos = 410,ypos = 450, color = (0, 255, 0))
        self.sayMessage('Red = Negative ',xpos = 410,ypos = 480, color = (255, 0, 0))
        self.sayMessage('Blue = Positive ',xpos = 410,ypos = 510,color = (0, 0, 255))
        

def playGame(GameNo):
    #initializations..
    global maxScore
    windowWidth, windowHeight = (800, 600)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    pygame.init()
    clock = pygame.time.Clock()
    game = Snake_and_Blocks(gameWindowWidth = windowWidth, gameWindowHeight = windowHeight)
    state = game.state() #will give a number 1-25
    totalReward = 0
    left = right = False
    while not game.PlayerDead:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.player.remember()
                return totalReward

##            if event.type == pygame.KEYDOWN:
##               if event.key == pygame.K_LEFT:
##                   left=True
##               elif event.key == pygame.K_RIGHT:
##                   right=True
##
##        if left:
##            game.player.moveLeft()
##            left = False
##        elif right:
##            game.player.moveRight()
##            right = False
##        
##        stateDash = 1
        

        action = np.argmax(game.player.Qtable[state,:] + np.random.randn(1,3)*(1./(GameNo + 1)))
        stateDash = game.step(action)
        r = game.checkCollision()
        game.gameDisplay.fill(BLACK)
        game.showState()
        pygame.draw.line(game.gameDisplay, WHITE, (game.hurdle.blocksCords[-1][0] + game.hurdle.blocksCords[-1][2] + game.hurdle.x_begin, 0),\
                         (game.hurdle.blocksCords[-1][0] + game.hurdle.blocksCords[-1][2] + game.hurdle.x_begin, windowHeight))
        game.hurdle.displayBlocks(game = game.gameDisplay, dcolor = RED, scolor = GREEN)
        game.hurdle.moveDown()
        if game.hurdle.blocksCords[0][1] >= windowHeight:
            game.hurdle.blocksCords = game.hurdle.buildBlocks()
            game.hurdle.safe = np.random.randint(5)
            game.score += 1
            r += 0.5
            if game.hurdle.fall < 50:
                if (game.score) % 5 == 0:
                    game.hurdle.fall += 5

        game.player.Qtable[state, action] += game.player.learningRate * (r + game.player.yeild*np.max(game.player.Qtable[stateDash, :]) - game.player.Qtable[state, action]) 
        totalReward += r
        state = stateDash
        game.player.showSnake(game = game.gameDisplay, color = BLUE)
        game.showScore()
        game.sayMessage('Game number : ' + str(GameNo),ypos = 40)
        game.sayMessage(''.join(['Maximum Score : ', str(maxScore)]), ypos = 70)
        pygame.display.update()
        clock.tick(60)
    print(''.join(['Game ', str(GameNo), ' reward -> ', str(totalReward)]))
    if game.score > maxScore: maxScore = game.score
    game.player.remember()
    rewardList[_] = totalReward
    #return totalReward



if __name__ == '__main__':
    rounds = 50

    for _ in range(rounds): playGame(_)
    
    plt.plot(rewardList.keys(), rewardList.values())
    plt.show()
    
    pygame.quit()
        
