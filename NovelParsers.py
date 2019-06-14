from bs4 import BeautifulSoup
from PageTools import PageTools
from PIL import Image
from io import BytesIO
import re

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
    
    
    def insertSpecialCases(self):
        
        self.novels["Trash of the Count's Family"] = ["https://www.wuxiaworld.com/novel/trash-of-the-counts-family","https://cdn.wuxiaworld.com/images/covers/tcf.jpg","miraclerifle","TCF"]
        self.novels["The Novel's Extra"] = ["https://www.wuxiaworld.com/novel/the-novels-extra","https://cdn.wuxiaworld.com/images/covers/tne.jpg","FudgeNouget","TNE"]
        self.novels["Stop, Friendly Fire!"] = ["https://www.wuxiaworld.com/novel/stop-friendly-fire","https://cdn.wuxiaworld.com/images/covers/sff.jpg","Boko","SFF"]
        self.novels["Sage Monarch"] = ["https://www.wuxiaworld.com/novel/sage-monarch","https://cdn.wuxiaworld.com/images/covers/sm.jpg","Deathblade","SM"]
        self.novels["Nine Star Hegemon Body Art"] = ["https://www.wuxiaworld.com/novel/nine-star-hegemon","https://cdn.wuxiaworld.com/images/covers/nshba.jpg","BornToBe","NSHBA"]
        self.novels["Dragon Prince Yuan"] = ["https://www.wuxiaworld.com/novel/dragon-prince-yuan","https://cdn.wuxiaworld.com/images/covers/yz.jpg","Yellowlaw","DPY"]
        self.novels["Coiling Dragon"] = ["https://www.wuxiaworld.com/novel/coiling-dragon-preview","https://cdn.wuxiaworld.com/images/covers/cdp.jpg","RWX","CDP"]
        self.novels["Dragon Talisman"][0] = "https://www.wuxiaworld.com/preview/dragon-talisman"

        
        self.novelSypnoses["Trash of the Count's Family"] = "N/A"
        self.novelSypnoses["The Novel's Extra"] = "N/A"
        self.novelSypnoses["Stop, Friendly Fire!"] = "N/A"
        self.novelSypnoses["Sage Monarch"] = "N/A"
        self.novelSypnoses["Nine Star Hegemon Body Art"] = "N/A"
        self.novelSypnoses["Dragon Prince Yuan"] = "N/A"
        self.novelSypnoses["Coiling Dragon"] = "N/A"
        
    
    def parseNovelList(self):
        
        # Handle key error if the novel doesn't have a sypnosis
        def checkForSypnosis(novel):
            try:
                novel['sypnosis']
            except KeyError:
                return False
            return True
        
        # Extract the required novel info
        self.novels = {novel['name']:[self.url+"/novel/"+novel['slug'], novel['coverUrl'], novel['translatorUserName']] for novel in self.jsonFile['items']}
        self.novelSypnoses = {novel['name']:(novel['sypnosis'] if checkForSypnosis(novel) else "N/A") for novel in self.jsonFile['items']}
        
        self.insertSpecialCases()
        
        self.novelNames = list(self.novels.keys())
        self.novelNames.sort()
    
    
    def loadNovelInfo(self, novelName):
        
        if novelName in self.novelLibrary.keys():
            return
        elif novelName == "Coiling Dragon":
            # Load the webpage for the novel
            soup = PageTools().getSoupFromUrl(self.novels[novelName][0])
            
            # Create a dummy book
            bookTitles = ["Preview"]
            
            # Create an empty dictionary to store all chapter names and links
            chapterLibrary = []
            bookToC = {}
            
            # Extract the html containing the chapter links and names
            chapterInfo = PageTools().getElementsFromSoup(soup,[{"class_":"section"},\
                          {"class_":"list-unstyled"},"li"], findAllEnableList = True)
            
            # Extract the chapter links and names
            chapterInfo = [[PageTools().getElementsFromSoup(chap, ["a"], findAllEnableList=True)[0]['href'],\
                            PageTools().getElementsFromSoup(chap, ["a"], findAllEnableList=True, onlyText=True)[0].replace("<",'').replace(">",'')] for chap in chapterInfo]
            chapterInfo = chapterInfo[0:3]
            
            # Store chapters for each book
            bookToC["Preview"] = chapterInfo
            chapterLibrary.extend(bookToC["Preview"])
            
            # Download cover image
            try:
                coverImage = PageTools().downloadPage(self.novels[novelName][1])
            except:
                coverImage = PageTools().downloadPage("http://admin.johnsons.net/janda/files/flipbook-coverpage/nocoverimg.jpg")

            # Add the books, chapters, and the cover to the novel library
            self.novelLibrary[novelName] = [bookTitles, chapterLibrary, bookToC, coverImage]
            return
        
        # Load the webpage for the novel
        soup = PageTools().getSoupFromUrl(self.novels[novelName][0])
        
        # Parse all of the book names/sections
        bookTitles = PageTools().getElementsFromSoup(soup, [{"id":"accordion"},{"class_":"title"}], onlyText = True)
        
        
        # Download cover image
        try:
            coverImage = PageTools().downloadPage(self.novels[novelName][1])
        except:
            coverImage = PageTools().downloadPage("http://admin.johnsons.net/janda/files/flipbook-coverpage/nocoverimg.jpg")
        
        # Create an empty dictionary to store all chapter names and links
        chapterLibrary = []
        bookToC = {}
        for i, bookTitle in enumerate(bookTitles):
            
            # Extract the html containing the chapter links and names
            chapterInfo = PageTools().getElementsFromSoup(soup,[{"id":"collapse-{}".format(i)},\
                          {"class_":"row"},{"class_":"col-sm-6"},{"class_":"chapter-item"}])
            
            # Extract the chapter links and names
            chapterInfo = [[self.url+PageTools().getElementsFromSoup(chap, ["a"])[0]['href'],\
                            PageTools().getElementsFromSoup(chap, ["a"], onlyText=True)[0].replace("<",'').replace(">",'')] for chap in chapterInfo]
            
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
        
        hasSpoiler = None
        
        # Extract the chapter title and the chapter content
        chapterTitle = soup.find(class_="caption clearfix")
        content = chapterTitle.find_next_sibling(class_="fr-view")
        chapterTitle = chapterTitle.find("h4")
        
        # Get the chapter title, make it hidden if it contains spoilers
        try:
            if chapterTitle.attrs["class"][0] == "text-spoiler":
                hasSpoiler = chapterTitle.text
                chapterTitle = "Chapter name hidden due to potential spoilers"
            else:
                chapterTitle = chapterTitle.text
        except IndexError:
            chapterTitle = chapterTitle.text
        
        # Remove characters that might corrupt the ebook file
        chapterTitle = chapterTitle.replace("<",'&lt;').replace(">",'&gt;')
        
        
        for a in content.find_all("a"):
            a.decompose()
        
        # Add html header to the chapter
        #chapter = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<!DOCTYPE html>\n\n"
        chapter = '<html xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<title>{0}</title>\n</head>\n<body>\n<h1>{0}</h1>\n'.format(chapterTitle)
        #print(str(content))
        chapter += str(content)
        if hasSpoiler != None:
            chapter += "<strong>The chapter name is: {}</strong>".format(hasSpoiler)
        #chapter += "</body>\n</html>"
        # Return the chapter as a BeautifulSoup html object
        return BeautifulSoup(chapter, "html.parser")


class GTParser:
    
    def __init__(self):
        
        self.url = "https://gravitytales.com"
        
        # Initialise variables
        self.novels = {}
        self.novelNames = []
        #self.novelSypnoses = None
        self.parseNovelList()
        
        # Container for all novels that are requested
        self.novelLibrary = {}
    
    
    def clearNovelCache(self):
        self.novelLibrary = {}
    
    
    def insertSpecialCases(self):
        pass
        
    
    def parseNovelList(self):
        
        soup = PageTools().getSoupFromUrl(self.url+"/vote")
        
        # Extract the required novel info
        novelInfo = PageTools().getElementsFromSoup(soup, [{"class_":"col-xs-12 col-sm-6 col-md-3 col-lg-3 image"}])
        authorInfo = PageTools().getElementsFromSoup(soup, [{"class_":"col-xs-12 col-sm-6 col-md-6 col-lg-7 details"},\
                                                     {"class_":"label label-primary"}],findAllEnableList = [True, False], onlyText=True)
        
        for novel, author in zip(novelInfo,authorInfo):
            midHtml = PageTools().getElementsFromSoup(novel, ["a"])[0]
            innerHtml = PageTools().getElementsFromSoup(novel, ["img"])[0]
            self.novels[innerHtml['title']] = [midHtml['href'], innerHtml['src'], author]
                       
        #self.novelSypnoses = {novel['name']:(novel['sypnosis'] if checkForSypnosis(novel) else "N/A") for novel in self.jsonFile['items']}
        
        self.insertSpecialCases()
        
        self.novelNames = list(self.novels.keys())
        self.novelNames.sort()
    
    
    def loadNovelInfo(self, novelName):
        
        if novelName in self.novelLibrary.keys():
            return
        
        # Load the webpage for the novel
        soup = PageTools().getSoupFromUrl(self.novels[novelName][0]+"/chapters")
        
        # Parse all of the book names/sections
        bookTitles = PageTools().getElementsFromSoup(soup, [{"id":"chaptergroups"}, "a"], onlyText = True)
        
        # Download cover image
        try:
            coverImage = PageTools().downloadPage(self.novels[novelName][1])
        except:
            coverImage = PageTools().downloadPage("http://admin.johnsons.net/janda/files/flipbook-coverpage/nocoverimg.jpg")
        
        # Create an empty dictionary to store all chapter names and links
        chapterBlocks = PageTools().getElementsFromSoup(soup, [{"class":"tab-content"}, "div"])
        
        chapterLibrary = []
        bookToC = {}
        for bookTitle, chapterBlock in zip(bookTitles, chapterBlocks):
            
            # Extract the html containing the chapter links and names
            chapterInfo = PageTools().getElementsFromSoup(chapterBlock,["td"], findAllEnableList = True)
            
            # Extract the chapter links and names
            chapterInfo = [[PageTools().getElementsFromSoup(chap, ["a"], findAllEnableList=True)[0]['href'],\
                            PageTools().getElementsFromSoup(chap, ["a"], findAllEnableList=True, onlyText=True)[0].replace("<",'').replace(">",'')] for chap in chapterInfo]
            
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
        
        # Extract the chapter title and the chapter content
        chapterTitle = soup.find(id="contentElement")
        content = chapterTitle.find(id="chapterContent")
        chapterTitle = chapterTitle.find("h4")
        
        # Get the chapter title, make it hidden if it contains spoilers
        chapterTitle = chapterTitle.text
        
        # Remove characters that might corrupt the ebook file
        chapterTitle = chapterTitle.replace("<",'&lt;').replace(">",'&gt;')
        
        
        chapter = '<html xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<title>{0}</title>\n</head>\n<body>\n<h1>{0}</h1>'.format(chapterTitle)
        chapter += str(content.decode_contents())
        
        # Return the chapter as a BeautifulSoup html object
        return BeautifulSoup(chapter, "html.parser")


class VNParser:
    
    def __init__(self):
        
        self.url = "https://www.volarenovels.com"
        
        # Download and parse the Volare Novels API JSON file
        self.jsonFile = PageTools().getJsonFromUrl(self.url+"/api/novels")
        self.novels = None
        self.novelNames = None
        self.novelSypnoses = None
        self.parseNovelList()
        
        # Container for all novels that are requested
        self.novelLibrary = {}
    
    
    def clearNovelCache(self):
        self.novelLibrary = {}
    
    
    def insertSpecialCases(self):
        
        pass
        
    
    def parseNovelList(self):
        
        # Handle key error if the novel doesn't have a sypnosis
        def checkForSypnosis(novel):
            try:
                novel['sypnosis']
            except KeyError:
                return False
            return True
        
        # Extract the required novel info
        self.novels = {novel['name']:[self.url+"/novel/"+novel['slug'], novel['coverUrl'], novel['translatorUserName']] for novel in self.jsonFile['items']}
        self.novelSypnoses = {novel['name']:(novel['sypnosis'] if checkForSypnosis(novel) else "N/A") for novel in self.jsonFile['items']}
        
        self.insertSpecialCases()
        
        self.novelNames = list(self.novels.keys())
        self.novelNames.sort()
    
    
    def loadNovelInfo(self, novelName):
        
        if novelName in self.novelLibrary.keys():
            return
        
        # Load the webpage for the novel
        soup = PageTools().getSoupFromUrl(self.novels[novelName][0])
        
        # Parse all of the book names/sections
        bookTitles = PageTools().getElementsFromSoup(soup, [{"id":"accordion"},{"class_":"title"}], onlyText = True)
        
        
        # Download cover image
        try:
            coverImage = PageTools().downloadPage(self.novels[novelName][1])
        except:
            coverImage = PageTools().downloadPage("http://admin.johnsons.net/janda/files/flipbook-coverpage/nocoverimg.jpg")
        
        # Create an empty dictionary to store all chapter names and links
        chapterLibrary = []
        bookToC = {}
        bookTitles = [bookTitle.strip(" ").strip("\n") for bookTitle in bookTitles]
        for i, bookTitle in enumerate(bookTitles):
            
            # Extract the html containing the chapter links and names
            chapterInfo = PageTools().getElementsFromSoup(soup,[{"id":"collapse-{}".format(i)},\
                          {"class_":"row"},{"class_":"col-sm-6"},{"class_":"chapter-item"}])
            
            # Extract the chapter links and names
            chapterInfo = [[self.url+PageTools().getElementsFromSoup(chap, ["a"])[0]['href'],\
                            PageTools().getElementsFromSoup(chap, ["a"], onlyText=True)[0].replace("<",'').replace(">",'')] for chap in chapterInfo]
            
            # Store chapters for each book
            bookToC[bookTitle ] = chapterInfo
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
        
        hasSpoiler = None
        
        # Extract the chapter title and the chapter content
        chapterTitle = soup.find(class_="caption clearfix")
        content = chapterTitle.find_next_sibling(class_="jfontsize_content fr-view")
        chapterTitle = chapterTitle.find("h4")
        
        # Get the chapter title, make it hidden if it contains spoilers
        try:
            if chapterTitle.attrs["class"][0] == "text-spoiler":
                hasSpoiler = chapterTitle.text
                chapterTitle = "Chapter name hidden due to potential spoilers"
            else:
                chapterTitle = chapterTitle.text
        except IndexError:
            chapterTitle = chapterTitle.text
        
        # Remove characters that might corrupt the ebook file
        chapterTitle = chapterTitle.replace("<",'&lt;').replace(">",'&gt;')
        
        
        for a in content.find_all("a"):
            a.decompose()
        
        # Add html header to the chapter
        #chapter = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<!DOCTYPE html>\n\n"
        chapter = '<html xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<title>{0}</title>\n</head>\n<body>\n<h1>{0}</h1>\n'.format(chapterTitle)
        #print(str(content))
        chapter += str(content)
        if hasSpoiler != None:
            chapter += "<strong>The chapter name is: {}</strong>".format(hasSpoiler)
        #chapter += "</body>\n</html>"
        # Return the chapter as a BeautifulSoup html object
        return BeautifulSoup(chapter, "html.parser")
