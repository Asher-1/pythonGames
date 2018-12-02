class Level( object ):
    # defaults
    balls = 2
    head_pos = (320,50)

    goals_pos = [ (150,300), (490,300) ]
    goals_forces = [ (0,0), (0,0) ]
    goals = len( goals_pos )
    gravity = (0,0)

    time = 50

    title = "NO TITLE"

class LevelTut( Level ):
    balls = 4

    head_pos = (250,100)

    goals_pos = [ (500,100) ]
    goals_forces = [ (0,0) ]
    goals = len( goals_pos )
    gravity = (0,0)

    title = "Tutorial"

class Level0( Level ):
    balls = 2

    gravity = (0,0)
    goals_pos = [ (50,30), (600,30) ]
    goals_forces = [ (0,0), (0,0) ]
    goals = len( goals_pos )

    title = "No Love"


class Level1( Level ):
    balls = 2
    head_pos = (320,50)

    goals_pos = [ (150,300), (490,300) ]
    goals_forces = [ (0,0), (0,0)]
    goals = len( goals_pos )

    title = "Gong love"


class Level2( Level ):
    balls = 2
    head_pos = (320,50)

    goals_pos = [ (20,420), (620,20) ]
    goals_forces = [ (0,0), (0,0) ]
    goals = len( goals_pos )

    title = "Shy Love"


class Level3( Level ):
    balls = 2
    head_pos = (320,400)

    goals_pos = [ (150,300), (180,350) ]
    goals_forces = [ (0,0), (0,0) ]
    goals = len( goals_pos )
    gravity = (0,-30)

    title = "Fall in Love"

class LevelKisses( Level ):
    balls = 2
    head_pos = (320,50)

    goals_pos = [ (150,300), (490,300) ]
    goals_forces = [ (250,0), (-250,0) ]
    goals = len( goals_pos )

    title = "Kisses"


class LevelTantric( Level ):
    balls = 2
    head_pos = (320,50)

    goals_pos = [ (150,150), (490,150) ]
    goals_forces = [ (25,0), (-25,0) ]
    goals = len( goals_pos )

    title = "Tantric Love"


class Level5( Level ):
    balls = 8
    head_pos = (280,50)
    gravity = (0,-10)

    goals_pos = [ (640/2,480/2) ]
    goals_forces = [ (0,0) ]
    goals = len( goals_pos )

    title = "Pregnant"

class LevelMenage( Level ):
    balls = 2
    head_pos = (320,50)

    goals_pos = [ (640/2-75,200), (640/2+75,200), (640/2,200 + 150*0.866) ]
    goals_forces = [ (86,50), (-86,50), (0,-100), ]
#    goals_forces = [ (0,0), (0,0), (0,0), ]
    goals = len( goals_pos )

    title = "Menage a 3"

class Level6( Level ):
    balls = 8
    head_pos = (280,100)

    gravity = (0,-15)
    goals_pos = [ (320,340), (320,400) ]
    goals_forces = [ (0,0), (0,0) ]
    goals = len( goals_pos )

    title = "Twins" 


class LevelSwingers( Level ):
    balls = 2
    head_pos = (320,50)

    goals_pos = [ (150,300), (490,300), (640/2,250), (640/2,350) ]
    goals_forces = [ (250,0), (-250,0), (0,250), (0,-250) ]
    goals = len( goals_pos )

    title = "Swingers"

class LevelLong( Level ):
    balls = 7
    head_pos = (320,50)

    goals_pos = [ (320,240) ]
    goals_forces = [ (0,0) ]
    goals = len( goals_pos )

    title = "Solo Love"

class LevelColumn( Level ):
    balls = 2
    head_pos = (320,50)

    goals_pos = [ (150,150), (149,200), (148,250), (147,300)]
    goals_forces = [ (0,-160), (0,-160), (0,-160), (0,-160)]
    goals = len( goals_pos )

    title = "Tandem Love"

class LevelMachine( Level ):
    balls = 2
    head_pos = (320,50)

    goals_pos = [ (300,240), (340,240), (640/2,240) ]
    goals_forces = [ (-1600,0), (1800,0), (0,2000) ]
    goals = len( goals_pos )

    title = "Rejected Love"

class LevelPussy( Level ):
    balls = 2
    head_pos = (320,50)
    time=70

    goals_pos = [ (150,150), (170,200), (130,200), (110,250), (190,250)]
    goals_forces = [ (0,-100), (0,-100), (0,-100), (0,-100), (0,-100)]
    goals = len( goals_pos )

    title = "Pussy Love"

class LevelOrgy( Level ):
    time = 60
    balls = 2
    head_pos = (320,50)

    goals_pos = [ (150,300), (490,300), (640/2,150), (640/2,400), (150,250), (490,250) ]
    goals_forces = [ (250,0), (-250,0), (0,250), (0,-250), (250,0),(-250,0) ]
    goals = len( goals_pos )

    title = "Orgy"

class LevelWorm( Level ):
    time = 60
    balls = 2
    head_pos = (500,400)

    gravity = (0,-100)

    goals_pos = [ (150,400), (200,400), (250,400), (300,400), (350,400)]
    goals_forces = [ (0,-100), (0,-200), (0,-300), (0,-400), (0,-500)]
    goals = len( goals_pos )

    title = "Worm Love"


class LevelLove( Level ):
    balls = 2
    head_pos = (320,264)
    time=90

    goals_pos = [ (640/2-75,200), (640/2+75,200), (640/2,200 + 150*0.866), (640/2-75,200+150*0.866), (640/2+75,200+150*0.866), (640/2,200) ]
    goals_forces = [ (86,50), (-86,50), (0,-100), (86,-50), (-86,-50), (0,100), ]
#    goals_forces = [ (0,0), (0,0), (0,0), ]
    goals = len( goals_pos )

    title = "Dunga Dunga"


levels = [ LevelTut, Level0, Level1, Level2, Level3, LevelKisses, LevelTantric, Level5, LevelMenage, LevelMachine, Level6, LevelSwingers, LevelLong, LevelColumn, LevelWorm, LevelPussy, LevelOrgy, LevelLove ]
