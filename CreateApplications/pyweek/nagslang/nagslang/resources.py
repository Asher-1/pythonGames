import os
import sys

try:
    from pkg_resources import resource_filename
except ImportError:
    # OK, we're most likely running under py2exe, so this is safe
    # (for values of safe that are unconcerned about py2exe being involved)
    def resource_filename(mod, path):
        # There are better ways of doing this, but I've spent too much
        # time going down this rabbithole already
        return os.path.join(os.path.dirname(__file__), '..', 'data', path)
import pygame


class ResourceNotFound(Exception):
    pass


class Resources(object):
    CONVERT_ALPHA = True

    def __init__(self, resource_module, language=None):
        self.resource_module = resource_module
        self.lang_dialect = language
        self.language = language.split('_', 1)[0] if language else None
        self._cache = {}

    def create_resource_path(self, *path_fragments):
        return resource_filename(self.resource_module,
                                 os.path.join(*path_fragments))

    def get_resource_path(self, *path_fragments):
        for mod, full_path_fragments in self.lang_locations(path_fragments):
            path = resource_filename(mod, os.path.join(*full_path_fragments))
            if os.path.exists(path):
                return path
        raise ResourceNotFound(os.path.join(*path_fragments))

    def lang_locations(self, path_fragments):
        '''
        For each resource module, yield:
        * (<module>, (<lang>_<dialect>, <path>))
        * (<module>, (<lang>, <path>))
        * (<module>, (<path>, ))
        '''
        for module in (self.resource_module,):
            if self.lang_dialect:
                yield (module, (self.lang_dialect,) + path_fragments)
            if self.language != self.lang_dialect:
                yield (module, (self.language,) + path_fragments)
            yield (module, path_fragments)

    def get_file(self, *path_fragments, **kw):
        mode = kw.get('mode', "rU")
        try:
            path = self.get_resource_path(*path_fragments)
        except ResourceNotFound:
            if 'w' in mode:
                path = self.create_resource_path(*path_fragments)
            else:
                raise
        return file(path, mode)

    def get_image(self, *name_fragments, **kw):
        transforms = kw.get('transforms', ())
        basedir = kw.get('basedir', 'images')

        path = (basedir,) + name_fragments

        if path not in self._cache:
            fn = self.get_resource_path(*path)
            image = pygame.image.load(fn)
            if self.CONVERT_ALPHA:
                if not pygame.display.get_init():
                    print >> sys.stderr, ("Display not initialized, "
                                          "image '%s' not loaded."
                                          % os.path.join(*path))
                    return
                image = image.convert_alpha(pygame.display.get_surface())
            self._cache[path] = image

        key = (path, transforms)
        if key not in self._cache:
            image = self._cache[path]
            for mutator in transforms:
                image = mutator(image)
            self._cache[key] = image

        return self._cache[key]

    def get_font(self, file_name, font_size):
        basedir = 'fonts'
        key = (basedir, file_name, font_size)

        if key not in self._cache:
            fn = self.get_resource_path(basedir, file_name)
            self._cache[key] = pygame.font.Font(fn, font_size)

        return self._cache[key]


resources = Resources('data')
