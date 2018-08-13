from kivy.app import App
from kivy.uix.scatter import ScatterPlane
from kivy.properties import ObjectProperty, BooleanProperty, ListProperty
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.core.text import Label as CoreLabel
import random


nodes = [
    {
        'name': 'hobarey',
        'inPorts': [
            'in0',
            'in1',
            'in2',
            'in3',
        ],
        'outPorts':[
            'out0',
            'out1',
        ]
    },
    {
        'name': 'heley',
        'inPorts': [
        ],
        'outPorts':[
            'out0',
            'out1',
        ]
    },
    {
        'name': 'evet',
        'inPorts': [
            'in0',
        ],
        'outPorts':[
            'out0',
            'out1',
        ]
    },
]


class Canvas(ScatterPlane):
    app = ObjectProperty()

    def on_touch_down(self, touch):
        if touch.is_triple_tap:
            self.app.buildNode(*self.to_local(touch.x, touch.y))

        return super(Canvas, self).on_touch_down(touch)


class Edge(Widget):
    app = ObjectProperty()
    fromPort = ObjectProperty()
    toPort = ObjectProperty()

    def setFromX(self, obj, value):
        self.fromX = value

    def setFromY(self, obj, value):
        self.fromY = value

    def setToX(self, obj, value):
        self.toX = value

    def setToY(self, obj, value):
        self.toY = value


class Port(Widget):
    isInPort = BooleanProperty(False)
    app = ObjectProperty()
    grab = BooleanProperty(False)
    flow = ObjectProperty()

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.grab = True
            self.app.edgeCandidate = True
        else:
            self.grab = False

        return super(Port, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.grab:
            if self.isInPort:
                if self.flow:
                    self.app.deleteItem(self.flow)

                    self.grab = False
                    self.flow.fromPort.grab = True

                    self.flow = False
                    return super(Port, self).on_touch_move(touch)

                self.edge.fromX = touch.x
                self.edge.fromY = touch.y
                self.app.toPort = self
            else:
                self.edge.toX = touch.x
                self.edge.toY = touch.y
                self.app.fromPort = self

            self.edge.width = 2

        return super(Port, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        self.edge.fromX = self.center_x
        self.edge.fromY = self.center_y
        self.edge.toX = self.center_x
        self.edge.toY = self.center_y
        self.edge.width = 0.1

        self.app.portMessage = ''

        if self.app.edgeCandidate and self.collide_point(touch.x, touch.y):
            self.app.addFlow(self)

        return super(Port, self).on_touch_up(touch)


class NodeEmpty(Image):
    app = ObjectProperty()


class NodeTopLeft(Image):
    app = ObjectProperty()


class NodeTopRight(Image):
    app = ObjectProperty()


class NodeBottomLeft(Image):
    app = ObjectProperty()


class NodeBottomRight(Image):
    app = ObjectProperty()


class NodeIn(Image):
    app = ObjectProperty()
    textTexture = ObjectProperty()

    def setText(self, text):
        label = CoreLabel(
            text=text,
            font_size=12,
            color=(0, 0, 0, 1),
        )

        label.refresh()
        texture = label.texture
        textureSize = list(texture.size)

        self.textTexture = texture
        self.textSize = textureSize


class NodeOut(Image):
    app = ObjectProperty()
    textTexture = ObjectProperty()

    def setText(self, text):
        label = CoreLabel(
            text=text,
            font_size=12,
            color=(0, 0, 0, 1),
        )

        label.refresh()
        texture = label.texture
        textureSize = list(texture.size)

        self.textTexture = texture
        self.textSize = textureSize


class NodeContainer(GridLayout):
    app = ObjectProperty()
    grab = BooleanProperty(False)
    nameTexture = ObjectProperty()
    edges = ListProperty()

    def watchEdges(self, obj, value):
        self.edges.append(value)

    def setNameText(self, text):
        label = CoreLabel(
            text=text,
            font_size=12,
            color=(0, 0, 0, 1),
            bold=True
        )

        label.refresh()
        texture = label.texture
        textureSize = list(texture.size)

        self.nameTexture = texture
        self.nameSize = textureSize

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            if touch.is_double_tap:
                self.app.deleteItem(self)
                return False

            touchLocal = self.to_local(touch.x, touch.y, relative=True)
            if 20 < touchLocal[0] < 95:
                self.grab = True
            else:
                self.grab = False
        else:
            self.grab = False

        return super(NodeContainer, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.grab:
            self.x += touch.dpos[0]
            self.y += touch.dpos[1]

        return super(NodeContainer, self).on_touch_move(touch)


class SuApp(App):
    def build(self):
        self.canvas = Canvas()
        self.canvas.app = self

        self.edgeCandidate = False
        self.fromPort = None
        self.toPort = None

        return self.canvas

    def buildNode(self, x, y):
        node = random.choice(nodes)  # DEBUG

        name = node['name'].upper()
        maxPortCount = max(len(node['inPorts']), len(node['outPorts']))

        nodeContainer = NodeContainer()
        nodeContainer.app = self

        nodeContainer.rows = maxPortCount + 2
        nodeContainer.cols = 2

        newItem00 = NodeTopLeft()
        newItem00.app = self

        newItem02 = NodeTopRight()
        newItem02.app = self

        nodeContainer.add_widget(newItem00)
        nodeContainer.add_widget(newItem02)

        inPortsPop = [i for i in node['inPorts']]
        outPortsPop = [i for i in node['outPorts']]

        for i in range(maxPortCount):
            if inPortsPop:
                text = inPortsPop.pop(0)
                newItemIn = NodeIn()
                newItemIn.setText(text)
                newItemIn.app = self
                newItemIn.port.bind(flow=nodeContainer.watchEdges)
            else:
                newItemIn = NodeEmpty()
                newItemIn.app = self

            if outPortsPop:
                text = outPortsPop.pop(0)
                newItemOut = NodeOut()
                newItemOut.setText(text)
                newItemOut.app = self
                newItemOut.port.bind(flow=nodeContainer.watchEdges)
            else:
                newItemOut = NodeEmpty()
                newItemOut.app = self

            nodeContainer.add_widget(newItemIn)
            nodeContainer.add_widget(newItemOut)

        newItem30 = NodeBottomLeft()
        newItem30.app = self

        newItem32 = NodeBottomRight()
        newItem32.app = self

        nodeContainer.add_widget(newItem30)
        nodeContainer.add_widget(newItem32)
        nodeContainer.center = x, y

        nodeContainer.setNameText(name)

        self.canvas.add_widget(nodeContainer)

    def addFlow(self, otherPort):
        if otherPort.isInPort:
            self.toPort = otherPort
        else:
            self.fromPort = otherPort

        if self.fromPort and self.toPort and not self.toPort.flow:
            newItem = Edge()
            newItem.app = self
            newItem.fromX = self.fromPort.center_x
            newItem.fromY = self.fromPort.center_y
            newItem.toX = self.toPort.center_x
            newItem.toY = self.toPort.center_y
            self.fromPort.bind(center_x=newItem.setFromX)
            self.fromPort.bind(center_y=newItem.setFromY)
            self.toPort.bind(center_x=newItem.setToX)
            self.toPort.bind(center_y=newItem.setToY)

            self.fromPort.flow = newItem
            self.toPort.flow = newItem
            newItem.fromPort = self.fromPort
            newItem.toPort = self.toPort

            self.canvas.add_widget(newItem)

        self.edgeCandidate = False
        self.fromPort = None
        self.toPort = None

    def deleteItem(self, item):
        self.canvas.remove_widget(item)
        if hasattr(item, 'edges'):
            while item.edges:
                edge = item.edges.pop(0)
                if edge:
                    edge.fromPort.flow = False
                    edge.toPort.flow = False
                    self.canvas.remove_widget(edge)


if __name__ == '__main__':
    SuApp().run()
