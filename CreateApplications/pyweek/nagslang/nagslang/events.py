"""Events to post."""

import pygame
import pygame.locals


class Event(object):
    TYPE = None

    @classmethod
    def post(cls, **data):
        ev = pygame.event.Event(cls.TYPE, **data)
        pygame.event.post(ev)

    @classmethod
    def matches(cls, ev):
        return ev.type == cls.TYPE


class QuitEvent(Event):
    TYPE = pygame.locals.QUIT


class UserEvent(Event):
    TYPE = pygame.locals.USEREVENT

    @classmethod
    def post(cls, **data):
        super(UserEvent, cls).post(user_type=cls.__name__, **data)

    @classmethod
    def matches(cls, ev):
        return (super(UserEvent, cls).matches(ev)
                and ev.user_type == cls.__name__)


class ScreenChange(UserEvent):
    @classmethod
    def post(cls, new_screen, player=None):
        super(ScreenChange, cls).post(screen=new_screen)


class DeathEvent(UserEvent):
    @classmethod
    def post(cls):
        super(DeathEvent, cls).post()


class DoorEvent(UserEvent):
    @classmethod
    def post(cls, destination, dest_pos):
        super(DoorEvent, cls).post(destination=destination, dest_pos=dest_pos)


class AddDrawableEvent(UserEvent):
    '''When you are in a corner and can't return a Result'''
    @classmethod
    def post(cls, drawable):
        super(AddDrawableEvent, cls).post(drawable=drawable)
