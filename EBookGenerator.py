import zipfile
import uuid


class EBookGenerator:
    
    # TODO: implement different ebook formats (MOBI, or newer/older versions of EPUB)
    
    def generateEBook(self, htmlFiles, novelName, bookName, author, coverImage):
        
        # Replace invalid characters with spaces
        for character in "\\/<>|:*\"?":
            novelName = novelName.replace(character, " ")
            bookName = bookName.replace(character, " ")
        
        # Ceate the ebook file
        epub = zipfile.ZipFile(novelName + ", " + bookName + ".epub", "w", zipfile.ZIP_DEFLATED)

        # Generate unique ID for the book and create containers for book info
        uniqueid = uuid.uuid1().hex
        manifest = ""
        spine = ""
        tableOfContentsChapters = ""
        
        # Write each HTML file to the ebook and format the spine, manifest, and table of contents
        for i, html in enumerate(htmlFiles):
            basename = "{}.xhtml".format(i)
            manifest += '<item id="file_{}" href="{}" media-type="application/xhtml+xml"/>'.format(i+1, basename)
            spine += '<itemref idref="file_{}" />'.format(i+1)
            epub.writestr("OEBPS/"+basename, str(html))
            tableOfContentsChapters += '''<li class="toc-Chapter-rw" id="{}">
                <a href="{}">{}</a>
                </li>'''.format(i, "{}.xhtml".format(i), html.title.string.replace("<",'&lt;').replace(">",'&gt;'))
        
        # Format the metadata of the book
        metadata = '''<dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">{}</dc:title>
            <dc:creator xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:ns0="http://www.idpf.org/2007/opf" ns0:role="aut" ns0:file-as="Unbekannt">{}</dc:creator>
            <dc:language xmlns:dc="http://purl.org/dc/elements/1.1/">en</dc:language>
            <dc:identifier xmlns:dc="http://purl.org/dc/elements/1.1/">{}</dc:identifier>'''.format(novelName+" "+bookName, author, uniqueid)

        # Format the index
        index_tpl = '''<package version="3.1"
        xmlns="http://www.idpf.org/2007/opf" unique-identifier="''' + uniqueid + '''">
            <metadata>{}</metadata>
            <manifest>{}<item href="toc.xhtml" id="toc" properties="nav" media-type="application/xhtml+xml"/>
            <item href="cover.jpg" id="cover" media-type="image/jpeg" properties="cover-image"/></manifest>
            <spine><itemref idref="toc"/>{}</spine>
        </package>'''.format(metadata, manifest, spine)
        
        # Format the table of contents
        tableOfContents = '''<?xml version='1.0' encoding='utf-8'?>
            <!DOCTYPE html>
            <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
            <head>
                <title>{}</title>
            </head>
            <body>
                <section class="frontmatter TableOfContents">
                    <header>
                        <h1>Contents</h1>
                    </header>
                    <nav id="toc" role="doc-toc" epub:type="toc">
                        <ol>
                        {}
                </ol></nav></section></body></html>'''.format(novelName+" "+bookName, tableOfContentsChapters)
        
        # Write all of the formated data and the cover image to the book
        epub.writestr("mimetype", "application/epub+zip")
        epub.writestr("META-INF/container.xml", '''<container version="1.0"
                  xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
          <rootfiles>
            <rootfile full-path="OEBPS/Content.opf" media-type="application/oebps-package+xml"/>
          </rootfiles>
        </container>''')
        epub.writestr("OEBPS/Content.opf", index_tpl)
        epub.writestr("OEBPS/toc.xhtml", tableOfContents)
        epub.writestr("OEBPS/cover.jpg", coverImage)
        
        epub.close()
    
    
    def readImage(self, image_path):
        
        # Open the image and return the image in a binary format
        with open(image_path, "rb") as img:
            return img.read()
