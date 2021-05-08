#pylint:disable=E0401
"""This is our main driver class for the chess Engine"""
import pygame as p
import ChessEngine as ce

WIDTH = HEIGHT = 1080
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
BORDER_WIDTH = 2
COLOR = "black"
IMAGES = {}
'''initialise a global dictionary '''

def loadImages():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "wR", "wN", "wB", "wQ", "wK", "bp", "wp"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

"""
	This is the main driver method for the game
"""

def main():
    p.init()
    screen = p.display.set_mode((WIDTH+BORDER_WIDTH, HEIGHT+BORDER_WIDTH), 0, 30)
    clock = p.time.Clock()
    screen.fill(p.Color("black"))
    chessBorder(screen, BORDER_WIDTH, WIDTH, HEIGHT, COLOR)    #border of chess
    gs = ce.GameState()
    validMoves = gs.getValidMove()
    moveMade = False #flag to move made 
    animate = False # flag for animation
    loadImages()
    running = True
    sqSelected = ()  #no square is selected, keep track of the last click of the user(tuple:(row, col))
    playerClicks = [] #keep track of player (two tuple: [(6, 4)], (4, 4))
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            #mouseHandler
            elif e.type == p.MOUSEBUTTONDOWN:
            	location = p.mouse.get_pos()    #pos(x, y)
            	row = location[1]//SQ_SIZE
            	col = location[0]//SQ_SIZE
            	if sqSelected == (row, col):# playee clocked twice
            		sqSelected = ()#deselect
            		playerClicks =[]#clear player click
            	else:
            		sqSelected = (row, col)
            		playerClicks.append(sqSelected)
            	if  len(playerClicks) == 2:#after click twice
            		move = ce.Move(playerClicks[0], playerClicks[1], gs.board)
            		#print(move.getChessNotation())
            		for i in range(len(validMoves)):
            		    if move == validMoves[i]:
            		    	gs.makeMove(validMoves[i])
            		    	moveMade = True
            		    	sqSelected = () #user reset
            		    	playerClicks = []
            		    	animate = True
            		if  not moveMade:
            			playerClicks =[sqSelected]
            			
            #key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:                # undu when "z" pressed
                    gs.undoMove()
                    moveMade = True 
                    animate = False 
                if e.type == p.K_r:          # reset the board when 'r' is pressed 
                	gs = ce.GameState()
                	validMoves = gs.getValidMove()
                	sqSelected = ()
                	playerClicks = []
                	moveMade = False 
                    animate = False

        if moveMade:
            if animate:
            	animateMove(gs.moveLog[-1], screen, gs.board, clock) #animate call
            validMoves = gs.getValidMove()
            moveMade = False 
            animate = False
        drawGameState(screen, gs, validMoves, sqSelected)
        clock.tick(MAX_FPS)
        p.display.flip()
        
#border
def chessBorder(screen, barderLen, w, h,c):
	p.draw.rect(screen, c, [0, 0, h, barderLen])
	p.draw.rect(screen, c, [0, h, w, barderLen])
	p.draw.rect(screen, c, [0, 0, barderLen, h])
	p.draw.rect(screen, c,[w, 0, barderLen, h + barderLen])
	
'''Heighlight and moved for place selected
'''
def heightlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): #sqSelected is a piece that can be moved
        	#heightlight selected square 
	        s = p.Surface((SQ_SIZE, SQ_SIZE))
	        s.set_alpha(100) #transperancy value
	        s.fill(p.Color('blue'))
	        screen.blit(s, (c*SQ_SIZE,r*SQ_SIZE))
	        #heightlight moves from that square
	        s.fill(p.Color('yellow'))
	        for move in validMoves:
	            if move.startRow == r and move.startCol ==c:
	                screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))

#This is the board  method 
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)  #draw square on chess board
    heightlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board) #draw pieses in board

def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("pink")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
                
'''
Animate a move
'''
def animateMove(move, screen, board, clock):
	global colors
	dR = move.endRow - move.startRow
	dC = move.endCol - move.startCol 
	framePerSquare = 10 #frame to mmove one square 
	frameCount = (abs(dR) + abs(dC)) * framePerSquare 
	for frame in range(frameCount + 1):
		r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)                                  
		drawBoard(screen)
		drawPieces(screen, board) 
		#erase the piece from its ending square 
		color = colors[(move.endRow + move.endCol) % 2] 
		endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
		p.draw.rect(screen, color, endSquare)
		#draw captured piece into rectangles
		if move.pieceCaptured != '--':
			screen.blit(IMAGES[move.pieceCaptured], endSquare)
		#draw moving piece
		screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r* SQ_SIZE, SQ_SIZE, SQ_SIZE))
		p.display.flip()
		clock.tick(60)
		
		
if __name__ == "__main__":
    main()
	