# Dependencies
import pygame
from vectors import PointWithinRectangle

# Object Classes

class Connection():
    # Connection Class is used to represent an event Connection 
    # EventList refers to the list of Connections for an event that the Connection will be in

    def __init__(self, EventList, Function):
        self.EventList = EventList
        self.Function = Function

    def Disconnect(self):
        self.EventList.remove(self) 

class UIObject(): # EventDrivenObject + special methods
    # UIObject contains base components of all UIObjects including Form which contains UIObjects 
    Events = tuple(["OnPropertyChange"]) # Default UI Events

    def __init__(self):
        self.__dict__["Callbacks"] = {} # Callbacks contains Connections for events 

        self.Active = True # Elements are activated by default (so are rendered, process events)

        self.AddEvents(UIObject.Events) # This AddEvents function is called at all __init__ levels if the class has events to add

    def __setattr__(self, PropertyName, PropertyValue): # intercepts setting values for event-handling
        OldValue = None

        if hasattr(self, PropertyName):
            OldValue = getattr(self, PropertyName)
        
        self.__dict__[PropertyName] = PropertyValue # set value

        # note that we do not need a check for Callbacks as __init__ is called before this func 
        self.Fire("OnPropertyChange", PropertyName, OldValue, PropertyValue) # event fire (PropertyName, OldValue, NewValue)

    def Warn(self, Message): # Used to make specific prints for the object 
        print("UIObject [" + self.__class__.__name__ +  "] WARNING: " + Message)

    def AddEvents(self, EventNames): # Similar to builder design pattern, you can add more events at stages 
        for EventName in EventNames:
            if not (EventName in self.Callbacks):
                self.Callbacks[EventName] = []
            else:
                self.Warn(F"{EventName} is already an event!")

    def Connect(self, EventName, Function): # Create Connection to an event in the object 
        if EventName in self.Callbacks:
            CallbackConnection = Connection(self.Callbacks[EventName], Function)
            self.Callbacks[EventName].append(CallbackConnection)
            return CallbackConnection
        else:
            self.Warn(F"{EventName} is not an event!")

    def Fire(self, EventName, *args, **kwargs): # Used to signal an event happening: passed arguments to ALL current Connections
        if EventName in self.Callbacks:
            for Connection in self.Callbacks[EventName]:
                Connection.Function(self, *args, **kwargs) # CallbackData[0] is a Function
        else:
            self.Warn(F"{EventName} is not an event!")

    def ProcessEvents(self, Events): # All UIObjects have this but there is no default processing (that does something)
        pass

    def Render(self, Screen): # No default rendering protocol for all objects 
        pass

class Form(UIObject):
    # Form Object is a container for visual UIObjects: switching between forms changes the UIObjects rendered on screen
    Events = tuple(["OnLoad"])

    CurrentForm = None # This class-wide property is used at the end (see # Current Form Behaviour)

    def __init__(self, Name):
        super().__init__()

        self.Name = Name
        self.Active = False # disabled until set as current form; to prevent unwanted rendering and processing in between form switches 
        self.Entities = []
        
        self.AddEvents(Form.Events)

        def SetAsCurrentForm(self, PreviousForm):
            pygame.display.set_caption("Chess - " + self.Name)

        self.Connect("OnLoad", SetAsCurrentForm)

    def AddEntity(self, Entity):
        self.Entities.append(Entity)

    def ProcessEvents(self, Events):
        for Entity in self.Entities:
            if Entity.Active:
                Entity.ProcessEvents(Events)

    def Render(self, Screen):
        Screen.fill(self.BackgroundColour)

        for Entity in self.Entities:
            if Entity.Active:
                Entity.Render(Screen)

class App(Form):
    # Special kind of form which contains an app that controls rendering and processing (used for ChessGame which has rendering and processing  in itself)
    # It essentially combines the power of a unique app and a form by rendering/processing form elements on top

    Events = tuple(["EventProcessed"])

    def __init__(self, Name, RenderFunction=Form.Render, ProcessFunction=Form.ProcessEvents):
        super().__init__(Name)

        self.RenderFunction = RenderFunction 
        self.EventFunction = ProcessFunction

        self.AddEvents(App.Events)

    def Render(self, Screen):
        self.RenderFunction(self, Screen)

        for Entity in self.Entities: # The order means form elements are rendered on top of the app
            if Entity.Active:
                Entity.Render(Screen)

    def ProcessEvents(self, Events):
        self.Fire("EventProcessed", self.EventFunction(self, Events))

        for Entity in self.Entities:
            if Entity.Active:
                Entity.ProcessEvents(Events)

class Box(UIObject): 
    # Used as a rectangle container for subclasses TextLabel, ImageLabel
    Events = ("OnClick","OnMouseEnter", "OnMouseLeave")

    def __init__(self):
        super().__init__()

        # External Variables
        self.BackgroundColour = (255,255,255)
        self.BackgroundEnabled = True
        self.Size = (100,100)
        self.Position = (100,100)

        #Internal Variables
        self.Rectangle = pygame.Rect(100,100,100,100)
        self.MouseIn = False

        self.OutlineSize = 0
        self.OutlineColour = (29,20,20)
        self.OutlineRectangle = self.Rectangle

        self.AddEvents(Box.Events)

        def UpdatePosition(Object, PropertyName, OldValue, NewValue): # Updates the Internal variable dependent on other variables
            if PropertyName == "Position":
                self.Rectangle = pygame.Rect(NewValue[0], NewValue[1], self.Rectangle.width, self.Rectangle.height)
            elif PropertyName == "Size":
                self.Rectangle = pygame.Rect(self.Rectangle.left, self.Rectangle.top, NewValue[0], NewValue[1])
        
        def UpdateOutline(Object, PropertyName, OldValue, NewValue): # Similar to UpdatePosition
            if (PropertyName == "Size") or (PropertyName == "Position") or (PropertyName == "OutlineSize") or (PropertyName == "OutlineColour"):
                Left = self.Rectangle.left - self.OutlineSize
                Top = self.Rectangle.top - self.OutlineSize
                Width = self.Rectangle.width + (self.OutlineSize * 2)
                Height = self.Rectangle.height + (self.OutlineSize * 2)
                
                self.OutlineRectangle = pygame.Rect(Left, Top, Width, Height) # OutlineRectangle rendered underneath with dimensions of box plus some padding for the outline to be visible
              
        self.Connect("OnPropertyChange", UpdatePosition)
        self.Connect("OnPropertyChange", UpdateOutline)

    def ProcessEvents(self, Events):
        MousePosition = pygame.mouse.get_pos()

        if PointWithinRectangle(MousePosition[0], MousePosition[1], self.Rectangle.left, self.Rectangle.top, self.Rectangle.width, self.Rectangle.height):
            if not self.MouseIn:
                self.MouseIn = True
                self.Fire("OnMouseEnter")
        elif self.MouseIn:
            self.MouseIn = False
            self.Fire("OnMouseLeave")
            
        for Event in Events:
            if Event.type == pygame.MOUSEBUTTONDOWN:
                if self.Rectangle.collidepoint(Event.pos): # does the same thing as PointWithinRectangle 
                    self.Fire("OnClick", Event)

    def Render(self, Screen):
        if self.OutlineSize > 0:
            pygame.draw.rect(Screen, self.OutlineColour, self.OutlineRectangle)

        if self.BackgroundEnabled:
            pygame.draw.rect(Screen, self.BackgroundColour, self.Rectangle)

class TextLabel(Box):
    # A form of box with text overlayed
    Events = tuple([])

    def __init__(self):
        super().__init__()
        
        self.TextSize = 32
        self.FontName = "freesansbold.ttf"

        self.Text = ""
        self.TextColour = (0,0,0)

        self.Font = pygame.font.Font(self.FontName, self.TextSize)
    
        self.AddEvents(TextLabel.Events)

        def UpdateFont(Object, PropertyName, OldValue, NewValue): 
            if (PropertyName == "TextSize") or (PropertyName == "FontName"):
                self.Font = pygame.font.Font(self.FontName, self.TextSize) # Font object is a container controlling TextSize + Font
                self.PrepareFontToRender() 
            elif (PropertyName == "Text") or (PropertyName == "TextColour") or (PropertyName == "BackgroundColour") or (PropertyName == "Rectangle"):
                self.PrepareFontToRender()

        self.Connect("OnPropertyChange", UpdateFont)
        
    def PrepareFontToRender(self): # Font object -> object that can be drawn to screen 
        self.FontToRender = self.Font.render(self.Text, True, self.TextColour, self.BackgroundColour) # creates an object similar to a rectangle 
        FontRectangle = self.FontToRender.get_rect()

        self.AlignedX = self.Rectangle.left + (self.Rectangle.width - FontRectangle.width)/2 # align text with background box
        self.AlignedY = self.Rectangle.top + (self.Rectangle.height - FontRectangle.height)/2

    def Render(self, Screen):
        Box.Render(self, Screen)

        Screen.blit(self.FontToRender, (self.AlignedX, self.AlignedY, self.Rectangle.width, self.Rectangle.height)) 

class ImageLabel(Box):
    # Box with an image overlayed 
    Events = tuple([])

    def __init__(self):
        super().__init__()

        self.ImageSource = None
        self.Image = None

        self.AddEvents(ImageLabel.Events)

        def UpdateImage(self, PropertyName, OldValue, NewValue):
            if PropertyName == "ImageSource":
                self.Image = pygame.image.load("Images\\" + self.ImageSource)
                self.Image = pygame.transform.scale(self.Image, self.Rectangle.size)

        self.Connect("OnPropertyChange", UpdateImage)

    def Render(self, Screen):
        Box.Render(self, Screen)
        Screen.blit(self.Image, self.Position)
        
# Current Form Behaviour

def SetCurrentForm(FormToSet): # Only one form enabled at a time 
    if Form.CurrentForm:
        Form.CurrentForm.Active = False

    FormToSet.Fire("OnLoad", Form.CurrentForm)

    FormToSet.Active = True
    Form.CurrentForm = FormToSet

# Update and Render can be called by the event loop in the main code file

def Update(Events): 
    if Form.CurrentForm and Form.CurrentForm.Active:
        Form.CurrentForm.ProcessEvents(Events)

def Render(Screen):
    if Form.CurrentForm and Form.CurrentForm.Active:
        Form.CurrentForm.Render(Screen)
