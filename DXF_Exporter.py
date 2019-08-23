#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback

_app = None
_ui = None

#Global Set of EventHandlers
_handlers = []

#Format for Pathdisplay
_pathFormat = '<div align="left"><i>{}</i></div>'

#pathForSaving
_path = None

#Selected Faces for Export
faceSelection = None

# Event handler that reacts to when the command is destroyed. This terminates the script.            
class MyCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            #Iterate through selection and cast Selection elements to Faces
            if faceSelection:
                faceSelectionList = []
                design = _app.activeProduct
                rootComp = adsk.fusion.Component.cast(design.rootComponent)
                sketches = rootComp.sketches
                                
                dxfSketches = []
                                
                for i in range(faceSelection.selectionCount):
                    faceSelectionList.append(faceSelection.selection(i))
                
                nameCounter = 1
                for f in faceSelectionList:
                    fCast = adsk.fusion.BRepFace.cast(f.entity)
                    sketch = sketches.add(fCast)
                    sketch.name = 'DXF_sketch' + str(nameCounter)
                    dxfSketches.append(sketch)
                                        
                    nameCounter += 1

                if _path:
                    for s in dxfSketches:
                        fileName = _path + '/' + s.name + '.dxf'
                        s.saveAsDXF(fileName)                 
                else:
                    _ui.messageBox('no path selected.')
                
                                    
            else:
                _ui.messageBox('no faces selected.')                
            
            # When the command is done, terminate the script
            # This will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for Input Changes
class MyCommandInputChangedHandler(adsk.core.InputChangedEventHandler):    
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            inputs = eventArgs.inputs
            cmdInput = eventArgs.input            
            inputId = cmdInput.id
                    
            #Create FolderDialog wenn Folder Button is pressed
            if inputId == 'DestFolderSel':
                # Set styles of folder dialog.
                folderDlg = _ui.createFolderDialog()
                folderDlg.title = 'Selection Destination Folder' 
            
                # Show folder dialog
                dlgResult = folderDlg.showDialog()
                if dlgResult == adsk.core.DialogResults.DialogOK:
                    global _path
                    _path = folderDlg.folder
                    inputs.itemById('selectedFolder').formattedText = _pathFormat.format(_path)
                    
            #Everytime a face is selected or deselected copy the selection to global _selectedFaces
            elif inputId == 'faceSelector':
                global faceSelection
                faceSelection = inputs.itemById('faceSelector')
                                        
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
                

# Event handler that reacts when the command definitio is executed which
# results in the command being created and this event being fired.
class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):    
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # Get the command that was created.
            cmd = adsk.core.Command.cast(args.command)

            # Connect to the command destroyed event.
            onDestroy = MyCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)

            # Connect to the input changed event.           
            onInputChanged = MyCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)    

            # Get the CommandInputs collection associated with the command.
            inputs = cmd.commandInputs

            #Add Button for Destinaton Folder Selection
            inputs.addBoolValueInput('DestFolderSel','Dest. Folder',False)
            
            #Add Text Field for displaying the currently selected Folder
            pathMsg = _pathFormat.format('no Path selected')
            inputs.addTextBoxCommandInput('selectedFolder','',pathMsg,2,True)
            
            #Add Selection for Faces to Export
            faceSelector = inputs.addSelectionInput('faceSelector','Select Faces','_blank_')
            faceSelector.addSelectionFilter('PlanarFaces')
            faceSelector.setSelectionLimits(0)            

        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def run(context):
    global _app, _ui
    _app = adsk.core.Application.get()
    _ui = _app.userInterface

    try:
        cmdDef = _ui.commandDefinitions.itemById('DXFExport')
        if not cmdDef:
            cmdDef = _ui.commandDefinitions.addButtonDefinition('DXFExport','SketchToDXFExport','A Tool to quickly Export multiple Sketches to DXF-File')

        # Connect to the command created event.
        onCommandCreated = MyCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)
                
        # Execute the command definition.
        cmdDef.execute()

        # Prevent this module from being terminated when the script returns, because we are waiting for event handlers to fire.
        adsk.autoTerminate(False)

    except:
        if _ui:
           _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
