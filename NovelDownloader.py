from PageTools import PageTools
from EBookGenerator import EBookGenerator
from multiprocessing.pool import ThreadPool

class NovelDownloader:

    def generateBookFromToMulti(parser, novelName, startChapter, endChapter, customCoverFilename = None, customBookName = None, callback=None, poolSize = 50, idnum = None, bsParser = None):
        
        # Download and clean all of the chapters
        chapterLinks = parser.getNovelChapterLinks(novelName)
        chapterLinks = list(dict.fromkeys(chapterLinks))
        chapterLinks = list(enumerate(chapterLinks[startChapter:endChapter+1]))
        
        pot_of_soup = [None]*len(chapterLinks)
        if callback == None:
            def callback(id):
                return False
        def downloadPage(link):
            if bsParser == None:
                pot_of_soup[link[0]] = PageTools().getSoupFromUrl(link[1])
            else:
                pot_of_soup[link[0]] = PageTools().getSoupFromUrl(link[1], parser = bsParser)
            if callback(idnum):
                raise RuntimeError("Process terminated")
        with ThreadPool(poolSize) as pool:
            pool.map(downloadPage, chapterLinks, chunksize=1)
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
    
    
    def generateBookFromTo(parser, novelName, startChapter, endChapter, customCoverFilename = None, customBookName = None, callback=None, idnum = None, bsParser = None):
        
        # Download and clean all of the chapters
        chapterLinks = parser.getNovelChapterLinks(novelName)
        chapterLinks = list(dict.fromkeys(chapterLinks))
        
        pot_of_soup = []
        if callback == None:
            def callback(id):
                return False
        for link in chapterLinks[startChapter:endChapter+1]:
            if bsParser == None:
                pot_of_soup.append(PageTools().getSoupFromUrl(link))
            else:
                pot_of_soup.append(PageTools().getSoupFromUrl(link, parser = bsParser))
            callback(idnum)
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
    
    
    def generateBookMulti(parser, novelName, bookName, customCoverFilename = None, customBookName = None, callback=None, poolSize = 50, idnum = None, bsParser = None):
        
        # Download and clean all of the chapters in the book
        chapterLinks = parser.getNovelBookChapterLinks(novelName, bookName)
        chapterLinks = list(enumerate(chapterLinks))
        pot_of_soup = [None]*len(chapterLinks)
        if callback == None:
            def callback(id):
                return False
        def downloadPage(link):
            if bsParser == None:
                pot_of_soup[link[0]] = PageTools().getSoupFromUrl(link[1])
            else:
                pot_of_soup[link[0]] = PageTools().getSoupFromUrl(link[1], parser = bsParser)
            if callback(idnum):
                raise RuntimeError("Process terminated")
        with ThreadPool(poolSize) as pool:
            pool.map(downloadPage, chapterLinks, chunksize=1)
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
    
    
    def generateBook(parser, novelName, bookName, customCoverFilename = None, customBookName = None, callback=None, idnum = None, bsParser = None):
        
        # Download and clean all of the chapters in the book
        chapterLinks = parser.getNovelBookChapterLinks(novelName, bookName)
        pot_of_soup = []
        if callback == None:
            def callback(id):
                return False
        for link in chapterLinks:
            if bsParser == None:
                pot_of_soup.append(PageTools().getSoupFromUrl(link))
            else:
                pot_of_soup.append(PageTools().getSoupFromUrl(link, parser = bsParser))
            callback(idnum)
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
    
    
    def generateBooks(parser, novelName, bookNames, customCoverFilename = None, customBookNames = None, callback=None, idnum = None, bsParser = None):
        
        # If no custom book names are input, fill the input list with None objects
        if customBookNames == None:
            customBookNames = [None] * len(bookNames)
        
        # Download each book separately
        for bookName, customBookName in zip(bookNames, customBookNames):
            self.generateBook(parser, novelName, bookNames, customCoverFilename, customBookName, callback, idnum, bsParser)

