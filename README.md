
# Novel 2 E-Book
This Python program will download books and chapters from novels availaible on [WuxiaWorld](https://www.wuxiaworld.com) and [Gravity Tales](https://gravitytales.com/) and saves them into the .epub format.

Visit [novel-ebook.com](https://novel-ebook.com) for a webapp with the similar functionality which includes many more novels made by [MakeYourLifeEasier](https://github.com/MakeYourLifeEasier). Beware this site is still under development.

## Getting Started

To run this script you'll need to have Python 3.7.x installed which you can find [here](https://www.python.org/downloads/ "Python Download Link").

### Features

- Download your favourite novels from [WuxiaWorld](https://www.wuxiaworld.com) and [Gravity Tales](https://gravitytales.com/) and save them as .epub files
- Automatically adds some metadata like title, cover, and author (translator used as author as it was easier to implement)
- Concurrent download of chapters - *significantly* faster download of books

### Usage

Download the precompiled program from [releases](https://github.com/EternalTrail/Wuxiaworld-2-eBook/releases), unzip the file, and run novel2ebook.exe to launch the program.

After that just select the novel you want to read, select the chapter range or the book you want to download and hit the "Download" button. Once the download is finished, the novel willl be stored in the same folder as the program/source. If you want to read on your Kindle device I highly recommend using [Calibre](https://calibre-ebook.com/) which can automatically convert *and* upload your freshly cooked ebooks to your device. Keep it mind that it will take some time for the book to be downloaded, so don't close the window or the console (or do as you please, *you do you*). 

Alternatively, you can download the source, install the requirements as mentioned below, navigate to the folder where you stored the source code using the console and write:

```
python novel2ebook.py
```

to launch the program or just use the start.bat file. If you didn't add Python to the PATH variable during the installation or afterwards the write

```
path/where/you/installed/python.exe novel2ebook.py
```

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

If you come across bugs or suggestions for future updates don't hesitate to open up a "new issue" in the issue tab or write me an email at [andriux19960823@gmail.com](mailto:andriux19960823@gmail.com).


### Planned features and updates

- Cover editing and custom covers
- More ebook formats
- More websites

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* This program was initially created by [MakeYourLifeEasier](https://github.com/MakeYourLifeEasier) so thanks to him and all of the wonderful people on StackExchange, you guys are the best.
