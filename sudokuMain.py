# try: from cmu_cs3_graphics import *
# except: from cmu_graphics import *
from cmu_graphics import *
import math, random, copy 

"'Extra Features: '"
"'1. Preferences: color preferences and show/do not show legals'"
"'2. Set all singletons'"
"'3. Board Variation: color mode (instead of numbers, play with different colors'"
"'4. Board Transformations: rotate board, row block swaps, row swaps'"
"'5. Additional Hint: X-Wing hint (eliminate legals)'"

## Source: https://www.cs.cmu.edu/~112-3/notes/term-project.html
import os
def removeTempFiles(path, suffix='.DS_Store'):
    if path.endswith(suffix):
        print(f'Removing file: {path}')
        os.remove(path)
    elif os.path.isdir(path):
        for filename in os.listdir(path):
            removeTempFiles(path + '/' + filename, suffix)

removeTempFiles('sampleFiles')
# removeTempFiles('sampleFiles', '.txt') # be careful

import sys, os

def runPipCommand(pipCommand, pipPackage=None): 
    # first upgrade pip:
    command = f"'{sys.executable}' -m pip -q install --upgrade pip"
    os.system(command)
    # input the package from the user if it's not supplied in the call:
    if pipPackage == None:
        pipPackage = input(f'Enter the pip package for {pipCommand} --> ')
    # then run pip command:
    command = f"'{sys.executable}' -m pip {pipCommand} {pipPackage}"
    os.system(command)

runPipCommand('install --upgrade', 'cmu_graphics')
runPipCommand('install', 'pyjokes') # <-- replace 'pyjokes' with your module!

import pyjokes
print(pyjokes.get_joke())

#################################

from runAppWithScreens import *
from sudokuSplash import *
from sudokuHelp import *
from sudokuSettings import *
from sudokuCreate import *
from sudokuPlay import *

##################################
# main
##################################


def main():
    runAppWithScreens(initialScreen = 'splash', height = 750, width = 700)

main()

# cmu_graphics.run()