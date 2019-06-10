
# WuxiaWorld-2-eBook
This Python script will download chapters from novels availaible on wuxiaworld.com and saves them into the .epub format.

Visit [novel-ebook.com](https://novel-ebook.com) for a webapp with the similar functionality made by [MakeYourLifeEasier](https://github.com/MakeYourLifeEasier). Beware this site is still under development.

## Getting Started

To run this script you'll need to have Python 3.7.x installed which you can find [here](https://www.python.org/downloads/ "Python Download Link").

### Features

- Download and save you favorite Novels from wuxiaworld.com into a .epub file
- Automatically adds some metadata like title and cover

### Prerequisites

As mentioned before this script was written for Python version 3.7.x. It may work with other versions too but none are tested.
Additionally the Python image library (Pillow), lxml and Beautifulsoup4 are required.
To install all dependencies just use the console to navigate into the project folder and write

```
pip install -r requirements.txt
```

### Usage

Download the precompiled program from [releases](https://github.com/EternalTrail/Wuxiaworld-2-eBook/releases)

Additionally, you can download the script and navigate to the folder using the console then write

```
python wuxiaworld2ebook.py
```

or just use the start.bat file. If you didn't add Python to the PATH variable during the installation or afterwards the write

```
path/where/you/installed/python.exe wuxiaworld2ebook.py
```

After that just select the novel you want to read, select the chapter range or the book you want to download and hit the "Download" button. Keep it mind that it will take some time for the script to finish, so don't close the window or the console if the program doesn't respond.

## Keep in mind!

If you come across bugs or suggestions for future updates don't hesitate to open up a "new issue" in the issue tab or write me an email at [andriux19960823@gmail.com](mailto:andriux19960823@gmail.com).


### Planned features and updates

- Cover editing and custom covers
- More ebook formats

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* This program was initially created by [MakeYourLifeEasier](https://github.com/MakeYourLifeEasier) so thanks to him and all of the wonderful people on StackExchange, you guys are the best.
