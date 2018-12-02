import serge.blocks.themes

theme = serge.blocks.themes.Manager()
theme.load({
    'main' : ('', {
    
     # Properties of the bat
	 'bat-size' : (20, 100),
	 'bat-initial-position' : (150, 100),
	 'bat-colour' : (0, 0, 255),
	 'ball-mass' : 10,
	 'bat-speed': 10,

	 # Properties of the ball
	 'ball-radius' : 20,
	 'ball-initial-position' : (250, 100),
	 'ball-colour' : (255, 255, 255),
     'ball-initial-velocity' : (500.0, 0.0),
    
     # Gravity
     'gravity-x' : 0.0,
     'gravity-y' : 9800.0,
     
     # Walls etc
     'floor-size' : (600, 20),
     'floor-position' : (325, 420),
     'floor-colour' : (255, 0, 0),
     'ceiling-size' : (600, 20),
     'ceiling-position' : (325, 40),
     'ceiling-colour' : (255, 0, 0),
     'wall-size' : (20, 360),
     'wall-l-position' : (35, 230),
     'wall-r-position' : (615, 230),
     'wall-colour' : (255, 0, 0),
     
     # AI
     'ai-bat-initial-position' : (450, 250),
     'ai-bat-speed' : 5,
     'ai-bat-avoid-distance' : 100,
     'ai-bat-return-distance': 100,
     
     # Sound 
     'sound-max-velocity' : 1200.0,
    }),
    
    '__default__' : 'main',

})

get = theme.getProperty
