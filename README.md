
# Novel 2 E-Book
This Python program will download books and chapters from novels on [Read Light Novel](https://www.readlightnovel.org/) website and saves them as .epub ebooks. About **_3500_ novels** available as of the latest release. 

**Please note that the quality of the formatting is worse than what you could get with the Master branch. The only reason for this program is for downloading novels that are not in the Master branch!**

Visit [novel-ebook.com](https://novel-ebook.com) for a webapp with the same functionality but with about 2000 supported novels made by [MakeYourLifeEasier](https://github.com/MakeYourLifeEasier). Beware this site is still in beta and you may experience problems. 

## Getting Started

To run this script you'll need to have Python 3.7.x installed which you can find [here](https://www.python.org/downloads/ "Python Download Link").

### Features

- Download your favourite novels from as .epub books from [Read Light Novel](https://www.readlightnovel.org/) website
- Automatically adds some metadata like title and cover
- Concurrent download of chapters - *significantly* faster download of books

### Usage

Download the source, install the requirements as mentioned below, navigate to the folder where you stored the source code using the console and write:

```
python novel2ebook.py
```

to launch the program or just use the start.bat file. If you didn't add Python to the PATH variable during the installation or afterwards, then write:

```
path/where/you/installed/python.exe novel2ebook.py
```
After that just select the novel you want to read, select the chapter range or the book you want to download and hit the "Download" button. Once the download is finished, the novel willl be stored in the same folder as the program/source. If you want to read on your Kindle device I highly recommend using [Calibre](https://calibre-ebook.com/) which can automatically convert *and* upload your freshly cooked ebooks to your device. Keep it mind that it will take some time for the book to be downloaded, so don't close the window or the console (or do as you please, *you do you*). 

### Prerequisites

As mentioned before this script was written for Python version 3.7.x. It may work with other versions too but none are tested.
Additionally the Python image library (Pillow), lxml, and BeautifulSoup4 are required.
To install all dependencies just use the console to navigate into the project folder and write

```
pip install -r requirements.txt
```

## For developers

If you make any changes to the source and want to package it up, just run the install.bat file to compile it (Requires PyInstaller).

## Keep in mind!

There are currently no plans to add any more features or websites to this project but if you have suggestions for future updates or come across any bugs don't hesitate to open up a "new issue" in the issue tab or write me an email at [andriux19960823@gmail.com](mailto:andriux19960823@gmail.com).

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* This program was initially created by [MakeYourLifeEasier](https://github.com/MakeYourLifeEasier) so thanks to him and all of the wonderful people on StackExchange, you guys are the best.
