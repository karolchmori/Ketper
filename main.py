import maya.cmds as mc
import sys
import os

script_dir = "F:\Individual\Programming\Ketper"  # Change this to your script's directory
if script_dir not in sys.path:
    sys.path.append(script_dir)

os.chdir(script_dir)

import util
import importlib
import dataFunctions as utils
import ElementsUI as elUI
import tabUtils
import tabCreation
import tabRigging
import tabLighting 
#import randomFunctions as ram


importlib.reload(utils)
importlib.reload(util)
importlib.reload(elUI)
importlib.reload(tabUtils)
importlib.reload(tabCreation)
importlib.reload(tabRigging)
importlib.reload(tabLighting)
#importlib.reload(ram)


mainWidth = 380
mainHeight = 700



def mainWindow(*args, **kwargs):
    if mc.window('mainWindow', exists= True):
        mc.deleteUI('mainWindow')
    
    mc.window('mainWindow', s=False, t='Ketper', wh=[mainWidth,mainHeight])
    form = mc.formLayout()
    tabs = mc.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
    mc.formLayout( form, edit=True, attachForm=((tabs, 'top', 0), (tabs, 'left', 0), (tabs, 'bottom', 0), (tabs, 'right', 0)) )

    child1 = tabUtils.page(mainWidth,mainHeight)
    child2 = tabCreation.page(mainWidth,mainHeight)
    child3 = tabRigging.page(mainWidth,mainHeight)
    child4 = tabLighting.page(mainWidth,mainHeight)
     
    mc.tabLayout( tabs, edit=True, tabLabel=((child1, 'Utils'), (child2, 'Build'), (child3, 'Rigging'), (child4, 'Lighting')) )

    mc.showWindow('mainWindow')



mainWindow()


