Maslow CNC - Ground Control
======================

## Overview

Ground Control is the program which allows you to control the [Maslow CNC machine](http://www.maslowcnc.com/).

From within Ground Control, you can move the machine to where you want to begin a cut, calibrate the machine, open and run a [g-code](/wiki/G-Code-and-MaslowCNC) file, or monitor the progress of an ongoing cut.

At present, the UI looks like this:

![UI](/Documentation/GroundControl.JPG)

Ground Control is written in [Python](https://www.python.org/). It was chosen because it has good cross platform support and is relatively simple to work with.

Two of the goals of Ground Control are:

1) It runs on as many platforms as possible.
2) It is as easy as possible for members of the community to contribute to making the program better.

### Index

* [Installation](#installation)
* [Documentation](#documentation)
* [Development Setup](#development-setup)
* [Support](#support)
* [How To Contribute](#how-to-contribute)
* [Program Data Flow](#program-data-flow)
* [Beginner's Tips](#beginners-tips)

----
## Installation

For Windows and OS X binaries, see the [releases](https://github.com/MaslowCNC/GroundControl/releases) page.

For help installing binaries, see the [installation guides](https://github.com/MaslowCNC/GroundControl/wiki#gc-installation-guides).

## Documentation

Ground control documentation is available on the [project wiki](/wiki).

For help in using Ground Control, see the [users guide](/wiki/Ground-Control-Users-Guide).

## Development Setup

Ground Control is built using the 2.7.x version of the Python language. 2.7 was chosen instead of 3.x because the support for compiling binaries for the 3.x version is not good enough yet.

Maslow uses the [Kivy framework](https://kivy.org/#home) for the UI  and the [pyserial](https://pythonhosted.org/pyserial/) module for USB communication.

You might also consider taking a look at [Virtual Environments](http://docs.python-guide.org/en/latest/dev/virtualenvs/) to save you from python version headaches later on. This is not a prerequisite for installation on any platform.

### Windows

To setup your computer to run Ground Control from the source code, first download and install [Python version 2.7.x](https://www.python.org/downloads/).

Once you have installed Python 2.7.x, open the command prompt and type

```bat
python --version
```

You should then see something similar to this:

```bat
Python 2.7.11
```

If python does not open, it is most likely an issue with the `PATH` environment variable.

For more information about configuring the `PATH` in Windows, see [superuser: How to add python to the windows path](http://superuser.com/questions/143119/how-to-add-python-to-the-windows-path).

Next, you need to install Kivy and Pyserial. Fortunately, python comes with a built in package manager, `pip` which will install both of them for you.

#### Installing pyserial

To install pyserial, type:

```bat
python -m pip install pyserial
```

#### Installing Kivy

Installing Kivy is a little more complicated. First, check to make sure your version of `pip` is up to date by running:

```bat
python -m pip install --upgrade pip wheel setuptools
```

then install dependencies:

```bat
python -m pip install docutils pygments pypiwin32 kivy.deps.sdl2 kivy.deps.glew
```

and finally install Kivy:

```bat
python -m pip install kivy
```

### OS X

To install Python on OS X, first install [Homebrew](https://brew.sh/)

```bash
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

then install Python:

```bash
brew install python
```

Install required dependencies:

```bash
pip install -r requirements_osx.txt
```

### Linux

Python is bundled with all major linux distributions.  You can confirm the version of python you have installed with:

```bash
python --version
```

See documentation for your linux distro on how to install Python 2.7.x if it is not installed.

Once Python 2.7.x is installed, install required dependencies:

```bash
pip install -r requirements_linux.txt
```

### Running Ground Control

Ground Control can be run from the command line. From within the project folder, run the following:

```bash
python main.py
```

## Support

If you have any questions or issues with this process please get in touch through the [Maslow forums](http://www.maslowcnc.com/forums/#!/dev).

If you had any issues which you were able to resolve, please consider raising a Pull Request on this `README.md` file with corrections or additions.  For more information, see [How To Contribute](#how-to-contribute) below.

## How To Contribute

Maslow is an open source project, get involved!

### Bugs

If you find a bug in the software, report it on the [issues page](/issues).

### Feature requests

If you have an idea for a new feature, let us know in the [Maslow forums](http://www.maslowcnc.com/forums/#!/dev).

### Contributing

If you want to get involved, say hi in the [Maslow forums](http://www.maslowcnc.com/forums/#!/dev).

If you've already jumped in and started making the software better, feel free to submit a pull request! You can learn more about how to do that here [Github Help: Creating a pull request](https://help.github.com/articles/creating-a-pull-request/)

## Program Data Flow

![Program Data Flow](/Documentation/GroundControlDataFlow.png)

## Beginner's Tips
### In the .kv file:
Kivy uses groundcontrol.kv as a description language for most of the widgets in GroundControl; some tips:
1. Class References: 
	`root.X` refers to things inside the class.  You can add your own variables, but they don't get initialized in time to be used (so root.data doesn't work)
	but you can use `app.X` to refer to things in the app namespace, so `app.data` will always work.  BUT you must define the variable in `DataStructures/data.py`;
	things put in the data dict at runtime *will not work*.
	
2. Formatting:
	You can include format strings and logic in the .kv file; eg `text: "{Z: %.2f}"%app.data.zPos` will automatically expand/update when `app.data.zPos` changes.
	But, if it's a text input field, you need to hook the field to an event -- changing the text in the box *will not* update `app.data.zPos`.

3. Referring to UI bits in code:
	If you want to refer to a widget in the code, you need to give it an id, *and* you need to put a `id:id` statement after the widget definition starts
	Otherwise, you won't be able to access it in the code.  If you put an `id:id` statement in place but you don't declare a widget with that id, it will
	crash when you bring up the widget.
	
4. Attributes:
	Most attributes (eg. `text_size`, `multiline`, `disabled`, etc) are not inheritable (you can't set the attribute in the "GridLayout" portion); 
	they have to be decorated on each control.
	
5. Layouts:
	GridLayout's et al don't support "span" to span columns or rows.  If you want to do that kind of thing, redo the grid to the large size and put
	sub-GridLayouts in the cells.   Try to make the cells the same size so they line up nicely.
	The Layouts will not actually work unless you have `rows` & `columns` attributes in them.  The log file will complain about this, so watch for it.
	You can auto-size-to-the-minimum *sometimes* with `size_hint_x: None`.  But if you give it a 2 (ie, `size_hint_x: 2` for 2%), it always works 
	kinda (it always works but may not do what you expected).
	
6. Coordinate Systems:
	Kivy defines things as origin is bottom-left, an increasing Y is up, increasing X is right.
	Please use `self.origin` in the code -- if you draw something, 0,0 is the bottom-left of the application, not the bottom-left of your widget.
	
7. Events:
	Always bind to the `on_touch_up` event.  If you bind to the `on_touch_down` instead, you get a behavior that looks like a click-through:
	* You catch the `on_touch_down`, and pop-up a menu with a button on it.
	* The mouse is still down... so it will select a file (if file_dialog), or if the next dialog catches the `on_touch_up` event, it will fire as soon as the click is released
	
### Python Tips:
1. If an object begins with a capital letter, it is a global object (eg, `CanvasSize=4`).  Don't do `CamelCase`; do `camelCase` instead.
2. If you want to persist values across functions, they need to be in the object-space (`self.x`) or in the global-space (`CanvasSize`), or in App-space 
	(`app.data.X` or `self.data.X` after init)
	If you use a variable without the `self.`, it will work but it won't be persisted, so it can be annoying to figure out what (didn't) happened.
3. If you want to call another function in your class, preface it with `self.` (eg, `self.recomputethis()` -- and the self arg gets passed in automagically)
4. Always remember to call the super if you're implementing `__init__`
5. Remember - your dialog/widget/etc can go away *without* calling the callback function - the user just clicks back to the main window.
	Don't count on the callback to save state.  Don't use the callback to put the machine in a known state (because it may not get executed).
6. Dialogs don't get to close themselves; when your `self.done` is executed, call your callback function, and your parent can get data out of 
	your dialog and is responsible for closing you.  But see rule #5.
7. Remember - Python is case-sensitive... and filename/directory/case sensitive as well.
8. Much mumbo-jumbo about how to save data in the .ini file
9. Some mumbo-jumbo about how to use the logger
10. If you need to send a command to Maslow, use the `self.data.gcode_queue.put('GCode-Here')`
11. Mumbo-jumbo about how to get data back from Maslow
12. On the g-code canvas, 0,0 is the center, and bottom-left is -X,-Y (y axis is reversed compared to old computer code, but "usual" in math terms).
13. json does not know about tuples.  It will make the variables a _list_ and if your functions can't handle that, you need to convert them.

### General UI Layout:
* frontPage - is the root host for all widgets.
  * screenControls - has all the buttons on the main screen (both the top bar and the right side)

