import tkinter as tk
from tkinter import ttk
from PIL import ImageTk


class TKWrapper():
    
    def __init__(self, width=50, height=50):
        
        #Initialise Tkinter GUI
        self.main = tk.Tk()
        self.main.title("Wuxiaworld-2-eBook")
        self.main.geometry("{}x{}".format(width, height))
        self.main.resizable(True, True)
        self.app = tk.Frame(self.main)
        self.app.grid()
        self.guiElements = {}
        self.columnsRows = [0]
    
    
    def appendColumn(self, columnNumber):
        
        # Append columns to the list until we reach the column number input
        while columnNumber+1 > len(self.columnsRows):
            self.columnsRows.append(0)
    
    
    def incrementRow(self, column, rowspan = 1):
        
        self.columnsRows[column] += rowspan
    
    
    def insertImage(self, elementName, imageInput, column, kwargs={}):
        
        self.appendColumn(column)
        
        # Convert input Pillow Image to the correct format and put it in the GUI grid
        imageInput = ImageTk.PhotoImage(imageInput)
        image = tk.Label(self.app, image=imageInput)
        image.grid(column = column, row = self.columnsRows[column], **kwargs)
        image.image = imageInput
        
        # Manage rows
        if 'rowspan' in kwargs.keys():
            self.incrementRow(column, kwargs['rowspan'])
        else:
            self.incrementRow(column)
        
        # Store the reference to the created image label
        self.guiElements[elementName] = image
    
    
    def replaceImage(self, elementName, imageInput):
        
        imageInput = ImageTk.PhotoImage(imageInput)
        self.guiElements[elementName]['image'] = imageInput
        self.guiElements[elementName].image = imageInput
    
    
    def createLabel(self, elementName, labelText, column, kwargs={}):
        
        self.appendColumn(column)
        
        # Create a label
        label = ttk.Label(self.app, text = labelText)
        label.grid(column = column, row = self.columnsRows[column], **kwargs)
        
        # Manage rows
        if 'rowspan' in kwargs.keys():
            self.incrementRow(column, kwargs['rowspan'])
        else:
            self.incrementRow(column)
        
        # Store the reference to the created label
        self.guiElements[elementName] = label
    
    
    def createCheckbutton(self, elementName, column, kwargs={}, kwargs2={}):
        
        self.appendColumn(column)
        
        # Create a boolean variable and the corresponding checkbutton
        boolVar = tk.BooleanVar()
        checkbutton = ttk.Checkbutton(self.app, variable=boolVar, offvalue=False, onvalue=True, state="enabled", **kwargs)
        checkbutton.grid(column = column, row = self.columnsRows[column], **kwargs2)
        
        # Manage rows
        if 'rowspan' in kwargs2.keys():
            self.incrementRow(column, kwargs2['rowspan'])
        else:
            self.incrementRow(column)
        
        # Store references to the boolean variable and the checkbutton
        self.guiElements[elementName] = [boolVar, checkbutton]
    
    
    def createCombobox(self, elementName, column, initialData=None, kwargs={}, kwargs2={}, varFunction = None):
        
        self.appendColumn(column)
        
        # Create a string variable and a corresponding combobox
        strVar = tk.StringVar()
        combobox = ttk.Combobox(self.app, textvariable = strVar, state = "readonly", **kwargs)
        combobox.grid(column = column, row = self.columnsRows[column], **kwargs2)
        
        # If a callback function is one of the inputs, attach it to the string variable
        if varFunction != None:
            strVar.trace("w", varFunction)
        
        # If data was input, store it in the combobox
        if initialData != None:
            combobox["values"] = initialData
            combobox.current(0)
        
        # Manage rows
        if 'rowspan' in kwargs2.keys():
            self.incrementRow(column, kwargs2['rowspan'])
        else:
            self.incrementRow(column)
        
        # Store references to the string varaible and the combobox
        self.guiElements[elementName] = [strVar, combobox]
    
    
    def createButton(self, elementName, labelText, column, kwargs={}, kwargs2={}):
        
        self.appendColumn(column)
        
        # Create a button
        button = ttk.Button(self.app, text = labelText, **kwargs)
        button.grid(column = column, row = self.columnsRows[column], **kwargs2)
        
        # Manage Rows
        if 'rowspan' in kwargs2.keys():
            self.incrementRow(column, kwargs2['rowspan'])
        else:
            self.incrementRow(column)
        
        # Store a reference to the button
        self.guiElements[elementName] = button
    
    
    def begin(self):
    
        # Launch the GUI
        self.main.mainloop()
