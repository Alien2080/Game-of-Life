#region imports
import math
import pygame
import random
import time
#endregion imports

#region constants
VERSION = 0.1
RESOLUTION = (1920, 1080)
FRAME_PER_SECOND = 120
GAME_TICK_DELAY_MS = 250
# CELL_COLOUR = (66, 245, 191) # Cyan?
CELL_COLOUR = (66, 179, 245) # Blue
# BORDER_COLOUR = (132, 66, 245) # Purple
BORDER_COLOUR = (255, 255, 255) # Black
BORDER_SIZE = 1
BOARD_DIMENSIONS = (100, 100)
CELL_SIZE = 10

#endregion constants

def main():
    #region intial setup
    pygame.init()

    # Set up the drawing window.
    screen = pygame.display.set_mode([RESOLUTION[0], RESOLUTION[1]])
    pygame.display.set_caption('Game of Life - version: {}'.format(VERSION))

    #region fonts
    # Set up font for UI elements.
    t0 = time.time()
    font = pygame.font.SysFont(None, 48)
    print('time needed for Font creation :', time.time()-t0)
    #endregion fonts

    #region events
    RENDER_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(RENDER_EVENT, math.floor(1000/FRAME_PER_SECOND))

    GAME_TICK_EVENT = pygame.USEREVENT + 2
    pygame.time.set_timer(GAME_TICK_EVENT, GAME_TICK_DELAY_MS)
    #endregion events

    #region sprites
    board = Board(BOARD_DIMENSIONS)
    spriteGroup = pygame.sprite.Group()
    spriteGroup.add(board)
    #endregion sprites
    
    #endregion intial setup
    # Main game loop.
    running = True
    paused = True
    lastClickedSquare = (0, 0)
    while running:    
        for event in pygame.event.get():
            # Did the user click the window close button?
            if event.type == pygame.QUIT:
                running = False

            # Key press events.
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PAUSE or event.key == pygame.K_ESCAPE:
                    if paused:
                        paused = False                     
                    else:                      
                        paused = True               
                if event.key == pygame.K_SPACE:
                    board.calculateNextBoardState() 

            # Main game calculations.
            elif event.type == GAME_TICK_EVENT and not paused:
                board.calculateNextBoardState()               
                   
            # Render screen changes.
            elif event.type == RENDER_EVENT:
                renderScreen(screen, [spriteGroup], font, paused) 

        # Mouse key events.
        # elif event.type == pygame.MOUSEBUTTONDOWN:
        pos = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if click[0] == True: # evaluate left button
            x = int((pos[0] - board.rect.x) / board.cellSize)
            y = int((pos[1] - board.rect.y) / board.cellSize)
            if x != lastClickedSquare[0] or y != lastClickedSquare[1]:
                if board.boardState[y][x] == 1:
                    board.boardState[y][x] = 0
                elif board.boardState[y][x] == 0:                   
                    board.boardState[y][x] = 1
                spriteGroup.update()
                lastClickedSquare = (x, y)                       
    pygame.quit()


def renderScreen(screen, spriteGroups, font, paused):
    # Wipe screen.
    screen.fill("black")
    # Draw sprites.
    for group in spriteGroups:
              group.draw(screen)
    # Draw UI text.
    # mousePosText = font.render('mouse position: {}'.format(pygame.mouse.get_pos()), True, 'grey')
    # screen.blit(mousePosText, (20, 20))
    # Paused text.
    if paused:
        pausedText = font.render('Paused', True, 'black')
        text_width, text_height = font.size('Paused')
        screen.blit(pausedText, (RESOLUTION[0]/2 - text_width/2, 2*RESOLUTION[1]/3 - text_height/2))
    pygame.display.update()


class Board(pygame.sprite.Sprite):
    def __init__(self, boardDimensions):
        super(Board, self).__init__()
        self.cellSize = CELL_SIZE
        self.length = boardDimensions[0]
        self.height = boardDimensions[1]    
        # create board state
        # self.boardState = [[random.randint(0, 1)] * self.length for i in range(self.height)]
        self.boardState = [[0] * self.length for i in range(self.height)]
        self.nextBoardState = [[0] * self.length for i in range(self.height)]
        # draw board
        self.surface = pygame.Surface((self.length * self.cellSize, self.height * self.cellSize), pygame.SRCALPHA)        
        self.image = self.surface
        self.rect = self.image.get_rect()
        self.rect.center = (RESOLUTION[0]/2, RESOLUTION[1]/2)
        # self.rect.topleft = (0, 0)
        self.drawGrid()
    
    def drawGrid(self):
        self.surface.fill((201, 201, 201))
        for x in range(self.length):
            pygame.draw.line(self.surface, "grey", (x * self.cellSize, 0), (x * self.cellSize, self.height * self.cellSize), BORDER_SIZE*2)
        for y in range(self.height):
            pygame.draw.line(self.surface, "grey", (0, y * self.cellSize), (self.length * self.cellSize, y * self.cellSize), BORDER_SIZE*2)


        
    def update(self):
        self.drawGrid()
        borderWidth = BORDER_SIZE * 2
        borderOffset = BORDER_SIZE          
        for x in range(self.length):
            for y in range(self.height):
                # draw cells if alive.                  
                if self.boardState[y][x] == 1:   
                    xStart = x * self.cellSize
                    xEnd = (x+1) * self.cellSize
                    yStart = y * self.cellSize
                    yEnd = (y+1) * self.cellSize                      
                    pygame.draw.rect(self.surface, CELL_COLOUR, (xStart+borderOffset, yStart+borderOffset, self.cellSize-borderOffset, self.cellSize-borderOffset))
                    pygame.draw.line(self.surface, BORDER_COLOUR, (xStart, yStart), (xEnd, yStart), borderWidth)
                    pygame.draw.line(self.surface, BORDER_COLOUR, (xEnd, yStart), (xEnd, yEnd), borderWidth)
                    pygame.draw.line(self.surface, BORDER_COLOUR, (xEnd, yEnd), (xStart, yEnd), borderWidth)
                    pygame.draw.line(self.surface, BORDER_COLOUR, (xStart, yEnd), (xStart, yStart), borderWidth)
    
    def calculateNextBoardState(self):
        for x in range(self.length):
            for y in range(self.height):
                self.nextBoardState[y][x] = self.boardState[y][x]

        for x in range(self.length):
            for y in range(self.height):
                try:                        
                    neighbours = 0
                    if y-1 > -1:
                        # count neighbours in row above cell
                        if x-1 > -1:          
                            neighbours += self.boardState[y-1][x-1]
                        neighbours += self.boardState[y-1][x]
                        neighbours += self.boardState[y-1][x+1]
                    # count neighbours same row above cell
                    if x-1 > -1:
                        neighbours += self.boardState[y][x-1]
                    neighbours += self.boardState[y][x+1]             
                except:
                    pass
                try:
                     # count neighbours in row below cell
                    if x-1 > -1:
                        neighbours += self.boardState[y+1][x-1]
                    neighbours += self.boardState[y+1][x]
                    neighbours += self.boardState[y+1][x+1]
                except:
                    pass
                finally:
                    if self.boardState[y][x] == 1: # Alive
                        if neighbours >= 4:
                            self.nextBoardState[y][x] = 0
                        if neighbours <= 1:
                            self.nextBoardState[y][x] = 0
                    elif self.boardState[y][x] == 0: # Dead
                        if neighbours == 3:
                            self.nextBoardState[y][x] = 1 

        for x in range(self.length):
            for y in range(self.height):
                self.boardState[y][x] = self.nextBoardState[y][x]
        self.update()
        

if __name__ == '__main__':
         main()