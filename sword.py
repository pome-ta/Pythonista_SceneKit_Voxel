import numpy as np
from PIL import Image as ImageP
from objc_util import load_framework, ObjCClass, ObjCInstance, on_main_thread, nsurl
import ui
import random
import pdbg

load_framework('SceneKit')

SCNView = ObjCClass('SCNView')
SCNScene = ObjCClass('SCNScene')
SCNNode = ObjCClass('SCNNode')
SCNCamera = ObjCClass('SCNCamera')
SCNLight = ObjCClass('SCNLight')
SCNBox = ObjCClass('SCNBox')

UIColor = ObjCClass('UIColor')
UIImage = ObjCClass('UIImage')
NSData = ObjCClass('NSData')

img = ImageP.open('./assets/img.PNG')
np_img = np.asanyarray(img)
palette = img.getpalette()
np_palette = np.asanyarray(palette).reshape(-1, 3)
np_index = np_img[::10, ::10]
index = np_index[::-1]
inde_x, inde_y = index.shape


class SceneView:
  @on_main_thread
  def __init__(self):
    self.view = self.create_view()
    self.view_did_load()

  def create_view(self):
    scnView = SCNView.alloc()
    scnView.initWithFrame_options_(((0, 0), (100, 100)), None)
    #self.scnView.autorelease()
    scnView.autoresizingMask = ((1 << 1) | (1 << 4))
    #scnView.backgroundColor = UIColor.blackColor()
    
    scnView.allowsCameraControl = True
    scnView.showsStatistics = True
    '''
    OptionNone = 0
    ShowPhysicsShapes = (1 << 0)
    ShowBoundingBoxes = (1 << 1)
    ShowLightInfluences = (1 << 2)
    ShowLightExtents = (1 << 3)
    ShowPhysicsFields = (1 << 4)
    ShowWireframe = (1 << 5)
    RenderAsWireframe = (1 << 6)
    ShowSkeletons = (1 << 7)
    ShowCreases = (1 << 8)
    ShowConstraints = (1 << 9)
    ShowCameras = (1 << 10)
    '''
    #scnView.debugOptions = (1 << 1) | (1 << 3) | (1 << 5) | (1 << 9) | (1 << 10)
    return scnView

  def view_did_load(self):
    bkSky_URL = NSData.dataWithContentsOfURL_(
      nsurl('./assets/Background_sky.png'))
    tex_bks = UIImage.alloc().initWithData_(bkSky_URL)
    scene = SCNScene.scene()
    #scene.background().contents = tex_bks
    scene.lightingEnvironment().contents = tex_bks
    scene.lightingEnvironment().intensity = 1.24

    # --- Light
    omni_object = SCNLight.light()
    omni_object.type = 'omni'
    omni_object.castsShadow = True
    omni_node = SCNNode.node()
    omni_node.light = omni_object
    omni_node.position = (-16, -16, 8)
    scene.rootNode().addChildNode_(omni_node)

    cameraNode = SCNNode.node()
    cameraNode.camera = SCNCamera.camera()
    cameraNode.position = (0.0, -2, 32)
    scene.rootNode().addChildNode_(cameraNode)

    boxs = self.create_boxNode_marix(inde_x, inde_y)
    scene.rootNode().addChildNode_(boxs)

    self.view.scene = scene

  def create_boxNode_marix(self, x=1, y=1):
    boxNode = SCNNode.node()
    for i in range(x):
      for j in range(y):
        if index[j][i]:
          p = np_palette[index[j][i]]

          r = p[0] / 255
          g = p[1] / 255
          b = p[2] / 255
          box = SCNBox.box()
          box.material().lightingModelName = 'SCNLightingModelPhysicallyBased'
          box.firstMaterial().diffuse(
          ).contents = UIColor.colorWithRed_green_blue_alpha_(r, g, b, 1)
          box.width = 1
          box.height = 1
          box.length = 1
          box.chamferRadius = 0.05
          _boxNode = SCNNode.node()
          _boxNode.geometry = box
          _boxNode.position = (i, j, random.random() / 8)
          boxNode.addChildNode_(_boxNode)
    boxNode.position = (-((x - 1) / 2), -((y - 1) / 2), 0)
    return boxNode


class View(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.bg_color = 'maroon'
    self.instance = ObjCInstance(self)
    scn = SceneView()
    self.instance.addSubview_(scn.view)


if __name__ == '__main__':
  view = View()
  view.present(style='fullscreen', orientations=['portrait'])

