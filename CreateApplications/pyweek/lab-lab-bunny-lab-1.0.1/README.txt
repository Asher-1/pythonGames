Lab Lab Bunny Lab
=================

Entry in PyWeek #13  <http://www.pyweek.org/13/>
Code, drawing and sounds: Daniel Darabos ("cyhawk") <darabos.daniel@gmail.com>
Music: Beata Darabos ("bejus") <bejus79@gmail.com> (Vocals: Daniel Darabos)


DEPENDENCIES:
-------------

This game uses Python and Pyglet.

  Python (2.5 or newer):     http://www.python.org/
  Pyglet (it's bundled):     http://www.pyglet.org/


RUNNING THE GAME:
-----------------

  python run_game.py


TROUBLESHOOTING:
----------------

Problem: I get static noise after some sound effects. Or I don't hear music.
Solution: Make sure AVBin is installed. On Mac OS X try starting the game like
this:

  arch -i386 python run_game.py

This forces Python to 32-bit mode which allows it to load the 32-bit AVBin
library which in my experience fixes the static. Plus it allows the game to
play music.

On Linux try this:

  PYGLET_AUDIO=alsa python run_game.py

This makes Pyglet prefer ALSA over OpenAL which may work better for you. If
everything else fails you can mute sounds and/or music by editing the settings
at the beginning of run_game.py.

---

Problem: Game window too big or too small.
Solution: Start the game in full screen mode:

  python run_game.py -f

This will use your current resolution which is hopefully something you like.

---

Problem: The laboratory is a mess and I cannot engineer a rabbit that would
         clean up.
Solution: You can start with a clean slate by deleting the "save_game" file.
For example:

  rm save_game; python run_game.py


BUNNY WAR SONG LYRICS:
----------------------

It's cold out there, nuclear winter,
  come in and shut the saloon's door tight.
The loneliest arm is plucking the strings
  in this post-apocalyptic night.
A few days ago attached to a shoulder
  it waved, hugged and raised a cup.
But I for one welcome our overlords,
  their white fur shines in the mist.

I was the first to run, the last to fall,
  the rabbits still outran us all.
They jumped from left, jumped up from the right,
  one jumped right up and snatched my eye,
They jumped from front, jumped up from the rear,
  one jumped right up and snatched my ear,
[Little by little I ran all out,
  the bunnies nibbled me parts away,]
But I for one welcome our overlords,
  their red fur shines in the mist.


[instrumental]


I'm sure they ate ten times their weight
  in human meat on that bloody day.
Yet the limb that's strumming the cords right now
  made it back to the pub somehow.
Who do I thank? Who sated the pack?
  I thank you Jimmy a.k.a. Humpback!
Anyway I for one welcome our overlords,
  their white fur shines in the mist.


LICENSE:
--------

This game is released under the GPL (version 3). Thanks for playing!
