from bs4 import BeautifulSoup
from PageTools import PageTools
from PIL import Image
from io import BytesIO
import re

noCoverLink = "http://admin.johnsons.net/janda/files/flipbook-coverpage/nocoverimg.jpg"

class ReadLightNovelParser:
    
    def __init__(self):
        
        self.url = "https://www.readlightnovel.org/"
        
        # Create containers
        self.novels = {}
        self.novelNames = None
        self.novelSypnoses = {}
        self.parseNovelList()
        
        # Container for all novels that are requested
        self.novelLibrary = {}
    
    
    def clearNovelCache(self):
        self.novelLibrary = {}
    
    
    def parseNovelList(self):
        
        soup = PageTools().getSoupFromUrl(self.url+"novel-list")
        books = PageTools().getElementsFromSoup(soup,[{"class_":"col-lg-12"},{"class_":"list-by-word-body"},"li"])
        
        for book in books:
            if PageTools().getElementsFromSoup(book, ["a"])[0]['href'] == "#":
                continue
            linkTitle = PageTools().getElementsFromSoup(book, [{"data-toggle":"popover"}])[0]
            self.novels[linkTitle.string] = [linkTitle['href'], PageTools().getElementsFromSoup(book, ["img"])[0]['src'], "N/A"]
            self.novelSypnoses[linkTitle.string] = PageTools().getElementsFromSoup(book, [{"class_":"pop-summary"}], onlyText=True)[0]
        
        self.novelNames = list(self.novels.keys())
        self.novelNames.sort()
    
    
    def loadNovelInfo(self, novelName):
        
        if novelName in self.novelLibrary.keys():
            return
            
        # Load the webpage for the novel
        soup = PageTools().getSoupFromUrl(self.novels[novelName][0])
        
        # Download cover image
        try:
            coverImage = PageTools().downloadPage(self.novels[novelName][1])
        except:
            coverImage = PageTools().downloadPage(noCoverLink)
        
        # Parse all of the book names/sections
        bookTitles = PageTools().getElementsFromSoup(soup, [{"id":"accordion"},{"class_":"panel-title"}], onlyText = True)
        
        # Create an empty dictionary to store all chapter names and links
        chapterLibrary = []
        bookToC = {}
        for i, bookTitle in enumerate(bookTitles):
            
            # Extract the html containing the chapter links and names
            chapterInfo = PageTools().getElementsFromSoup(soup,[{"id":"collapse-{}".format(i+1)},{"class_":"chapter-chs"},"a"])
            
            # Extract the chapter links and names
            chapterInfo = [[chap['href'], bookTitle+", "+chap.string.replace("<",'').replace(">",'')] for chap in chapterInfo]
            
            # Store chapters for each book
            bookToC[re.sub("\n", "", bookTitle)] = chapterInfo
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
        return [chapter[1] for chapter in self.novelLibrary[novelName][2][bookName]]
    
    
    def cleanChapter(self, soup):
        
        # Extract the chapter title and the chapter content
        content = soup.find(class_="desc")
        # Remove characters that might corrupt the ebook file
        chapterTitle = re.search("Chapter \d*", content.decode_contents()).group()
        
        for script in content.find_all("script"):
            script.decompose()
        
        for div in content.find_all("div"):
            div.decompose()
        
        # Add html header to the chapter
        chapter = '<html xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<title>{0}</title>\n</head>\n<body>\n<h1>{0}</h1>\n'.format(chapterTitle)
        chapter += re.sub(" \.", ".", content.decode_contents()).strip("\n"+chapterTitle)
        
        # Return the chapter as a BeautifulSoup html object
        return BeautifulSoup(chapter, "html.parser")


if __name__ == "__main__":
    pass