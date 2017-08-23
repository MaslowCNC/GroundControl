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

----
## Installation

For Windows and OS X binaries, see the [releases](releases) page.

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
