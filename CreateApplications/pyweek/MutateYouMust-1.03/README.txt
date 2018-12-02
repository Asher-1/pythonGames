Mutate You Must!
===============

Entry in PyWeek #13  <http://www.pyweek.org/13/>
Team: ESIFOKS
Members: Archy, Blinkmann, HerzogIgzorn, Pumpenkarl


You might need to install some of these before running the game:

  Python 2.7 (Windows: 32Bit!) 	http://www.python.org/


RUNNING 

THE GAME:

On Windows or Mac OS X, locate the "run_game.pyw" file and double-click it.

Othewise open a terminal / console and "cd" to the game directory and run:

  python run_game.py

FULLSCREEN:
	To start in fullscreen start with -f
	
ON CRASH:
	The crashes we expirienced were mostly due to audio playback issues of pyglet on some Linux
	platforms. If this happens please try to deactivate sound effects by starting the game with -e .
	If this does not help please try -s to remove music too. Thanks!


STORY:
In a galaxy far far away lives an extremely brutal and martial race, the Siforps.
Just now, they discuss which planet they should annihilate next. 
The choices are "Kronox 3" and a planet called "Earth".

Wastl, an impatient but eager Siforp decides to go to war on his own. 

Grown up at the most degenerated and most brutal orphanage of his planet, 
he was adopted by an horrible family at the young age of 84 Siforp years.
Wastl condamned his new father because he was an alcohol addict and a waster.
His mother ate everything she could find, even his small food rations.

So the choice of his target planet was easy. On Earth he could find plenty of his objects of hate.
Equipped with a mutation beam, he decided to mutate the Earthlings, so they fight their own kind.




HOW TO PLAY THE GAME:

With "LEFT KLICK" you can mutate a building.
After mutating, creeps will spawn out of that bulding and make their way through the "HQ".
In every map you have a limited amount of mutations and every building can just spawn 1 creep.
The maximum mutation amount and the specific mutant, you need to win the level, is listed on 
the right side in the box. 


Tower and Building Overview:

HQ : This is the TARGET of your MUTANTS. Most HQs can only be captured by SPECIFIC MUTANTS.

ORPHANAGE: Two headed ORPHANS make their way through the defense lines. 
They are WEAK against GATLING BUNKERS and STRONG against TANKS. Other Mutants eat them to RESTORE their HEALTH
 
FAST FOOD RESTAURANT: Mutated FATSOS spawn here. Thay are WEAK against TANKS and STRONG against GATLING BUNKERS. 
They can CARRY ORPHANS, so they have their lunch always with them.

BEER GARDEN. This DRUNK mutants are EQUALLY RESISTANT to every tower. 
They puke while walking, which makes the mutants behind them FASTER.

TANK: This tower ist STRONG against FATSOS. WEAK against ORPHANS .

GATLING BUNKER: STRONG against ORPHANS. WEAK against FATSOS .

ARTILLERY: EFFECTIVE against ALL MUTANTS, HIGH RANGE.




LICENSE:

All code and graphics except pyglet are the original work of Julian Moschüring, Thomas Blickling and Robert Schrader. They're placed in the public domain.

The following sound files were created by Florian Jindra, they are distributed under a Creative Commons by Attribution license:
mutate_music.wav
win.wav
lose.wav
click_01.wav
click_02.wav
click_03.wav
fatso_eat_01.wav
fatso_eat_02.wav
fatso_eat_03.wav
fatso_eat_04.wav
fatso_eat_05.wav
orphan_die.wav
zonk.wav

all other sound files were downloaded from freesound.org and edited:
http://www.freesound.org/people/redjim/sounds/32579/
http://www.freesound.org/people/sagetyrtle/sounds/37226/
http://www.freesound.org/search/?q=fart&f=pack:%22Farting+Around%22&s=num_downloads+desc&advanced=0
http://www.freesound.org/search/?q=fart&f=pack:%22farts+and+burps%22&s=num_downloads+desc&advanced=0
http://www.freesound.org/people/andriala/sounds/21742/
http://www.freesound.org/people/shawshank73/sounds/81746/
http://www.freesound.org/people/sandyrb/sounds/35643/
http://www.freesound.org/people/shawshank73/sounds/81433/
http://www.freesound.org/people/kantouth/sounds/104401/
http://www.freesound.org/people/alienbomb/sounds/39071/
http://www.freesound.org/people/Matt_G/sounds/30749/
http://www.freesound.org/people/soundscalpel.com/sounds/110622/

The font file used for the title, AddElectricCity.ttf, was created by Atsushi Aoki(aoki@add.jp.org). It's distributed as Freeware, and is available here:
http://www.urbanfonts.com/fonts/Add_Electric_City.htm

-------------------PyGlet


Copyright (c) 2006-2008 Alex Holkner
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

  * Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
  * Redistributions in binary form must reproduce the above copyright 
    notice, this list of conditions and the following disclaimer in
    the documentation and/or other materials provided with the
    distribution.
  * Neither the name of pyglet nor the names of its
    contributors may be used to endorse or promote products
    derived from this software without specific prior written
    permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
