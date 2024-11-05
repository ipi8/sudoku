from cmu_graphics import *
import math, random, copy
import itertools

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
     
    def getXWing(self): 
        for row in range(9): 
            for col in range(9): 
                if self.board[row][col] == 0: 
                    if self.findEmptyCellInRow(row, col) != None: 
                        (row1, col1) = self.findEmptyCellInRow(row, col)
                    if self.findEmptyCellInCol(row, col) != None: 
                        (row2, col2) = self.findEmptyCellInCol(row, col)
                    if self.board[row2][col1] == 0:
                        row1Intersect = self.legals[row][col].intersection(self.legals[row1][col1])
                        row2Intersect = self.legals[row2][col2].intersection(self.legals[row2][col1])
                        intersect = row1Intersect.intersection(row2Intersect)
                        if intersect != set(): 
                            if (self.isLockedPair(row, col, row1, col1) and not self.inOtherSpace(row2, col2, row2, col1, intersect) or 
                                self.isLockedPair(row2, col2, row2, col1) and not self.inOtherSpace(row, col, row1, col1, intersect) or 
                                self.isLockedPair(row, col, row2, col2) and not self.inOtherSpace(row1, col1, row2, col1, intersect) or 
                                self.isLockedPair(row1, col1, row2, col1) and not self.inOtherSpace(row, col, row2, col2, intersect)): 
                                # row1Intersect = self.legals[row][col].intersection(self.legals[row1][col1])
                                # row2Intersect = self.legals[row2][col2].intersection(self.legals[row2][col1])
                                if row1Intersect == row2Intersect and row1Intersect != set(): 
                                    return (((row, col), (row1, col1), (row2, col2), 
                                            (row2, col1)), row1Intersect)
                                    # self.xWingList.append((row, col, row1, col1, row2, col2, 
                                    #                         row2, col1, row1Intersect))
        return None, None

    def isLockedPair(self, r1, c1, r2, c2): 
        if len(self.legals[r1][c2]) == 2 and self.legals[r1][c1] == self.legals[r2][c2]: 
            return True
        return False
    
    def inOtherSpace(self, r1, c1, r2, c2, intersect):
        print(r1, c1, r2, c2, intersect)
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
        for col in range(9): 
            if self.board[row][col] == 0 and col != col1: 
                return (row, col)
        return None

    def findEmptyCellInCol(self, row1, col): 
        for row in range(9): 
            if self.board[row][col] == 0 and row != row1: 
                return (row, col)
        return None

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

def create_onScreenStart(app):
    # app.EMH = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', 
    #            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', 
    #            '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', 
    #            '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', 
    #            '41', '42', '43', '44', '45', '46', '47', '48', '49', '50']
    # app.EE = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', 
    #            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', 
    #            '21', '22', '23', '24', '25']
    # if app.selectedLevel == 'Easy' or app.selectedLevel == 'Medium' or app.selectedLevel == 'Hard': 
    #     app.boardNum = random.choice(app.EMH)
    # elif app.selectedLevel == 'Expert' or app.selectedLevel == 'Evil': 
    #     app.boardNum = random.choice(app.EE)
    app.rows = 9
    app.cols = 9
    app.createBoard = State([[0 for _ in range(app.rows)] for _ in range(app.cols)])
    # app.userSolution = copy.deepcopy(app.createBoard)
    app.createLegals = app.createBoard.legals
    app.boardWidth = 500
    app.boardHeight = 500
    app.boardLeft = (app.width-app.boardWidth)/2
    app.boardTop = (app.height-app.boardHeight)*5/12
    app.cellBorderWidth = 1
    app.selection = (0, 0)
    # app.gameOver = False
    app.createSolution = None
    # app.nColor = None
    app.selectedNum = None
    app.reset = False
    app.play = False
    # app.userSolution.automaticLegal = False if app.selectedLevel == 'Easy' else True
    # app.highlightLegal = None
    # app.editLegals = False
    # app.singleton = False
    # app.undo = False
    # app.redo = False
    app.message = ''
    app.filePath = ''
    app.file = False
    # app.createBoard.printBoard()
    app.create = False
    # app.createSolution.printBoard()

def create_redrawAll(app):
    drawLabel('Sudoku', app.width/2, app.height/12, size=30, bold = True)
    colorHome = 'lightGray' if app.home == True else None
    drawRect(app.returnX, app.returnY, app.returnWidth, app.returnHeight,
             fill = colorHome, border = 'black', align = 'center')
    drawLabel('Home', app.returnX, app.returnY, size = 14)
    colorPlay = 'lightGray' if app.play == True else None
    drawRect(app.width - app.returnX, app.returnY, 
             app.returnWidth, app.returnHeight,
             fill = colorPlay, border = 'black', align = 'center')
    drawLabel('Play (p)', app.width - app.returnX, app.returnY, size = 14)
    colorReset = 'lightGray' if app.reset == True else None
    drawRect(app.width - app.returnX - app.returnX - 20, app.returnY, 
             app.returnWidth, app.returnHeight,
             fill = colorReset, border = 'black', align = 'center')
    drawLabel('Reset (r)', app.width - 2 * app.returnX - 20, 
             app.returnY, size = 14)
    drawLabel(app.message, app.width/2, app.height/12 + 25, size = 15, 
            bold = True, fill = 'red')
    drawRect(app.width/2, 725, 680, 20, fill = None, border = 'black', align = 'center')
    drawLabel('Click below to enter a file pathway to your board and press enter: ', app.width/2, 680, 
            bold = True, size = 16)
    drawLabel(f'{app.filePath}', app.width/2, 715)
    # if app.userSolution.board == app.solution.board: 
    #     drawLabel('Complete!!', app.width/2, app.height/12+25, size = 15, 
    #          bold = True, fill = 'green')
    # else: 
    #     drawLabel(app.message, app.width/2, app.height/12 + 25, size = 15, 
    #         bold = True, fill = 'red')
    # draw undo button
    # undoColor = 'lightGray' if app.undo == True else None
    # drawRect(app.boardLeft + 190, app.boardTop + app.boardHeight + 110, 
    #         app.returnWidth, 30, fill = undoColor, border = 'black')
    # drawLabel('Undo (u)', app.boardLeft + 190 + app.returnWidth/2, 
    #         app.boardTop + app.boardHeight + 110 + 15, size = 14, bold = True)
    # # draw redo button
    # redoColor = 'lightGray' if app.redo == True else None
    # drawRect(app.boardLeft + 190 + 80, app.boardTop + app.boardHeight + 110, 
    #         app.returnWidth, 30, fill = redoColor, border = 'black')
    # drawLabel('Redo (r)', app.boardLeft + 190 + 80 + app.returnWidth/2, 
    #         app.boardTop + app.boardHeight + 110 + 15, size = 14, bold = True)
    # # draw automatic legals button
    # if app.userSolution.automaticLegal == True: 
    #     drawRect(app.boardLeft + 5, app.boardTop + app.boardHeight + 70, 
    #             170, 30, fill = 'white', border = 'black')
    #     drawLabel('Automatic Legals (a)', app.boardLeft + 90, app.boardTop + app.boardHeight + 85, 
    #             size = 16, bold = True, fill = 'green', align = 'center')
    # else: 
    #     drawRect(app.boardLeft + 5, app.boardTop + app.boardHeight + 70, 
    #             170, 30, fill = 'gray')
    #     drawRect(app.boardLeft, app.boardTop + app.boardHeight + 65, 
    #             170, 30, fill = 'white', border = 'black')
    #     drawLabel('Automatic Legals (a)', app.boardLeft + 85, app.boardTop + app.boardHeight + 80, 
    #             size = 16, bold = True, fill = 'red', align = 'center')
    # # draw edit legals button
    # if app.editLegals == True: 
    #     drawRect(app.boardLeft + 190 + 5, app.boardTop + app.boardHeight + 70, 
    #             150, 30, fill = 'white', border = 'black')
    #     drawLabel('Edit Legals (e)', app.boardLeft + 190 + 80, app.boardTop + app.boardHeight + 85, 
    #             size = 16, bold = True, fill = 'green', align = 'center')
    # else: 
    #     drawRect(app.boardLeft + 190 + 5, app.boardTop + app.boardHeight + 70, 
    #             150, 30, fill = 'gray')
    #     drawRect(app.boardLeft + 190, app.boardTop + app.boardHeight + 65, 
    #             150, 30, fill = 'white', border = 'black')
    #     drawLabel('Edit Legals (e)', app.boardLeft + 190 + 75, app.boardTop + app.boardHeight + 80, 
    #             size = 16, bold = True, fill = 'red', align = 'center')
    # # draw hint button
    # color = 'lightGray' if app.singleton == True else None
    # drawRect(app.boardLeft + 360, app.boardTop + app.boardHeight + 67.5, 
    #         app.boardWidth - 360, 30, fill = color, border = 'black')
    # drawLabel('Singleton (s)', app.boardLeft + 360 + (app.boardWidth - 360)/2, 
    #         app.boardTop + app.boardHeight + 67.5 + 15, 
    #         size = 16, bold = True, fill = 'black')
    # drawRect(app.boardLeft + 360, app.boardTop + app.boardHeight + 110, 
    #         app.boardWidth - 360, 30, fill = color, border = 'black')
    # drawLabel('Set all singles (S)', app.boardLeft + 360 + (app.boardWidth - 360)/2, 
    #         app.boardTop + app.boardHeight + 110 + 15, 
    #         size = 16, bold = True, fill = 'black')
    drawBoard(app)
    drawBoardBorder(app)
    drawNumButtons(app)
    drawLegals(app)

def create_onMousePress(app, mouseX, mouseY): 
    if ((app.width/2 - 340) < mouseX < (app.width/2 + 340) and 
        (725 - 10) < mouseY < (725 + 10)): 
        app.file = True
    elif not ((app.width/2 - 100) < mouseX < (app.width/2 + 100) and 
        (725 - 10) < mouseY < (725 + 10)): 
        app.file = False
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
    if (((app.width - 2*app.returnX - 20 - app.returnWidth/2) < mouseX < (app.width - 2*app.returnX - 20 + app.returnWidth/2)) and
        ((app.returnY - app.returnHeight/2) < mouseY < (app.returnY + app.returnHeight / 2))): 
        app.reset = True
    if ((app.width - app.returnX - app.returnWidth/2) < mouseX < (app.width - app.returnX + app.returnWidth/2) and 
        (app.returnY - app.returnHeight/2) < mouseY < (app.returnY + app.returnHeight/2)): 
        app.createSolution = solveSudoku(app)
        app.play = True

        # if app.selectedLevel == 'Easy' or app.selectedLevel == 'Medium' or app.selectedLevel == 'Hard': 
        #     app.boardNum = random.choice(app.EMH)
        # elif app.selectedLevel == 'Expert' or app.selectedLevel == 'Evil': 
        #     app.boardNum = random.choice(app.EE)
        # app.board = State(getBoard(f'/Users/yyp/Documents/15-112/TP/tp-starter-files/boards/{app.selectedLevel}-{app.boardNum}.png.txt'))
        # app.solution = solveSudoku(app)
        # app.userSolution = copy.deepcopy(app.board)
        # app.legals = app.userSolution.legals
        # app.userSolution.automaticLegal = False if app.selectedLevel == 'Easy' else True
        # app.selection = (0, 0)
    # if (app.boardLeft < mouseX < (app.boardLeft + 170) and 
    #     ((app.boardTop + app.boardHeight + 75) < mouseY < (app.boardTop + app.boardHeight + 105))): 
    #     app.userSolution.automaticLegal = not app.userSolution.automaticLegal
    # if ((app.boardLeft + 190) < mouseX < (app.boardLeft + 190 + 150) and 
    #     ((app.boardTop + app.boardHeight + 75) < mouseY < (app.boardTop + app.boardHeight + 105))): 
    #     app.editLegals = not app.editLegals
    # if (((app.boardLeft + 360) < mouseX < (app.boardLeft + app.boardWidth)) and 
    #     ((app.boardTop + app.boardHeight + 67.5) < mouseY < (app.boardTop + app.boardHeight + 97.5))): 
    #     app.singleton = True
    #     setSingletons(app, 's')
    # if (((app.boardLeft + 360) < mouseX < (app.boardLeft + app.boardWidth)) and 
    #     ((app.boardTop + app.boardHeight + 110) < mouseY < (app.boardTop + app.boardHeight + 140))): 
    #     setSingletons(app, 'S')
    # if ((app.boardLeft + 190) < mouseX < (app.boardLeft + 190 + app.returnWidth) and 
    #     (app.boardTop + app.boardHeight + 110) < mouseY < (app.boardTop + app.boardHeight + 140)): 
    #     app.undo = True
    #     app.userSolution.undo()
    #     app.legals = app.userSolution.legals
    # if ((app.boardLeft + 270) < mouseX < (app.boardLeft + 270 + app.returnWidth) and 
    #     (app.boardTop + app.boardHeight + 110) < mouseY < (app.boardTop + app.boardHeight + 140)): 
    #     app.redo = True
    #     app.userSolution.redo()
    #     app.legals = app.userSolution.legals

    for i in range(9): 
        cellX, cellY = app.boardLeft + app.boardWidth/9*i, app.boardTop + app.boardHeight + 10
        if ((cellX < mouseX < cellX + app.boardWidth/9 - 10) and 
            (cellY < mouseY < cellY+ app.boardHeight/9 - 10) and app.selection!= None): 
            app.selectedNum = i+1
            row, col = app.selection
            app.createBoard.set(row, col, app.selectedNum)
            app.createLegals = app.createBoard.legals
            # app.createSolution = solveSudoku(app)
            # for row in range(9):
            #     for col in range(9): 
            #         if app.createSolution.board[row][col] == 0:  
            #             app.message = 'Invalid board'

        # elif ((cellX < mouseX < cellX + app.boardWidth/9 - 10) and 
        #     (cellY < mouseY < cellY+ app.boardHeight/9 - 10) and 
        #     app.editLegals and app.selection!= None): 
        #     app.selectedNum = i+1
        #     row, col = app.selection
        #     if app.selectedNum in app.legals[row][col]: 
        #         app.legals[row][col].remove(app.selectedNum)
        #         if app.selectedNum == app.solution.board[row][col]: 
        #             app.message = f'You made an error in row: {row}, column: {col}'
        #     else: 
        #         app.legals[row][col].add(app.selectedNum)

def create_onKeyPress(app, key): 
    if not app.keysDisabled: 
        if app.file == True: 
            if key == 'backspace': 
                app.filePath = app.filePath[:-1]
            elif key == 'enter': 
                app.createBoard = State(getBoard(f'{app.filePath}'))
                app.createLegals = app.createBoard.legals
                app.file = False
            else: 
                app.filePath += key
        else: 
            if key == 'up': 
                moveSelection(app, -1, 0)
            elif key == 'down': 
                moveSelection(app, 1, 0)
            elif key == 'left': 
                moveSelection(app, 0, -1)
            elif key == 'right': 
                moveSelection(app, 0, 1)
            elif key == 'p': 
                app.createSolution = solveSudoku(app)
                app.play = True
            elif key == 'r': 
                app.reset = True
        # elif key == 'n': 
        #     if app.selectedLevel == 'Easy' or app.selectedLevel == 'Medium' or app.selectedLevel == 'Hard': 
        #         app.boardNum = random.choice(app.EMH)
        #     elif app.selectedLevel == 'Expert' or app.selectedLevel == 'Evil': 
        #         app.boardNum = random.choice(app.EE)
        #     app.board = State(getBoard(f'/Users/yyp/Documents/15-112/TP/tp-starter-files/boards/{app.selectedLevel}-{app.boardNum}.png.txt'))
        #     app.solution = solveSudoku(app)
        #     app.userSolution = copy.deepcopy(app.board)
        #     app.legals = app.userSolution.legals
        #     app.selection = (0, 0)
        #     app.userSolution.automaticLegal = False if app.selectedLevel == 'Easy' else True
        # elif key == 'a': 
        #     app.userSolution.automaticLegal = not app.userSolution.automaticLegal
        # elif key == 'e': 
        #     app.editLegals = not app.editLegals
        # elif key == 's' or key == 'S': 
        #     app.singleton = True
        #     setSingletons(app, key)
        # elif key == 'u': 
        #     app.undo = True
        #     app.userSolution.undo()
        #     app.legals = app.userSolution.legals
        # elif key == 'r': 
        #     app.redo = True
        #     app.userSolution.redo()
        #     app.legals = app.userSolution.legals
            elif (key in {'1', '2', '3', '4', '5', '6', '7', '8', '9'} and app.selection != None): 
                app.selectedNum = int(key)
                row, col = app.selection
                app.createBoard.set(row, col, int(key))
                app.createLegals = app.createBoard.legals
                # app.createSolution = solveSudoku(app)
                # app.message = 'Invalid board' if app.createSolution == None else ''

        # elif (key in {'1', '2', '3', '4', '5', '6', '7', '8', '9'} and
        #     app.editLegals and app.selection != None): 
        #     row, col = app.selection
        #     if int(key) in app.legals[row][col]: 
        #         app.legals[row][col].remove(int(key))
        #         if int(key) == app.solution.board[row][col]: 
        #             app.message = f'You made an error in row: {row}, column: {col}'
        #     else: 
        #         app.legals[row][col].add(int(key))

def create_onMouseRelease(app, mouseX, mouseY): 
    if app.home == True: 
        setActiveScreen('splash')
        app.home = False
    if app.reset == True: 
        app.createBoard = State([[0 for _ in range(app.rows)] for _ in range(app.cols)])
        app.createLegals = app.createBoard.legals
        app.reset = False
    if app.play == True: 
        if app.createSolution == None: 
            app.message = 'Invalid board'
        elif app.createSolution != None: 
            app.board = State(copy.deepcopy(app.createBoard.board))
            app.legals = app.createLegals
            app.create = True
            app.userSolution = copy.deepcopy(app.createBoard)
            setActiveScreen('game')
        app.play = False
    app.selectedNum = None
    # app.singleton = False
    # app.undo = False
    # app.redo = False

def create_onKeyRelease(app, key): 
    if app.reset == True: 
        app.createBoard = State([[0 for _ in range(app.rows)] for _ in range(app.cols)])
        app.createLegals = app.createBoard.legals
        app.reset = False
    if app.play == True: 
        if app.createSolution == None: 
            app.message = 'Invalid board'
        elif app.createSolution != None: 
            app.board = app.createBoard
            app.legals = app.createLegals
            app.create = True
            app.userSolution = copy.deepcopy(app.createBoard)
            setActiveScreen('game')
        app.play = False
    app.selectedNum = None
    # app.singleton = False
    # app.undo = False
    # app.redo = False

def setSingletons(app, key): 
    if key.islower(): 
        singletonSet = False
        for row in range(9): 
            if singletonSet == True: 
                break
            for col in range(9): 
                if len(app.createLegals[row][col]) == 1: 
                    value = list(app.createLegals[row][col])[0]
                    app.createBoard.set(row, col, value)
                    singletonSet = True
                    break
        if singletonSet == False: 
            app.message = 'No singletons at this time'
    else: 
        for row in range(9): 
            for col in range(9): 
                if len(app.createLegals[row][col]) == 1: 
                    value = list(app.createLegals[row][col])[0]
                    app.createBoard.set(row, col, value)

def moveSelection(app, drow, dcol): 
    if (0 <= app.selection[0] + drow < app.rows and 
        0 <= app.selection[1] + dcol < app.cols): 
        app.selection = (app.selection[0] + drow, app.selection[1] + dcol)

def drawLegals(app): 
    cellWidth, cellHeight = getCellSize(app)
    legalWidth, legalHeight = cellWidth/3, cellHeight/3
    for row in range(9): 
        for col in range(9): 
            cellLeft, cellTop = getCellLeftTop(app, row, col)
            legals = app.createLegals[row][col]
            for value in legals: 
                legalCx = cellLeft + legalWidth*((value-1)%3) + legalWidth/2
                legalCy = cellTop + legalHeight*((value-1)//3) + legalHeight/2
                drawLabel(str(value), legalCx, legalCy, fill = 'gray')

def drawNumButtons(app): 
    for i in range(9): 
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
    if not app.createBoard.equals(0, row, col): 
        color = 'yellow' if (row, col) == app.selection else 'lightGray'
    else: 
        color = 'yellow' if (row, col) == app.selection else None
    labelCx = cellLeft + cellWidth / 2
    labelCy = cellTop + cellHeight / 2
    drawRect(cellLeft, cellTop, cellWidth, cellHeight, fill = color, 
             border = 'black', borderWidth = app.cellBorderWidth)
    if not app.createBoard.equals(0, row, col): 
        drawLabel(str(app.createBoard.board[row][col]), labelCx, labelCy, size = 18, bold = True)
    
    

    # if app.board.equals(0, row, col):
    # # if app.board[row][col] == 0: 
    #     drawRect(cellLeft, cellTop, cellWidth, cellHeight, fill = color, 
    #              border = 'black', borderWidth = app.cellBorderWidth)
    #     if not app.userSolution.equals(0, row, col): 
    #         labelCx = cellLeft + cellWidth / 2
    #         labelCy = cellTop + cellHeight / 2
    #         color = 'yellow' if (row, col) == app.selection else 'white'
    #         drawRect(cellLeft, cellTop, cellWidth, cellHeight, fill = color, 
    #             border = 'black', borderWidth = app.cellBorderWidth)
    #         # numColor = 'black' if app.userSolution[row][col] == app.solution[row][col] else 'red'
    #         numColor = 'black' if app.userSolution.equals(app.solution, row, col) else 'red'
    #         drawLabel(app.userSolution.board[row][col], labelCx, labelCy, 
    #                 fill = numColor, size = 20, bold = True)
    # elif not app.board.equals(0, row, col): 
    # # elif app.board[row][col] != 0: 
    #     labelCx = cellLeft + cellWidth / 2
    #     labelCy = cellTop + cellHeight / 2
    #     color = 'yellow' if (row, col) == app.selection else 'lightGray'
    #     drawRect(cellLeft, cellTop, cellWidth, cellHeight, fill = color, 
    #          border = 'black', borderWidth = app.cellBorderWidth)
    #     drawLabel(str(app.board.board[row][col]), labelCx, labelCy, size = 18, bold = True)
    

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
    # t1 = time.time()
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

def print2dList(L):
    print(repr2dList(L))

def distance(x1, y1, x2, y2): 
    return ((x1-x2)**2 + (y1-y2)**2)**0.5