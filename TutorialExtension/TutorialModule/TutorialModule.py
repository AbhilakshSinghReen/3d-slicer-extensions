import logging
import os
from time import sleep

import vtk

import qt
import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

import requests


#
# TutorialModule
#

class TutorialModule(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "TutorialModule"  # TODO: make this more human readable by adding spaces
        self.parent.categories = ["Examples"]  # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["John Doe (AnyWare Corp.)"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#TutorialModule">module documentation</a>.
"""
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
"""

        # Additional initialization step after application startup is complete
        slicer.app.connect("startupCompleted()", registerSampleData)


#
# Register sample data sets in Sample Data module
#

def registerSampleData():
    """
    Add data sets to Sample Data module.
    """
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    import SampleData
    iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')

    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.

    # TutorialModule1
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='TutorialModule',
        sampleName='TutorialModule1',
        # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
        # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
        thumbnailFileName=os.path.join(iconsPath, 'TutorialModule1.png'),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
        fileNames='TutorialModule1.nrrd',
        # Checksum to ensure file integrity. Can be computed by this command:
        #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
        checksums='SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95',
        # This node name will be used when the data set is loaded
        nodeNames='TutorialModule1'
    )

    # TutorialModule2
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='TutorialModule',
        sampleName='TutorialModule2',
        thumbnailFileName=os.path.join(iconsPath, 'TutorialModule2.png'),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        fileNames='TutorialModule2.nrrd',
        checksums='SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97',
        # This node name will be used when the data set is loaded
        nodeNames='TutorialModule2'
    )


#
# TutorialModuleWidget
#

class TutorialModuleWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._updatingGUIFromParameterNode = False

    def setup(self):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/TutorialModule.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = TutorialModuleLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)
        
        # Buttons
        self.ui.loadVolumeButton.connect('clicked(bool)', self.onLoadVolumeButtonClick)
        self.ui.segmentWithTsButton.connect('clicked(bool)', self.onSegmentWithTsButtonClick)

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

    def cleanup(self):
        """
        Called when the application closes and the module widget is destroyed.
        """
        self.removeObservers()

    def enter(self):
        """
        Called each time the user opens this module.
        """
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self):
        """
        Called each time the user opens a different module.
        """
        # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
        self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    def onSceneStartClose(self, caller, event):
        """
        Called just before the scene is closed.
        """
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event):
        """
        Called just after the scene is closed.
        """
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self):
        """
        Ensure parameter node exists and observed.
        """
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

        # Select default input nodes if nothing is selected yet to save a few clicks for the user
        if not self._parameterNode.GetNodeReference("InputVolume"):
            firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
            if firstVolumeNode:
                self._parameterNode.SetNodeReferenceID("InputVolume", firstVolumeNode.GetID())

    def setParameterNode(self, inputParameterNode):
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        if inputParameterNode:
            self.logic.setDefaultParameters(inputParameterNode)

        # Unobserve previously selected parameter node and add an observer to the newly selected.
        # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
        # those are reflected immediately in the GUI.
        if self._parameterNode is not None and self.hasObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode):
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
        self._parameterNode = inputParameterNode
        if self._parameterNode is not None:
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

        # Initial GUI update
        self.updateGUIFromParameterNode()

    def updateGUIFromParameterNode(self, caller=None, event=None):
        """
        This method is called whenever parameter node is changed.
        The module GUI is updated to show the current state of the parameter node.
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
        self._updatingGUIFromParameterNode = True
        
        # All the GUI updates are done
        self._updatingGUIFromParameterNode = False

    def updateParameterNodeFromGUI(self, caller=None, event=None):
        """
        This method is called when the user makes any change in the GUI.
        The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch

        self._parameterNode.SetNodeReferenceID("InputVolume", self.ui.inputSelector.currentNodeID)
        self._parameterNode.SetNodeReferenceID("OutputVolume", self.ui.outputSelector.currentNodeID)
        self._parameterNode.SetParameter("Threshold", str(self.ui.imageThresholdSliderWidget.value))
        self._parameterNode.SetParameter("Invert", "true" if self.ui.invertOutputCheckBox.checked else "false")
        self._parameterNode.SetNodeReferenceID("OutputVolumeInverse", self.ui.invertedOutputSelector.currentNodeID)

        self._parameterNode.EndModify(wasModified)
    
    def onLoadVolumeButtonClick(self):
        volumePath = self.ui.volumePathTextBox.text
        
        volumeNode = self.logic.loadVolume(volumePath)
        if volumeNode is None:
            return
        
        segmentationNode = self.logic.getSegmentationNode()
        segmentEditorNode = self.logic.getSegmentEditorNode()

        self.ui.embeddedSegmentEditorWidget.setMRMLScene(slicer.mrmlScene)
        self.ui.embeddedSegmentEditorWidget.setSegmentationNodeSelectorVisible(False)
        self.ui.embeddedSegmentEditorWidget.setSourceVolumeNodeSelectorVisible(False)

        self.ui.embeddedSegmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
        self.ui.embeddedSegmentEditorWidget.setSegmentationNode(segmentationNode)
        self.ui.embeddedSegmentEditorWidget.setSourceVolumeNode(volumeNode)

    def getPositionAndSize(self):
        "Validates and extracts position and size information from the 3 text boxes."

        def isValidNonNegativeFloatStr(input_str):
            if not input_str.replace(".", "").isnumeric():
                return False
            
            input_num = float(input_str)

            return input_num >= 0.0
        
        errors = []
        
        positionXStr = self.ui.shapePositionXTextBox.text
        if not isValidNonNegativeFloatStr(positionXStr):
            errors.append("Position X must be a valid non-negative number.")
        
        positionYStr = self.ui.shapePositionYTextBox.text
        if not isValidNonNegativeFloatStr(positionYStr):
            errors.append("Position Y must be a valid non-negative number.")
        
        sizeStr = self.ui.shapeSizeTextBox.text
        if not isValidNonNegativeFloatStr(sizeStr):
            errors.append("Size must be a valid non-negative number.")

        if len(errors) > 0:
            slicer.util.errorDisplay("\n".join(errors))
            return False, False

        position = (float(positionXStr), float(positionYStr))
        size = float(sizeStr)

        return position, size
    
    def onSegmentWithTsButtonClick(self):
        qt.QApplication.setOverrideCursor(qt.Qt.WaitCursor)

        self.logic.segmentWithTotalSegmentatorApi()

        qt.QApplication.restoreOverrideCursor()


#
# TutorialModuleLogic
#

class TutorialModuleLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self):
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """
        ScriptedLoadableModuleLogic.__init__(self)

        self.loadedVolumePath = None
        self.volumeNode = None
        self.segmentationNode = None
        self.segmentEditorNode = None

        self.baseUrl = "http://localhost:8000"
        self.apiBaseUrl = "http://localhost:8000/api"
        self.addSegmentationTaskEndpoint = f"{self.apiBaseUrl}/add-segmentation-task"
        self.getSegmentationTaskResultEndpoint = self.apiBaseUrl + "/get-segmentation-task-result?task_id={{taskId}}"
    
    def setDefaultParameters(self, parameterNode):
        """
        Initialize parameter node with default settings.
        """
        if not parameterNode.GetParameter("Threshold"):
            parameterNode.SetParameter("Threshold", "100.0")
        if not parameterNode.GetParameter("Invert"):
            parameterNode.SetParameter("Invert", "false")

    def getSegmentEditorNode(self):
        segmentEditorSingletonTag = "SegmentEditor"
        segmentEditorNode = slicer.mrmlScene.GetSingletonNode(segmentEditorSingletonTag, "vtkMRMLSegmentEditorNode")

        if segmentEditorNode is None:
            segmentEditorNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLSegmentEditorNode")
            segmentEditorNode.UnRegister(None)
            segmentEditorNode.SetSingletonTag(segmentEditorSingletonTag)
            self.segmentEditorNode = slicer.mrmlScene.AddNode(segmentEditorNode)
        
        return self.segmentEditorNode
    
    def getSegmentationNode(self):
        if self.segmentationNode is not None:
            return self.segmentationNode
        
        self.segmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")

        return self.segmentationNode
    
    def loadVolume(self, volumePath):
        if not os.path.exists(volumePath):
            slicer.util.errorDisplay("The given volume path does not exist.")
            return
        
        if not os.path.isfile(volumePath) or \
          (not volumePath.endswith(".nii") and not volumePath.endswith(".nii.gz")):
            slicer.util.errorDisplay("The given path is not a Nifti image.")
            return
        
        if volumePath == self.loadedVolumePath:
            slicer.util.messageBox("This volume is already loaded.")
            return
        
        self.volumeNode = slicer.util.loadVolume(volumePath)
        self.loadedVolumePath = volumePath
        return self.volumeNode

    def getCurrentSliceIndices(self):
        "Get the current slice indices for Axial, Coronal, and Sagittal."

        if self.volumeNode is None:
            return {
                'axial': -1,
                'coronal': -1,
                'sagittal': -1,
            }
        
        sliceIndices = {}
        
        for viewName, planeName in zip(["Red", "Green", "Yellow"], ["axial", "coronal", "sagittal"]):
            sliceWidget = slicer.app.layoutManager().sliceWidget(viewName)
            sliceLogic = sliceWidget.sliceLogic()

            sliceOffset = sliceLogic.GetSliceOffset()
            sliceIndex = sliceLogic.GetSliceIndexFromOffset(sliceOffset) - 1

            sliceIndices[planeName] = sliceIndex
            
        return sliceIndices

    def addSegmentationTask(self, volumePath):
        with open(volumePath, "rb") as f:
            files = {"file": f}
            addResponse = requests.post(self.addSegmentationTaskEndpoint, files=files)
        
        if addResponse.status_code != 206:
            return None
        
        addResponseData = addResponse.json()

        taskId = addResponseData.get('result', {}).get('taskId', None)
        return taskId
    
    def getSegmentationTaskUpdate(self, taskId):
        getSegmentationTaskResultEndpoint = self.getSegmentationTaskResultEndpoint.replace("{{taskId}}", taskId)

        getStatusReponse = requests.get(getSegmentationTaskResultEndpoint)
        if getStatusReponse.status_code != 200:
            return {
                "status": "failed",
            }
        
        getStatusReponseData = getStatusReponse.json()

        return getStatusReponseData["result"]
    
    def loadSegmentationFromUrl(self, segmentationFileUrl):
        loadedVolumeDir = os.path.dirname(self.loadedVolumePath)
        segmentationSavePath = os.path.join(loadedVolumeDir, "segmentation.nii.gz")

        getSegmentationResponse = requests.get(segmentationFileUrl)

        if getSegmentationResponse.status_code != 200:
            slicer.util.errorDisplay("Could not download segmentation file from server.")
            return
        
        with open(segmentationSavePath, "wb") as f:
            f.write(getSegmentationResponse.content)
        
        if self.segmentationNode is not None:
            segmentationNode = self.segmentationNode

            slicer.mrmlScene.RemoveNode(segmentationNode) # remove the segmentation node from the scene

            # Remove other related nodes
            associated_nodes = slicer.util.getNodesByClass("vtkMRMLSegmentationDisplayNode")
            for node in associated_nodes:
                if node.GetSegmentationNode() == segmentationNode:
                    slicer.mrmlScene.RemoveNode(node)

            # Check for remaining references to the segmentation node
            remaining_references = slicer.util.getNodesByClass("vtkMRMLSegmentationNode")
            for node in remaining_references:
                if node.GetAssociatedNodeID() == segmentationNode.GetID():
                    slicer.mrmlScene.RemoveNode(node)

        self.segmentationNode = slicer.util.loadSegmentation(segmentationSavePath)
        self.segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(self.volumeNode)

    def segmentWithTotalSegmentatorApi(self):
        newTaskId = self.addSegmentationTask(self.loadedVolumePath)
        if newTaskId == None:
            print("Task add failed")
            slicer.util.errorDisplay("Failed to add segmentation task to server.")
            return
        
        segmentationTaskUpdate = {
            "status": "queued",
        }
        while segmentationTaskUpdate["status"] != "completed" and segmentationTaskUpdate["status"] != "failed":
            segmentationTaskUpdate = self.getSegmentationTaskUpdate(newTaskId)
            sleep(1)

        if segmentationTaskUpdate["status"] == "failed":
            slicer.util.errorDisplay("Server failed to segment the loaded volume.")
            return
        
        segmentationFileUrl = segmentationTaskUpdate["segmentationFileUrl"]
        self.loadSegmentationFromUrl(f"{self.baseUrl}/{segmentationFileUrl}")


#
# TutorialModuleTest
#

class TutorialModuleTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_TutorialModule1()

    def test_TutorialModule1(self):
        """ Ideally you should have several levels of tests.  At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).  At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.  For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

        self.delayDisplay("Starting the test")

        # Get/create input data

        import SampleData
        registerSampleData()
        inputVolume = SampleData.downloadSample('TutorialModule1')
        self.delayDisplay('Loaded test data set')

        inputScalarRange = inputVolume.GetImageData().GetScalarRange()
        self.assertEqual(inputScalarRange[0], 0)
        self.assertEqual(inputScalarRange[1], 695)

        outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
        threshold = 100

        # Test the module logic

        logic = TutorialModuleLogic()

        # Test algorithm with non-inverted threshold
        logic.process(inputVolume, outputVolume, threshold, True)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], threshold)

        # Test algorithm with inverted threshold
        logic.process(inputVolume, outputVolume, threshold, False)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], inputScalarRange[1])

        self.delayDisplay('Test passed')
