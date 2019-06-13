import zipfile
import uuid


class EBookGenerator:
    
    
    def generateEBook(self, htmlFiles, novelName, bookName, author, coverImage):
        
        # Replace invalid characters with spaces
        for character in "\\/<>|:*\"?":
            novelName = novelName.replace(character, " ")
            bookName = bookName.replace(character, " ")
        
        # Ceate the ebook file
        epub = zipfile.ZipFile(novelName + ", " + bookName + ".epub", "w", zipfile.ZIP_DEFLATED)

        # Replace more invalid characters
        novelName = novelName.replace('&', "&amp;")
        bookName = bookName.replace('&', "&amp;")
        
        # Create containers for book info
        manifest = ""
        spine = ""
        tableOfContents = ""
        
        # Write each HTML file to the ebook and format the spine, manifest, and table of contents
        for i, html in enumerate(htmlFiles):
            basename = "{}.xhtml".format(i)
            manifest += '<item id="file_{}" href="Text/{}" media-type="application/xhtml+xml"/>'.format(i+1, basename)
            spine += '<itemref idref="file_{}" />'.format(i+1)
            epub.writestr("OEBPS/Text/"+basename, str(html))
            tableOfContents += '<li class="toc-Chapter-rw" id="{}"><a href="{}">{}</a></li>'\
                                       .format(i, "{}.xhtml".format(i), html.title.string.replace("<",'&lt;')\
                                       .replace(">",'&gt;').replace('&', "&amp;"))
        
        # Write all of the formated data and the cover image to the book
        epub.writestr("mimetype", "application/epub+zip")
        epub.writestr("META-INF/container.xml", ('<?xml version="1.0" encoding="UTF-8"?>\n<container version="1.0" '
                                                'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n   <rootfiles>\n'
                                                '<rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>\n'
                                                '</rootfiles>\n</container>'))
        epub.writestr("OEBPS/toc.ncx", ('<?xml version="1.0" encoding="utf-8" ?>\n<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"\n'
                                        ' "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd"><ncx version="2005-1"'
                                        ' xmlns="http://www.daisy.org/z3986/2005/ncx/">\n  <head>\n    '
                                        '<meta content="ID_UNKNOWN" name="dtb:uid"/>\n    <meta content="0" name="dtb:depth"/>\n    '
                                        '<meta content="0" name="dtb:totalPageCount"/>\n    <meta content="0" name="dtb:maxPageNumber"/>\n'
                                        '  </head>\n  <docTitle>\n    <text>Unknown</text>\n  </docTitle>\n  <navMap>\n    '
                                        '<navPoint id="navPoint-1" playOrder="1">\n      <navLabel>\n        <text>Start</text>\n      '
                                        '</navLabel>\n      <content src="Text/Section0001.xhtml"/>\n    </navPoint>\n  </navMap>\n</ncx>'))
        epub.writestr("OEBPS/content.opf", ('<package version="3.1" xmlns="http://www.idpf.org/2007/opf" unique-identifier="{0}">'
                                            '<metadata><dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">{1}</dc:title><dc:creator '
                                            'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:ns0="http://www.idpf.org/2007/opf" '
                                            'ns0:role="aut" ns0:file-as="Unbekannt">{2}</dc:creator><dc:language '
                                            'xmlns:dc="http://purl.org/dc/elements/1.1/">en</dc:language><dc:identifier '
                                            'xmlns:dc="http://purl.org/dc/elements/1.1/">{0}</dc:identifier></metadata><manifest>'
                                            '{3}<item href="Text/toc.xhtml" id="toc" properties="nav" media-type="application/xhtml+xml"/>'
                                            '<item href="Images/cover.jpg" id="cover" media-type="image/jpeg" properties="cover-image"/>'
                                            '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/></manifest>'
                                            '<spine toc="ncx"><itemref idref="toc"/>{4}</spine></package>').format(uuid.uuid1().hex, \
                                            novelName+" "+bookName, author, manifest, spine))
        epub.writestr("OEBPS/Text/toc.xhtml", ('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html>\n<html xmlns='
                                               '"http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">\n'
                                               '<head>\n<title>{}</title>\n</head>\n<body>\n<section class="frontmatter '
                                               'TableOfContents">\n<header>\n<h1>Contents</h1>\n</header>\n'
                                               '<nav id="toc" role="doc-toc" epub:type="toc">\n<ol>\n{}</ol>\n</nav>\n'
                                               '</section>\n</body>\n</html>').format(novelName+" "+bookName, tableOfContents))
        epub.writestr("OEBPS/Images/cover.jpg", coverImage)
        epub.close()
    
    
    def readImage(self, image_path):
        
        # Open the image and return the image in binary
        with open(image_path, "rb") as img:
            return img.read()
