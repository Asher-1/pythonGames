Make Me
=======

Team entry "gamebyalex2" for PyWeek #6 (http://www.pyweek.org/6).

This is a modified version of the original submission, featuring several
bug fixes, a larger map and some new parts to collect.

Requirements
------------

 * Python 2.5
 * One of:
   - Mac OS X 10.3 or later
   - Windows XP or later
   - Linux with GTK 2.2 (most distros will suffice).

To hear music, you will also need AVbin (http://code.google.com/p/avbin).
This is included with every release distribution of pyglet.

A current version of pyglet is included in this distribution, you do not need
to install it.

Playing the game
----------------

Run 'run_game.py'.

Most instructions are introduced gradually during gameplay.  In case you miss
or forget one...

  * Arrow keys move you around.  Depending on the parts you have attached
    the arrow keys behave differently.
  * Wherever you see a "save" sign, stand (or float) in front of it and
    press "S" to save your game.  The saved game overwrites any previously
    saved game.  Saved games are stored on disk per-user.
  * Press spacebar to view your blueprints.  Click on the arrows next to
    one of your parts to swap that part (there are no swappable parts at
    the beginning of the game).
  * You can also use keys 1, 2 and 3 to quickly change your head, torso
    or leg part, respectively, without going to the blueprints.
  * Press escape to return to the main menu.

Known issues:
    - The menu screen flickers during camera movement on at least on Macbook
      Pro when running Windows XP.
    - The darkness effect used in the last third of the game requires
      OpenGL 1.4 or later and a 32-bit video buffer.  Most graphics
      cards made in recent years, including integrated graphics, support this.
      If your card does not support it, or you are running in a 16-bit video
      mode without a compositor, the game will be easier as the dark areas
      will not be painted out.

Please report any problems to the issue tracker at http://www.pyglet.org, or
mail me at Alex.Holkner@gmail.com.  Bug reports are highly valued as they
are the only way we find out where pyglet does not yet work.

Acknowledgements
----------------

Music loops from http://www.soundsnap.com:
 "Dopekick-Childhoods" by Andrew Potterton
 "K-Kiddies.mp3" by Andrew Potterton
 "Musty-Flows-C-83.5.mp3" by Andrew Potterton
 "Angelica_01.mp3" by "mikedred"

Sound effects based on source material from http://www.soundsnap.com:
 "slide.wav" by "rebecca"
 "click.wav" by "sofa sound"
 "clunk.wav" by "justsound_girl"
 "squeak.wav" by "Reeouchii"
 "explosion.wav" by "discostu"
 "break.wav" by "shriek"
 "bleep.wav" by "discostu"
 "heart.wav" by "discostu"
 "coin.wav" by "sofa sound"
 "drip.wav" by "justsound_girl"
 "bell.wav" by "m idea"

Fonts from http://1001freefonts.com:
 "Attract more women" by Jakob Fischer at www.pizaadude.dk

License
-------

Copyright 2008 Alex Holkner and Rebecca Wong, all rights reserved.  Please
contact me at Alex.Holkner@gmail.com if you wish to use the code or artwork
for anything besides personal use.
