from cmu_graphics import *
import math, random, copy
from PIL import Image

from runAppWithScreens import *

def splash_onScreenStart(app): 
    app.playX = app.width/2
    app.playY = app.height*1/3
    app.buttonWidth = app.width/3
    app.buttonHeight = app.height/7
    app.createX = app.width/2
    app.createY = app.height*1/2
    app.settingX = app.width/2
    app.settingY = app.height*4/6
    app.helpX = app.width/2
    app.helpY = app.height*5/6
    ## Source: https://www.dreamstime.com/photos-images/grid-paper.html
    app.image = Image.open('gridPaper.png')
    app.image = CMUImage(app.image)
    

def splash_redrawAll(app): 
    pilImage = app.image.image
    drawImage(app.image, 350, 375, align = 'center', 
                width = 700,
                height = 750)
    drawLabel('Sudoku', app.width/2, app.height/5, size = 30, bold = True)
    drawRect(app.playX, app.playY, app.buttonWidth, app.buttonHeight, 
             fill = 'white', border = 'black', align = 'center')
    drawLabel('Play', app.playX, app.playY, size = 20, bold = True)
    drawRect(app.settingX, app.settingY, app.buttonWidth, app.buttonHeight, 
             fill = 'white', border = 'black', align = 'center')
    drawLabel('Settings', app.settingX, app.settingY, size = 20, bold = True)
    drawRect(app.createX, app.createY, app.buttonWidth, app.buttonHeight, 
             fill = 'white', border = 'black', align = 'center')
    drawLabel('Create', app.createX, app.createY, size = 20, bold = True)
    drawRect(app.helpX, app.helpY, app.buttonWidth, app.buttonHeight, 
             fill = 'white', border = 'black', align = 'center')
    drawLabel('Help', app.helpX, app.helpY, size = 20, bold = True)

def splash_onMousePress(app, mouseX, mouseY): 
    if ((app.playX - app.buttonWidth/2) < mouseX < (app.playX + app.buttonWidth/2) and 
        (app.playY - app.buttonHeight/2) < mouseY < (app.playY + app.buttonHeight/2)): 
        setActiveScreen('game')
    elif ((app.settingX - app.buttonWidth/2) < mouseX < (app.settingX + app.buttonWidth/2) and 
        (app.settingY - app.buttonHeight/2) < mouseY < (app.settingY + app.buttonHeight/2)): 
        setActiveScreen('setting')
    elif ((app.helpX - app.buttonWidth/2) < mouseX < (app.helpX + app.buttonWidth/2) and 
        (app.helpY - app.buttonHeight/2) < mouseY < (app.helpY + app.buttonHeight/2)): 
        setActiveScreen('help')
    elif ((app.createX - app.buttonWidth/2) < mouseX < (app.createX + app.buttonWidth/2) and 
        (app.createY - app.buttonHeight/2) < mouseY < (app.createY + app.buttonWidth/2)): 
        setActiveScreen('create')

    ########use if circular buttons########
    # if distance(mouseX, mouseY, app.width/2, app.height*2/5) < (app.height/6): 
    #     setActiveScreen('game')
    # elif distance(mouseX, mouseY, app.width/2, app.height*3/5) < (app.height/6): 
    #     setActiveScreen('setting')
    # elif distance(mouseX, mouseY, app.width/2, app.height*4/5) < (app.height/6): 
    #     setActiveScreen('help')
    
def distance(x1, y1, x2, y2): 
    return ((x1-x2)**2 + (y1-y2)**2)**0.5