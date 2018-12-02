Werewolf Sonata
===============

Entry in PyWeek #17  <http://www.pyweek.org/17/>

URL:
    http://pyweek.org/e/nagslang
Team:
    Cape Viper
Members:
    Simon Cross
    David Fraser
    Neil Muller
    Adrianna Pinska
    Stefano Rivera
    David Sharpe
    Jeremy Thurgood
License:
    see LICENSE.txt

Requirements
============

The game requires pygame and pymunk. Requirements can be installed by

  pip install -e .

Or

  pip install -r requirements.txt

It was developed using python 2.7, pymunk 4.0 and pygame 1.9.2. Older
versions may or may not work.

The editor also requires Albow 2.2.0 from
http://www.cosc.canterbury.ac.nz/greg.ewing/python/Albow/


Running the Game
----------------

On Windows or Mac OS X, locate the "run_game.pyw" file and double-click it.

Othewise open a terminal / console and "cd" to the game directory and run:

  python run_game.py


How to Play the Game
--------------------

Move Lyca, the werewolf insurance assessor, around the screen with the arrow
keys or A, S, W, D.

Fire a gun or claw aliens with Z or CTRL.

Change between werewolf and human by pressing C.

Interact with doors and other objects using SPACE.

There are no ducks.


Development notes
-----------------

Creating a source distribution with::

   ./scripts/build_unix.sh

You may also generate Windows executables and OS X applications::

   python setup.py py2exe
   python setup.py py2app

Later you might be able to upload files to PyWeek with::

   python pyweek_upload.py

Later you might be able to upload to the Python Package Index with::

   python setup.py register
   python setup.py sdist upload

