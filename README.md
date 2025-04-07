# Datapack Toolkit
An easy worldgen datapack configuration tool made in a weekend.

Currently supports biome definition ordering/removal.
That means you can pick and choose which biome overhaul you want, from whichever datapacks you want.

The result are modified datapacks ready to be used.

## Using Datapack Toolkit
Simply download the latest version and run the app!
No installation is necessary.

Load your datapack(s) by clicking ***Import datapack*** in the top left.
Export modified versions by clicking ***Export datapack(s)***.

## Working on Datapack Toolkit

### Prerequisites 
Datapack Toolkit is built in Python and Qt.

After picking the right IDE, make sure you have Python **3.12** installed.

Create a virtual environment (ideally). Your IDE should take care of this. [Or if not...](https://doc.qt.io/qtforpython-6/gettingstarted.html#installation)

You only need **PySide6** to work on the app:

    pip install pyside6

That's all. Have fun reating my spaghetti :3

I should note that on the off-chance anybody _will_ try to work on the code,
the current datapack and biome management class `biomeblender` will later be removed in favour of multiple, more flexible options.
See `datapackmanager`.

### Packaging

Datapack Toolkit is packaged using PyInstaller.
It has [requirements](https://pyinstaller.org/en/stable/requirements.html).
If you're good to go, run:

    pip install pyinstaller

Package the app in your terminal. Make sure you're in the project directory and run the following command to package the app:

    pyinstaller --onefile --noconsole --icon "src/assets/app.ico" --name "dptoolkit" "src/main.py"

Include the assets folder with the app for the icon to work properly.
(I know there's a command.. I'll get around to streamlining this later... For now this is fine...)

## Plans for Datapack Toolkit

There is currently one feature _definitely_ planned to be implemented (by me):
- Structure generation configuration
  - I.e. spacing and separation

There are other thins I would like to do:
- Biome removal/replacement (such as for _Terralith_ or _Alpine_)
- Noise/density function scale adjustment (such as for _Continents_)

Internally, datapack and biome management will later be completely separated, but y'know. Spaghetti for now... mhmm.. i wan spaghetti now...

![](https://raw.githubusercontent.com/everloste/DatapackToolkit/refs/heads/main/code.png)
