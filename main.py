import pygame as p
from pyFiles import engine
from pyFiles import AI as ai
from pystockfish import *

width = 800
height = 512
dimension = 8
sqSize = height // dimension
clock = p.time.Clock()
maxFps = 15
images = {}
p.display.set_caption("Chess Engine")
p.display.set_icon(p.image.load("images/icon.png"))

def loadImage():
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bp', 'wQ', 'wK', 'wB', 'wN', 'wR', 'wp']
    for piece in pieces:
        images[piece] = p.transform.scale(p.image.load(f"images/{piece}.png"), (sqSize, sqSize))

def main():
    p.init()
    screen = p.display.set_mode((width, height))
    screen.fill(p.Color('white'))
    gs = engine.gameState()
    validMoves = gs.getVaildMoves()
    madeMove = False
    #print(gs.board)
    loadImage()
    sqSeleected = ()
    playerClicked = []
    gameOver = False
    running = True
    playerOneHuman = True
    playerTwoHuman = False

    while running:

        humanTurn = (gs.whiteToMove and playerOneHuman) or (not gs.whiteToMove and playerTwoHuman)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN and not gameOver and humanTurn:
                col, row = p.mouse.get_pos()
                col //= sqSize
                row //= sqSize
                if (row, col) != sqSeleected:
                    sqSeleected = (row, col)
                    playerClicked.append(sqSeleected)
                else:
                    sqSeleected = ()
                    playerClicked = []

                if len(playerClicked) == 2 and col < 8:
                    move = engine.move(playerClicked[0], playerClicked[1], gs.board)
                    global movE
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            if not move.isPawnPromotion:
                                gs.makeMove(validMoves[i])
                            elif p.mouse.get_pressed() == (1, 0, 0):
                                gs.makeMove(validMoves[i], 'Q')
                            elif p.mouse.get_pressed() == (0, 0, 1):
                                gs.makeMove(validMoves[i], 'N')
                            elif p.mouse.get_pressed() == (0, 1, 0):
                                gs.makeMove(validMoves[i], 'R')
                            elif p.mouse.get_pressed() == (1, 0, 1):
                                gs.makeMove(validMoves[i], 'B')
                            madeMove = True
                            print(f'move : {validMoves[i].getChessNotation()}, player : {"Black" if gs.whiteToMove else "White"}')
                            sqSeleected = ()
                            playerClicked = []
                    if not madeMove:
                        playerClicked = [sqSeleected]

            elif e.type == p.KEYDOWN and e.key == p.K_z:
                if len(gs.moveLog) > 0:
                    playerClicked = []
                    sqSeleected = ()
                    gs.undoMove()
                    gameOver = False
                    madeMove = True

            elif e.type == p.KEYDOWN and e.key == p.K_r:
                gs = engine.gameState()
                validMoves = gs.getVaildMoves()
                sqSeleected = ()
                playerClicked = []
                madeMove = False
        if not gameOver and not humanTurn:
            if len(validMoves) > 0:
                if gs.whiteToMove:
                    AIMove = ai.getbestMove(gs, validMoves, 4)
                else:
                    AIMove  =ai.getbestMove(gs, validMoves, 1)
                if AIMove is not None:
                    gs.makeMove(AIMove)
                else:
                    print('None')
                    AIMove = ai.getRandomMove(validMoves)
                    gs.makeMove(AIMove)
                print(f'move : {AIMove.getChessNotation()}, player : {"Black" if gs.whiteToMove else "White"}')
            madeMove = True

        #if madeMove or movE == 9 or p.event == p.MOUSEBUTTONDOWN:
        #    drawGameState(screen, gs, validMoves, sqSeleected)
        drawGameState(screen, gs, validMoves, sqSeleected, True)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawEndGameText(screen, 'black wins by checkMate')

            if not gs.whiteToMove:
                drawEndGameText(screen, 'white wins by checkMate')

        elif gs.staleMate:
            gameOver = True
            drawEndGameText(screen, 'stalemate')


        clock.tick(maxFps)
        p.display.flip()
        if madeMove:
            validMoves = gs.getVaildMoves()
            madeMove = False


def drawGameState(screen, gs, validmoves, sqselected, dm=False):
    global movE
    drawBoard(screen)
    highLight(screen, gs, validmoves, sqselected, True)
    if len(gs.moveLog) > 0:
        highLight(screen, sq=False, move=gs.moveLog[-1])
        drawGameLogText(screen, gs.moveLog)
    drawPieces(screen, gs)
    highLight(screen, gs, validmoves, sqselected, False)


def highLight(screen, gs=None, validmoves=(), sqselected=(), sq=False, move=None, last=False):

    if move is not None:
        r1, c1 = move.startRow, move.startCol
        r2, c2 = move.endRow, move.endCol

        h = p.Surface((sqSize, sqSize))
        h.fill(p.Color(204, 204, 51))
        screen.blit(h, (c1*sqSize, r1*sqSize))
        h.fill(p.Color(255, 255, 100))
        screen.blit(h, (c2*sqSize, r2*sqSize))
    if sqselected != ():
        r, c = sqselected
        if c < 8 and gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b') :
            if sq:
                s = p.Surface((sqSize, sqSize))
                s.set_alpha(80)
                s.fill(p.Color('dark green'))
                screen.blit(s, (c*sqSize, r*sqSize))

            else:
                for move in validmoves:
                    if move.startRow == r and move.startCol == c:
                        p.draw.circle(screen, p.Color('dark green'), (move.endCol*sqSize+sqSize*0.5, move.endRow*sqSize+sqSize*0.5), 10)



def drawBoard(screen):
    colors = [p.Color(218, 223, 229), p.Color(50, 131, 173)]
    for r in range(dimension):
        for c in range(dimension):
            color = colors[(r+c) % 2]
            p.draw.rect(screen, color, p.Rect(c*sqSize, r*sqSize, sqSize, sqSize))
    p.draw.rect(screen, p.Color('black'), p.Rect(8*sqSize, 0, 288, sqSize*8))


def drawPieces(screen, gs):
    for r in range(dimension):
        for c in range(dimension):
            piece = gs.board[r][c]
            if piece != '--':
                screen.blit(images[piece], p.Rect(c*sqSize, r*sqSize, sqSize, sqSize))


def drawEndGameText(screen, text):
    font = p.font.SysFont('arial', 32, True, True)
    textObject = font.render(text, False, p.Color(0, 102, 204), p.Color('grey'))
    textloc = p.Rect(0, 0, width, height).move(width/2 - textObject.get_width()/2, height/2. - textObject.get_height()/2)
    screen.blit(textObject, textloc)

def drawGameLogText(screen, moveLog):
    font = p.font.SysFont('monospace', 16, False, False)
    j = 1
    t = (str(int(j))+'-') if j % 1 == 0 else ''
    w = 8 * sqSize
    h = 0
    for move in moveLog:
        t = (str(int(j)) + '-') if j % 1 == 0 else ''
        textObject = font.render((t + move.getChessNotation()), True, p.Color('white'))
        l = 3 if j % 1 == 0 else 5
        if w + 2*textObject.get_width() > width and j % 1 == 0:
            w = 8 * sqSize
            h += textObject.get_height() + 5
        textloc = p.Rect(w, h, sqSize*4, sqSize*8)
        screen.blit(textObject, textloc)
        w += textObject.get_width() + l
        j += 0.5



if __name__ == '__main__':
    main()

