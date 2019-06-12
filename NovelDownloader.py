from PageTools import PageTools
from EBookGenerator import EBookGenerator

class NovelDownloader:

    def generateBookFromTo(parser, novelName, startChapter, endChapter, customCoverFilename = None, customBookName = None, callback=None):
        
        # Download and clean all of the chapters
        chapterLinks = parser.getNovelChapterLinks(novelName)
        pot_of_soup = []
        for link in chapterLinks[startChapter:endChapter+1]:
            pot_of_soup.append(PageTools().getSoupFromUrl(link))
            callback()
        chapters = [parser.cleanChapter(soup) for soup in pot_of_soup]
        
        # Download or load the cover image
        if customCoverFilename == None:
            image = parser.getImageBinary(novelName)
        else:
            image = EBookGenerator().readImage(customCoverFilename)
        
        # Generate the ebook with a custom name or with start and end chapters as the name
        if customBookName != None:
            EBookGenerator().generateEBook(chapters, novelName, customBookName, parser.novels[novelName][2], image)
        else:
            EBookGenerator().generateEBook(chapters, novelName, "{}-{}".format(startChapter+1, endChapter+1), parser.novels[novelName][2], image)
    
    
    def generateBook(parser, novelName, bookName, customCoverFilename = None, customBookName = None, callback=None):
        
        # Download and clean all of the chapters in the book
        chapterLinks = parser.getNovelBookChapterLinks(novelName, bookName)
        pot_of_soup = []
        for link in chapterLinks:
            pot_of_soup.append(PageTools().getSoupFromUrl(link))
            callback()
        chapters = [parser.cleanChapter(soup) for soup in pot_of_soup]
        
        # Download or load the cover image
        if customCoverFilename == None:
            image = parser.getImageBinary(novelName)
        else:
            image = EBookGenerator().readImage(customCoverFilename)
        
        # Generate the ebook with a custom name or the name on the website
        if customBookName != None:
            EBookGenerator().generateEBook(chapters, novelName, customBookName, parser.novels[novelName][2], image)
        else:
            EBookGenerator().generateEBook(chapters, novelName, bookName, parser.novels[novelName][2], image)
    
    
    def generateBooks(parser, novelName, bookNames, customCoverFilename = None, customBookNames = None, callback=None):
        
        # If no custom book names are input, fill the input list with None objects
        if customBookNames == None:
            customBookNames = [None] * len(bookNames)
        
        # Download each book separately
        for bookName, customBookName in zip(bookNames, customBookNames):
            self.generateBook(parser, novelName, bookNames, customCoverFilename, customBookName, callback)

