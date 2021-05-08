#pylint:disable=W0105
"""
This is the file to put current state of the game
"""
class GameState():
    def __init__(self):
        """board is of size 8X8"""
        self.board=[
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]
        ]              
        self.moveFunctions = {'p' : self.getPawnMoves, 'R' : self.getRookMoves,'B' : self.getBishopMoves, 'N' : self.getKnightMoves, 'Q' : self.getQueenMoves, 'K' : self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()#coordinates for the square where an passant capture is possible 
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, 
        																	self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]
        
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  #log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove   #swap player
        #update king location if moved
        if move.pieceMoved == 'wK':
        	self.whiteKingLocation = (move.endRow, move.endCol)
        #update king location
        elif move.pieceMoved == 'bK':
        	self.blackKingLocation = (move.endRow, move.endCol)
        
        #pawn promotion
        if move.isPawnPromotion:
        	self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

		#enpassant move
        if move.isEnpassantMove:
        	self.board[move.startRow][move.endCol] = '--' #capturing the pawn
        # update enpassantpossible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
        	self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
        	self.enpassantPossible = () 
        #castle move 
        if move.isCastleMove:#king side castling
        	if move.endCol - move.startCol == 2: 
        		self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]#move the rook
        		self.board[move.endRow][move.endCol + 1] = '--' #erase old rook
        	else: #queen side castle move 
        		self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2] #move 2 square away 
        		self.board[move.endRow][move.endCol - 2] = '--'
        
        #update castling right - whenever it is a rook or king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, 
        																	self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))
    
    #undo the moves
    def undoMove(self):
    	if len(self.moveLog) != 0:
    		move = self.moveLog.pop()
    		self.board[move.startRow][move.startCol] = move.pieceMoved
    		self.board[move.endRow][move.endCol] = move.pieceCaptured
    		self.whiteToMove = not self.whiteToMove # swap
		#update king location if needed
    	if move.pieceMoved == 'wK':
    		self.whiteKingLocation = (move.startRow, move.startCol)
    	elif move.pieceMoved == 'bK':
    		self.blackKingLocation = (move.startRow, move.startCol)
    	
    	#undo en enpassant 
    	if move.isEnpassantMove:
    		self.board[move.endRow][move.endCol] = '--'#leave landing square blank
    		self.board[move.startRow][move.endCol] = move.pieceCaptured 
    		self.enpassantPossible = (move.endRow, move. endCol)
    	#undu 3 square pawn advance
    	if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
    		self.enpassantPossible = () 
    	#undo castle right 
    	self.castleRightsLog.pop()
    	self.currentCastlingRight = self.castleRightsLog[-1]
    		
    	#undu the castle move 
    	if move.isCastleMove:
    		if move.endCol - move.startCol == 2: #king side 
    			self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
    			self.board[move.endRow][move.endCol - 1] = '--'
    		else:
    			self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
    			self.board[move.endRow][move.endCol + 1] = '--'
    '''
    Update the castle right the move
    '''
    def updateCastleRights(self, move):
    	if move.pieceMoved == 'wk':
    		self.currentCastlingRight.wks = False 
    		self.currentCastlingRight.wqs = False 
    	elif move.pieceMoved == 'bk':
    		self.currentCastlingRight.bks = False 
    		self.currentCastlingRight.bqs = False 
    	elif move.pieceMoved == 'wR':
    		if move.startRow == 7:
    			if move.startCol == 0:
    				self.currentCastlingRight.wqs = False 
    			elif move.startCol == 7:
    				self.currentCastlingRight.wks = False 
    	elif move.pieceMoved == 'bR':
    		if move.startRow == 0:
    			if move.startCol == 0:
    				self.currentCastlingRight.bqs = False 
    			elif move.startCol == 7:
    				self.currentCastlingRight.bks = False
    
    """
    All the move considering check
    """
    def getValidMove(self):
    	tempEnpassantPossible = self.enpassantPossible
    	#copy current castling right 
    	tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, 
        														 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
    	#1 generate all the move
    	moves = self.getAllPossibleMove() 
    	if self.whiteToMove:
    		 self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves) 
    	else:
    		 self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
    		 
    	#2 for each move, make a move
    	for i in range(len(moves) - 1, -1, -1): #when remove elements from list always go backwards the list,it avoids max bugs
        	self.makeMove(moves[i])
        	self.whiteToMove = not self.whiteToMove
        	#3 generate all opponents move
        	#4 for each of your opponent move,see if they attack your King
        	if self.inCkeck():
        		#5 if they do attack your King ,not a valid move
        		moves.remove(moves[i])
        	self.whiteToMove = not self.whiteToMove
        	self.undoMove()
    	
    	if len(moves) == 0:  #check if stalle or mate
            if self.inCkeck:
            	self.checkMate = True
            else:
            	self.staleMate = True
    	self.enpassantPossible = tempEnpassantPossible 
    	self.currentCastlingRight = tempCastleRights
    	return moves


    '''determine if current players is in check
    '''
    def inCkeck(self):
    	if self.whiteToMove:
    		return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
    	else:
    		return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
    
    '''determine if the enemy can attack the square r, c
    '''
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove #switch to opponents move
        oppMoves = self.getAllPossibleMove()
        self.whiteToMove = not self.whiteToMove #switch the turn back
        for move in oppMoves:
        	if move.endRow == r and move.endCol == c: #square under attack
        	    return True
        return False
    	
    '''All move without considering check'''
    def getAllPossibleMove(self):
        moves = []
        for r in range(len(self.board)):#no of row
            for c in range(len(self.board[r])):#no of vol
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) #call the appropriate function to move
        return  moves

    '''get all the pawn mover for the pawn location'''
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove: #white pawn move
            if self.board[r-1][c] == "--":#1 square pawn advance
                moves.append(Move((r, c),(r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--": #2 square pawn advance
                    moves.append(Move((r, c),(r-2, c), self.board))
            if c-1 >= 0:
                if self.board[r-1][c-1][0] == 'b': # enemy piece to capture
                    moves.append(Move((r, c),(r-1, c-1), self.board))
                elif (r-1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c),(r-1, c-1), self.board, enpassantPossible=True))
            if c+1 <= 7: # captured to the right
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c),(r-1, c+1), self.board))
                elif (r-1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c),(r-1, c+1), self.board, enpassantPossible=True))
        else: #black pawn to move
            if self.board[r+1][c] == "--":
            	moves.append(Move((r, c), (r+1, c), self.board))
            	if r == 1 and self.board[r+2][c] == "--":
            		moves.append(Move((r, c),(r+2, c),self.board))
            if c-1 >= 0:
            	if self.board[r+1][c-1][0] == 'w': #enemy piece to capture
            		moves.append(Move((r, c),(r+1, c-1), self.board))
            	elif (r+1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c),(r+1, c-1), self.board, enpassantPossible=True))
            if c+1 <= 7:
            	if self.board[r+1][c+1][0] == 'w': #enemy piece to capture
            		moves.append(Move((r, c),(r+1, c+1), self.board))
            	elif (r+1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c),(r+1, c+1), self.board, enpassantPossible=True))
             		
    '''get all the rook mover for the rook location'''
    def getRookMoves(self, r, c, moves):
        direction = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in direction:
        	for i in range(1, 8):
        		endRow = r + d[0] * i
        		endCol = c + d[1] * i
        		if 0 <= endRow < 8 and 0 <= endCol < 8:#on the board
        			endPiece = self.board[endRow][endCol]
        			if endPiece == '--':
        				moves.append(Move((r, c),(endRow, endCol),self.board))
        			elif endPiece[0] == enemyColor:
        				moves.append(Move((r, c),(endRow, endCol),self.board))
        				break
        			else:# friendly piece valid
        				break
        		else:# off the board
        			break

    
    '''get all the bishop mover for the bishop location'''
    def getBishopMoves(self, r, c, moves):
        direction = ((-1,- 1), (1, -1), (-1, 1), (1, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in direction:
        	for i in range(1, 8):
        		endRow = r + d[0] * i
        		endCol = c + d[1] * i
        		if 0 <= endRow < 8 and 0 <= endCol < 8:#on the board
        			endPiece = self.board[endRow][endCol]
        			if endPiece == '--':
        				moves.append(Move((r, c),(endRow, endCol), self.board))
        			elif endPiece[0] == enemyColor:
        				moves.append(Move((r, c),(endRow, endCol), self.board))
        				break
        			else:# fraindly piece valid
        				break
        		else:# off the board
        			break
    
    '''get all the knight mover for the knight location'''
    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2,- 1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for m in knightMoves:
        	endRow = r + m[0]
        	endCol = c + m[1]
        	if 0 <= endRow < 8 and 0 <= endCol < 8:#on the board
        		endPiece = self.board[endRow][endCol]
        		if endPiece[0] != allyColor:
        			moves.append(Move((r, c),(endRow, endCol), self.board))

    '''get all the queen mover for the queen location'''
    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    '''get all the king mover for the king location'''
    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1,- 1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
        	endRow = r + kingMoves[i][0]
        	endCol = c + kingMoves[i][1]
        	if 0 <= endRow < 8 and 0 <= endCol < 8:#on the board
        		endPiece = self.board[endRow][endCol]
        		if endPiece[0] != allyColor:
        			moves.append(Move((r, c), (endRow, endCol), self.board)) 
        
    '''
    Generate all valid moves for the king at (r, c) and add the, to the move list
    '''
    def getCastleMoves(self, r, c, moves):
    	if self.squareUnderAttack(r, c):
    		return #cant' castlenwhile in check
    	if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
    		self.getKingsideCastleMoves(r, c, moves)
    	if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
    		self.getQueensideCastleMoves(r, c, moves)
    		
    def getKingsideCastleMoves(self, r, c, moves):
    	if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
    		if not self.squareUnderAttack(r, c + 1) and  not self.squareUnderAttack(r, c + 2):
    			moves.append(Move((r, c), (r, c+2), self.board, isCastleMove = True))
    	
    def getQueensideCastleMoves(self, r, c, moves):
    	if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3]:
    		if not self.squareUnderAttack(r, c - 1) and  not self.squareUnderAttack(r, c - 2):
    			moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove = True))

class CastleRights():
	def __init__(self, wks, bks, wqs, bqs):
		self.wks = wks 
		self.bks = bks 
		self.wqs = wqs 
		self.bqs = bqs 
		
class Move():
	#maps keys to values
	#key : value
	ranksToRows = {"1" : 7,"2": 6, "3" : 5,"4": 4, "5" : 3, "6": 2, "7" : 1, "8": 0}
	rowsToRanks = {v: k for k, v in ranksToRows.items()}
	
	filesToCols = {"a" : 0, "b": 1, "c" : 2, "d": 3, "e" : 4, "f": 5, "g" : 6, "h": 7}
	colsToFiles = {v: k for k, v in filesToCols.items()}
	
	def  __init__(self, startSq, endSq, board, enpassantPossible = False, isCastleMove = False):
		self.startRow = startSq[0]
		self.startCol = startSq[1]
		self.endRow = endSq[0]
		self.endCol = endSq[1]
		self.pieceMoved = board[self.startRow][self.startCol]          #old move stored here                                   
		self.pieceCaptured = board[self.endRow][self.endCol]          #and here
		#pawn promotion
		self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
        #en passant
		self.isEnpassantMove = enpassantPossible
		if self.isEnpassantMove:
			self.pieceCaptured = 'wp' if self.pieceCaptured == 'bp' else 'bp'
		
		self.isCastleMove = isCastleMove
		self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow*10 + self.endCol
		
	'''Overideing the equal meyhod'''
	def __eq__(self, other):
	    if isinstance(other, Move):
	    	return self.moveID == other.moveID
	    return False

	def getChessNotation(self):
		#you can get add to make like real chess notation
		return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)                                          
	
	def getRankFile(self, r, c):
		return self.colsToFiles[c] + self.rowsToRanks[r]
		
	