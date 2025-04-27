![Datapack Toolkit logo](https://raw.githubusercontent.com/everloste/DatapackToolkit/refs/heads/main/assets/title-export.png)

An easy-to-use Minecraft worldgen datapack configuration tool created in a weekend.

Currently supports:
- Picking biome definition providers
- Editing structure set placement
- Custom configuration screens

The result are modified datapacks ready to be used.

## Using Datapack Toolkit
No installation is necessary. Simply download the latest version, extract, and run the app! (Run the executable named `dptoolkit`)

Load your datapack(s), make your changes, and export. **You can also load mods!**

They should then be put in the same order in-game as they were in Datapack Toolkit if you want the same results!
Datapack Toolkit takes their order into consideration.

## Working on Datapack Toolkit

### Prerequisites 
Datapack Toolkit is built in Python and Qt.

After picking the right IDE, make sure you have Python 3.12 installed. 3.13 might bork things.

Create a virtual environment (ideally). Your IDE should take care of this. [If not...](https://doc.qt.io/qtforpython-6/gettingstarted.html#installation)

Install the app's package requirements. Which right now is really just PySide6.

    pip install -r requirements.txt

And that's all. Have fun reating my spaghetti :3

### Packaging using PyInstaller

Datapack Toolkit can be packaged for use as a standalone app using PyInstaller. Make sure it's installed as a package.

Open your terminal. Make sure you're in the project directory and run the following command to package the app:

    pyinstaller -D -w -y --icon=src/assets/icon.ico --add-data=src/assets:src/assets --name=dptoolkit src/__main__.py

Make sure the `assets` folder is included alongside the exported executable.

### Compiling using Nuitka

You can also compile Datapack Toolkit using Nuitka. This is preferred over PyInstaller as the performance and size of the compiled app is somewhat better.

This is what is used since version 0.25.4.25.

cd to the project directory. Then run the command.

Command for Windows:

```
python -m nuitka --standalone --enable-plugin=pyside6 --output-filename=dptoolkit --include-data-dir=assets=assets --windows-console-mode=attach --windows-icon-from-ico=assets/icon.ico src/__main__.py
```

You can also compile for Linux on Windows using WSL.

Command for Linux:

```
python3 -m nuitka --standalone --enable-plugin=pyside6 --output-filename=dptoolkit --include-data-dir=assets=assets src/__main__.py
```

Make sure the `assets` folder is included alongside the compiled executable.

## Plans for Datapack Toolkit

There are a few thins I would like to do:
- Biome removal/replacement (such as for _Terralith_ or _Alpine_)

and now... mhmm.. i wan spaghetti now...

![](https://raw.githubusercontent.com/everloste/DatapackToolkit/refs/heads/main/code.png)
