from bs4 import BeautifulSoup
from PageTools import PageTools
from EBookGenerator import EBookGenerator
from TKWrapper import TKWrapper
from PIL import Image
from io import BytesIO


class WWParser:
    
    def __init__(self):
        
        self.url = "https://www.wuxiaworld.com"
        
        # Download and parse the WuxiaWorld API JSON file
        self.jsonFile = PageTools().getJsonFromUrl(self.url+"/api/novels")
        self.novels = None
        self.novelNames = None
        self.novelSypnoses = None
        self.parseNovelList()
        
        # Container for all novels that are requested
        self.novelLibrary = {}
    
    
    def clearNovelCache(self):
        self.novelLibrary = {}
    
    
    def parseNovelList(self):
        
        # Handle key error if the novel doesn't have a sypnosis
        def checkForSypnosis(novel):
            try:
                novel['sypnosis']
            except KeyError:
                return False
            return True
        
        # Extract the required novel info
        self.novels = {novel['name']:[self.url+"/novel/"+novel['slug'], novel['coverUrl'], novel['translatorUserName'],\
                       novel['abbreviation']] for novel in self.jsonFile['items']}
        self.novelSypnoses = [{novel['name']:novel['sypnosis']} if checkForSypnosis(novel) else\
                              {novel['name']:"N/A"} for novel in self.jsonFile['items']]
        
        self.novelNames = list(self.novels.keys())
        self.novelNames.sort()
    
    
    def loadNovelInfo(self, novelName):
        
        if novelName in self.novelLibrary.keys():
            return
        
        # Load the webpage for the novel
        soup = PageTools().getSoupFromUrl(self.novels[novelName][0])
        
        # Parse all of the book names/sections
        bookTitles = PageTools().getElementsFromSoup(soup, [{"id":"accordion"},{"class_":"title"}], findAllEnableList = True, onlyText = True)
        
        
        # Download cover image
        coverImage = PageTools().downloadPage(self.novels[novelName][1])
        
        # Create an empty dictionary to store all chapter names and links
        chapterLibrary = []
        bookToC = {}
        for i, bookTitle in enumerate(bookTitles):
            
            # Extract the html containing the chapter links and names
            chapterInfo = PageTools().getElementsFromSoup(soup,[{"id":"collapse-{}".format(i)},\
                          {"class_":"row"},{"class_":"col-sm-6"},{"class_":"chapter-item"}], findAllEnableList = True)
            
            # Extract the chapter links and names
            chapterInfo = [[self.url+PageTools().getElementsFromSoup(chap, ["a"], findAllEnableList=True)[0]['href'],\
                            PageTools().getElementsFromSoup(chap, ["a"], findAllEnableList=True, onlyText=True)[0]] for chap in chapterInfo]
            
            # Store chapters for each book
            bookToC[bookTitle] = chapterInfo
            chapterLibrary.extend(bookToC[bookTitle])
        
        # Add the books, chapters, and the cover to the novel library
        self.novelLibrary[novelName] = [bookTitles, chapterLibrary, bookToC, coverImage]
    
    
    def getNovelNames(self):
        
        return self.novelNames
    
    
    def getImageBinary(self, novelName):
        
        self.loadNovelInfo(novelName)
        return self.novelLibrary[novelName][3]
    
    
    def getImagePillow(self, novelName):
        
        return Image.open(BytesIO(self.getImageBinary(novelName)))
    
    
    def getNovelBookNames(self, novelName):
        
        self.loadNovelInfo(novelName)
        return self.novelLibrary[novelName][0]
    
    
    def getNovelChapterLinks(self, novelName):
        
        self.loadNovelInfo(novelName)
        return [chapter[0] for chapter in self.novelLibrary[novelName][1]]
    
    
    def getNovelChapterNames(self, novelName):
        
        self.loadNovelInfo(novelName)
        return [chapter[1] for chapter in self.novelLibrary[novelName][1]]
    
    
    def getNovelBookChapterLinks(self, novelName, bookName):
        
        self.loadNovelInfo(novelName)
        return [chapter[0] for chapter in self.novelLibrary[novelName][2][bookName]]
    
    
    def getNovelBookChapterNames(self, novelName, bookName):
        
        self.loadNovelInfo(novelName)
        return [chapter[0] for chapter in self.novelLibrary[novelName][2][bookName]]
    
    
    def cleanChapter(self, soup):
        
        has_spoiler = None
        
        # Extract the chapter title and the chapter content
        chapter_title = soup.find(class_="caption clearfix")
        content = chapter_title.find_next_sibling(class_="fr-view")
        chapter_title = chapter_title.find("h4")
        
        # Get the chapter title, make it hidden if it contains spoilers
        try:
            if chapter_title.attrs["class"][0] == "text-spoiler":
                has_spoiler = chapter_title.text
                chapter_title = "Chapter name hidden due to potential spoilers"
            else:
                chapter_title = chapter_title.text
        except IndexError:
            chapter_title = chapter_title.text

        for a in content.find_all("a"):
            a.decompose()
        
        # Add html header to the chapter
        chapter = '<html xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<title>{0}</title>\n</head>\n<body>\n<h1>{0}</h1>'.format(chapter_title)
        chapter += str(content)
        if has_spoiler != None:
            chapter += "<strong>The chapter name is: {}</strong>".format(has_spoiler)
        
        # Return the chapter as a BeautifulSoup html object
        return BeautifulSoup(chapter, "html.parser")
    
    
    def generateBookFromTo(self, novelName, startChapter, endChapter, customCoverFilename = None, customBookName = None):
        
        # Download and clean all of the chapters
        chapterLinks = self.getNovelChapterLinks(novelName)
        pot_of_soup = [PageTools().getSoupFromUrl(link) for link in chapterLinks[startChapter:endChapter+1]]
        chapters = [self.cleanChapter(soup) for soup in pot_of_soup]
        
        # Download or load the cover image
        if customCoverFilename == None:
            image = self.getImageBinary(novelName)
        else:
            image = EBookGenerator().readImage(customCoverFilename)
        
        # Generate the ebook with a custom name or with start and end chapters as the name
        if customBookName != None:
            EBookGenerator().generateEBook(chapters, novelName, customBookName, self.novels[novelName][2], image)
        else:
            EBookGenerator().generateEBook(chapters, novelName, "{}-{}".format(startChapter+1, endChapter+1), self.novels[novelName][2], image)
    
    
    def generateBook(self, novelName, bookName, customCoverFilename = None, customBookName = None):
        
        # Download and clean all of the chapters in the book
        chapterLinks = self.getNovelBookChapterLinks(novelName, bookName)
        pot_of_soup = [PageTools().getSoupFromUrl(link) for link in chapterLinks]
        chapters = [self.cleanChapter(soup) for soup in pot_of_soup]
        
        # Download or load the cover image
        if customCoverFilename == None:
            image = self.getImageBinary(novelName)
        else:
            image = EBookGenerator().readImage(customCoverFilename)
        
        # Generate the ebook with a custom name or the name on the website
        if customBookName != None:
            EBookGenerator().generateEBook(chapters, novelName, customBookName, self.novels[novelName][2], image)
        else:
            EBookGenerator().generateEBook(chapters, novelName, bookName, self.novels[novelName][2], image)
    
    
    def generateBooks(self, novelName, bookNames, customCoverFilename = None, customBookNames = None):
        
        # If no custom book names are input, fill the input list with None objects
        if customBookNames == None:
            customBookNames = [None] * len(bookNames)
        
        # Download each book separately
        for bookName, customBookName in zip(bookNames, customBookNames):
            self.generateBook(novelName, bookNames, customCoverFilename, customBookName)


class WWGui:
    
    def __init__(self):
        
        # Create an instance of the Tkinter wrapper and the WuxiaWorld parser
        self.TKW = TKWrapper(690,340)
        self.WW = WWParser()

        # Create all UI elements
        self.TKW.createLabel("NovelLabel", "Select Novel: ", 0, {"pady":10, "padx":10, "sticky":"W"})
        self.TKW.createLabel("BookLabel", "Select Book: ", 0, {"pady":10, "padx":10, "sticky":"W"})
        self.TKW.createLabel("EndLabel", "Select Ending Chapter: ", 0, {"pady":10, "padx":10, "sticky":"W"})
        self.TKW.createLabel("ChaptersOnlyLabel", "Download separate chapters: ", 0, {"pady":10, "padx":10, "sticky":"W"})
        self.TKW.createCombobox("NovelCombobox", 1, self.WW.getNovelNames(), {"width":42})
        self.TKW.createCombobox("BookCombobox", 1, self.WW.getNovelBookNames(self.WW.getNovelNames()[0]), {"width":42})
        self.TKW.createCombobox("EndCombobox", 1, self.WW.getNovelBookNames(self.WW.getNovelNames()[0]), {"width":42})
        self.TKW.guiElements["EndCombobox"][1].configure(state="disabled")
        self.TKW.createCheckbutton("ChaptersOnly", 1, {"command":self.onChapterCheckboxChange}, {"sticky":"W"})
        self.TKW.createButton("DownloadButton", "Download", 1, {"command":self.onDownloadButtonClick})
        
        # Attach functions after creating the comboboxes to prevent errors on startup
        self.TKW.guiElements["NovelCombobox"][0].trace("w", self.onNovelFieldChange)
        self.TKW.guiElements["BookCombobox"][0].trace("w", self.onBookFieldChange)
        
        # Insert the cover image of the first book on WW
        self.coverImage = self.WW.getImagePillow(self.WW.getNovelNames()[0])
        self.TKW.insertImage("CoverImage", self.coverImage, 2, {"sticky":"W", "pady":20, "padx":20, "rowspan":20})
        
        # Launch the GUI
        self.TKW.begin()
    
    
    def onNovelFieldChange(self, index, value, op):
        
        # Get the selected novel name and replace the image accordingly
        novel = self.TKW.guiElements["NovelCombobox"][0].get()
        self.TKW.replaceImage("CoverImage", self.WW.getImagePillow(novel))
        
        # Set the values of the comboboxes to either the chapters or the books
        if self.TKW.guiElements["ChaptersOnly"][0].get():
            self.TKW.guiElements["BookCombobox"][1]["values"] = self.WW.getNovelChapterNames(novel)
            self.TKW.guiElements["EndCombobox"][1]["values"] = self.WW.getNovelChapterNames(novel)
        else:   
            self.TKW.guiElements["BookCombobox"][1]["values"] = self.WW.getNovelBookNames(novel)
        
        # Set the selected items in both comboboxes to the first element
        self.TKW.guiElements["BookCombobox"][1].current(0)
        self.TKW.guiElements["EndCombobox"][1].current(0)
        
    
    
    def onBookFieldChange(self, index, value, op):
        
        # If the checkbutton is checked, make sure that the end chapter is always
        # after the starting chapter
        if self.TKW.guiElements["ChaptersOnly"][0].get():
            novel = self.TKW.guiElements["NovelCombobox"][0].get()
            chapterList = self.WW.getNovelChapterNames(novel)
            chapIndex = chapterList.index(self.TKW.guiElements["BookCombobox"][0].get())
            
            if self.TKW.guiElements["EndCombobox"][0].get() in chapterList:
                endChapIndex = chapterList.index(self.TKW.guiElements["EndCombobox"][0].get())
            else:
                endChapIndex = chapIndex
            
            if chapIndex+1 < len(chapterList):
                self.TKW.guiElements["EndCombobox"][1]["values"] = chapterList[chapIndex+1:]
            else:
                self.TKW.guiElements["EndCombobox"][1]["values"] = [chapterList[-1]]
            
            if chapIndex < endChapIndex-1:
                self.TKW.guiElements["EndCombobox"][1].current(endChapIndex-chapIndex-1)
            else:
                self.TKW.guiElements["EndCombobox"][1].current(0)
        
    
    
    def onChapterCheckboxChange(self):
        
        # When the checkbutton is clicked, set the values of the comboboxes accordingly
        novel = self.TKW.guiElements["NovelCombobox"][0].get()
        if self.TKW.guiElements["ChaptersOnly"][0].get():
            self.TKW.guiElements["BookLabel"]['text'] = 'Select Starting Chapter:'
            self.TKW.guiElements["EndCombobox"][1].configure(state = "readonly")
            
            self.TKW.guiElements["BookCombobox"][1]["values"] = self.WW.getNovelChapterNames(novel)
            self.TKW.guiElements["EndCombobox"][1]["values"] = self.WW.getNovelChapterNames(novel)
        else:
            self.TKW.guiElements["BookLabel"]['text'] = 'Select Book:'
            self.TKW.guiElements["BookCombobox"][1]["values"] = self.WW.getNovelBookNames(novel)
            self.TKW.guiElements["EndCombobox"][1].configure(state = "disabled")
        self.TKW.guiElements["BookCombobox"][1].current(0)
        self.TKW.guiElements["EndCombobox"][1].current(0)
        
    
    
    def onDownloadButtonClick(self):
        
        # When the download button is clicked, download the book or the chapters
        # depending on the checkbutton state
        novel = self.TKW.guiElements["NovelCombobox"][0].get()
        if self.TKW.guiElements["ChaptersOnly"][0].get():
            chapterList = self.WW.getNovelChapterNames(novel)
            startChapter = chapterList.index(self.TKW.guiElements["BookCombobox"][0].get())
            endChapter = chapterList.index(self.TKW.guiElements["EndCombobox"][0].get())
            self.WW.generateBookFromTo(novel, startChapter, endChapter)
        else:
            self.WW.generateBook(novel, self.TKW.guiElements["BookCombobox"][0].get())


if __name__ == "__main__":
    WWGui()