from bs4 import BeautifulSoup
import PageTools
from PIL import Image
from io import BytesIO
import re
import requests
import json
import gc

noCoverLink = "http://admin.johnsons.net/janda/files/flipbook-coverpage/nocoverimg.jpg"

class WuxiaWorldParser:
    
    def __init__(self):
        
        self.url = "https://www.wuxiaworld.com"
        
        self.name = "Wuxia World"
        
        self.jsonFile = None
        self.novels = None
        self.novelNames = None
        self.novelSypnoses = None
        self.isLoaded = False
        self.bsParser = "html.parser"

        # Container for all novels that are requested
        self.novelLibrary = {}
    
    
    def load(self):
        if not self.isLoaded:
            # Download and parse the WuxiaWorld API JSON file
            url = self.url+"/api/novels/search"
            payload = '{"title":"","tags":[],"language":"Any","genres":[],"active":null,"sortType":"Name","sortAsc":false,"searchAfter":null,"count":500}'
            self.jsonFile = PageTools.getJsonFromPost(url,payload)
            self.parseNovelList()
            self.isLoaded = True
    
    
    def clearNovelCache(self):
        self.novelLibrary = {}
    
    
    def insertSpecialCases(self):
        pass
        # self.novels["Trash of the Count's Family"] = ["https://www.wuxiaworld.com/novel/trash-of-the-counts-family","https://cdn.wuxiaworld.com/images/covers/tcf.jpg","miraclerifle","TCF"]
        # self.novels["The Novel's Extra"] = ["https://www.wuxiaworld.com/novel/the-novels-extra","https://cdn.wuxiaworld.com/images/covers/tne.jpg","FudgeNouget","TNE"]
        # self.novels["Stop, Friendly Fire!"] = ["https://www.wuxiaworld.com/novel/stop-friendly-fire","https://cdn.wuxiaworld.com/images/covers/sff.jpg","Boko","SFF"]
        # self.novels["Sage Monarch"] = ["https://www.wuxiaworld.com/novel/sage-monarch","https://cdn.wuxiaworld.com/images/covers/sm.jpg","Deathblade","SM"]
        # self.novels["Nine Star Hegemon Body Art"] = ["https://www.wuxiaworld.com/novel/nine-star-hegemon","https://cdn.wuxiaworld.com/images/covers/nshba.jpg","BornToBe","NSHBA"]
        # self.novels["Dragon Prince Yuan"] = ["https://www.wuxiaworld.com/novel/dragon-prince-yuan","https://cdn.wuxiaworld.com/images/covers/yz.jpg","Yellowlaw","DPY"]
        # self.novels["Coiling Dragon"] = ["https://www.wuxiaworld.com/novel/coiling-dragon-preview","https://cdn.wuxiaworld.com/images/covers/cdp.jpg","RWX","CDP"]

        
        # self.novelSypnoses["Trash of the Count's Family"] = "N/A"
        # self.novelSypnoses["The Novel's Extra"] = "N/A"
        # self.novelSypnoses["Stop, Friendly Fire!"] = "N/A"
        # self.novelSypnoses["Sage Monarch"] = "N/A"
        # self.novelSypnoses["Nine Star Hegemon Body Art"] = "N/A"
        # self.novelSypnoses["Dragon Prince Yuan"] = "N/A"
        # self.novelSypnoses["Coiling Dragon"] = "N/A"
        
    
    def parseNovelList(self):
        
        # Handle key error if the novel doesn't have a sypnosis
        def checkForSypnosis(novel):
            try:
                novel['sypnosis']
            except KeyError:
                return False
            return True
        
        # Extract the required novel info
        self.novels = {novel['name']:[self.url+"/novel/"+novel['slug'], novel['coverUrl'], novel['id']] for novel in self.jsonFile['items']}
        self.novelSypnoses = {novel['name']:(novel['sypnosis'] if checkForSypnosis(novel) else "N/A") for novel in self.jsonFile['items']}
        
        self.insertSpecialCases()
        
        self.novelNames = list(self.novels.keys())
        self.novelNames.sort()
    
    
    def loadNovelInfo(self, novelName):
        
        if novelName in self.novelLibrary.keys():
            return
        elif novelName == "Coiling Dragon":
            # Load the webpage for the novel
            soup = PageTools.getSoupFromUrl(self.novels[novelName][0])
            
            # Create a dummy book
            bookTitles = ["Preview"]
            
            # Create an empty dictionary to store all chapter names and links
            chapterLibrary = []
            bookToC = {}
            
            # Extract the html containing the chapter links and names
            chapterInfo = PageTools.getElementsFromSoup(soup,[{"class_":"section"},\
                          {"class_":"list-unstyled"},"li"], findAllEnableList = True)
            
            # Extract the chapter links and names
            chapterInfo = [[PageTools.getElementsFromSoup(chap, ["a"], findAllEnableList=True)[0]['href'],\
                            PageTools.getElementsFromSoup(chap, ["a"], findAllEnableList=True, onlyText=True)[0].replace("<",'').replace(">",'')] for chap in chapterInfo]
            chapterInfo = chapterInfo[0:3]
            
            # Store chapters for each book
            bookToC["Preview"] = chapterInfo
            chapterLibrary.extend(bookToC["Preview"])
            
            # Download cover image
            try:
                coverImage = PageTools.downloadPage(self.novels[novelName][1])
            except:
                coverImage = PageTools.downloadPage(noCoverLink)

            # Add the books, chapters, and the cover to the novel library
            self.novelLibrary[novelName] = [bookTitles, chapterLibrary, bookToC, coverImage]
            return
        
        # Load the webpage for the novel
        soup = PageTools.getSoupFromUrl(self.novels[novelName][0])
        
        # Parse all of the book names/sections
        bookTitles = PageTools.getElementsFromSoup(soup, [{"id":"accordion"},{"class_":"title"}], onlyText = True)
        
        
        # Download cover image
        try:
            coverImage = PageTools.downloadPage(self.novels[novelName][1])
        except:
            coverImage = PageTools.downloadPage("http://admin.johnsons.net/janda/files/flipbook-coverpage/nocoverimg.jpg")
        
        # Create an empty dictionary to store all chapter names and links
        chapterLibrary = []
        bookToC = {}
        for i, bookTitle in enumerate(bookTitles):
            
            # Extract the html containing the chapter links and names
            chapterInfo = PageTools.getElementsFromSoup(soup,[{"id":"collapse-{}".format(i)},\
                          {"class_":"row"},{"class_":"col-sm-6"},{"class_":"chapter-item"}])
            
            # Extract the chapter links and names
            chapterInfo = [[self.url+PageTools.getElementsFromSoup(chap, ["a"])[0]['href'],\
                            PageTools.getElementsFromSoup(chap, ["a"], onlyText=True)[0].replace("<",'').replace(">",'')] for chap in chapterInfo]
            
            # Store chapters for each book
            bookToC[bookTitle] = chapterInfo
            chapterLibrary.extend(bookToC[bookTitle])
        
        # Add the books, chapters, and the cover to the novel library
        self.novelLibrary[novelName] = [bookTitles, chapterLibrary, bookToC, coverImage]
    
    
    def getNovelNames(self):
        
        self.load()
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
        chapter = '<html xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<title>{0}</title>\n</head>\n<body>\n<h1>{0}</h1>\n'.format(chapterTitle)
        chapter += str(content)
        if hasSpoiler != None:
            chapter += "<strong>The chapter name is: {}</strong>".format(hasSpoiler)
        
        # Collect some garbage to reduce RAM usage
        soup = None
        chapterTitle = None
        content = None
        gc.collect()
        
        # Return the chapter as a BeautifulSoup html object
        return BeautifulSoup(chapter, "html.parser")


class GravityTalesParser:
    
    def __init__(self):
        
        self.url = "https://gravitytales.com"
        
        self.name = "Gravity Tales"
        
        # Initialise variables
        self.novels = {}
        self.novelNames = []
        #self.novelSypnoses = None
        self.isLoaded = False
        self.bsParser = "html.parser"

        # Container for all novels that are requested
        self.novelLibrary = {}
    
    def load(self):
        self.parseNovelList()
        self.isLoaded = True
    
    
    def clearNovelCache(self):
        self.novelLibrary = {}
    
    
    def insertSpecialCases(self):
        pass
        
    
    def parseNovelList(self):
        
        soup = PageTools.getSoupFromUrl(self.url+"/vote")
        
        # Extract the required novel info
        novelInfo = PageTools.getElementsFromSoup(soup, [{"class_":"col-xs-12 col-sm-6 col-md-3 col-lg-3 image"}])
        authorInfo = PageTools.getElementsFromSoup(soup, [{"class_":"col-xs-12 col-sm-6 col-md-6 col-lg-7 details"},\
                                                     {"class_":"label label-primary"}],findAllEnableList = [True, False], onlyText=True)
        
        for novel, author in zip(novelInfo,authorInfo):
            midHtml = PageTools.getElementsFromSoup(novel, ["a"])[0]
            innerHtml = PageTools.getElementsFromSoup(novel, ["img"])[0]
            self.novels[innerHtml['title']] = [midHtml['href'], innerHtml['src'], author]
                       
        #self.novelSypnoses = {novel['name']:(novel['sypnosis'] if checkForSypnosis(novel) else "N/A") for novel in self.jsonFile['items']}
        
        self.insertSpecialCases()
        
        self.novelNames = list(self.novels.keys())
        self.novelNames.sort()
    
    
    def loadNovelInfo(self, novelName):
        
        if novelName in self.novelLibrary.keys():
            return
        
        # Load the webpage for the novel
        soup = PageTools.getSoupFromUrl(self.novels[novelName][0]+"/chapters")
        
        # Parse all of the book names/sections
        bookTitles = PageTools.getElementsFromSoup(soup, [{"id":"chaptergroups"}, "a"], onlyText = True)
        
        # Download cover image
        try:
            coverImage = PageTools.downloadPage(self.novels[novelName][1])
        except:
            coverImage = PageTools.downloadPage(noCoverLink)
        
        # Create an empty dictionary to store all chapter names and links
        chapterBlocks = PageTools.getElementsFromSoup(soup, [{"class":"tab-content"}, "div"])
        
        chapterLibrary = []
        bookToC = {}
        for bookTitle, chapterBlock in zip(bookTitles, chapterBlocks):
            
            # Extract the html containing the chapter links and names
            chapterInfo = PageTools.getElementsFromSoup(chapterBlock,["td"], findAllEnableList = True)
            
            # Extract the chapter links and names
            chapterInfo = [[PageTools.getElementsFromSoup(chap, ["a"], findAllEnableList=True)[0]['href'],\
                            PageTools.getElementsFromSoup(chap, ["a"], findAllEnableList=True, onlyText=True)[0].replace("<",'').replace(">",'')] for chap in chapterInfo]
            
            # Store chapters for each book
            bookToC[bookTitle] = chapterInfo
            chapterLibrary.extend(bookToC[bookTitle])
        
        # Add the books, chapters, and the cover to the novel library
        self.novelLibrary[novelName] = [bookTitles, chapterLibrary, bookToC, coverImage]
    
    
    def getNovelNames(self):
        
        self.load()
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
        chapterTitle = soup.find(id="contentElement")
        content = chapterTitle.find(id="chapterContent")
        chapterTitle = chapterTitle.find("h4")
        
        # Get the chapter title, make it hidden if it contains spoilers
        chapterTitle = chapterTitle.text
        
        # Remove characters that might corrupt the ebook file
        chapterTitle = chapterTitle.replace("<",'&lt;').replace(">",'&gt;')
        
        
        chapter = '<html xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<title>{0}</title>\n</head>\n<body>\n<h1>{0}</h1>'.format(chapterTitle)
        chapter += str(content.decode_contents())
        
        # Collect some garbage to reduce RAM usage
        soup = None
        chapterTitle = None
        content = None
        gc.collect()
        
        # Return the chapter as a BeautifulSoup html object
        return BeautifulSoup(chapter, "html.parser")


class VolareNovelsParser:
    
    def __init__(self):
        
        self.url = "https://www.volarenovels.com"
        
        self.name = "Volare Novels"
        
        # Download and parse the Volare Novels API JSON file
        self.jsonFile = None
        # url = self.url+"/api/novels/search"
        # payload = '{"title":"","language":null,"tags":[],"active":null,"sortType":"Name","sortAsc":true,"searchAfter":null,"count":500}'
        # self.jsonFile = PageTools.getJsonFromPost(url,payload)
        
        self.novels = None
        self.novelNames = None
        self.novelSypnoses = None
        self.isLoaded = False
        self.bsParser = "html.parser"
        
        # Container for all novels that are requested
        self.novelLibrary = {}
    
    
    def load(self):
        if not self.isLoaded:
            self.jsonFile = PageTools.getJsonFromUrl(self.url+"/api/novels")
            self.parseNovelList()
            self.isLoaded = True
    
    
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
        soup = PageTools.getSoupFromUrl(self.novels[novelName][0])
        
        # Parse all of the book names/sections
        bookTitles = PageTools.getElementsFromSoup(soup, [{"id":"accordion"},{"class_":"title"}], onlyText = True)
        
        
        # Download cover image
        try:
            coverImage = PageTools.downloadPage(self.novels[novelName][1])
        except:
            coverImage = PageTools.downloadPage(noCoverLink)
        
        # Create an empty dictionary to store all chapter names and links
        chapterLibrary = []
        bookToC = {}
        bookTitles = [bookTitle.strip(" ").strip("\n") for bookTitle in bookTitles]
        for i, bookTitle in enumerate(bookTitles):
            
            # Extract the html containing the chapter links and names
            chapterInfo = PageTools.getElementsFromSoup(soup,[{"id":"collapse-{}".format(i)},\
                          {"class_":"row"},{"class_":"col-sm-6"},{"class_":"chapter-item"}])
            
            # Extract the chapter links and names
            chapterInfo = [[self.url+PageTools.getElementsFromSoup(chap, ["a"])[0]['href'],\
                            PageTools.getElementsFromSoup(chap, ["a"], onlyText=True)[0].replace("<",'').replace(">",'')] for chap in chapterInfo]
            
            # Store chapters for each book
            bookToC[bookTitle ] = chapterInfo
            chapterLibrary.extend(bookToC[bookTitle])
        
        # Add the books, chapters, and the cover to the novel library
        self.novelLibrary[novelName] = [bookTitles, chapterLibrary, bookToC, coverImage]
    
    
    def getNovelNames(self):
        
        self.load()
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
        chapter = '<html xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<title>{0}</title>\n</head>\n<body>\n<h1>{0}</h1>\n'.format(chapterTitle)
        chapter += str(content)
        
        if hasSpoiler != None:
            chapter += "<strong>The chapter name is: {}</strong>".format(hasSpoiler)
        
        # Collect some garbage to reduce RAM usage
        soup = None
        chapterTitle = None
        content = None
        gc.collect()
        
        # Return the chapter as a BeautifulSoup html object
        return BeautifulSoup(chapter, "html.parser")


class TotallyTranslationsParser:
    
    def __init__(self):
        
        self.url = "https://totallytranslations.com"
        
        self.name = "Totally Translations"
        
        # Create containers
        self.novels = {}
        self.novelNames = None
        # self.novelSypnoses = None
        self.isLoaded = False
        self.bsParser = "html.parser"
        
        # Container for all novels that are requested
        self.novelLibrary = {}
    
    
    def load(self):
        if not self.isLoaded:
            self.parseNovelList()
            self.isLoaded = True
        
    
    def clearNovelCache(self):
        self.novelLibrary = {}
    
    
    def insertSpecialCases(self):
        
        pass
        
    
    def parseNovelList(self):
        
        novels = PageTools.getElementsFromUrl(self.url, [ {"class_":"col-md-6"}, {"class_":"slide"}], [False, True])
        
        for novel in novels:
            title = PageTools.getElementsFromSoup(novel, [ {"class_":"slide-description"}, "strong"], onlyText=True)[0]
            novelLink = PageTools.getElementsFromSoup(novel, [ {"class_":"slide-image"}, "a"])[0]
            imgLink = PageTools.getElementsFromSoup(novelLink, ["img"])[0]['src']
            self.novels[title] = [novelLink['href'], imgLink, "N/A"]
            
        self.insertSpecialCases()
        
        self.novelNames = list(self.novels.keys())
        self.novelNames.sort()
    
    
    def loadNovelInfo(self, novelName):
        
        if novelName in self.novelLibrary.keys():
            return
        
        # Load the webpage for the novel
        soup = PageTools.getElementsFromUrl(self.novels[novelName][0], [{"class_":"chapters-list"}])[0]
        
        titles = PageTools.getElementsFromSoup(soup, [{"class_":"chapters-title"}], onlyText=True)
        chapterBlocks = PageTools.getElementsFromSoup(soup, [{"class_":"clearfix chapters-acc"}])
        
        # Download cover image
        try:
            coverImage = PageTools.downloadPage(self.novels[novelName][1])
        except:
            coverImage = PageTools.downloadPage(noCoverLink)
        
        # Create an empty dictionary to store all chapter names and links
        chapterLibrary = []
        bookToC = {}
        for title, chapterBlock in zip(titles, chapterBlocks):
            chapters = PageTools.getElementsFromSoup(chapterBlock, ["a"])
            chapterInfo = [[chapter['href'], chapter.string.replace("<",'').replace(">",'')] for chapter in chapters]

            # Store chapters for each book
            bookToC[title] = chapterInfo
            chapterLibrary.extend(bookToC[title])
        
        # Add the books, chapters, and the cover to the novel library
        self.novelLibrary[novelName] = [titles, chapterLibrary, bookToC, coverImage]
    
    
    def getNovelNames(self):
        
        self.load()
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
        
        hasSpoiler = None
        
        # Extract the chapter title and the chapter content
        chapterTitle = soup.find(class_="entry-title fusion-post-title").string
        content = soup.find(class_="post-content")
        
        # Remove characters that might corrupt the ebook file
        chapterTitle = chapterTitle.replace("<",'&lt;').replace(">",'&gt;')
        

        for a in content.find_all("a"):
            a.decompose()
        
        for button in content.find_all("button"):
            button.decompose()
        
        # Add html header to the chapter
        chapter = '<html xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<title>{0}</title>\n</head>\n<body>\n<h1>{0}</h1>\n'.format(chapterTitle)
        chapter += str(content)
        if hasSpoiler != None:
            chapter += "<strong>The chapter name is: {}</strong>".format(hasSpoiler)
        
        # Collect some garbage to reduce RAM usage
        soup = None
        chapterTitle = None
        content = None
        gc.collect()
        
        # Return the chapter as a BeautifulSoup html object
        return BeautifulSoup(chapter, "html.parser")


class NovelleLeggereParser:
    
    def __init__(self):
        
        self.url = "https://www.novelleleggere.com/"
        
        self.name = "Novelle Leggere"
        
        # Create containers
        self.novels = {}
        self.novelNames = None
        # self.novelSypnoses = None
        self.isLoaded = False
        self.bsParser = "lxml"
        
        # Container for all novels that are requested
        self.novelLibrary = {}
    
    
    def load(self):
        if not self.isLoaded:
            self.parseNovelList()
            self.isLoaded = True
        
    
    def clearNovelCache(self):
        self.novelLibrary = {}
    
    
    def insertSpecialCases(self):
        del self.novels["The Legend of Randidly Ghosthound"]
        pass
        
    
    def parseNovelList(self):
        
        tables = PageTools.getElementsFromUrl(self.url, ["table"])
        tables = tables[0:2]
        
        for table in tables:
            novels = PageTools.getElementsFromSoup(table, ["strong","a"])
            
            for novel in novels:
                title = novel.text.strip()
                self.novels[title] = [novel['href'], "N/A", "N/A"]
                
        
        self.insertSpecialCases()
        
        self.novelNames = list(self.novels.keys())
        self.novelNames.sort()
    
    
    def loadNovelInfo(self, novelName):
        
        if novelName in self.novelLibrary.keys():
            return
        
        # Load the webpage for the novel
        soup = PageTools.getElementsFromUrl(self.novels[novelName][0], [{"id":"content"}],parser = 'lxml')[0]
        titles = PageTools.getElementsFromSoup(soup, [{"class_":"su-spoiler-title"}], onlyText=True)
        
        chapterBlocks = PageTools.getElementsFromSoup(soup, [{"class_":"display-posts-listing"}])
        self.novels[novelName][1] = PageTools.getElementsFromSoup(soup,["img"])[0]['src']
        
        # Special parsing conditions
        if novelName == "The Wandering Inn":
            titles = titles[4:]
        elif novelName == "Il Demone Contro il Cielo":
            titles = titles[1:]
            chapterBlocks = PageTools.getElementsFromSoup(soup, [{"class_":"su-spoiler-content su-u-clearfix su-u-trim"}])
        else:
            titles = titles[2:]
        
        if novelName == "Legendary Moonlight Sculptor":
            chapterBlocks = PageTools.getElementsFromSoup(soup, [{"class_":"su-spoiler-content su-u-clearfix su-u-trim"}])
            chapterBlocks = chapterBlocks[2:]
        
        # Download cover image
        try:
            coverImage = PageTools.downloadPage(self.novels[novelName][1])
        except:
            coverImage = PageTools.downloadPage(noCoverLink)
        
        # Create an empty dictionary to store all chapter names and links
        chapterLibrary = []
        bookToC = {}
        for title, chapterBlock in zip(titles, chapterBlocks):
            chapters = PageTools.getElementsFromSoup(chapterBlock, ["a"])
            
            chapterInfo = [[chapter['href'], chapter.string.replace("<",'').replace(">",'')] for chapter in chapters]

            # Store chapters for each book
            bookToC[title] = chapterInfo
            chapterLibrary.extend(bookToC[title])
        
        # Add the books, chapters, and the cover to the novel library
        self.novelLibrary[novelName] = [titles, chapterLibrary, bookToC, coverImage]
    
    
    def getNovelNames(self):
        
        self.load()
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
        
        hasSpoiler = None
        
        # Extract the chapter title and the chapter content
        chapterTitle = soup.find(class_="entry-title fusion-post-title").string
        content = soup.find(class_="post-content")
        
        # Remove characters that might corrupt the ebook file
        chapterTitle = chapterTitle.replace("<",'&lt;').replace(">",'&gt;')
        
        # Remove unnecessary objects and ads from the chapter
        for obj in content.find_all(**{"data-type":"post"}):
            obj.decompose()
        
        for n in content.find_all(class_="su-note"):
            n.decompose()
        
        for i in range(1,10):
            for ad in content.find_all(class_="quads-location quads-ad{}".format(i)):
                ad.decompose()
        
        # Add html header to the chapter
        chapter = '<html xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<title>{0}</title>\n</head>\n<body>\n<h1>{0}</h1>\n'.format(chapterTitle)
        chapter += str(content)
        if hasSpoiler != None:
            chapter += "<strong>The chapter name is: {}</strong>".format(hasSpoiler)
        
        # Collect some garbage to reduce RAM usage
        soup = None
        chapterTitle = None
        content = None
        gc.collect()
        
        # Return the chapter as a BeautifulSoup html object
        return BeautifulSoup(chapter, "html.parser")


class ReadLightNovelParser:
    
    def __init__(self):
        
        self.url = "https://www.readlightnovel.org/"
        self.name = "Read Light Novel"
        
        
        # Create containers
        self.novels = {}
        self.novelNames = None
        self.novelSypnoses = {}
        self.isLoaded = False
        self.bsParser = "html.parser"
        
        # Container for all novels that are requested
        self.novelLibrary = {}
    
    
    def load(self):
        if not self.isLoaded:
            self.parseNovelList()
            self.isLoaded = True
    
    
    def clearNovelCache(self):
        self.novelLibrary = {}
    
    
    def parseNovelList(self):
        
        soup = PageTools.getSoupFromUrl(self.url+"novel-list", parser="html5lib")
        books = PageTools.getElementsFromSoup(soup,[{"class_":"col-lg-12"},{"class_":"list-by-word-body"},"li"])
        
        for book in books:
            if PageTools.getElementsFromSoup(book, ["a"])[0]['href'] == "#":
                continue
            linkTitle = PageTools.getElementsFromSoup(book, [{"data-toggle":"popover"}])[0]
            
            self.novels[linkTitle.string] = [linkTitle['href'], PageTools.getElementsFromSoup(book, ["img"])[0]['src'], "N/A"]
            self.novelSypnoses[linkTitle.string] = PageTools.getElementsFromSoup(book, [{"class_":"pop-summary"}], onlyText=True)[0]
        
        self.novelNames = list(self.novels.keys())
        self.novelNames.sort()
    
    
    def loadNovelInfo(self, novelName):
        
        if novelName in self.novelLibrary.keys():
            return
            
        # Load the webpage for the novel
        soup = PageTools.getSoupFromUrl(self.novels[novelName][0])
        
        # Download cover image
        try:
            coverImage = PageTools.downloadPage(self.novels[novelName][1])
        except:
            coverImage = PageTools.downloadPage(noCoverLink)
        
        # Parse all of the book names/sections
        bookTitles = PageTools.getElementsFromSoup(soup, [{"id":"accordion"},{"class_":"panel-title"}], onlyText = True)
        
        # Create an empty dictionary to store all chapter names and links
        chapterLibrary = []
        bookToC = {}
        for i, bookTitle in enumerate(bookTitles):
            
            # Extract the html containing the chapter links and names
            chapterInfo = PageTools.getElementsFromSoup(soup,[{"id":"collapse-{}".format(i+1)},{"class_":"chapter-chs"},"a"])
            
            # Extract the chapter links and names
            chapterInfo = [[chap['href'], bookTitle+", "+chap.string.replace("<",'').replace(">",'')] for chap in chapterInfo]
            
            # Store chapters for each book
            bookToC[re.sub("\n", "", bookTitle)] = chapterInfo
            chapterLibrary.extend(bookToC[bookTitle])
        
        # Add the books, chapters, and the cover to the novel library
        self.novelLibrary[novelName] = [bookTitles, chapterLibrary, bookToC, coverImage]
    
    
    def getNovelNames(self):
        
        self.load()
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
        
        elements = ["ads-title","apester-element"]
        
        for element in elements:
            for script in content.find_all(class_=element):
                script.decompose()
        
        for a in content.find_all("a"):
            a.decompose()
        
        for hr in content.find_all("hr"):
            hr.decompose()
        
        for script in content.find_all("script"):
            script.decompose()
        
        for div in content.find_all("div"):
            div.decompose()
        
        # Add html header to the chapter
        chapter = '<html xmlns="http://www.w3.org/1999/xhtml">\n<head>\n<title>{0}</title>\n</head>\n<body>\n<h1>{0}</h1>\n'.format(chapterTitle)
        chapter += re.sub(" \.", ".", content.decode_contents()).strip("\n"+chapterTitle)
        
        # Collect some garbage to reduce RAM usage
        soup = None
        chapterTitle = None
        content = None
        gc.collect()
        
        # Return the chapter as a BeautifulSoup html object
        return BeautifulSoup(chapter, "html.parser")


if __name__ == "__main__":
    pass