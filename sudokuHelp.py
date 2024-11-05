from cmu_graphics import *
import math, random, copy

from runAppWithScreens import *

def help_onScreenStart(app): 
    app.returnX = app.width/14
    app.returnY = app.height/12
    app.returnWidth = app.width/10
    app.returnHeight = app.height/16

def help_redrawAll(app): 
    drawLabel('Settings', app.width/2, app.height/12, size = 30, bold = True)
    drawRect(app.returnX, app.returnY, app.returnWidth, app.returnHeight,
             fill = None, border = 'black', align = 'center')
    drawLabel('Home', app.returnX, app.returnY, size = 14)
    drawLabel('How to Play: Each row, column, and block must not have repeating values', 
            app.width/2, app.height/6, size = 16, bold = True)
    drawLabel("Press 'n' to load a new game", 
            app.width/2, app.height/6 + 50, size = 16)
    drawLabel('Mouse Only: User can only use mouse', 
            app.width/2, app.height/6 + 150, size = 16, bold = True)
    drawLabel('Press on number board to enter values ', 
            app.width/2, app.height/6 + 200, size = 16)
    drawLabel('Enter edit legal values mode + use number board to manually update legals ', 
            app.width/2, app.height/6 + 250, size = 16)
    drawLabel('Keyboard Only: User can only use keys ', 
            app.width/2, app.height/6 + 350, size = 16, bold = True)
    drawLabel('Press number keys on keyboard to enter values ', 
            app.width/2, app.height/6 + 400, size = 16)
    drawLabel("Press 'e' to enter edit legal values mode + use number keys to manually update legals ", 
            app.width/2, app.height/6 + 450, size = 16)
    ######## Write Instructions ########

def help_onMousePress(app, mouseX, mouseY): 
    if ((app.returnX - app.returnWidth/2) < mouseX < (app.returnX + app.returnWidth/2) and 
        (app.returnY - app.returnHeight/2) < mouseY < (app.returnY + app.returnHeight/2)): 
        setActiveScreen('splash')
    ######## Use if circular buttons ########
    # if distance(mouseX, mouseY, app.width/12, app.height/12) < (app.height/16): 
    #     setActiveScreen('splash')

def distance(x1, y1, x2, y2): 
    return ((x1-x2)**2 + (y1-y2)**2)**0.5