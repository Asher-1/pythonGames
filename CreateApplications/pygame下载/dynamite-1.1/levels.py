import os

music1 = os.path.join("data","music","music1.ogg")
music2 = os.path.join("data","music","music2.ogg")

levels = [
(os.path.join("data","levels","l1.tga"),"T1","Training Level 1","""Left click to walk to the blue pilar. Right click to place the dynamite.  Walk safely away from the bomb. Right click to detonate the dynamite.  Walk to the window to escape.""",3,music1,90),
	
(os.path.join("data","levels","l2.tga"),"T2","Training Level 2","""Use arrow keys to peek around the level.  Place your dynamite anywhere.  Right click a second time to pick the dynamite up again.  Avoid the guard and place the dynamite by the pilar.  Hide by the pilar until you can walk away and detonate it.""",3,music2,90),

(os.path.join("data","levels","l3.tga"),"T3","Training Level 3","""Place dynamite by first pilar.  Use the passage to get to the other side of the level.  Detonate dynamite to distract the guards.  Place dynamite by second pilar.  Hide by a wall.  If a guard brushes you, he will shoot.  Detonate when guards return.""",3,music1,90),
	
(os.path.join("data","levels","phil2.tga"),"1","Level 1","the garden",3,music2,120),
(os.path.join("data","levels","real3.tga"),"2","Level 2","the hacienda",4,music1,120),
(os.path.join("data","levels","phil4.tga"),"3","Level 3","the mansion",5,music2,120),
(os.path.join("data","levels","real1.tga"),"4","Level 4","the fortress",2,music1,150),
(os.path.join("data","levels","phil5.tga"),"5","Level 5","the station",4,music2,150),
(os.path.join("data","levels","real2.tga"),"6","Level 6","the castle",4,music1,150),
(os.path.join("data","levels","phil1.tga"),"7","Level 7","the tower",4,music2,180),
(os.path.join("data","levels","phil3.tga"),"8","Level 8","the hall",4,music1,180),

(os.path.join("data","levels","level10.tga"),"9","Level 9","the plantation",12,music2,300),
(os.path.join("data","levels","level9.tga"),"10","Level 10","the stronghold",13,music1,480),
]