The Serge engine.





What's New
==========

0.2.3
    New SurfaceDrawing class in serge.visual - helps with creating custom visual elements
    New attribute "update_angle" causes physics engine angles to propagate to the actor when set to True (default=False)
    Fixed bug in block.visual.Circle and CircleText where it was drawn at the incorrect location
    Added parameter visual_size to PhysicalConditions which causes size to match the actor's visual size
    Added block for implementing behaviours
    Added Font handling
    Added Global Sound and Music handling
    Added ability to specify a stroke width and colour for rectangle and circle blocks
    Added Mountable actors
    Added ActorCollections
    Added Music Play-lists
0.2.4
    Adding actor to composite actors is ok if the actor is already in the world    
    Removing child from composite actor can leave in the world
    Added global event broadcasting system
    Added fadeout for music
    Added scheduled actor removal from the world
    Added visible property for actors
    Behaviours can now return B_COMPLETE to pause themselves
    Theme can now be updated from a string
    Added ProgressBar visualblock
    Added ParallaxMotion behaviour
0.2.5
    Added Screenshot behaviour
    Behavior manager can now register all events in a module
    Can register multiple sprites from single tile-set
    Transparency works properly now for Rectangles and Circles
    Fixed bug with size of actor not updating after zooming
    Sprites can be registered by file pattern 
    Rotations now use filtering for improved quality
    Added MovieMaker util to help recording game-play
    Support rotation of Mounted Actors without pymunk
0.2.6
    Added MuteButton and utility to add to many worlds
    Added ability to clear actors with a tag from a world
    Added ToggledMenu block
    Fixed bug in SimpleVecs when you change a vector length
    Incorporated pymunk vec2d implementation
0.3
    Significantly extended the game created by the createGame utility. Includes help, credits and start screens
    Added block to track and report achievements
0.3.1
    Simplified template game with new text utilities
    Implemented conversation system
    Fixed issues with camera system
    Added block to interface to Tiled files
    Added block to darken a surface
0.3.2
    Added setSize method to directly set the size of a drawing
    Added a block for animate and then die actors
0.3.3
    Added a parameter in common to set the number of pygame audio channels to use
    Added behaviour to remove an actor when it is out of range
    Added behaviour to move an actor with a constant velocity
0.3.4
    Added duplicateItem method to registry to allow creation of aliased items
    Implemented a drag-n-drop block to help with drag and drop operations
    Added a finite state machine block
    forEach iteration can now work with setting attributes as well as method calls
    Added a spring towards point behaviour
    Added a behaviour sequence to control behaviours that run in sequences
    Generalized the tiled block to allow it to be used for general tile maps
    Implemented a block to help with fractal lines and shapes
    Implemented a block to help with running time intensive operations asynchronously 
    The number of physics steps used by pymunk can now be configured
    Fixed issue with animated sprites not advancing properly if the framerate of the animation was high
0.3.5
    Zones can now implement wouldContain to select actors based on certain criteria
    Improved text entry widget
    Keyboard now includes additional methods to help deal with entering text
    Added an L-system block to be used to generate plants, vegetation etc
0.4 
    First stand-alone release of the engine
    Includes documentation and two tutorials
0.4.1
    Fixed bug in MuteButton - would always mute music regardless of the flag setting
    Fixed bug in Sound - pause/un-pause behaviour was not working properly for sounds (ok for music)
    Added SoundTexture block to create sounds textures that depend on the location of actors etc
    Allowing converting alpha mode of sprites to drastically improve blitting
    Added profiler for collecting detailed timing from the engine
    Fixed bug when rendering multiple lines of text. Longest line was not always recognized resulting in cutoff
    Added FPS display to template game
    Added -S option to template game to go straight to the main screen, bypassing the start screen
    Added engine version number to credits screen on template game
0.4.2
    Added SimplePhysicsActor to blocks
    Added PolygonVisual as a visual element to handle polygon shapes
    Documented fysom finite state machine block
    Renderer can now return rendering order of its layers
    Mouse events now fire in the order of topmost layer first
    Backwards incompatibility: Static layers no longer fire first in the event order. Use layer orders instead.
    Added installDebugHook to serge.common. If you call this then the game will drop into pdb when an unhandled error occurs
    Added TextGenerator block to allow generation of randomized text
    ToggledMenu now sets layer properly for menu items
0.4.3
    Tiled layer now supports getLocationsWithSpriteName to find specific sprites on a layer
    Tiled object layers now support getting width and height from polygon objects
    Added new Storage block to handle SQL storage of game data
0.5
    Added online high score table block
    Added concurrent futures implementation (from Python 3)
    Added hasItem method to Registry
    AchievementsManager can reset the achievements
    Fixed bug in AchievementsGrid layers
    Implemented Font caching via Fonts.getFont to fix OSX pygame issue
    VerticalBar and HorizontalBar blocks can now specify item_width / height to fill from left / top
    Can set the icon file for the engine to a be a path name
    Template game: use file for icon
    Template game: start engine early to allow convert_alpha to work for
    Template game: incorporate option to record movie of game
    Template game: added font registration
    Template game: add file to music and screenshots folders to prevent errors when packaging
    Template game: use variable for screen width and height in theme
    Added Cellular Automaton block
0.5.1
    Added ability to set sprites at a location in a tiled layer
    Fixed networkx version number check
    Added BidirectionalDict as a utility class
    Added KeyboardBackWorld as behaviour and made template game use this
    Added constraints to drag and drop behaviour
0.5.2
    Fixed some issues with key handling on OSX for TextEntryWidget
    FocusManager now emits got-focus and lost-focus events
    ToggledMenu now supports mouse over colour
0.5.3
    Focus manager has resetFocus method to help when actors become inactive
    ToggleMenu can now change the options after initially created
    Added method to Renderer to return the background layer
    Added a MarkovNameGenerator block to generate names from Markov chains and examples
0.5.4
    Added packager tool to package up completed games into convenient distribution
    LoadingScreen can now include an icon as well as text
0.5.5
    Allow reloading of conversation file from textgen tool
    Added Timer actor block
    Allow stopping engine without processing events
    Text visual now supports fixed character width setting
    Added movement tween animation block
0.5.6
    Added a rule system for generating context sensitive text (textgenerator block)
    Added engine method (engine.getTimeSinceStart) to get the time since the start of the game
0.5.7
    Added playSequence method to Sound object to play sequence of sounds
    Added SequenceTimer and SequenceIntervalTimer blocks