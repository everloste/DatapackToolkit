# Datapack Toolkit
An easy-to-use Minecraft worldgen datapack configuration tool made in a weekend.

Currently supports:
- Picking biome definition providers
- Editing structure set placement

The result are modified datapacks ready to be used.

## Using Datapack Toolkit
Simply download the latest version and run the app!
No installation is necessary.

Load your datapack(s) by clicking ***Load*** in the top left.
Export modified versions by clicking ***Export***.

## Working on Datapack Toolkit

### Prerequisites 
Datapack Toolkit is built in Python and Qt.

After picking the right IDE, make sure you have Python **3.12** installed.

Create a virtual environment (ideally). Your IDE should take care of this. [Or if not...](https://doc.qt.io/qtforpython-6/gettingstarted.html#installation)

You only need **PySide6** to work on the app:

    pip install pyside6

That's all. Have fun reating my spaghetti :3

### Packaging

Datapack Toolkit is packaged using PyInstaller.
It has [requirements](https://pyinstaller.org/en/stable/requirements.html).
If you're good to go, run:

    pip install pyinstaller

Package the app in your terminal. Make sure you're in the project directory and run the following command to package the app:

    pyinstaller --onefile --noconsole --icon "src/assets/icon.ico" --add-data="src/assets":"assets" --name "dptoolkit" "src/main.py"

## Plans for Datapack Toolkit

There are a few thins I would like to do:
- Biome removal/replacement (such as for _Terralith_ or _Alpine_)
- Noise/density function scale adjustment (such as for _Continents_)
- A format to allow datapacks to define their own config screens

and now... mhmm.. i wan spaghetti now...

![](https://raw.githubusercontent.com/everloste/DatapackToolkit/refs/heads/main/code.png)
