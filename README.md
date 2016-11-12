GroundControl
======================




##Overview

Ground Control is the program which allows you to control the Maslow machine.

From within Ground Control, you can move the machine to where you want to begin a cut,
 calibrate the machine, open and run a g-code file, or monitor the progress of an ongoing
 cut.

 At present, the UI looks like this:
 ![UI](/Documentation/GroundControl.JPG)
 
Ground Control is written in the python programing language. Python was chosen because it
is a language with good cross platform support and is relatively simple to start working with.
Two of the goals of Ground Control are that it run on as many platforms as possible, and 
that it is as easy as possible for members of the community to contribute to making the 
program better.

##Setup
Ground Control is built using the 2.7.x version of the python language. 2.7 was chosen 
instead of 3.x because the support for compiling binaries for the 3.x version is not 
good enough yet. Maslow uses the Kivy framework for the UI (https://kivy.org/#home) and
the pyserial module for USB communication (https://pythonhosted.org/pyserial/).

###Installing Python
To setup your computer to run Ground Control from the source code, first install python
version 2.7.x, available for free here: https://www.python.org/downloads/

Once you have installed python 2.7.x open the command prompt and type 

```
>python --version
```

You should then see something similar to this:

```
Python 2.7.11
```

If python does not open, it is most likely an issue with needing to add python to you PATH.
You can find out more information about that here: http://superuser.com/questions/143119/how-to-add-python-to-the-windows-path

Next, you need to install Kivy and Pyserial. Fortunately, python comes with a built in
package manager which will install both of them for you. The python package manager is 
called pip.

To install pyserial, type:
```
>python -m pip install pyserial
```

and let pip do it's magic.

Installing Kivy is a little more complicated. First, check to make sure your version of
pip is up to date by running:

```
>python -m pip install --upgrade pip wheel setuptools
```

Then install dependencies by running:
```
python -m pip install docutils pygments pypiwin32 kivy.deps.sdl2 kivy.deps.glew
```

and finally install Kivy by running:

```
python -m pip install kivy
```

If you have any questions or issues with this process please get in touch through
the forums at http://www.maslowcnc.com/forums/#!/dev . If you had any issues which you
were able to resolve, please consider editing this README file to correct the parts which
were unclear.

##How To Run GC

Ground Control can be run from the command line using the command 

```
>python cncgc.py
```

If you are looking for a binary version of the software, check the releases on this page
or visit our website at www.maslowcnc.com. As of this writing, no binaries or installers
for the newest version of Ground Control are available because the software is still 
evolving so rapidly.


##How To Contribute


##Current Program Data Flow

![Program Data Flow](/Documentation/GroundControlDataFlow.png)