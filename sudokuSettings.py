from cmu_graphics import *
import math, random, copy

from runAppWithScreens import *

def setting_onScreenStart(app): 
    app.mouseDisabled = False
    app.keysDisabled = False
    app.gameLevels1 = ['Easy', 'Medium', 'Hard']
    app.gameLevels2 = ['Expert', 'Evil']
    app.selectedLevel = 'Easy'
    app.gameModes = ['Default', 'Mouse Only', 'Keys Only']
    app.selectedMode = 'Default'
    app.colorPreferences = [[rgb(227, 231, 211), rgb(208, 213, 201), rgb(189, 194, 191), 
                            rgb(171, 175, 170), rgb(152, 156, 148), rgb(124, 128, 118), 
                            rgb(95, 99, 88), rgb(66, 70, 58), rgb(37, 41, 28)], 
                            [rgb(222, 203, 198), rgb(212, 188, 183), rgb(201, 173, 167), 
                            rgb(178, 157, 160), rgb(154, 140, 152), rgb(134, 125, 141), 
                            rgb(130, 130, 155), rgb(93, 98, 131), rgb(64, 67, 94)], 
                            [rgb(183, 195, 243), rgb(193, 176, 220), rgb(198, 149, 192), 
                            rgb(206, 109, 156), rgb(214, 68, 120), rgb(207, 18, 89), 
                            rgb(172, 33, 90), rgb(136, 48, 91), rgb(108, 73, 103)], 
                            [rgb(182, 165, 116), rgb(215, 190, 130), rgb(148, 140, 101), 
                            rgb(81, 90, 71), rgb(115, 115, 86), rgb(169, 129, 78), 
                            rgb(169, 95, 35), rgb(136, 74, 27), rgb(91, 48, 17)], 
                            [rgb(250, 243, 221), rgb(172, 203, 177), rgb(195, 209, 179), 
                            rgb(143, 192, 169), rgb(124, 184, 170), rgb(104, 176, 171),
                            rgb(91, 154, 143), rgb(83, 141, 122), rgb(74, 124, 89)]]
    app.fillColor = app.colorPreferences[0]

def setting_redrawAll(app): 
    drawLabel('Settings', app.width/2, app.height/12, size = 30, bold = True)
    drawRect(app.returnX, app.returnY, app.returnWidth, app.returnHeight,
             fill = None, border = 'black', align = 'center')
    drawLabel('Home', app.returnX, app.returnY, size = 14)
    drawLabel('Game Mode', app.width/2, app.height/4 - 50, bold = True, size = 18)
    for i in range(len(app.gameModes)): 
        if app.selectedMode == app.gameModes[i]: 
            drawRect(app.width/4*(i+1)+6, app.height/4+6, app.width/7, app.height/12, 
             fill = 'white', border = 'black', align = 'center')
            drawLabel(app.selectedMode, app.width/4*(i+1)+6, app.height/4+6, 
                        bold = True, size = 14)
        else: 
            drawRect(app.width/4*(i+1)+6, app.height/4+6, app.width/7, app.height/12, 
             fill = 'gray', align = 'center')
            drawRect(app.width/4*(i+1), app.height/4, app.width/7, app.height/12, 
             fill = 'white', border = 'black', align = 'center')
            drawLabel(app.gameModes[i], app.width/4*(i+1), app.height/4, 
                        bold = True, size = 14)
    
    drawLabel('Difficulty', app.width/2, app.height/2 - 50, bold = True, size = 18)
    for i in range(len(app.gameLevels1)): 
        if app.selectedLevel == app.gameLevels1[i]: 
            drawRect(app.width/4*(i+1)+6, app.height/2+6, app.width/7, app.height/12, 
                    fill = 'white', border = 'black', align = 'center')
            drawLabel(app.selectedLevel, app.width/4*(i+1)+6, app.height/2+6, 
                    bold = True, size = 14)
        else: 
            drawRect(app.width/4*(i+1)+6, app.height/2+6, app.width/7, app.height/12, 
                    fill = 'gray', align = 'center')
            drawRect(app.width/4*(i+1), app.height/2, app.width/7, app.height/12, 
                    fill = 'white', border = 'black', align = 'center')
            drawLabel(app.gameLevels1[i], app.width/4*(i+1), app.height/2, 
                    bold = True, size = 14)
    for i in range(len(app.gameLevels2)): 
        if app.selectedLevel == app.gameLevels2[i]: 
            drawRect(app.width*3/8 + app.width*2/8*i + 6, app.height*3/5 + 6, app.width/7 + 6, 
                    app.height/12, fill = None, border = 'black', align = 'center')
            drawLabel(app.selectedLevel, app.width*3/8 + app.width*2/8*i + 6, 
                    app.height*3/5 + 6, bold = True, size = 14)
        else: 
            drawRect(app.width*3/8 + app.width*2/8*i + 6, app.height*3/5+6, 
                    app.width/7, app.height/12, fill = 'gray', align = 'center')
            drawRect(app.width*3/8 + app.width*2/8*i, app.height*3/5, app.width/7, 
                    app.height/12, fill = 'white', border = 'black', align = 'center')
            drawLabel(app.gameLevels2[i], app.width*3/8 + app.width*2/8*i, 
                    app.height*3/5, bold = True, size = 14)
    drawLabel('Color Preference', app.width/2, app.height/2 + 200, 
            bold = True, size = 18)
    for i in range(len(app.colorPreferences)): 
        if app.fillColor == app.colorPreferences[i]: 
            for value in [1, 2, 3, 4, 5, 6, 7, 8, 9]: 
                cx = app.width/6*(i+1)+6 + app.width/36*((value-1)%3) + app.width/72 - 35
                cy = app.height/2+256 + app.height/36*((value-1)//3) + app.height/72 - 35
                fillColor = app.fillColor[value-1]
                drawRect(cx, cy, app.width/36, app.height/36, 
                            fill = fillColor, align = 'center')
        else: 
            drawRect(app.width/6*(i+1)+6, app.height/2+256, app.width/12, 
                app.height/12, fill = 'gray', align = 'center')
            for value in [1, 2, 3, 4, 5, 6, 7, 8, 9]: 
                cx = app.width/6*(i+1)+6 + app.width/36*((value-1)%3) + app.width/72 - 35
                cy = app.height/2+256 + app.height/36*((value-1)//3) + app.height/72 - 35
                fillColor = app.colorPreferences[i][value-1]
                drawRect(cx, cy, app.width/36, app.height/36, 
                            fill = fillColor, align = 'center')


def setting_onMousePress(app, mouseX, mouseY): 
    if ((app.returnX - app.returnWidth/2) < mouseX < (app.returnX + app.returnWidth/2) and 
        (app.returnY - app.returnHeight/2) < mouseY < (app.returnY + app.returnHeight/2)): 
        setActiveScreen('splash')

    for i in range(len(app.gameModes)): 
        if ((app.width/4*(i+1) - app.width/14 < mouseX < app.width/4*(i+1) + app.width/14) and 
            (app.height/4 - app.height/24 < mouseY < app.height/4 + app.height/24)): 
            app.selectedMode = app.gameModes[i]
            if i == 1: 
                app.keysDisabled = True
                app.mouseDisabled = False
            elif i == 2: 
                app.keysDisabled = False
                app.mouseDisabled = True
            else: 
                app.keysDisabled = app.mouseDisabled = False
    
    for i in range(len(app.gameLevels1)): 
        if ((app.width/4*(i+1) - app.width/14 < mouseX < app.width/4*(i+1) + app.width/14) and 
            (app.height/2 - app.height/24 < mouseY < app.height/2 + app.height/24)): 
            app.selectedLevel = app.gameLevels1[i]
            # app.board = State(getBoard(f'/Users/yyp/Documents/15-112/TP/tp-starter-files/boards/{app.selectedLevel}-{app.boardNum}.png.txt'))
            # app.userSolution = copy.deepcopy(app.board)
            # app.solution = State(app.board.solveSudoku())
    for i in range(len(app.gameLevels2)): 
        if ((app.width*3/8 + app.width*2/8*i - app.width/14 < mouseX) and 
            (mouseX < app.width*3/8 + app.width*2/8*i + app.width/14) and 
            (app.height*3/5  - app.height/24 < mouseY < app.height*3/5 + app.height/24)): 
            app.selectedLevel = app.gameLevels2[i]
            # app.board = getBoard(f'/Users/yyp/Documents/15-112/TP/tp-starter-files/boards/{app.selectedLevel}-{app.boardNum}.png.txt')
            # app.userSolution = copy.deepcopy(app.board)
            # app.solution = solveSudoku(app.board)
    for i in range(len(app.colorPreferences)): 
        if ((app.width/6*(i+1) + 6 - app.width/24) < mouseX < (app.width/6*(i+1) + 6 + app.width/24) and 
            (app.height/2 + 256 - app.height/24) < mouseY < (app.height/2 + 256 + app.height/24)): 
            app.fillColor = app.colorPreferences[i]


## Source: CS Academy isLegalSudoku (https://cs3-112-f22.academy.cs.cmu.edu/exercise/4745)
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

def solveSudoku(board):
    currentSolution = copy.deepcopy(board)
    return solveSudokuHelper(currentSolution)

def findEmptyCell(currentSolution): 
    rows, cols = len(currentSolution), len(currentSolution[0])
    for row in range(rows): 
        for col in range(cols): 
            if currentSolution[row][col] == 0: 
                return (row, col)
    return None

def solveSudokuHelper(currentSolution):
    rows, cols = len(currentSolution), len(currentSolution[0])
    if findEmptyCell(currentSolution) == None: 
        return currentSolution
    else: 
        row, col = findEmptyCell(currentSolution)
        for i in range(1, cols + 2): 
            currentSolution[row][col] = i
            if isLegalSudoku(currentSolution): 
                solution = solveSudokuHelper(currentSolution)
                if solution != None: 
                    return solution
            else: 
                currentSolution[row][col] = 0
        return None

def areLegalValues(L): 
    n = len(L)
    seen = set()
    for value in L: 
        if type(value) != int: 
            return False
        if value < 0 or value > n: 
            return False
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
    blockSize = round(n**0.5)
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
    if (rows != 4) and (rows != 9): 
        return False
    if (rows != cols): 
        return False
        
    for row in range(rows): 
        if not isLegalRow(grid, row): 
            return False
    for col in range(cols): 
        if not isLegalCol(grid, col): 
            return False
    blocks = rows
    for block in range(blocks): 
        if not isLegalBlock(grid, block): 
            return False
    return True


def distance(x1, y1, x2, y2): 
    return ((x1-x2)**2 + (y1-y2)**2)**0.5