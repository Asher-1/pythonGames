#!/usr/bin/env python


import math
import os
import re
from gimpfu import *


def python_export(timg, tdrawable, export_path, export_type, visible_only, unpack_groups, autocrop):
    if export_type == 1:
        # Export Layer
        export_layer(export_path, tdrawable.name, timg, tdrawable, autocrop)
    elif export_type == 2:
        # Export All Layers
        if not unpack_groups:
            layers = timg.layers
        else:
            layers = unpack_layers_from(timg, visible_only)
        #
        for layer in layers:
            if not visible_only or layer.visible:
                export_layer(export_path, layer.name, timg, layer, autocrop)
        #
    elif export_type == 0:
        duplicate = timg.duplicate()
        duplicate.flatten()
        export_layer(export_path, os.path.splitext(timg.name)[0], duplicate, duplicate.layers[0], autocrop)
    elif export_type == 3:
        automatic_export(timg, export_path, timg)
    else:
        pdb.gimp_message('Unknown export type: "%s"' % export_type)


def export_layer(root_path, name, img, layer, autocrop):
    """Export a layer"""
    name = '%s.png' % name
    filename = os.path.join(root_path, name)
    #
    if autocrop:
        img, layer = get_new_image_from_layer(img, layer)
        pdb.plug_in_autocrop(img, layer)
    #
    pdb.file_png_save(img, layer, filename, os.path.split(filename)[1], 0, 9, 1, 1, 1, 1, 1)


def get_new_image_from_layer(image, layer):
    """Return a new image and layer which is only the selected layer"""
    pdb.gimp_edit_copy(layer)
    new_image = pdb.gimp_edit_paste_as_new()
    #
    return new_image, new_image.layers[0]


def unpack_layers_from(timg, visible_only):
    """Return all the layers in the image"""
    layers = []
    for layer in timg.layers:
        if not visible_only or layer.visible:
            if not is_group(layer):
                layers.append(layer)
            else:
                layers.extend(unpack_layers_from(layer, visible_only))
    #
    return layers


def automatic_export(image, export_path, base_image):
    """Automatically export based on the names of the layers"""
    for layer in image.layers:
        name, tags = get_tags_from_name(layer.name)
        export = 'export' in tags
        autocrop = 'autocrop' in tags
        if 'relativepath' in tags:
            if len(tags) != 2:
                raise ValueError('No path in relativepath tag')
            else:
                export_path = os.path.join(os.path.split(base_image.filename)[0], tags[1])
        if export:
            export_layer(export_path, name, base_image, layer, autocrop)
        if is_group(layer):
            automatic_export(layer, export_path, base_image)


def is_group(layer):
    """Return True if the layer is a group"""
    return hasattr(layer, 'layers')


def get_tags_from_name(name):
    """Return the tags from a name"""
    match = re.match('(\S+)(\s*\{(.*?)\})?', name)
    if not match:
        raise ValueError('Could not determine name from layer name "%s"' % name)
    name = match.groups()[0]
    tags = [] if not match.groups()[2] else [item.strip() for item in match.groups()[2].split(',')]
    return name, tags


register(
        "Serge_Image_Export",
        "Export the current image, or parts of it, as graphics",
        "Export the current image, or parts of it, as graphics",
        "Paul Paterson",
        "Paul Paterson",
        "2016",
        "<Image>/File/Serge Export...",
        "RGB*, GRAY*",
        [
            (PF_DIRNAME, "export_path", "Export Path", 0),
            (PF_RADIO, "export_type", "Export Type", 0, (
                ("Current Layer", 1), ("All Layers", 2), ("Image", 0), ("Automatic", 3),
             )),
            (PF_BOOL, "visible_only", "Visible only", 1),
            (PF_BOOL, "unpack_groups", "Unpack groups", 0),
            (PF_BOOL, "autocrop", "Auto crop layers", 0),
        ],
        [],
        python_export)

main()