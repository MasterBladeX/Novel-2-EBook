import urllib
import urllib.request
from bs4 import BeautifulSoup
import ssl
import json


class PageTools():

    def downloadPage(self, url, timeout = 5, attempts = 5):
        
        # Fake browser headers
        ssl._create_default_https_context = ssl._create_unverified_context
        urlReq = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh;Intel Mac OS X 10_9_3)'+\
                                        ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'})
        
        # Open url, read the response and return it, attempty
        for i in range(attempts):
            try:
                with urllib.request.urlopen(urlReq, timeout = timeout) as response:
                     return response.read()
            except:
                print("Connection to {} failed, retrying ({})...".format(url, i+1))
                pass
        raise urllib.error.URLError("Connection to {} timed-out/failed, retried {} times".format(url, attempts))
    
    def getJsonFromUrl(self, url):
    
        # Download the JSON stored in the url
        response = self.downloadPage(url).decode('utf8')
        jsonFile = json.loads(response)
        return jsonFile
    
    
    def getSoupFromUrl(self, url):
        
        # Parse the webpage response with the HTML parset
        soup = BeautifulSoup(self.downloadPage(url), 'html.parser')
        return soup
    
    
    def getElementsFromSoup(self, soup, elementRecursiveList, findAllEnableList = True, onlyText = False, recursionIndex = 0):
        
        # If a single boolean is input for findAllEnableList, we assume that it is the same for all elements
        if findAllEnableList == True or findAllEnableList == False:
            findAllEnableList = [findAllEnableList] * len(elementRecursiveList)
        
        # Check if inputs are of the correct type
        if not(isinstance(elementRecursiveList[0], str) or isinstance(elementRecursiveList[0], dict)):
            raise TypeError("Input object is not of the right type must be a string or a dictionary")
  
        if isinstance(elementRecursiveList[0], dict):
            if not (isinstance(list(elementRecursiveList[0].keys())[0], str)\
               or isinstance(elementRecursiveList[0][list(elementRecursiveList[0].keys())[0]], str)):
                raise TypeError("Input tuple contains objects of the wrong type. Recursion: {}".format(recursionIndex))
        
        # Find if this is the final recursion
        isLast = len(elementRecursiveList) == 1
        
        # Container for the requested info
        elementList = []
        
        # If the current request needs all of the elements matching the input do the following
        if findAllEnableList[0]:
            
            # Take slightly different approach to processing the info depending if using a string or a dictionary as an input 
            if isinstance(elementRecursiveList[0], dict):
                for element in soup.findAll(**elementRecursiveList[0]):
                    
                    # Finish up parsing of the page if this is the last recursion 
                    if isLast:
                        if onlyText:
                            text = [item for item in element.findAll(text=True) if item != '\n'][0].strip('\n')
                            elementList.append(text)
                        else:
                            elementList.append(element)
                    else:
                        elementList.extend(self.getElementsFromSoup(element, elementRecursiveList[1:], findAllEnableList[1:], onlyText, recursionIndex+1))
            else:
                for element in soup.findAll(elementRecursiveList[0]):
                    if isLast:
                        if onlyText:
                            text = [item for item in element.findAll(text=True) if item != '\n'][0].strip('\n')
                            elementList.append(text)
                        else:
                            elementList.append(element)
                    else:
                        elementList.extend(self.getElementsFromSoup(element, elementRecursiveList[1:], findAllEnableList[1:], onlyText, recursionIndex+1))
        else:
            if isinstance(elementRecursiveList[0], dict):
            
                # Same as above but we only take the first element we found as opposed to all elements
                # Similarly to above, we finish up if this is the last recursion
                if isLast:
                    if onlyText:
                        text = [strItem for strItem in soup.find(**elementRecursiveList[0]).findAll(text=True) if strItem != '\n'][0].strip('\n')
                        elementList.append(text)
                    else:
                        elementList.append(soup.find(**elementRecursiveList[0]))
                else:
                    elementList = self.getElementsFromSoup(soup.find(**elementRecursiveList[0]), elementRecursiveList[1:], findAllEnableList[1:], onlyText, recursionIndex+1)
            else:
                if isLast:
                    if onlyText:
                        text = [strItem for strItem in soup.find(elementRecursiveList[0]).findAll(text=True) if strItem != '\n'][0].strip('\n')
                        elementList.append(text)
                    else:
                        elementList.append(soup.find(elementRecursiveList[0]))
                else:
                    elementList.extend(self.getElementsFromSoup(soup.find(elementRecursiveList[0]), elementRecursiveList[1:], findAllEnableList[1:], onlyText, recursionIndex+1))
        
        return elementList
    
    
    def getElementsFromUrl(self, url, elementRecursiveList, findAllEnableList = True, onlyText = False, recursionIndex = 0):
        
        # Get the requested elements directly from the url
        return self.getElementsFromSoup(self.getSoupFromUrl(url), elementRecursiveList, findAllEnableList, onlyText, recursionIndex)
