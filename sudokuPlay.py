from cmu_graphics import *
import math, random, copy
import itertools
import sys
import os
import time

from runAppWithScreens import *

class State: 
    def __init__(self, board): 
        rows, cols = len(board), len(board[0])
        self.board = [[0 for _ in range(rows)] for _ in range(cols)]
        self.legals = [[{i for i in range(1, 10)} for _ in range(rows)] for _ in range(rows)]
        self.automaticLegal = True
        self.undoRedoList = []
        self.undoLastStep = False
        self.banList = []
        self.xWingList = []
        for row in range(rows): 
            for col in range(cols): 
                if board[row][col] != 0: 
                    self.set(row, col, board[row][col])
        self.undoRedoList = [(copy.deepcopy(self.board), copy.deepcopy(self.legals))]
        self.undoRedoIndex = len(self.undoRedoList)-1

    def equals(self, other, row, col): 
        if isinstance(other, State): 
            return self.board[row][col] == other.board[row][col]
        else: 
            return self.board[row][col] == other

    def printBoard(self):
        print2dList(self.board)

    def set(self, row, col, value): 
        self.board[row][col] = value
        regionList = getCellRegions(row, col)
        self.legals[row][col] = set()
        if self.automaticLegal == True: 
            for (row, col) in regionList: 
                self.ban(row, col, value)
        if self.undoLastStep == True: 
            self.undoRedoList = self.undoRedoList[0:self.undoRedoIndex+1]
            self.undoRedoList.append((copy.deepcopy(self.board), copy.deepcopy(self.legals)))
            self.undoRedoIndex = len(self.undoRedoList)-1
            self.undoLastStep = False
        else: 
            self.undoRedoList.append((copy.deepcopy(self.board), copy.deepcopy(self.legals)))
            self.undoRedoIndex = len(self.undoRedoList)-1
    
    def undo(self, key): 
        if 0 <= self.undoRedoIndex - 1 < len(self.undoRedoList): 
            self.undoRedoIndex -= 1
            if key == 'b': 
                self.board = self.undoRedoList[self.undoRedoIndex][0]
                self.legals = self.undoRedoList[self.undoRedoIndex][1]
            else: 
                self.board = copy.deepcopy(self.undoRedoList[self.undoRedoIndex][0])
                self.legals = copy.deepcopy(self.undoRedoList[self.undoRedoIndex][1])
            self.undoLastStep = True

    def redo(self): 
        if 0 <= self.undoRedoIndex + 1 < len(self.undoRedoList): 
            self.undoRedoIndex += 1
            self.board = copy.deepcopy(self.undoRedoList[self.undoRedoIndex][0])
            self.legals = copy.deepcopy(self.undoRedoList[self.undoRedoIndex][1])

    def ban(self, row, col, value): 
        if value in self.legals[row][col]: 
            self.legals[row][col].remove(value)
    
    ## Hint 2 Source: https://www.cs.cmu.edu/~112-3/notes/tp-sudoku-hints.html
    def getHint2(self): 
        for region in getAllRegions(): 
            for N in range(2, 6): 
                (targets, result) = self.applyRule2(region, N)
                if result != set() and result != None: 
                    return (targets, result)
        return None, None

    def applyRule2(self, region, N): 
        for regionList in itertools.combinations(region, N): 
            if self.cellIsFilled(regionList): 
                continue
            legalSet = set()
            targets = set()
            for (row, col) in regionList: 
                legalSet = legalSet.union(self.legals[row][col])
                targets.add((row, col))
            if len(legalSet) == N: 
                return targets, self.getBans(legalSet, targets)
        return None, None
    
    def cellIsFilled(self, regionList): 
        for (row, col) in regionList: 
            if self.board[row][col] != 0: 
                return True
        return False

    def getBans(self, legalSet, targets): 
        banSet = set()
        regions = self.getAllRegionsThatContainTargets(targets)
        for (row, col) in regions: 
            if (row, col) in targets: 
                continue
            for legal in legalSet: 
                if legal in self.legals[row][col]: 
                    banSet.add(('ban', row, col, legal))
        return banSet
     
     ## Source: https://www.sudokuwiki.org/X_Wing_Strategy
    def getXWing(self): 
        for row in range(9): 
            for col in range(9): 
                if self.board[row][col] == 0: 
                    rowList = self.findEmptyCellInRow(row, col)
                    colList = self.findEmptyCellInCol(row, col)
                    if rowList == [] or colList == []: 
                        continue
                    for (row1, col1) in rowList: 
                        for (row2, col2) in colList: 
                            if self.board[row2][col1] != 0: 
                                continue
                            else: 
                                row1Intersect = self.legals[row][col].intersection(self.legals[row1][col1])
                                row2Intersect = self.legals[row2][col2].intersection(self.legals[row2][col1])
                                intersect = row1Intersect.intersection(row2Intersect)
                                if intersect != set(): 
                                    for value in intersect: 
                                        if ((not self.inOtherSpace(row, col, row1, col1, value) and not self.inOtherSpace(row2, col2, row2, col1, value)) or
                                            (not self.inOtherSpace(row, col, row2, col2, value) and not self.inOtherSpace(row1, col1, row2, col1, value))): 
                                            return (((row, col), (row1, col1), (row2, col2), 
                                                    (row2, col1)), value)
        return None, None
        
    def inOtherSpace(self, r1, c1, r2, c2, intersect):
        if r1 == r2: 
            for col in range(9): 
                if col != c1 and col != c2: 
                    if intersect in self.legals[r1][col]: 
                        return True
        elif c1 == c2: 
            for row in range(9): 
                if row != r1 and row != r2: 
                    if intersect in self.legals[row][c1]: 
                        return True
        return False

    def findEmptyCellInRow(self, row, col1): 
        rowList = []
        for col in range(9): 
            if self.board[row][col] == 0 and col != col1: 
                rowList.append((row, col))
        return rowList

    def findEmptyCellInCol(self, row1, col): 
        colList = []
        for row in range(9): 
            if self.board[row][col] == 0 and row != row1: 
                colList.append((row, col))
        return colList

    def getAllRegionsThatContainTargets(self, targets): 
        L = []
        for region in getAllRegions(): 
            if targets.issubset(set(region)):
                L += region
        return L

# @staticmethod
def getRowRegion(row):
    return [(row, col) for col in range(9)]
# @staticmethod
def getColRegion(col):
    return [(row, col) for row in range(9)]
# @staticmethod
def getBlockRegion(block):
    L = []
    br = block // 3
    bc = block % 3
    for row in range(3*br, 3*br+3): 
        for col in range(3*bc, 3*bc+3): 
            L.append((row, col))
    return L
# @staticmethod
def getBlock(row, col):
    blockRow = row // 3
    blockCol = col // 3
    return blockRow * 3 + blockCol
# @staticmethod
def getBlockRegionByCell(row, col):
    blockNum = getBlock(row, col)
    return getBlockRegion(blockNum)
# @staticmethod
def getCellRegions(row, col):
    L = []
    L = getRowRegion(row) + getColRegion(col) + getBlockRegionByCell(row, col)
    return L
# @staticmethod
def getAllRegions():
    L = []
    for row in range(9): 
        L.append(getRowRegion(row))
    for col in range(9): 
        L.append(getColRegion(col))
    for block in range(9): 
        L.append(getBlockRegion(block))
    return L

## Source: https://www.cs.cmu.edu/~112-3/notes/term-project.html
def readFile(path):
    with open(path, "rt") as f:
        return f.read()

#returns a 2d list with board values
def getBoard(path): 
    fileContents = readFile(path)
    board = [[0 for i in range(9)]for j in range(9)]
    i = j = -1
    for row in fileContents.splitlines(): 
        i += 1
        for num in row.split(' '): 
            j = (j + 1) % 9
            board[i][j] = int(num)
    return board

def loadBoardPaths(filters):
    boardPaths = [ ]
    for filename in os.listdir(f'/Users/yyp/Documents/15-112/TP/tp-starter-files/boards/'):
        if filename.endswith('.txt'):
            if hasFilters(filename, filters):
                boardPaths.append(f'/Users/yyp/Documents/15-112/TP/tp-starter-files/boards/{filename}')
    return boardPaths

def hasFilters(filename, filters=None):
    if filters == None: return True
    for filter in filters:
        if filter not in filename:
            return False
    return True

def loadRandomBoard(filters=None):
    return random.choice(loadBoardPaths(filters))

def game_onScreenStart(app):
    if app.create == False: 
        # app.EMH = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', 
        #         '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', 
        #         '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', 
        #         '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', 
        #         '41', '42', '43', '44', '45', '46', '47', '48', '49', '50']
        # app.EE = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', 
        #         '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', 
        #         '21', '22', '23', '24', '25']
        # if app.selectedLevel == 'Easy' or app.selectedLevel == 'Medium' or app.selectedLevel == 'Hard': 
        #     app.boardNum = random.choice(app.EMH)
        # elif app.selectedLevel == 'Expert' or app.selectedLevel == 'Evil': 
        #     app.boardNum = random.choice(app.EE)
        # app.selectedLevel = 'Easy'
        # app.boardNum = '01'
        app.board = State(getBoard(f'{loadRandomBoard(filters = [app.selectedLevel.lower()])}')) 
        # app.board = State(getBoard(f'/Users/yyp/Documents/15-112/TP/Sudoku Contests/sc4b.txt'))
        # app.board = State(getBoard(f'/Users/yyp/Documents/15-112/TP/tp-starter-files/boards/{app.selectedLevel}-{app.boardNum}.png.txt'))
        # app.board = State([[6, 0, 0, 0, 3, 0, 0, 0, 0], 
        #                    [7, 3, 4, 0, 0, 0, 0, 0, 0], 
        #                    [2, 1, 0, 0, 0, 0, 0, 0, 0],
        #                    [9, 0, 6, 0, 0, 0, 0, 0, 0],
        #                    [8, 5, 1, 0, 0, 0, 0, 0, 0],
        #                    [0, 0, 0, 0, 0, 0, 0, 0, 0],
        #                    [0, 0, 0, 0, 0, 0, 0, 0, 0],
        #                    [0, 0, 0, 0, 0, 0, 0, 0, 0],
        #                    [0, 0, 0, 0, 0, 0, 0, 0, 0],])
    else: 
        print(app.createBoard.board)
        app.board = State(copy.deepcopy(app.createBoard.board))
    app.userSolution = copy.deepcopy(app.board)
    app.legals = app.userSolution.legals
    app.rows = 9
    app.cols = 9
    app.boardWidth = 500
    app.boardHeight = 500
    app.boardLeft = (app.width-app.boardWidth)/2
    app.boardTop = (app.height-app.boardHeight)*5/12
    app.cellBorderWidth = 1
    app.selection = (0, 0)
    app.solution = solveSudoku(app)
    # app.testBoard = None
    # testBacktracker(filters = ['evil'])
    app.nColor = None
    app.selectedNum = None
    app.userSolution.automaticLegal = False if app.selectedLevel == 'Easy' else True
    app.home = False
    app.load = False
    app.editLegals = False
    app.colorMode = False
    app.contestMode = False
    app.showLegals = True
    app.singleton = False
    app.singletonAll = False
    app.hint1Cell = None
    app.hint1Find = False
    app.hint1Set = False
    app.hint2Cell = None
    app.hint2Highlight = None
    app.hint2Find = False
    app.hint2Set = False
    app.xWingValue = None
    app.xWingCells = None
    app.undo = False
    app.redo = False
    app.message = ''
    app.board.printBoard()
    app.userSolution.printBoard()
    app.solution.printBoard()

def game_redrawAll(app):
    drawLabel('Sudoku', app.width/2, app.height/12, size=30, bold = True)
    homeColor = 'lightGray' if app.home == True else None
    drawRect(app.returnX, app.returnY, app.returnWidth, app.returnHeight,
             fill = homeColor, border = 'black', align = 'center')
    drawLabel('Home', app.returnX, app.returnY, size = 14)
    contestColor = 'green' if app.contestMode == True else 'red'
    drawRect(app.returnX, app.returnY + app.returnHeight + 20, 
             app.returnWidth, app.returnHeight,
             fill = None, border = 'black', align = 'center')
    drawLabel('Contest', app.returnX, app.returnY + app.returnHeight + 20, 
             fill = contestColor, bold = True, size = 14)
    legalColor = 'green' if app.showLegals == True else 'red'
    drawRect(app.returnX, app.returnY + 2*app.returnHeight + 2*20, 
             app.returnWidth, app.returnHeight,
             fill = None, border = 'black', align = 'center')
    drawLabel('Show', app.returnX, app.returnY + 2*app.returnHeight + 35, 
             fill = legalColor, bold = True, size = 14)
    drawLabel('Legals', app.returnX, app.returnY + 2*app.returnHeight + 45, 
             fill = legalColor, bold = True, size = 14)
    drawRect(app.returnX, app.returnY + 3*app.returnHeight + 3*20, 
             app.returnWidth, app.returnHeight,
             fill = None, border = 'black', align = 'center')
    drawLabel('Rotate', app.returnX, app.returnY + 3*app.returnHeight + 3*20, 
             bold = True, size = 14)
    drawRect(app.returnX, app.returnY + 4*app.returnHeight + 4*20, 
             app.returnWidth, app.returnHeight,
             fill = None, border = 'black', align = 'center')
    drawLabel('Swap', app.returnX, app.returnY + 4*app.returnHeight + 70, 
             bold = True, size = 14)
    drawLabel('Row', app.returnX, app.returnY + 4*app.returnHeight + 80, 
             bold = True, size = 14)
    drawLabel('Blocks', app.returnX, app.returnY + 4*app.returnHeight + 90, 
             bold = True, size = 14)
    drawRect(app.returnX, app.returnY + 5*app.returnHeight + 5*20, 
             app.returnWidth, app.returnHeight,
             fill = None, border = 'black', align = 'center')
    drawLabel('Swap', app.returnX, app.returnY + 5*app.returnHeight + 95, 
             bold = True, size = 14)
    drawLabel('Rows', app.returnX, app.returnY + 5*app.returnHeight + 105, 
             bold = True, size = 14)
    loadColor = 'lightGray' if app.load == True else None         
    drawRect(app.width - app.returnX, app.returnY, 
             app.returnWidth, app.returnHeight,
             fill = loadColor, border = 'black', align = 'center')
    drawLabel('Load (n)', app.width - app.returnX, app.returnY, size = 14)
    if app.contestMode==False and app.userSolution.board == app.solution.board: 
        drawLabel('Complete!! :)', app.width/2, app.height/12+25, size = 15, 
             bold = True, fill = 'green')
    elif app.contestMode == False:
        drawLabel(app.message, app.width/2, app.height/12 + 25, size = 15, 
            bold = True, fill = 'red')
    elif app.contestMode == True and not containsZeros(app.userSolution.board): 
        solution = formatSolution(app.userSolution.board)
        writeFile('/Users/yyp/Downloads/contestSolution.txt', solution)
    # draw undo button
    undoColor = 'lightGray' if app.undo == True else None
    drawRect(app.boardLeft + 190, app.boardTop + app.boardHeight + 110, 
            app.returnWidth, 30, fill = undoColor, border = 'black')
    drawLabel('Undo (u)', app.boardLeft + 190 + app.returnWidth/2, 
            app.boardTop + app.boardHeight + 110 + 15, size = 14, bold = True)
    # draw redo button
    redoColor = 'lightGray' if app.redo == True else None
    drawRect(app.boardLeft + 190 + 80, app.boardTop + app.boardHeight + 110, 
            app.returnWidth, 30, fill = redoColor, border = 'black')
    drawLabel('Redo (r)', app.boardLeft + 190 + 80 + app.returnWidth/2, 
            app.boardTop + app.boardHeight + 110 + 15, size = 14, bold = True)
    # draw automatic legals button
    if app.userSolution.automaticLegal == True: 
        drawRect(app.boardLeft + 5, app.boardTop + app.boardHeight + 70, 
                170, 30, fill = 'white', border = 'black')
        drawLabel('Automatic Legals (a)', app.boardLeft + 90, app.boardTop + app.boardHeight + 85, 
                size = 16, bold = True, fill = 'green', align = 'center')
    else: 
        drawRect(app.boardLeft + 5, app.boardTop + app.boardHeight + 70, 
                170, 30, fill = 'gray')
        drawRect(app.boardLeft, app.boardTop + app.boardHeight + 65, 
                170, 30, fill = 'white', border = 'black')
        drawLabel('Automatic Legals (a)', app.boardLeft + 85, app.boardTop + app.boardHeight + 80, 
                size = 16, bold = True, fill = 'red', align = 'center')
    # draw color mode button
    if app.colorMode == True: 
        drawRect(app.boardLeft + 5, app.boardTop + app.boardHeight + 110, 
                170, 30, fill = 'white', border = 'black')
        drawLabel('Color Mode (c)', app.boardLeft + 90, app.boardTop + app.boardHeight + 125, 
                size = 16, bold = True, fill = 'green', align = 'center')
    else: 
        drawRect(app.boardLeft + 5, app.boardTop + app.boardHeight + 110, 
                170, 30, fill = 'gray')
        drawRect(app.boardLeft, app.boardTop + app.boardHeight + 105, 
                170, 30, fill = 'white', border = 'black')
        drawLabel('Color Mode (c)', app.boardLeft + 85, app.boardTop + app.boardHeight + 120, 
                size = 16, bold = True, fill = 'red', align = 'center')
    # draw edit legals button
    if app.editLegals == True: 
        drawRect(app.boardLeft + 190 + 5, app.boardTop + app.boardHeight + 70, 
                150, 30, fill = 'white', border = 'black')
        drawLabel('Edit Legals (e)', app.boardLeft + 190 + 80, app.boardTop + app.boardHeight + 85, 
                size = 16, bold = True, fill = 'green', align = 'center')
    else: 
        drawRect(app.boardLeft + 190 + 5, app.boardTop + app.boardHeight + 70, 
                150, 30, fill = 'gray')
        drawRect(app.boardLeft + 190, app.boardTop + app.boardHeight + 65, 
                150, 30, fill = 'white', border = 'black')
        drawLabel('Edit Legals (e)', app.boardLeft + 190 + 75, app.boardTop + app.boardHeight + 80, 
                size = 16, bold = True, fill = 'red', align = 'center')
    # draw singleton buttons
    colors = 'lightGray' if app.singleton == True else None
    drawRect(app.boardLeft + 360, app.boardTop + app.boardHeight + 67.5, 
            app.boardWidth - 360, 30, fill = colors, border = 'black')
    drawLabel('Singleton (s)', app.boardLeft + 360 + (app.boardWidth - 360)/2, 
            app.boardTop + app.boardHeight + 67.5 + 15, 
            size = 16, bold = True, fill = 'black')
    colorS = 'lightGray' if app.singletonAll == True else None
    drawRect(app.boardLeft + 360, app.boardTop + app.boardHeight + 110, 
            app.boardWidth - 360, 30, fill = colorS, border = 'black')
    drawLabel('Set all singles (S)', app.boardLeft + 360 + (app.boardWidth - 360)/2, 
            app.boardTop + app.boardHeight + 110 + 15, 
            size = 16, bold = True, fill = 'black')
    # draw hint 1 buttons
    colorh1 = 'lightGray' if app.hint1Find == True else None
    drawRect(app.width - app.returnX, app.returnY + app.returnHeight + 20, 
            app.returnWidth, app.returnHeight, 
            fill = colorh1, border = 'black', align = 'center')
    drawLabel('Find h1(h)', app.width - app.returnX, 
            app.returnY + app.returnHeight + 20, size = 14)
    colorH1 = 'lightGray' if app.hint1Set == True else None
    drawRect(app.width - app.returnX, app.returnY + 2*app.returnHeight + 2*20, 
            app.returnWidth, app.returnHeight, 
            fill = colorH1, border = 'black', align = 'center')
    drawLabel('Set h1(H)', app.width - app.returnX, 
            app.returnY + 2*app.returnHeight + 2*20, size = 14)
    colorh2 = 'lightGray' if app.hint2Find == True else None
    drawRect(app.width - app.returnX, app.returnY + 3*app.returnHeight + 3*20, 
            app.returnWidth, app.returnHeight, 
            fill = colorh2, border = 'black', align = 'center')
    drawLabel('Find h2(g)', app.width - app.returnX, 
            app.returnY + 3*app.returnHeight + 3*20, size = 14)
    colorH2 = 'lightGray' if app.hint2Set == True else None
    drawRect(app.width - app.returnX, app.returnY + 4*app.returnHeight + 4*20, 
            app.returnWidth, app.returnHeight, 
            fill = colorH2, border = 'black', align = 'center')
    drawLabel('Set h2(G)', app.width - app.returnX, 
            app.returnY + 4*app.returnHeight + 4*20, size = 14)
    drawRect(app.width - app.returnX, app.returnY + 5*app.returnHeight + 5*20, 
            app.returnWidth, app.returnHeight, 
            fill = None, border = 'black', align = 'center')
    drawLabel('X-Wing', app.width - app.returnX, 
            app.returnY + 5*app.returnHeight + 95, size = 14)
    drawLabel('Find', app.width - app.returnX, 
            app.returnY + 5*app.returnHeight + 105, size = 14)
    drawRect(app.width - app.returnX, app.returnY + 6*app.returnHeight + 6*20, 
            app.returnWidth, app.returnHeight, 
            fill = None, border = 'black', align = 'center')
    drawLabel('X-Wing', app.width - app.returnX, 
            app.returnY + 6*app.returnHeight + 115, size = 14)
    drawLabel('Set', app.width - app.returnX, 
            app.returnY + 6*app.returnHeight + 125, size = 14)
    drawBoard(app)
    drawBoardBorder(app)
    drawNumButtons(app)
    drawLegals(app)

def game_onMousePress(app, mouseX, mouseY): 
    if app.create == True: 
        app.board = State(copy.deepcopy(app.createBoard.board))
        app.userSolution = copy.deepcopy(app.board)
        app.legals = app.userSolution.legals
        app.solution = solveSudoku(app)
        app.create = False
    app.message = ''
    if not app.mouseDisabled: 
        selectedCell = getCell(app, mouseX, mouseY)
        if selectedCell != None:
            if selectedCell == app.selection:
                app.selection = None
            else:
                app.selection = selectedCell
    if ((app.returnX - app.returnWidth/2) < mouseX < (app.returnX + app.returnWidth/2) and 
        (app.returnY - app.returnHeight/2) < mouseY < (app.returnY + app.returnHeight/2)): 
        app.home = True
    if (((app.returnX - app.returnWidth/2) < mouseX < (app.returnX + app.returnWidth/2)) and
        ((app.returnY + app.returnHeight/2 + 20) < mouseY < (app.returnY + 1.5*app.returnHeight + 20))): 
        app.contestMode = not app.contestMode
    if (((app.returnX - app.returnWidth/2) < mouseX < (app.returnX + app.returnWidth/2)) and
        ((app.returnY + 1.5*app.returnHeight + 2*20) < mouseY < (app.returnY + 2.5*app.returnHeight + 2*20))): 
        app.showLegals = not app.showLegals
    if (((app.returnX - app.returnWidth/2) < mouseX < (app.returnX + app.returnWidth/2)) and
        ((app.returnY + 2.5*app.returnHeight + 3*20) < mouseY < (app.returnY + 3.5*app.returnHeight + 3*20))): 
        rotateBoard(app)
    if (((app.returnX - app.returnWidth/2) < mouseX < (app.returnX + app.returnWidth/2)) and
        ((app.returnY + 3.5*app.returnHeight + 4*20) < mouseY < (app.returnY + 4.5*app.returnHeight + 4*20))): 
        swapBoardBlock(app)
    if (((app.returnX - app.returnWidth/2) < mouseX < (app.returnX + app.returnWidth/2)) and
        ((app.returnY + 4.5*app.returnHeight + 5*20) < mouseY < (app.returnY + 5.5*app.returnHeight + 5*20))): 
        swapRows(app)
    if ((app.width - app.returnX - app.returnWidth/2) < mouseX < (app.width - app.returnX + app.returnWidth/2) and 
        (app.returnY - app.returnHeight/2) < mouseY < (app.returnY + app.returnHeight/2) and 
        not app.mouseDisabled): 
        app.load = True
    if (app.boardLeft < mouseX < (app.boardLeft + 170) and 
        ((app.boardTop + app.boardHeight + 65) < mouseY < (app.boardTop + app.boardHeight + 95))and 
        not app.mouseDisabled): 
        app.userSolution.automaticLegal = not app.userSolution.automaticLegal
    if ((app.boardLeft + 190) < mouseX < (app.boardLeft + 190 + 150) and 
        ((app.boardTop + app.boardHeight + 65) < mouseY < (app.boardTop + app.boardHeight + 95))and 
        not app.mouseDisabled): 
        app.editLegals = not app.editLegals
    if (app.boardLeft < mouseX < (app.boardLeft + 170) and 
        ((app.boardTop + app.boardHeight + 105) < mouseY < (app.boardTop + app.boardHeight + 135))and 
        not app.mouseDisabled): 
        app.colorMode = not app.colorMode
    if (((app.boardLeft + 360) < mouseX < (app.boardLeft + app.boardWidth)) and 
        ((app.boardTop + app.boardHeight + 67.5) < mouseY < (app.boardTop + app.boardHeight + 97.5))and 
        not app.mouseDisabled and not app.contestMode): 
        app.singleton = True
        setSingletons(app, 's')
    if (((app.boardLeft + 360) < mouseX < (app.boardLeft + app.boardWidth)) and 
        ((app.boardTop + app.boardHeight + 110) < mouseY < (app.boardTop + app.boardHeight + 140))and 
        not app.mouseDisabled and not app.contestMode): 
        setSingletons(app, 'S')
        app.singletonAll = True
    if ((app.boardLeft + 190) < mouseX < (app.boardLeft + 190 + app.returnWidth) and 
        (app.boardTop + app.boardHeight + 110) < mouseY < (app.boardTop + app.boardHeight + 140) and 
        not app.mouseDisabled): 
        app.undo = True
    if ((app.boardLeft + 270) < mouseX < (app.boardLeft + 270 + app.returnWidth) and 
        (app.boardTop + app.boardHeight + 110) < mouseY < (app.boardTop + app.boardHeight + 140) and 
        not app.mouseDisabled): 
        app.redo = True
    #Hint 1 find
    if ((app.width-app.returnX-app.returnWidth/2) < mouseX < (app.width-app.returnX+0.5*app.returnWidth) and 
        (app.returnY + 0.5*app.returnHeight + 20) < mouseY < (app.returnY + 1.5*app.returnHeight + 20) and 
        not app.mouseDisabled and not app.contestMode): 
        app.hint1Find = True
    if ((app.width-app.returnX-app.returnWidth/2) < mouseX < (app.width-app.returnX+0.5*app.returnWidth) and 
        (app.returnY + 1.5*app.returnHeight + 2*20) < mouseY < (app.returnY + 2.5*app.returnHeight + 2*20) and 
        not app.mouseDisabled and not app.contestMode): 
        app.hint1Set = True
    if ((app.width-app.returnX-app.returnWidth/2) < mouseX < (app.width-app.returnX+0.5*app.returnWidth) and 
        (app.returnY + 2.5*app.returnHeight + 3*20) < mouseY < (app.returnY + 3.5*app.returnHeight + 3*20) and 
        not app.mouseDisabled and not app.contestMode): 
        app.hint2Find = True
    if ((app.width-app.returnX-app.returnWidth/2) < mouseX < (app.width-app.returnX+0.5*app.returnWidth) and 
        (app.returnY + 3.5*app.returnHeight + 4*20) < mouseY < (app.returnY + 4.5*app.returnHeight + 4*20) and 
        not app.mouseDisabled and not app.contestMode): 
        app.hint2Set = True
    if (((app.width-app.returnX-app.returnWidth/2) < mouseX < (app.width-app.returnX+0.5*app.returnWidth) and 
        (app.returnY + 4.5*app.returnHeight + 5*20) < mouseY < (app.returnY + 5.5*app.returnHeight + 5*20) and 
        not app.mouseDisabled and not app.contestMode)): 
        app.xWingCells, app.xWingValue = app.userSolution.getXWing()
        if app.xWingValue == None: 
            app.message = 'X-Wing Hint not applicable at this time'
    if (((app.width-app.returnX-app.returnWidth/2) < mouseX < (app.width-app.returnX+0.5*app.returnWidth) and 
        (app.returnY + 5.5*app.returnHeight + 6*20) < mouseY < (app.returnY + 6.5*app.returnHeight + 6*20) and 
        not app.mouseDisabled and not app.contestMode)): 
        app.xWingCells, app.xWingValue = app.userSolution.getXWing()
        if app.xWingValue == None: 
            app.message = 'X-Wing Hint not applicable at this time'
        xWingSet(app)

    for i in range(9): 
        cellX, cellY = app.boardLeft + app.boardWidth/9*i, app.boardTop + app.boardHeight + 10
        if ((cellX < mouseX < cellX + app.boardWidth/9 - 10) and 
            (cellY < mouseY < cellY+ app.boardHeight/9 - 10) and 
            not app.editLegals and app.selection!= None and
            not app.mouseDisabled): 
            app.selectedNum = i+1
            row, col = app.selection
            if (row, col) == app.hint1Cell: 
                app.hint1Cell = None
            app.hint2Highlight = None
            app.xWingCells = None
            # if app.hint2Cell != None: 
            #     for command in copy.deepcopy(app.hint2Cell): 
            #         if row in command[1:3] and col in command[1:3]: 
            #             app.hint2Cell.remove(command)
            app.userSolution.set(row, col, app.selectedNum)
            app.legals = app.userSolution.legals
            # if app.userSolution.board[row][col] != app.solution.board[row][col]: 
            #     app.message = f'You made an error in row: {row}, col: {col}'
        elif ((cellX < mouseX < cellX + app.boardWidth/9 - 10) and 
            (cellY < mouseY < cellY+ app.boardHeight/9 - 10) and 
            app.editLegals and app.selection!= None and 
            not app.mouseDisabled): 
            app.selectedNum = i+1
            row, col = app.selection
            app.hint2Highlight = None
            app.xWingCells = None
            # if ('ban', row, col, app.selectedNum) in app.hint2Cell: 
            #     app.hint2Cell.remove(('ban', row, col, app.selectedNum))
            if app.selectedNum in app.legals[row][col]: 
                app.legals[row][col].remove(app.selectedNum)
                if app.selectedNum == app.solution.board[row][col]: 
                    app.message = f'You made an error in row: {row}, column: {col}'
            else: 
                app.legals[row][col].add(app.selectedNum)

def game_onKeyPress(app, key): 
    if app.create == True: 
        app.board = State(copy.deepcopy(app.createBoard.board))
        app.userSolution = copy.deepcopy(app.board)
        app.legals = app.userSolution.legals
        app.solution = solveSudoku(app)
        app.create = False
    app.message = ''
    if not app.keysDisabled: 
        if key == 'up': 
            moveSelection(app, -1, 0)
        elif key == 'down': 
            moveSelection(app, 1, 0)
        elif key == 'left': 
            moveSelection(app, 0, -1)
        elif key == 'right': 
            moveSelection(app, 0, 1)
        elif key == 'n': 
            app.load = True
        elif key == 'a': 
            app.userSolution.automaticLegal = not app.userSolution.automaticLegal
        elif key == 'e': 
            app.editLegals = not app.editLegals
        elif key == 'c': 
            app.colorMode = not app.colorMode
        elif key == 's' and not app.contestMode: 
            app.singleton = True
            setSingletons(app, key)
        elif key == 'S' and not app.contestMode: 
            app.singletonAll = True
            setSingletons(app, key)
        elif key == 'h' and not app.contestMode: 
            app.hint1Find = True
        elif key == 'H' and not app.contestMode: 
            app.hint1Set = True
        elif key == 'g' and not app.contestMode: 
            app.hint2Find = True
        elif key == 'G' and not app.contestMode: 
            app.hint2Set = True
        elif key == 'u': 
            app.undo = True
        elif key == 'r': 
            app.redo = True
        elif (key in {'1', '2', '3', '4', '5', '6', '7', '8', '9'} and
            not app.editLegals and app.selection != None): 
            app.selectedNum = int(key)
            row, col = app.selection
            if (row, col) == app.hint1Cell: 
                app.hint1Cell = None
            app.hint2Highlight = None
            app.xWingCells = None
            # if app.hint2Cell != None: 
            #     for command in copy.deepcopy(app.hint2Cell): 
            #         if row in command[1:3] and col in command[1:3]: 
            #             app.hint2Cell.remove(command)
            app.userSolution.set(row, col, int(key))
            app.legals = app.userSolution.legals
        elif (key in {'1', '2', '3', '4', '5', '6', '7', '8', '9'} and
            app.editLegals and app.selection != None): 
            row, col = app.selection
            if app.hint2Highlight != None and (row, col) in app.hint2Highlight: 
                app.hint2Highlight.remove((row, col))
            app.hint2Highlight = None
            if app.xWingCells != None and (row, col) in app.xWingCells: 
                app.xWingCells = None
            # if ('ban', row, col, int(key)) in app.hint2Cell: 
            #     app.hint2Cell.remove(('ban', row, col, int(key)))
            if int(key) in app.legals[row][col]: 
                app.legals[row][col].remove(int(key))
                if int(key) == app.solution.board[row][col]: 
                    app.message = f'You made an error in row: {row}, col: {col}'
            else: 
                app.legals[row][col].add(int(key))

def game_onMouseRelease(app, mouseX, mouseY): 
    if app.home == True: 
        app.home = False
        setActiveScreen('splash')
    if app.load == True: 
        # if app.selectedLevel == 'Easy' or app.selectedLevel == 'Medium' or app.selectedLevel == 'Hard': 
        #     app.boardNum = random.choice(app.EMH)
        # elif app.selectedLevel == 'Expert' or app.selectedLevel == 'Evil': 
        #     app.boardNum = random.choice(app.EE)
        # app.board = State(getBoard(f'/Users/yyp/Documents/15-112/TP/tp-starter-files/boards/{app.selectedLevel}-{app.boardNum}.png.txt'))
        app.board = State(getBoard(f'{loadRandomBoard(filters = [app.selectedLevel.lower()])}'))
        app.solution = solveSudoku(app)
        app.userSolution = copy.deepcopy(app.board)
        app.legals = app.userSolution.legals
        app.userSolution.automaticLegal = False if app.selectedLevel == 'Easy' else True
        app.selection = (0, 0)
        app.load = False
        app.hint1Cell = None
        app.hint2Cell = None
        app.hint2Highlight = None
        app.xWingCells = None
    if app.hint1Find == True: 
        app.hint1Cell = hint1Find(app)
        if app.hint1Cell == None: 
            app.message = 'No singletons at this time'
        app.hint1Find = False
    if app.hint1Set == True: 
        app.hint1Cell = hint1Find(app)
        hint1Set(app)
        app.hint1Set = False
        app.hint1Cell = None
    if app.hint2Find == True: 
        app.hint2Find = False
        app.hint2Highlight, app.hint2Cell = app.userSolution.getHint2()
        if app.hint2Highlight == None: 
            app.message = 'No obvious tuples at this time'
    if app.hint2Set == True: 
        app.hint2Set = False
        if app.hint2Highlight == None: 
            app.hint2Highlight, app.hint2Cell = app.userSolution.getHint2()
        hint2Set(app)
        app.hint2Cell = None
        app.hint2Highlight = None
    if app.undo == True: 
        app.userSolution.undo(None)
        app.legals = app.userSolution.legals
        app.undo = False
    if app.redo == True: 
        app.userSolution.redo()
        app.legals = app.userSolution.legals
        app.redo = False
        
    app.selectedNum = None
    app.singleton = False
    app.singletonAll = False

def game_onKeyRelease(app, key): 
    if app.load == True: 
        # if app.selectedLevel == 'Easy' or app.selectedLevel == 'Medium' or app.selectedLevel == 'Hard': 
        #     app.boardNum = random.choice(app.EMH)
        # elif app.selectedLevel == 'Expert' or app.selectedLevel == 'Evil': 
        #     app.boardNum = random.choice(app.EE)
        # app.board = State(getBoard(f'/Users/yyp/Documents/15-112/TP/tp-starter-files/boards/{app.selectedLevel}-{app.boardNum}.png.txt'))
        app.board = State(getBoard(f'{loadRandomBoard(filters = [app.selectedLevel.lower()])}'))
        app.solution = solveSudoku(app)
        app.userSolution = copy.deepcopy(app.board)
        app.legals = app.userSolution.legals
        app.userSolution.automaticLegal = False if app.selectedLevel == 'Easy' else True
        app.selection = (0, 0)
        app.load = False
        app.hint1Cell = None
        app.hint2Cell = None
        app.hint2Highlight = None
        app.xWingCells = None
        app.load = False
    if app.hint1Find == True: 
        app.hint1Cell = hint1Find(app)
        if app.hint1Cell == None: 
            app.message = 'No singletons at this time'
        app.hint1Find = False
    if app.hint1Set == True: 
        app.hint1Cell = hint1Find(app)
        hint1Set(app)
        app.hint1Cell = None
        app.hint1Set = False
        app.hint1Cell = None
    if app.hint2Find == True: 
        app.hint2Find = False
        app.hint2Highlight, app.hint2Cell = app.userSolution.getHint2()
        if app.hint2Highlight == None: 
            app.message = 'No obvious tuples at this time'
    if app.hint2Set == True: 
        app.hint2Set = False
        if app.hint2Highlight == None: 
            app.hint2Highlight, app.hint2Cell = app.userSolution.getHint2()
        hint2Set(app)
        app.hint2Cell = None
        app.hint2Highlight = None
    if app.undo == True: 
        app.userSolution.undo(None)
        app.legals = app.userSolution.legals
        app.undo = False
    if app.redo == True: 
        app.userSolution.redo()
        app.legals = app.userSolution.legals
        app.redo = False
    app.selectedNum = None
    app.singleton = False
    app.singletonAll = False

def getCell(app, mouseX, mouseY): 
    cellWidth, cellHeight = getCellSize(app)
    x = (mouseX - app.boardLeft) // cellWidth
    y = (mouseY - app.boardTop) // cellHeight
    return (x, y)

## Source: http://pi.math.cornell.edu/~mec/Summer2009/Mahmood/Symmetry.html
## https://www.sudokuwiki.org/Gurths_Theorem
def rotateBoard(app): 
    tempBoard = [[0 for _ in range(9)] for _ in range(9)]
    for oldRow in range(9): 
        for oldCol in range(9): 
            newRow = oldCol
            newCol = -oldRow-1
            tempBoard[newRow][newCol] = app.board.board[oldRow][oldCol]
    app.board = State(tempBoard)
    app.solution = solveSudoku(app)
    app.userSolution = copy.deepcopy(app.board)
    app.legals = app.userSolution.legals
    app.selection = (0, 0)
    app.userSolution.automaticLegal = False if app.selectedLevel == 'Easy' else True

## Source: https://www.mathpages.com/home/kmath661/kmath661.htm
def swapBoardBlock(app): 
    tempBoard = [[0 for _ in range(9)] for _ in range(9)]
    for row in range(9): 
        for col in range(9): 
            tempBoard[row-3][col] = app.board.board[row][col]
    app.board = State(tempBoard)
    app.solution = solveSudoku(app)
    app.userSolution = copy.deepcopy(app.board)
    app.legals = app.userSolution.legals
    app.selection = (0, 0)
    app.userSolution.automaticLegal = False if app.selectedLevel == 'Easy' else True

## Source: https://www.mathpages.com/home/kmath661/kmath661.htm
def swapRows(app): 
    tempBoard = app.board.board
    swapR11 = random.randint(0, 2)
    swapR12 = random.randint(0, 2)
    swapR21 = random.randint(3, 5)
    swapR22 = random.randint(3, 5)
    swapR31 = random.randint(6, 8)
    swapR32 = random.randint(6, 8)
    tempBoard[swapR11], tempBoard[swapR12] = tempBoard[swapR12], tempBoard[swapR11]
    tempBoard[swapR21], tempBoard[swapR22] = tempBoard[swapR22], tempBoard[swapR21]
    tempBoard[swapR31], tempBoard[swapR32] = tempBoard[swapR32], tempBoard[swapR31]
    app.board = State(tempBoard)
    app.solution = solveSudoku(app)
    app.userSolution = copy.deepcopy(app.board)
    app.legals = app.userSolution.legals
    app.selection = (0, 0)
    app.userSolution.automaticLegal = False if app.selectedLevel == 'Easy' else True

def xWingSet(app): 
    for coord in app.xWingCells: 
        row, col = coord
        rowList = getRowRegion(row)
        colList = getColRegion(col)
        for (i, j) in rowList: 
            if (i, j) not in app.xWingCells:
                if app.xWingValue in app.userSolution.legals[i][j]:
                    app.userSolution.legals[i][j].remove(app.xWingValue)
        for (i, j) in colList: 
            if (i, j) not in app.xWingCells: 
                if app.xWingValue in app.userSolution.legals[i][j]:
                    app.userSolution.legals[i][j].remove(app.xWingValue)
    app.xWingCells = None

def hint1Find(app): 
    for row in range(9): 
        for col in range(9): 
            if len(app.legals[row][col]) == 1: 
                return (row, col)
    return None

def hint1Set(app): 
    if app.hint1Cell != None: 
        row, col = app.hint1Cell
        value = list(app.legals[row][col])[0]
        app.userSolution.set(row, col, value)
    else: 
        app.message = 'No singletons at this time'

def hint2Set(app): 
    if app.hint2Cell == None: 
        app.message = 'No obvious tuples at this time'
    else: 
        for (command, row, col, value) in app.hint2Cell: 
            if command == 'ban': 
                app.userSolution.legals[row][col].remove(value)

def setSingletons(app, key): 
    if key == 's': 
        singletonSet = False
        for row in range(9): 
            if singletonSet == True: 
                break
            for col in range(9): 
                if len(app.legals[row][col]) == 1: 
                    value = list(app.legals[row][col])[0]
                    app.userSolution.set(row, col, value)
                    singletonSet = True
                    break
        if singletonSet == False: 
            app.message = 'No singletons at this time'
    elif key == 'b': 
        for row in range(9): 
            for col in range(9): 
                if len(app.tempSolution.legals[row][col]) == 1: 
                    value = list(app.tempSolution.legals[row][col])[0]
                    app.tempSolution.set(row, col, value)
    else: 
        for row in range(9): 
            for col in range(9): 
                if len(app.legals[row][col]) == 1: 
                    value = list(app.legals[row][col])[0]
                    app.userSolution.set(row, col, value)

def moveSelection(app, drow, dcol): 
    if (0 <= app.selection[0] + drow < app.rows and 
        0 <= app.selection[1] + dcol < app.cols): 
        app.selection = (app.selection[0] + drow, app.selection[1] + dcol)

def drawLegals(app): 
    if app.showLegals == True: 
        cellWidth, cellHeight = getCellSize(app)
        legalWidth, legalHeight = cellWidth/3, cellHeight/3
        for row in range(9): 
            for col in range(9): 
                cellLeft, cellTop = getCellLeftTop(app, row, col)
                legals = app.legals[row][col]
                for value in legals: 
                    legalCx = cellLeft + legalWidth*((value-1)%3) + legalWidth/2
                    legalCy = cellTop + legalHeight*((value-1)//3) + legalHeight/2
                    if app.colorMode == True: 
                        fillColor = app.fillColor[value-1]
                        drawRect(legalCx, legalCy, legalWidth, legalHeight, 
                                fill = fillColor, align = 'center')
                    else: 
                        drawLabel(str(value), legalCx, legalCy, fill = 'gray')
                if app.colorMode == True and (row, col) == app.selection: 
                    drawRect(cellLeft, cellTop, cellWidth, cellHeight, fill = None, 
                        border = 'yellow', borderWidth = 5*app.cellBorderWidth)
                elif app.colorMode == True and (row, col) == app.hint1Cell: 
                    drawRect(cellLeft, cellTop, cellWidth, cellHeight, fill = None, 
                        border = 'pink', borderWidth = 5*app.cellBorderWidth)
                elif (app.hint2Highlight != None and app.hint2Highlight != set() and 
                    app.colorMode == True): 
                    for (row2, col2) in app.hint2Highlight: 
                        if (row, col) == (row2, col2) and (row, col) != app.selection:
                            drawRect(cellLeft, cellTop, cellWidth, cellHeight, 
                                    fill = None, border = 'pink', 
                                    borderWidth = 5*app.cellBorderWidth)

def drawNumButtons(app): 
    for i in range(9): 
        if app.colorMode == True: 
            numColor = app.fillColor[i]
        else: 
            numColor = 'lightGray' if i+1 == app.selectedNum else None
        drawRect(app.boardLeft + app.boardWidth/9*i + 5, app.boardTop + app.boardHeight + 10, 
                app.boardWidth/9 - 10, app.boardHeight/9 - 10, fill = numColor, border = 'black')
        numCx = (app.boardLeft + app.boardWidth/9*i + 5) + (app.boardWidth/9 - 10) / 2
        numCy = (app.boardTop + app.boardHeight + 10) + (app.boardHeight/9 - 10) / 2
        drawLabel(str(i + 1), numCx, numCy, fill = 'black', size = 14, bold = True)

def drawBoard(app):
    for row in range(app.rows):
        for col in range(app.cols):
            drawCell(app, row, col)

def drawBoardBorder(app):
    for i in range(4):
        drawLine(app.boardLeft + i*app.boardWidth/3, app.boardTop, 
                app.boardLeft + i*app.boardWidth/3, app.boardTop + app.boardHeight, 
                lineWidth = 4*app.cellBorderWidth)
        drawLine(app.boardLeft, app.boardTop + i*app.boardHeight/3, 
            app.boardLeft + app.boardWidth, app.boardTop + i*app.boardHeight/3, 
            lineWidth = 4*app.cellBorderWidth)

#draw cells, cell background, and cell nums
def drawCell(app, row, col):
    cellLeft, cellTop = getCellLeftTop(app, row, col)
    cellWidth, cellHeight = getCellSize(app)
    color =  'pink' if (row, col) == app.hint1Cell else None
    if (row, col) == app.selection and app.fillColor != app.colorPreferences[0]: 
        color = app.fillColor[1]
    elif (row, col) == app.selection and app.fillColor == app.colorPreferences[0]: 
        color = 'yellow'
    fillColor = app.fillColor[app.userSolution.board[row][col]-1]
    selectedWidth = 5*app.cellBorderWidth if (row, col) == app.selection else app.cellBorderWidth
    labelCx = cellLeft + cellWidth / 2
    labelCy = cellTop + cellHeight / 2
    if app.board.equals(0, row, col):
        if app.colorMode == True: 
            color = 'black' if color == None else color
            if not app.userSolution.equals(0, row, col): 
                drawRect(cellLeft, cellTop, cellWidth, cellHeight, fill = fillColor, 
                        border = color, borderWidth = selectedWidth)
            if (app.userSolution.board[row][col] != 0 and 
                not app.userSolution.equals(app.solution, row, col)):
                drawLabel('X', labelCx, labelCy, fill = 'red', size = 25, bold = True)
            if app.hint2Highlight != None and app.hint2Highlight != set(): 
                for (row2, col2) in app.hint2Highlight: 
                    if (row, col) == (row2, col2) and (row, col) != app.selection:
                        drawRect(cellLeft, cellTop, cellWidth, cellHeight, 
                                fill = None, border = 'pink', 
                                borderWidth = 5*app.cellBorderWidth)
            drawRect(cellLeft, cellTop, cellWidth, cellHeight, fill = None, 
                    border = 'black', borderWidth = selectedWidth)
        else: 
            drawRect(cellLeft, cellTop, cellWidth, cellHeight, fill = color, 
                    border = 'black', borderWidth = app.cellBorderWidth)
            if app.hint2Highlight != None and app.hint2Highlight != set(): 
                for (row2, col2) in app.hint2Highlight: 
                    if (row, col) == (row2, col2) and (row, col) != app.selection:
                        color = 'pink'
                        drawRect(cellLeft, cellTop, cellWidth, cellHeight, 
                                fill = color, border = 'black', 
                                borderWidth = app.cellBorderWidth)
            if app.xWingCells != None: 
                for coord in app.xWingCells: 
                    (row3, col3) = coord
                    if (row, col) == (row3, col3) and (row, col) != app.selection: 
                        color = 'pink'
                        drawRect(cellLeft, cellTop, cellWidth, cellHeight, 
                                fill = color, border = 'black', 
                                borderWidth = app.cellBorderWidth)
            if not app.userSolution.equals(0, row, col): 
                if (not app.userSolution.equals(app.solution, row, col) and 
                    app.contestMode == False):
                    numColor = 'red'
                elif (not app.userSolution.equals(app.solution, row, col) and 
                    app.contestMode == True):
                    solution = formatSolution(app.userSolution.board)
                    writeFile('/Users/yyp/Downloads/contestSolution.txt', solution)
                    sys.exit('Incorrect')
                else: numColor = 'black'
                drawLabel(app.userSolution.board[row][col], labelCx, labelCy, 
                        fill = numColor, size = 18, bold = True)
    elif not app.board.equals(0, row, col): 
        if app.colorMode == True: 
            color = 'black' if color == None else color
            drawRect(cellLeft, cellTop, cellWidth, cellHeight, fill = fillColor, 
                    border = color, borderWidth = selectedWidth)
        else: 
            if (row, col) == app.selection and app.fillColor != app.colorPreferences[0]: 
                color = app.fillColor[1]
            elif (row, col) == app.selection and app.fillColor == app.colorPreferences[0]: 
                color = 'yellow'
            else: 
                color = 'lightGray'
            drawRect(cellLeft, cellTop, cellWidth, cellHeight, fill = color, 
                    border = 'black', borderWidth = app.cellBorderWidth)
            drawLabel(str(app.board.board[row][col]), labelCx, labelCy, 
                    size = 18, bold = True)
    

def getCellLeftTop(app, row, col):
    cellWidth, cellHeight = getCellSize(app)
    cellLeft = app.boardLeft + col * cellWidth
    cellTop = app.boardTop + row * cellHeight
    return (cellLeft, cellTop)

def getCellSize(app):
    cellWidth = app.boardWidth / app.cols
    cellHeight = app.boardHeight / app.rows
    return (cellWidth, cellHeight)

def getCell(app, x, y):
    dx = x - app.boardLeft
    dy = y - app.boardTop
    cellWidth, cellHeight = getCellSize(app)
    row = math.floor(dy / cellHeight)
    col = math.floor(dx / cellWidth)
    if (0 <= row < app.rows) and (0 <= col < app.cols):
      return (row, col)
    else:
      return None

########## backtracking to solve sudoku ##########

## method 2 ##
def solveSudoku(app): 
    t1 = time.time()
    # app.tempSolution = copy.deepcopy(app.testBoard)
    app.tempSolution = copy.deepcopy(app.board)
    setSingletons(app, 'b')
    result = solveSudokuHelper(app)
    # print(time.time() - t1)
    return result
    # return solveSudokuHelper(app)

def findLeastLegals(app): 
    bestRow, bestCol = None, None
    bestLength = 10
    for row in range(9): 
        for col in range(9): 
            if (len(app.tempSolution.legals[row][col]) < bestLength and 
                len(app.tempSolution.legals[row][col]) != 0): 
                bestRow, bestCol = row, col
                bestLength = len(app.tempSolution.legals[row][col])
                if bestLength == 1: 
                    return bestRow, bestCol
    return bestRow, bestCol

def solveSudokuHelper(app): 
    (row, col) = findLeastLegals(app)
    if (row, col) == (None, None): 
        return app.tempSolution
    else: 
        for legal in app.tempSolution.legals[row][col]: 
            app.tempSolution.set(row, col, legal)
            if isLegalSudoku(app.tempSolution.board): 
                solution = solveSudokuHelper(app)
                if solution != None and not containsZeros(solution.board): 
                    app.tempSolution.undoRedoList = [(app.tempSolution.board, app.tempSolution.legals)]
                    return solution
                else: 
                    app.tempSolution.undo('b')
            else: 
                app.tempSolution.undo(None)
    return None

def containsZeros(board): 
    for row in range(9): 
        if 0 in board[row]:
            return True
    return False

## Source: CS Academy isLegalSudoku (https://cs3-112-f22.academy.cs.cmu.edu/exercise/4745)
def areLegalValues(L): 
    n = len(L)
    seen = set()
    for value in L: 
        # if type(value) != int: 
        #     return False
        # if value < 0 or value > n: 
        #     return False
        if value != 0 and value in seen: 
            return False
        seen.add(value)
    return True
        
def isLegalRow(grid, row): 
    return areLegalValues(grid[row])

def isLegalCol(grid, col): 
    rows = len(grid)
    values = [grid[row][col] for row in range(rows)]
    return areLegalValues(values)

def isLegalBlock(grid, block): 
    n = len(grid)
    blockSize = rounded(n**0.5)
    startRow = block // blockSize * blockSize
    startCol = block % blockSize  * blockSize
    values = []
    for drow in range(blockSize): 
        for dcol in range(blockSize): 
            row, col = startRow + drow, startCol + dcol
            values.append(grid[row][col])
    return areLegalValues(values)

def isLegalSudoku(grid):
    rows, cols = len(grid), len(grid[0])
    # if (rows != 4) and (rows != 9): 
    #     return False
    # if (rows != cols): 
    #     return False
    for i in range(9): 
        if not isLegalRow(grid, i): 
            return False
        elif not isLegalCol(grid, i): 
            return False
        elif not isLegalBlock(grid, i): 
            return False
    return True
    # for row in range(rows): 
    #     if not isLegalRow(grid, row): 
    #         return False
    # for col in range(cols): 
    #     if not isLegalCol(grid, col): 
    #         return False
    # blocks = rows
    # for block in range(blocks): 
    #     if not isLegalBlock(grid, block): 
    #         return False
    # return True


# copy print2dList from here:
# https://www.cs.cmu.edu/~112/notes/notes-2d-lists.html#printing
def repr2dList(L):
    if (L == []): return '[]'
    output = [ ]
    rows = len(L)
    cols = max([len(L[row]) for row in range(rows)])
    M = [['']*cols for row in range(rows)]
    for row in range(rows):
        for col in range(len(L[row])):
            M[row][col] = repr(L[row][col])
    colWidths = [0] * cols
    for col in range(cols):
        colWidths[col] = max([len(M[row][col]) for row in range(rows)])
    output.append('[\n')
    for row in range(rows):
        output.append(' [ ')
        for col in range(cols):
            if (col > 0):
                output.append(', ' if col < len(L[row]) else '  ')
            output.append(M[row][col].rjust(colWidths[col]))
        output.append((' ],' if row < rows-1 else ' ]') + '\n')
    output.append(']')
    return ''.join(output)

def formatSolution(board): 
    result = ''
    for row in range(9): 
        for col in range(9): 
            result = result + str(board[row][col]) + ' '
        result += '\n'
    return result

def print2dList(L):
    print(repr2dList(L))

def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)

## Source: https://www.cs.cmu.edu/~112-3/notes/tp-sudoku-hints.html
def testBacktracker(filters):
        time0 = time.time()
        boardPaths = sorted(loadBoardPaths(filters))
        failedPaths = [ ]
        for boardPath in boardPaths:
            app.testBoard = State(getBoard(boardPath))
            print(boardPath)
            solution = solveSudoku(app)
            if not solution:
                failedPaths.append(boardPath)
        print()
        totalCount = len(boardPaths)
        failedCount = len(failedPaths)
        okCount = totalCount - failedCount
        time1 = time.time()
        if len(failedPaths) > 0:
            print('Failed boards:')
            for path in failedPaths:
                print(f'    {path}')
        percent = rounded(100 * okCount/totalCount)
        print(f'Success rate: {okCount}/{totalCount} = {percent}%')
        print(f'Total time: {rounded(time1-time0)} seconds')

def distance(x1, y1, x2, y2): 
    return ((x1-x2)**2 + (y1-y2)**2)**0.5