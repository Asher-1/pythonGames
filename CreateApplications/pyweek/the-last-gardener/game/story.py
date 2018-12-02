from __future__ import division, print_function, unicode_literals

# The 'cutscenes' are made up of a n-tuple of 2-tuples
# Each 2-tuple is like: ('text', 'file name of image to swap to.png')
# Images are 800x600, but be mindful that the bottom 100 pixels
# will be covered by the transparent text box
# tuple[1] can be None if you don't want to change the image
# Word wrap is done automatically

slides = {
    'intro': (
        ('Once upon a time, the world was peaceful. '
         'But one day, aliens invaded.', 'story_1.png'),
        ('Most of humanity perished in the initial assault. '
         'The survivors went into hiding. ', 'story_2.png'),
        ('You happen to be the last remaining gardener. '
         'Lawns still need to be mowed, and the human resistance '
         'has offered to pay for your services.', 'story_3.png'),
        ('You still need money, so you accept the offer.', None),
        ('Each day you send out a lawnmower drone '
         'with the sole purpose of mowing the lawn. '
         'Good luck!', 'story_4.png'),
        ('Arrow keys control your movement. '
         'Use the Shift key to focus and slow your speed. '
         'When focused, your hitbox is shown. '
         'The Escape key will pause the game.', 'tutorial_1.png'),
        ('Mowing the lawn is done automatically.'
         'Mow the required amount of the lawn to win, '
         'even if the drone gets destroyed or runs out of fuel. '
         'After all, the drones are expendable.' , 'tutorial_2.png'),
        ('Mow the entire lawn for a bonus! '
         'Make sure to avoid anything bad, however. '
         'Your drone can only take a few hits.' , None),
    ),
    'halfway': (
        ('Things are getting pretty harrowing out there. '
         'You considered quitting for a while, but you still '
         'need the money.', 'story_5.png'),
        ('Better get back to work now.', None),
    ),
    'finale': (
        ('The human resistance has asked you to mow the lawn of '
         'the UN building. Their members will be inside '
         'negotiating a peace treaty with the aliens.', 'story_6.png'),
        ('The building seems to be guarded by some sort of massive '
         'alien guardian. It will take your best '
         'gardening skills to mow this lawn.', 'story_7.png'),
    ),
    'ending': (
        ('After witnessing your gardening skills in practice at the UN, '
         'the aliens have asked you to become their worldwide gardener '
         'in exchange for peace on Earth. You accept.', 'story_8.png'),
        ('As you leave for your new home, you look back on the '
         'world you saved. They are grateful to you.', 'story_9.png'),
        ('' , 'story_10.png'), #Yes I'm aware this is stupidly hacky.
    ),
}
