# -*- coding: utf-8 -*-
#Copyright (c) 2012, Walter Bender
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import gtk
from time import time
import os

from gettext import gettext as _

from plugins.plugin import Plugin
from TurtleArt.tapalette import make_palette, define_logo_function
from TurtleArt.talogo import primitive_dictionary, logoerror, \
    media_blocks_dictionary
from TurtleArt.taconstants import DEFAULT_SCALE, ICON_SIZE, CONSTANTS, \
    MEDIA_SHAPES, SKIN_PATHS, BLOCKS_WITH_SKIN, PYTHON_SKIN, \
    PREFIX_DICTIONARY, VOICES
from TurtleArt.tautils import convert, round_int, debug_output, get_path, \
    data_to_string
from TurtleArt.tajail import myfunc, myfunc_import


def _num_type(x):
    """ Is x a number type? """
    if type(x) == int:
        return True
    if type(x) == float:
        return True
    if type(x) == ord:
        return True
    return False


def _string_to_num(x):
    """ Try to comvert a string to a number """
    xx = convert(x.replace(self.tw.decimal_point, '.'), float)
    if type(xx) is float:
        return xx
    else:
        xx, xflag = chr_to_ord(x)
        if xflag:
            return xx
        else:
            raise logoerror("#syntaxerror")


def _millisecond():
    """ Current time in milliseconds """
    return time() * 1000


class Turtle_blocks_extras(Plugin):
    """ a class for defining the extra palettes that distinguish Turtle Blocks
    from Turtle Art """

    def __init__(self, parent):
        self.tw = parent

    def setup(self):
        SKIN_PATHS.append('plugins/turtle_blocks_extras/images')

        self.heap = self.tw.lc.heap
        self.keyboard = self.tw.lc.keyboard
        self.title_height = int((self.tw.canvas.height / 20) * self.tw.scale)

        # set up Turtle Block palettes
        self._flow_palette()

        self._media_palette()

        self._sensor_palette()

        self._extras_palette()

        self._portfolio_palette()

    # Palette definitions

    def _flow_palette(self):
        palette = make_palette('flow',
                               colors=["#FFC000", "#A08000"],
                               help_string=_('Palette of flow operators'))

        # internally expanded macro
        palette.add_block('while',
                          style='clamp-style-boolean',
                          label=_('while'),
                          prim_name='while',
                          default=[None, None, None],
                          special_name=_('while'),
                          help_string=_('do-while-True operator that uses \
boolean operators from Numbers palette'))

        # internally expanded macro
        palette.add_block('until', 
                          style='clamp-style-boolean',
                          label=_('until'),
                          prim_name='until',
                          default=[None, None, None],
                          special_name=_('until'),
                          help_string=_('do-until-True operator that uses \
boolean operators from Numbers palette'))

    def _media_palette(self):

        palette = make_palette('media',
                               colors=["#A0FF00", "#80A000"],
                               help_string=_('Palette of media objects'),
                               position=7)

        palette.add_block('journal',
                          style='box-style-media',
                          label=' ',
                          default='None',
                          special_name=_('journal'),
                          help_string=_('Sugar Journal media object'))
        PREFIX_DICTIONARY['journal'] = '#smedia_'
        BLOCKS_WITH_SKIN.append('journal')
        MEDIA_SHAPES.append('journalsmall')
        MEDIA_SHAPES.append('journaloff')
        MEDIA_SHAPES.append('journalon')

        palette.add_block('audio',
                          style='box-style-media',
                          label=' ',
                          special_name=_('audio'),
                          default='None',
                          help_string=_('Sugar Journal audio object'))
        BLOCKS_WITH_SKIN.append('audio')
        PREFIX_DICTIONARY['audio'] = '#saudio_'
        MEDIA_SHAPES.append('audiosmall')
        MEDIA_SHAPES.append('audiooff')
        MEDIA_SHAPES.append('audioon')

        palette.add_block('video',
                          style='box-style-media',
                          label=' ',
                          special_name=_('video'),
                          default='None',
                          help_string=_('Sugar Journal video object'))
        BLOCKS_WITH_SKIN.append('video')
        PREFIX_DICTIONARY['video'] = '#svideo_'
        MEDIA_SHAPES.append('videosmall')
        MEDIA_SHAPES.append('videooff')
        MEDIA_SHAPES.append('videoon')

        palette.add_block('description',
                          style='box-style-media',
                          label=' ',
                          special_name=_('description'),
                          default='None',
                          help_string=_('Sugar Journal description field'))
        BLOCKS_WITH_SKIN.append('description')
        PREFIX_DICTIONARY['description'] = '#sdescr_'
        MEDIA_SHAPES.append('descriptionsmall')
        MEDIA_SHAPES.append('descriptionoff')
        MEDIA_SHAPES.append('descriptionon')

        palette.add_block('string',
                          style='box-style',
                          label=_('text'),
                          default=_('text'),
                          special_name=_('text'),
                          help_string=_('string value'))

        primitive_dictionary['show'] = self._prim_show
        palette.add_block('show',
                          style='basic-style-1arg',
                          label=_('show'),
                          default=_('text'),
                          prim_name='show',
                          logo_command='label',
                          help_string=_('draws text or show media from the \
Journal'))
        self.tw.lc.def_prim('show', 1,
            lambda self, x: primitive_dictionary['show'](x, True))

        palette.add_block('showaligned',
                          hidden=True,
                          colors=["#A0FF00", "#80A000"],
                          style='basic-style-1arg',
                          label=_('show aligned'),
                          default=_('text'),
                          prim_name='showaligned',
                          logo_command='label',
                          help_string=_('draws text or show media from the \
Journal'))
        self.tw.lc.def_prim('showaligned', 1,
            lambda self, x: primitive_dictionary['show'](x, False))

        # deprecated
        primitive_dictionary['write'] = self._prim_write
        palette.add_block('write',
                          hidden=True,
                          colors=["#A0FF00", "#80A000"],
                          style='basic-style-1arg',
                          label=_('show'),
                          default=[_('text'), 32],
                          prim_name='write',
                          logo_command='label',
                          help_string=_('draws text or show media from the \
Journal'))
        self.tw.lc.def_prim('write', 2,
            lambda self, x, y: primitive_dictionary['write'](x, y))

        primitive_dictionary['setscale'] = self._prim_setscale
        palette.add_block('setscale',
                          style='basic-style-1arg',
                          label=_('set scale'),
                          prim_name='setscale',
                          default=33,
                          logo_command='setlabelheight',
                          help_string=_('sets the scale of media'))
        self.tw.lc.def_prim('setscale', 1,
            lambda self, x: primitive_dictionary['setscale'](x))

        primitive_dictionary['savepix'] = self._prim_save_picture
        palette.add_block('savepix',
                          style='basic-style-1arg',
                          label=_('save picture'),
                          prim_name='savepix',
                          default=_('picture name'),
                          help_string=_('saves a picture to the Sugar \
Journal'))
        self.tw.lc.def_prim('savepix', 1,
                            lambda self, x: primitive_dictionary['savepix'](x))

        primitive_dictionary['savesvg'] = self._prim_save_svg
        palette.add_block('savesvg',
                          style='basic-style-1arg',
                          label=_('save SVG'),
                          prim_name='savesvg',
                          default=_('picture name'),
                          help_string=_('saves turtle graphics as an SVG file \
in the Sugar Journal'))
        self.tw.lc.def_prim('savesvg', 1,
                            lambda self, x: primitive_dictionary['savesvg'](x))

        palette.add_block('scale',
                          style='box-style',
                          label=_('scale'),
                          prim_name='scale',
                          value_block=True,
                          logo_command='labelsize',
                          help_string=_('holds current scale value'))
        self.tw.lc.def_prim('scale', 0, lambda self: self.tw.lc.scale)

        palette.add_block('mediawait',
                          style='basic-style-extended-vertical',
                          label=_('media wait'),
                          prim_name='mediawait',
                          help_string=_('wait for current video or audio to \
complete'))
        self.tw.lc.def_prim('mediawait', 0, self.tw.lc.media_wait, True)

        palette.add_block('mediastop',
                          style='basic-style-extended-vertical',
                          label=_('media stop'),
                          prim_name='mediastop',
                          help_string=_('stop video or audio'))
        self.tw.lc.def_prim('mediastop', 0, self.tw.lc.media_stop, True)

        palette.add_block('mediapause',
                          style='basic-style-extended-vertical',
                          label=_('media pause'),
                          prim_name='mediapause',
                          help_string=_('pause video or audio'))
        self.tw.lc.def_prim('mediapause', 0, self.tw.lc.media_pause, True)

        palette.add_block('mediaplay',
                          style='basic-style-extended-vertical',
                          label=_('media resume'),
                          prim_name='mediaplay',
                          help_string=_('resume playing video or audio'))
        self.tw.lc.def_prim('mediaplay', 0, self.tw.lc.media_play, True)

        primitive_dictionary['speak'] = self._prim_speak
        palette.add_block('speak',
                          style='basic-style-1arg',
                          label=_('speak'),
                          prim_name='speak',
                          default=_('hello'),
                          help_string=_('speaks text'))
        self.tw.lc.def_prim('speak', 1,
                            lambda self, x: primitive_dictionary['speak'](x))

        primitive_dictionary['sinewave'] = self._prim_sinewave
        palette.add_block('sinewave',
                          style='basic-style-3arg',
                          # TRANS: pitch, duration, amplitude
                          label=[_('sinewave'), _('pitch'), _('duration'), ''],
                          prim_name='sinewave',
                          default=[1000, 5000, 1],
                          help_string=_('plays a sinewave at frequency, \
amplitude, and duration (in seconds)'))
        self.tw.lc.def_prim('sinewave', 3,
                            lambda self,
                            x, y, z: primitive_dictionary['sinewave'](x, y, z))

    def _sensor_palette(self):

        palette = make_palette('sensor',
                               colors=["#FF6060", "#A06060"],
                               help_string=_('Palette of sensor blocks'),
                               position=6)

        primitive_dictionary['mousebutton'] = self._prim_mouse_button
        palette.add_block('mousebutton',
                          style='box-style',
                          label=_('button down'),
                          prim_name='mousebutton',
                          value_block=True,
                          help_string=_('returns 1 if mouse button is \
pressed'))
        self.tw.lc.def_prim('mousebutton', 0,
                            lambda self: primitive_dictionary['mousebutton']())

        palette.add_block('mousex',
                          style='box-style',
                          label=_('mouse x'),
                          prim_name='mousex',
                          value_block=True,
                          help_string=_('returns mouse x coordinate'))
        self.tw.lc.def_prim('mousex', 0,
                            lambda self: self.tw.mouse_x - (
                self.tw.canvas.width / 2))

        palette.add_block('mousey',
                          style='box-style',
                          label=_('mouse y'),
                          prim_name='mousey',
                          value_block=True,
                          help_string=_('returns mouse y coordinate'))
        self.tw.lc.def_prim('mousey', 0,
                            lambda self: (
                self.tw.canvas.height / 2) - self.tw.mouse_y)

        primitive_dictionary['kbinput'] = self._prim_kbinput
        palette.add_block('kbinput',
                          style='basic-style-extended-vertical',
                          label=_('query keyboard'),
                          prim_name='kbinput',
                          help_string=_('query for keyboard input (results \
stored in keyboard block)'))
        self.tw.lc.def_prim('kbinput', 0,
                            lambda self: primitive_dictionary['kbinput']())

        palette.add_block('keyboard',
                          style='box-style',
                          label=_('keyboard'),
                          prim_name='keyboard',
                          value_block=True,
                          logo_command='make "keyboard readchar',
                          help_string=_('holds results of query-keyboard \
block as ASCII'))
        self.tw.lc.def_prim('keyboard', 0, lambda self: self.tw.lc.keyboard)

        '''
        palette.add_block('keyboard_chr',
                          style='box-style',
                          label='chr(%s)' % (_('keyboard')),
                          prim_name='keyboard_chr',
                          value_block=True,
                          logo_command='make "keyboard readchar',
                          help_string=_('holds results of query-keyboard \
block as character'))
        self.tw.lc.def_prim('keyboard_chr', 0,
                            lambda self: chr(self.tw.lc.keyboard))

        primitive_dictionary['keyboardnum'] = self._prim_keyboard_num
        palette.add_block('keyboard_num',
                          style='box-style',
                          label='num(%s)' % (_('keyboard')),
                          prim_name='keyboard_num',
                          value_block=True,
                          logo_command='make "keyboard readchar',
                          help_string=_('holds results of query-keyboard \
block as number'))
        self.tw.lc.def_prim('keyboard_num', 0,
                            lambda self: primitive_dictionary['keyboardnum']())
        '''

        primitive_dictionary['readpixel'] = self._prim_readpixel
        palette.add_block('readpixel',
                          style='basic-style-extended-vertical',
                          label=_('read pixel'),
                          prim_name='readpixel',
                          logo_command=':keyboard',
                          help_string=_('RGB color under the turtle is pushed \
to the stack'))
        self.tw.lc.def_prim('readpixel', 0,
                            lambda self: primitive_dictionary['readpixel']())

        primitive_dictionary['see'] = self._prim_see
        palette.add_block('see',
                          style='box-style',
                          label=_('turtle sees'),
                          prim_name='see',
                          help_string=_('returns the color that the turtle \
"sees"'))
        self.tw.lc.def_prim('see', 0,
                            lambda self: primitive_dictionary['see']())

        primitive_dictionary['time'] = self._prim_time
        palette.add_block('time',
                          style='box-style',
                          label=_('time'),
                          prim_name='time',
                          value_block=True,
                          help_string=_('elapsed time (in seconds) since \
program started'))
        self.tw.lc.def_prim('time', 0,
                            lambda self: primitive_dictionary['time']())

    def _extras_palette(self):

        palette = make_palette('extras',
                               colors=["#FF0000", "#A00000"],
                               help_string=_('Palette of extra options'),
                               position=8)

        primitive_dictionary['push'] = self._prim_push
        palette.add_block('push',
                          style='basic-style-1arg',
                          #TRANS: push adds a new item to the program stack
                          label=_('push'),
                          prim_name='push',
                          logo_command='tapush',
                          help_string=_('pushes value onto FILO (first-in \
last-out heap)'))
        self.tw.lc.def_prim('push', 1,
                            lambda self, x: primitive_dictionary['push'](x))
        define_logo_function('tapush', 'to tapush :foo\rmake "taheap fput \
:foo :taheap\rend\rmake "taheap []\r')

        primitive_dictionary['printheap'] = self._prim_printheap
        palette.add_block('printheap',
                          style='basic-style-extended-vertical',
                          label=_('show heap'),
                          prim_name='printheap',
                          logo_command='taprintheap',
                          help_string=_('shows values in FILO (first-in \
last-out heap)'))
        self.tw.lc.def_prim('printheap', 0,
                            lambda self: primitive_dictionary['printheap']())
        define_logo_function('taprintheap', 'to taprintheap \rprint :taheap\r\
end\r')

        primitive_dictionary['clearheap'] = self._prim_emptyheap
        palette.add_block('clearheap',
                          style='basic-style-extended-vertical',
                          label=_('empty heap'),
                          prim_name='clearheap',
                          logo_command='taclearheap',
                          help_string=_('emptys FILO (first-in-last-out \
heap)'))
        self.tw.lc.def_prim('clearheap', 0,
                            lambda self: primitive_dictionary['clearheap']())
        define_logo_function('taclearheap', 'to taclearheap\rmake "taheap []\r\
end\r')

        primitive_dictionary['pop'] = self._prim_pop
        palette.add_block('pop',
                          style='box-style',
                          #TRANS: pop removes a new item from the program stack
                          label=_('pop'),
                          prim_name='pop',
                          value_block=True,
                          logo_command='tapop',
                          help_string=_('pops value off FILO (first-in \
last-out heap)'))
        self.tw.lc.def_prim('pop', 0,
                            lambda self: primitive_dictionary['pop']())
        define_logo_function('tapop', 'to tapop\rif emptyp :taheap [stop]\r\
make "tmp first :taheap\rmake "taheap butfirst :taheap\routput :tmp\rend\r')

        primitive_dictionary['isheapempty'] = self._prim_is_heap_empty
        palette.add_block('isheapempty',
                          style='box-style',
                          label=_('empty heap?'),
                          prim_name='isheapempty',
                          value_block=True,
                          help_string=_('returns True if heap is empty'))
        self.tw.lc.def_prim('isheapempty', 0,
                            lambda self: primitive_dictionary['isheapempty']())

        primitive_dictionary['print'] = self._prim_print
        palette.add_block('comment',
                          style='basic-style-1arg',
                          label=_('comment'),
                          prim_name='comment',
                          default=_('comment'),
                          string_or_number=True,
                          help_string=_('places a comment in your code'))
        self.tw.lc.def_prim('comment', 1,
            lambda self, x: primitive_dictionary['print'](x, True))

        palette.add_block('print',
                          style='basic-style-1arg',
                          label=_('print'),
                          prim_name='print',
                          logo_command='label',
                          string_or_number=True,
                          help_string=_('prints value in status block at \
bottom of the screen'))
        self.tw.lc.def_prim('print', 1,
            lambda self, x: primitive_dictionary['print'](x, False))

        primitive_dictionary['chr'] = self._prim_chr
        palette.add_block('chr',
                          style='number-style-1arg',
                          label='chr',
                          prim_name='chr',
                          help_string=_('Python chr operator'))
        self.tw.lc.def_prim('chr', 1,
                            lambda self, x: primitive_dictionary['chr'](x))

        primitive_dictionary['int'] = self._prim_int
        palette.add_block('int',
                          style='number-style-1arg',
                          label='int',
                          prim_name='int',
                          help_string=_('Python int operator'))
        self.tw.lc.def_prim('int', 1,
                            lambda self, x: primitive_dictionary['int'](x))

        primitive_dictionary['myfunction'] = self._prim_myfunction
        palette.add_block('myfunc1arg',
                          style='number-style-var-arg',
                          label=[_('Python'), 'f(x)', 'x'],
                          prim_name='myfunction',
                          default=['x', 100],
                          string_or_number=True,
                          help_string=_('a programmable block: used to add \
advanced single-variable math equations, e.g., sin(x)'))
        self.tw.lc.def_prim('myfunction', 2,
            lambda self, f, x: primitive_dictionary['myfunction'](f, [x]))

        palette.add_block('myfunc2arg',
                          hidden=True,
                          colors=["#FF0000", "#A00000"],
                          style='number-style-var-arg',
                          label=[_('Python'), 'f(x,y)', ' '],
                          prim_name='myfunction2',
                          default=['x+y', 100, 100],
                          string_or_number=True,
                          help_string=_('a programmable block: used to add \
advanced multi-variable math equations, e.g., sqrt(x*x+y*y)'))
        self.tw.lc.def_prim('myfunction2', 3,
            lambda self, f, x, y: primitive_dictionary['myfunction'](
                f, [x, y]))

        palette.add_block('myfunc3arg',
                          hidden=True,
                          colors=["#FF0000", "#A00000"],
                          style='number-style-var-arg',
                          label=[_('Python'), 'f(x,y,z)', ' '],
                          prim_name='myfunction3',
                          default=['x+y+z', 100, 100, 100],
                          string_or_number=True,
                          help_string=_('a programmable block: used to add \
advanced multi-variable math equations, e.g., sin(x+y+z)'))
        self.tw.lc.def_prim('myfunction3', 4,
            lambda self, f, x, y, z: primitive_dictionary['myfunction'](
                f, [x, y, z]))

        primitive_dictionary['userdefined'] = self._prim_myblock
        palette.add_block('userdefined',
                          style='basic-style-var-arg',
                          label=' ',
                          prim_name='userdefined',
                          string_or_number=True,
                          special_name=_('Python block'),
                          default=100,
                          help_string=_('runs code found in the tamyblock.py \
module found in the Journal'))
        self.tw.lc.def_prim('userdefined', 1,
            lambda self, x: primitive_dictionary['userdefined']([x]))
        BLOCKS_WITH_SKIN.append('userdefined')
        PYTHON_SKIN.append('userdefined')

        palette.add_block('userdefined2args',
                          hidden=True,
                          colors=["#FF0000", "#A00000"],
                          style='basic-style-var-arg',
                          label=' ',
                          prim_name='userdefined2',
                          string_or_number=True,
                          special_name=_('Python block'),
                          default=[100, 100],
                          help_string=_('runs code found in the tamyblock.py \
module found in the Journal'))
        self.tw.lc.def_prim('userdefined2', 2,
            lambda self, x, y: primitive_dictionary['userdefined']([x, y]))
        BLOCKS_WITH_SKIN.append('userdefined2args')
        PYTHON_SKIN.append('userdefined2args')

        palette.add_block('userdefined3args',
                          hidden=True,
                          colors=["#FF0000", "#A00000"],
                          style='basic-style-var-arg',
                          label=' ',
                          prim_name='userdefined3',
                          special_name=_('Python block'),
                          default=[100, 100, 100],
                          string_or_number=True,
                          help_string=_('runs code found in the tamyblock.py \
module found in the Journal'))
        self.tw.lc.def_prim('userdefined3', 3,
            lambda self, x, y, z: primitive_dictionary['userdefined'](
                [x, y, z]))
        BLOCKS_WITH_SKIN.append('userdefined3args')
        PYTHON_SKIN.append('userdefined3args')
        MEDIA_SHAPES.append('pythonsmall')
        MEDIA_SHAPES.append('pythonoff')
        MEDIA_SHAPES.append('pythonon')

        palette.add_block('cartesian',
                          style='basic-style-extended-vertical',
                          label=_('Cartesian'),
                          prim_name='cartesian',
                          help_string=_('displays Cartesian coordinates'))
        self.tw.lc.def_prim('cartesian', 0,
                             lambda self: self.tw.set_cartesian(True))

        palette.add_block('polar',
                          style='basic-style-extended-vertical',
                          label=_('polar'),
                          prim_name='polar',
                          help_string=_('displays polar coordinates'))
        self.tw.lc.def_prim('polar', 0,
                             lambda self: self.tw.set_polar(True))

        palette.add_block('addturtle',
                          style='basic-style-1arg',
                          label=_('turtle'),
                          prim_name='turtle',
                          default=1,
                          string_or_number=True,
                          help_string=_('chooses which turtle to command'))
        self.tw.lc.def_prim('turtle', 1,
            lambda self, x: self.tw.canvas.set_turtle(x))

        primitive_dictionary['skin'] = self._prim_reskin
        palette.add_block('skin',
                          hidden=True,
                          colors=["#FF0000", "#A00000"],
                          style='basic-style-1arg',
                          label=_('turtle shell'),
                          prim_name='skin',
                          help_string=_("put a custom 'shell' on the turtle"))
        self.tw.lc.def_prim('skin', 1,
            lambda self, x: primitive_dictionary['skin'](x))

        # macro
        palette.add_block('reskin',
                          style='basic-style-1arg',
                          label=_('turtle shell'),
                          help_string=_("put a custom 'shell' on the turtle"))

        primitive_dictionary['clamp'] = self._prim_clamp
        palette.add_block('sandwichclamp',
                          style='clamp-style-collapsible',
                          label=' ',
                          special_name=_('top'),
                          prim_name='clamp',
                          help_string=_('top of a collapsible stack'))
        self.tw.lc.def_prim('clamp', 1, primitive_dictionary['clamp'], True)

        palette.add_block('sandwichclampcollapsed',
                          hidden=True,
                          style='clamp-style-collapsed',
                          label=_('click to open'),
                          prim_name='clamp',
                          special_name=_('top'),
                          help_string=_('top of a collapsed stack'))

    def _portfolio_palette(self):

        palette = make_palette('portfolio',
                               colors=["#0606FF", "#0606A0"],
                               help_string=_('Palette of presentation \
templates'),
                               position=9)

        primitive_dictionary['hideblocks'] = self._prim_hideblocks
        palette.add_block('hideblocks',
                          style='basic-style-extended-vertical',
                          label=_('hide blocks'),
                          prim_name='hideblocks',
                          help_string=_('declutters canvas by hiding blocks'))
        self.tw.lc.def_prim('hideblocks', 0,
                            lambda self: primitive_dictionary['hideblocks']())

        primitive_dictionary['showblocks'] = self._prim_showblocks
        palette.add_block('showblocks',
                          style='basic-style-extended-vertical',
                          label=_('show blocks'),
                          prim_name='showblocks',
                          help_string=_('restores hidden blocks'))
        self.tw.lc.def_prim('showblocks', 0,
                            lambda self: primitive_dictionary['showblocks']())

        palette.add_block('fullscreen',
                          style='basic-style-extended-vertical',
                          label=_('Fullscreen').lower(),
                          prim_name='fullscreen',
                          help_string=_('hides the Sugar toolbars'))
        self.tw.lc.def_prim('fullscreen', 0,
                             lambda self: self.tw.set_fullscreen())

        primitive_dictionary['bulletlist'] = self._prim_list
        palette.add_block('list',
                          hidden=True,
                          colors=["#0606FF", "#0606A0"],
                          style='bullet-style',
                          label=_('list'),
                          string_or_number=True,
                          prim_name='bulletlist',
                          default=['∙ ', '∙ '],
                          help_string=_('presentation bulleted list'))
        self.tw.lc.def_prim('bulletlist', 1,
                             primitive_dictionary['bulletlist'], True)

        # macros
        palette.add_block('picturelist',
                          style='basic-style-extended',
                          label=' ',
                          help_string=_('presentation template: list of \
bullets'))
        MEDIA_SHAPES.append('list')

        palette.add_block('picture1x1a',
                          style='basic-style-extended',
                          label=' ',
                          help_string=_('presentation template: select \
Journal object (no description)'))
        MEDIA_SHAPES.append('1x1a')

        palette.add_block('picture1x1',
                          style='basic-style-extended',
                          label=' ',
                          help_string=_('presentation template: select \
Journal object (with description)'))
        MEDIA_SHAPES.append('1x1')

        palette.add_block('picture2x2',
                          style='basic-style-extended',
                          label=' ',
                          help_string=_('presentation template: select four \
Journal objects'))
        MEDIA_SHAPES.append('2x2')

        palette.add_block('picture2x1',
                          style='basic-style-extended',
                          label=' ',
                          help_string=_('presentation template: select two \
Journal objects'))
        MEDIA_SHAPES.append('2x1')

        palette.add_block('picture1x2',
                          style='basic-style-extended',
                          label=' ',
                          help_string=_('presentation template: select two \
Journal objects'))
        MEDIA_SHAPES.append('1x2')

        # Display-dependent constants
        palette.add_block('leftpos',
                          style='box-style',
                          label=_('left'),
                          prim_name='lpos',
                          logo_command='lpos',
                          help_string=_('xcor of left of screen'))
        self.tw.lc.def_prim('lpos', 0, lambda self: CONSTANTS['leftpos'])

        palette.add_block('bottompos',
                          style='box-style',
                          label=_('bottom'),
                          prim_name='bpos',
                          logo_command='bpos',
                          help_string=_('ycor of bottom of screen'))
        self.tw.lc.def_prim('bpos', 0, lambda self: CONSTANTS['bottompos'])

        palette.add_block('width',
                          style='box-style',
                          label=_('width'),
                          prim_name='hres',
                          logo_command='width',
                          help_string=_('the canvas width'))
        self.tw.lc.def_prim('hres', 0, lambda self: CONSTANTS['width'])

        palette.add_block('rightpos',
                          style='box-style',
                          label=_('right'),
                          prim_name='rpos',
                          logo_command='rpos',
                          help_string=_('xcor of right of screen'))
        self.tw.lc.def_prim('rpos', 0, lambda self: CONSTANTS['rightpos'])

        palette.add_block('toppos',
                          style='box-style',
                          label=_('top'),
                          prim_name='tpos',
                          logo_command='tpos',
                          help_string=_('ycor of top of screen'))
        self.tw.lc.def_prim('tpos', 0, lambda self: CONSTANTS['toppos'])

        palette.add_block('height',
                          style='box-style',
                          label=_('height'),
                          prim_name='vres',
                          logo_command='height',
                          help_string=_('the canvas height'))
        self.tw.lc.def_prim('vres', 0, lambda self: CONSTANTS['height'])

        palette.add_block('titlex',
                          hidden=True,
                          colors=["#0606FF", "#0606A0"],
                          style='box-style',
                          label=_('title x'),
                          logo_command='titlex',
                          prim_name='titlex')
        self.tw.lc.def_prim('titlex', 0, lambda self: CONSTANTS['titlex'])

        palette.add_block('titley',
                          hidden=True,
                          colors=["#0606FF", "#0606A0"],
                          style='box-style',
                          label=_('title y'),
                          logo_command='titley',
                          prim_name='titley')
        self.tw.lc.def_prim('titley', 0, lambda self: CONSTANTS['titley'])

        palette.add_block('leftx',
                          hidden=True,
                          colors=["#0606FF", "#0606A0"],
                          style='box-style',
                          label=_('left x'),
                          prim_name='leftx',
                          logo_command='leftx')
        self.tw.lc.def_prim('leftx', 0, lambda self: CONSTANTS['leftx'])

        palette.add_block('topy',
                          hidden=True,
                          colors=["#0606FF", "#0606A0"],
                          style='box-style',
                          label=_('top y'),
                          prim_name='topy',
                          logo_command='topy')
        self.tw.lc.def_prim('topy', 0, lambda self: CONSTANTS['topy'])

        palette.add_block('rightx',
                          hidden=True,
                          colors=["#0606FF", "#0606A0"],
                          style='box-style',
                          label=_('right x'),
                          prim_name='rightx',
                          logo_command='rightx')
        self.tw.lc.def_prim('rightx', 0, lambda self: CONSTANTS['rightx'])

        palette.add_block('bottomy',
                          hidden=True,
                          colors=["#0606FF", "#0606A0"],
                          style='box-style',
                          label=_('bottom y'),
                          prim_name='bottomy',
                          logo_command='bottomy')
        self.tw.lc.def_prim('bottomy', 0, lambda self: CONSTANTS['bottomy'])

        # deprecated blocks

        primitive_dictionary['t1x1'] = self._prim_t1x1
        palette.add_block('template1x1',
                          hidden=True,
                          colors=["#0606FF", "#0606A0"],
                          style='portfolio-style-1x1',
                          label=' ',
                          prim_name='t1x1',
                          default=[_('Title'), 'None'],
                          special_name=_('presentation 1x1'),
                          string_or_number=True,
                          help_string=_('presentation template: select \
Journal object (with description)'))
        self.tw.lc.def_prim('t1x1', 2,
            lambda self, a, b: primitive_dictionary['t1x1'](a, b))

        primitive_dictionary['t1x1a'] = self._prim_t1x1a
        palette.add_block('template1x1a',
                          hidden=True,
                          colors=["#0606FF", "#0606A0"],
                          style='portfolio-style-1x1',
                          label=' ',
                          prim_name='t1x1a',
                          default=[_('Title'), 'None'],
                          special_name=_('presentation 1x1'),
                          string_or_number=True,
                          help_string=_('presentation template: select \
Journal object (no description)'))
        self.tw.lc.def_prim('t1x1a', 2,
            lambda self, a, b: primitive_dictionary['t1x1a'](a, b))

        primitive_dictionary['2x1'] = self._prim_t2x1
        palette.add_block('template2x1',
                          hidden=True,
                          colors=["#0606FF", "#0606A0"],
                          style='portfolio-style-2x1',
                          label=' ',
                          prim_name='t2x1',
                          default=[_('Title'), 'None', 'None'],
                          special_name=_('presentation 2x1'),
                          string_or_number=True,
                          help_string=_("presentation template: select two \
Journal objects"))
        self.tw.lc.def_prim('t2x1', 3,
            lambda self, a, b, c: primitive_dictionary['t2x1'](a, b, c))

        primitive_dictionary['1x2'] = self._prim_t1x2
        palette.add_block('template1x2',
                          hidden=True,
                          colors=["#0606FF", "#0606A0"],
                          style='portfolio-style-1x2',
                          label=' ',
                          prim_name='t1x2',
                          default=[_('Title'), 'None', 'None'],
                          special_name=_('presentation 1x2'),
                          string_or_number=True,
                          help_string=_("presentation template: select two \
Journal objects"))
        self.tw.lc.def_prim('t1x2', 3,
            lambda self, a, b, c: primitive_dictionary['t1x2'](a, b, c))

        primitive_dictionary['t2x2'] = self._prim_t2x2
        palette.add_block('template2x2',
                          hidden=True,
                          colors=["#0606FF", "#0606A0"],
                          style='portfolio-style-2x2',
                          label=' ',
                          prim_name='t2x2',
                          default=[_('Title'), 'None', 'None', 'None', 'None'],
                          special_name=_('presentation 2x2'),
                          string_or_number=True,
                          help_string=_("presentation template: select four \
Journal objects"))
        self.tw.lc.def_prim('t2x2', 5,
            lambda self, a, b, c, d, e: primitive_dictionary['t2x2'](
                a, b, c, d, e))

        palette.add_block('templatelist',
                          hidden=True,
                          colors=["#0606FF", "#0606A0"],
                          style='bullet-style',
                          label=' ',
                          prim_name='bullet',
                          default=[_('Title'), '∙ '],
                          special_name=_('presentation bulleted list'),
                          string_or_number=True,
                          help_string=_('presentation template: list of \
bullets'))
        self.tw.lc.def_prim('bullet', 1, self._prim_list, True)

    # Block primitives

    def _prim_emptyheap(self):
        """ Empty FILO """
        self.tw.lc.heap = []

    def _prim_kbinput(self):
        """ Query keyboard """
        if len(self.tw.keypress) == 1:
            self.tw.lc.keyboard = ord(self.tw.keypress[0])
        else:
            try:
                self.tw.lc.keyboard = {'Escape': 27, 'space': 32, ' ': 32,
                    'Return': 13, 'KP_Up': 2, 'KP_Down': 4, 'KP_Left': 1,
                    'KP_Right': 3}[self.tw.keypress]
            except KeyError:
                self.tw.lc.keyboard = 0
        self.tw.lc.update_label_value('keyboard', self.tw.lc.keyboard)
        self.tw.keypress = ''

    def _prim_list(self, blklist):
        """ Expandable list block """
        self._prim_showlist(blklist)
        self.tw.lc.ireturn()
        yield True

    def _prim_myblock(self, x):
        """ Run Python code imported from Journal """
        if self.tw.lc.bindex is not None and \
           self.tw.lc.bindex in self.tw.myblock:
            try:
                if len(x) == 1:
                    myfunc_import(self, self.tw.myblock[self.tw.lc.bindex],
                                  x[0])
                else:
                    myfunc_import(self, self.tw.myblock[self.tw.lc.bindex], x)
            except:
                raise logoerror("#syntaxerror")

    def _prim_myfunction(self, f, x):
        """ Programmable block """
        try:
            y = myfunc(f, x)
            if str(y) == 'nan':
                debug_output('Python function returned NAN',
                             self.tw.running_sugar)
                self.tw.lc.stop_logo()
                raise logoerror("#notanumber")
            else:
                return y
        except ZeroDivisionError:
            self.tw.lc.stop_logo()
            raise logoerror("#zerodivide")
        except ValueError, e:
            self.tw.lc.stop_logo()
            raise logoerror('#' + str(e))
        except SyntaxError, e:
            self.tw.lc.stop_logo()
            raise logoerror('#' + str(e))
        except NameError, e:
            self.tw.lc.stop_logo()
            raise logoerror('#' + str(e))
        except OverflowError:
            self.tw.lc.stop_logo()
            raise logoerror("#overflowerror")
        except TypeError:
            self.tw.lc.stop_logo()
            raise logoerror("#notanumber")

    def _prim_is_heap_empty(self):
        """ is FILO empty? """
        if len(self.tw.lc.heap) == 0:
            return 1
        else:
            return 0

    def _prim_pop(self):
        """ Pop value off of FILO """
        if len(self.tw.lc.heap) == 0:
            raise logoerror("#emptyheap")
        else:
            if len(self.tw.lc.heap) == 1:
                self.tw.lc.update_label_value('pop')
            else:
                self.tw.lc.update_label_value('pop', self.tw.lc.heap[-2])
            return self.tw.lc.heap.pop(-1)

    def _prim_print(self, n, flag):
        """ Print object n """
        if flag and (self.tw.hide or self.tw.step_time == 0):
            return
        if type(n) == list:
            self.tw.showlabel('print', n)
        elif type(n) == str or type(n) == unicode:
            if n[0:6] == 'media_' and \
               n[6:].lower not in media_blocks_dictionary:
                try:
                    if self.tw.running_sugar:
                        from sugar.datastore import datastore
                        try:
                            dsobject = datastore.get(n[6:])
                        except:
                            debug_output("Couldn't open %s" % (n[6:]),
                                         self.tw.running_sugar)
                        self.tw.showlabel('print', dsobject.metadata['title'])
                        dsobject.destroy()
                    else:
                        self.tw.showlabel('print', n[6:])
                except IOError:
                    self.tw.showlabel('print', n)
            else:
                self.tw.showlabel('print', n)
        elif type(n) == int:
            self.tw.showlabel('print', n)
        else:
            self.tw.showlabel('print',
                str(round_int(n)).replace('.', self.tw.decimal_point))

    def _prim_printheap(self):
        """ Display contents of heap """
        heap_as_string = str(self.tw.lc.heap)
        if len(heap_as_string) > 80:
            self.tw.showlabel('print', str(self.tw.lc.heap)[0:79] + '…')
        else:
            self.tw.showlabel('print', str(self.tw.lc.heap))

    def _prim_push(self, val):
        """ Push value onto FILO """
        self.tw.lc.heap.append(val)
        self.tw.lc.update_label_value('pop', val)

    '''
    def _prim_keyboard_num(self):
        """ Return a number when a number is typed. """
        if self.tw.lc.keyboard < 48 or self.tw.lc.keyboard > 57:
            return -1
        else:
            return self.tw.lc.keyboard - 48
    '''

    def _prim_readpixel(self):
        """ Read r, g, b, a from the canvas and push b, g, r to the stack """
        r, g, b, a = self.tw.canvas.get_pixel()
        self.tw.lc.heap.append(b)
        self.tw.lc.heap.append(g)
        self.tw.lc.heap.append(r)

    def _prim_reskin(self, media):
        """ Reskin the turtle with an image from a file """
        scale = int(ICON_SIZE * float(self.tw.lc.scale) / DEFAULT_SCALE)
        if scale < 1:
            return
        self.tw.lc.filepath = None
        dsobject = None
        if os.path.exists(media[6:]):  # is it a path?
            self.tw.lc.filepath = media[6:]
        elif self.tw.running_sugar:  # is it a datastore object?
            from sugar.datastore import datastore
            try:
                dsobject = datastore.get(media[6:])
            except:
                debug_output("Couldn't open skin %s" % (media[6:]),
                             self.tw.running_sugar)
            if dsobject is not None:
                self.tw.lc.filepath = dsobject.file_path
        if self.tw.lc.filepath == None:
            self.tw.showlabel('nojournal', self.tw.lc.filepath)
            return
        pixbuf = None
        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(self.tw.lc.filepath,
                                                          scale, scale)
        except:
            self.tw.showlabel('nojournal', self.tw.lc.filepath)
            debug_output("Couldn't open skin %s" % (self.tw.lc.filepath),
                         self.tw.running_sugar)
        if pixbuf is not None:
            self.tw.active_turtle.set_shapes([pixbuf])
            pen_state = self.tw.active_turtle.get_pen_state()
            if pen_state:
                self.tw.canvas.setpen(False)
            self.tw.canvas.forward(0)
            if pen_state:
                self.tw.canvas.setpen(True)

    def _prim_save_picture(self, name):
        """ Save canvas to file as PNG """
        self.tw.save_as_image(name)

    def _prim_save_svg(self, name):
        """ Save SVG to file """
        self.tw.canvas.svg_close()
        self.tw.save_as_image(name, svg=True)

    def _prim_speak(self, text):
        """ Speak text """
        if type(text) == float and int(text) == text:
            text = int(text)

        lang = os.environ['LANG'][0:2]
        if lang in VOICES:
            language_option = '-v ' + VOICES[lang]
        else:
            language_option = ''
        os.system('espeak %s "%s" --stdout | aplay' % (
                language_option, str(text)))
        if self.tw.sharing():
            if language_option == '':
                event = 'S|%s' % (data_to_string([self.tw.nick, 'None', text]))
            else:
                event = 'S|%s' % (data_to_string([self.tw.nick,
                                                  language_option, text]))
            self.tw.send_event(event)

    def _prim_sinewave(self, pitch, amplitude, duration):
        """ Create a Csound score to play a sine wave. """
        self.orchlines = []
        self.scorelines = []
        self.instrlist = []

        try:
            pitch = abs(float(pitch))
            amplitute = abs(float(amplitude))
            duration = abs(float(duration))
        except ValueError:
            self.tw.lc.stop_logo()
            raise logoerror("#notanumber")

        self._play_sinewave(pitch, amplitude, duration)

        if self.tw.running_sugar:
            path = os.path.join(get_path(self.tw.activity, 'instance'),
                                'tmp.csd')
        else:
            path = os.path.join('/tmp', 'tmp.csd')
        # Create a csound file from the score.
        self._audio_write(path)
        # Play the csound file.
        os.system('csound ' + path + ' > /dev/null 2>&1')

    def _play_sinewave(self, pitch, amplitude, duration, starttime=0,
              pitch_envelope=99, amplitude_envelope=100, instrument=1):

        pitenv = pitch_envelope
        ampenv = amplitude_envelope
        if not 1 in self.instrlist:
            self.orchlines.append("instr 1\n")
            self.orchlines.append("kpitenv oscil 1, 1/p3, p6\n")
            self.orchlines.append("aenv oscil 1, 1/p3, p7\n")
            self.orchlines.append("asig oscil p5*aenv, p4*kpitenv, p8\n")
            self.orchlines.append("out asig\n")
            self.orchlines.append("endin\n\n")
            self.instrlist.append(1)

        self.scorelines.append("i1 %s %s %s %s %s %s %s\n" % (
                str(starttime), str(duration), str(pitch), str(amplitude),
                str(pitenv), str(ampenv), str(instrument)))

    def _audio_write(self, file):
        """ Compile a .csd file. """

        csd = open(file, "w")
        csd.write("<CsoundSynthesizer>\n\n")
        csd.write("<CsOptions>\n")
        csd.write("-+rtaudio=alsa -odevaudio -m0 -d -b256 -B512\n")
        csd.write("</CsOptions>\n\n")
        csd.write("<CsInstruments>\n\n")
        csd.write("sr=16000\n")
        csd.write("ksmps=50\n")
        csd.write("nchnls=1\n\n")
        for line in self.orchlines:
            csd.write(line)
        csd.write("\n</CsInstruments>\n\n")
        csd.write("<CsScore>\n\n")
        csd.write("f1 0 2048 10 1\n")
        csd.write("f2 0 2048 10 1 0 .33 0 .2 0 .143 0 .111\n")
        csd.write("f3 0 2048 10 1 .5 .33 .25 .2 .175 .143 .125 .111 .1\n")
        csd.write("f10 0 2048 10 1 0 0 .3 0 .2 0 0 .1\n")
        csd.write("f99 0 2048 7 1 2048 1\n")
        csd.write("f100 0 2048 7 0. 10 1. 1900 1. 132 0.\n")
        csd.write(self.scorelines.pop())
        csd.write("e\n")
        csd.write("\n</CsScore>\n")
        csd.write("\n</CsoundSynthesizer>")
        csd.close()

    def _prim_mouse_button(self):
        """ Return 1 if mouse button is pressed """
        if self.tw.mouse_flag == 1:
            return 1
        else:
            return 0

    def _prim_see(self):
        """ Read r, g, b from the canvas and return a corresponding palette
        color """
        r, g, b, a = self.tw.canvas.get_pixel()
        color_index = self.tw.canvas.get_color_index(r, g, b)
        self.tw.lc.update_label_value('see', color_index)
        return color_index

    def _prim_setscale(self, scale):
        """ Set the scale used by the show block """
        self.tw.lc.scale = scale
        self.tw.lc.update_label_value('scale', scale)

    def _prim_show(self, string, center=False):
        """ Show is the general-purpose media-rendering block. """
        if type(string) == str or type(string) == unicode:
            if string in  ['media_', 'descr_', 'audio_', 'video_',
                           'media_None', 'descr_None', 'audio_None',
                           'video_None']:
                pass
            elif string[0:6] in ['media_', 'descr_', 'audio_', 'video_']:
                self.tw.lc.filepath = None
                self.tw.lc.pixbuf = None  # Camera writes directly to pixbuf
                self.tw.lc.dsobject = None
                if string[6:].lower() in media_blocks_dictionary:
                    media_blocks_dictionary[string[6:].lower()]()
                elif os.path.exists(string[6:]):  # is it a path?
                    self.tw.lc.filepath = string[6:]
                elif self.tw.running_sugar:  # is it a datastore object?
                    from sugar.datastore import datastore
                    try:
                        self.tw.lc.dsobject = datastore.get(string[6:])
                    except:
                        debug_output("Couldn't find dsobject %s" % (
                                string[6:]), self.tw.running_sugar)
                    if self.tw.lc.dsobject is not None:
                        self.tw.lc.filepath = self.tw.lc.dsobject.file_path
                if self.tw.lc.pixbuf is not None:
                    self.tw.lc.insert_image(center=center, pixbuf=True)
                elif self.tw.lc.filepath is None:
                    if self.tw.lc.dsobject is not None:
                        self.tw.showlabel('nojournal',
                            self.tw.lc.dsobject.metadata['title'])
                    else:
                        self.tw.showlabel('nojournal', string[6:])
                    debug_output("Couldn't open %s" % (string[6:]),
                                 self.tw.running_sugar)
                elif string[0:6] == 'media_':
                    self.tw.lc.insert_image(center=center)
                elif string[0:6] == 'descr_':
                    mimetype = None
                    if self.tw.lc.dsobject is not None and \
                       'mime_type' in self.tw.lc.dsobject.metadata:
                        mimetype = self.tw.lc.dsobject.metadata['mime_type']
                    description = None
                    if self.tw.lc.dsobject is not None and \
                       'description' in self.tw.lc.dsobject.metadata:
                        description = self.tw.lc.dsobject.metadata[
                            'description']
                    self.tw.lc.insert_desc(mimetype, description)
                elif string[0:6] == 'audio_':
                    self.tw.lc.play_sound()
                elif string[0:6] == 'video_':
                    self.tw.lc.play_video()
                if self.tw.lc.dsobject is not None:
                    self.tw.lc.dsobject.destroy()
            else:  # assume it is text to display
                x, y = self.tw.lc.x2tx(), self.tw.lc.y2ty()
                if center:
                    y -= self.tw.canvas.textsize
                self.tw.canvas.draw_text(string, x, y,
                                         int(self.tw.canvas.textsize * \
                                             self.tw.lc.scale / 100.),
                                         self.tw.canvas.width - x)
        elif type(string) == float or type(string) == int:
            string = round_int(string)
            x, y = self.tw.lc.x2tx(), self.tw.lc.y2ty()
            if center:
                y -= self.tw.canvas.textsize
            self.tw.canvas.draw_text(string, x, y,
                                     int(self.tw.canvas.textsize * \
                                         self.tw.lc.scale / 100.),
                                     self.tw.canvas.width - x)

    def _prim_showlist(self, sarray):
        """ Display list of media objects """
        x = self.tw.canvas.xcor / self.tw.coord_scale
        y = self.tw.canvas.ycor / self.tw.coord_scale
        for s in sarray:
            self.tw.canvas.setxy(x, y, pendown=False)
            self._prim_show(s)
            y -= int(self.tw.canvas.textsize * self.tw.lead)

    def _prim_time(self):
        """ Number of seconds since program execution has started or
        clean (prim_clear) block encountered """
        elapsed_time = int(time() - self.tw.lc.start_time)
        self.tw.lc.update_label_value('time', elapsed_time)
        return elapsed_time

    def _prim_hideblocks(self):
        """ hide blocks and show showblocks button """
        self.tw.hideblocks()
        if self.tw.running_sugar:
            self.tw.activity.stop_turtle_button.set_icon("hideshowoff")
            self.tw.activity.stop_turtle_button.set_tooltip(_('Show blocks'))

    def _prim_showblocks(self):
        """ show blocks and show stop turtle button """
        self.tw.showblocks()
        if self.tw.running_sugar:
            self.tw.activity.stop_turtle_button.set_icon("stopiton")
            self.tw.activity.stop_turtle_button.set_tooltip(_('Stop turtle'))

    def _prim_chr(self, x):
        """ Chr conversion """
        try:
            return chr(int(x))
        except ValueError:
            self.tw.lc.stop_logo()
            raise logoerror("#notanumber")

    def _prim_int(self, x):
        """ Int conversion """
        try:
            return int(x)
        except ValueError:
            self.tw.lc.stop_logo()
            raise logoerror("#notanumber")

    def _prim_clamp(self, blklist):
        """ Run clamp blklist """
        self.tw.lc.icall(self.tw.lc.evline, blklist[:])
        yield True
        self.tw.lc.procstop = False
        self.tw.lc.ireturn()
        yield True

    # Deprecated blocks

    def _prim_t1x1(self, title, media):
        """ title, one image, and description """
        xo = self.tw.calc_position('t1x1')[2]
        x = -(self.tw.canvas.width / 2) + xo
        y = self.tw.canvas.height / 2
        self.tw.canvas.setxy(x, y, pendown=False)
        # save the text size so we can restore it later
        save_text_size = self.tw.canvas.textsize
        # set title text
        self.tw.canvas.settextsize(self.title_height)
        self._prim_show(title)
        # calculate and set scale for media blocks
        myscale = 45 * (self.tw.canvas.height - self.title_height * 2) \
                      / self.tw.canvas.height
        self._prim_setscale(myscale)
        # set body text size
        self.tw.canvas.settextsize(self.tw.lc.body_height)
        # render media object
        # leave some space below the title
        y -= int(self.title_height * 2 * self.tw.lead)
        self.tw.canvas.setxy(x, y, pendown=False)
        self._prim_show(media)
        if self.tw.running_sugar:
            x = 0
            self.tw.canvas.setxy(x, y, pendown=False)
            self._prim_show(media.replace('media_', 'descr_'))
        # restore text size
        self.tw.canvas.settextsize(save_text_size)

    def _prim_t2x1(self, title, media1, media2):
        """ title, two images (horizontal), two descriptions """
        xo = self.tw.calc_position('t2x1')[2]
        x = -(self.tw.canvas.width / 2) + xo
        y = self.tw.canvas.height / 2
        self.tw.canvas.setxy(x, y, pendown=False)
        # save the text size so we can restore it later
        save_text_size = self.tw.canvas.textsize
        # set title text
        self.tw.canvas.settextsize(self.title_height)
        self._prim_show(title)
        # calculate and set scale for media blocks
        myscale = 45 * (self.tw.canvas.height - self.title_height * 2) / \
                  self.tw.canvas.height
        self._prim_setscale(myscale)
        # set body text size
        self.tw.canvas.settextsize(self.tw.lc.body_height)
        # render four quadrents
        # leave some space below the title
        y -= int(self.title_height * 2 * self.tw.lead)
        self.tw.canvas.setxy(x, y, pendown=False)
        self._prim_show(media1)
        x = 0
        self.tw.canvas.setxy(x, y, pendown=False)
        self._prim_show(media2)
        y = -self.title_height
        if self.tw.running_sugar:
            self.tw.canvas.setxy(x, y, pendown=False)
            self._prim_show(media2.replace('media_', 'descr_'))
            x = -(self.tw.canvas.width / 2) + xo
            self.tw.canvas.setxy(x, y, pendown=False)
            self._prim_show(media1.replace('media_', 'descr_'))
        # restore text size
        self.tw.canvas.settextsize(save_text_size)

    def _prim_t1x2(self, title, media1, media2):
        """ title, two images (vertical), two desciptions """
        xo = self.tw.calc_position('t1x2')[2]
        x = -(self.tw.canvas.width / 2) + xo
        y = self.tw.canvas.height / 2
        self.tw.canvas.setxy(x, y, pendown=False)
        # save the text size so we can restore it later
        save_text_size = self.tw.canvas.textsize
        # set title text
        self.tw.canvas.settextsize(self.title_height)
        self._prim_show(title)
        # calculate and set scale for media blocks
        myscale = 45 * (self.tw.canvas.height - self.title_height * 2) / \
                 self.tw.canvas.height
        self._prim_setscale(myscale)
        # set body text size
        self.tw.canvas.settextsize(self.tw.lc.body_height)
        # render four quadrents
        # leave some space below the title
        y -= int(self.title_height * 2 * self.tw.lead)
        self.tw.canvas.setxy(x, y, pendown=False)
        self._prim_show(media1)
        if self.tw.running_sugar:
            x = 0
            self.tw.canvas.setxy(x, y, pendown=False)
            self._prim_show(media1.replace('media_', 'descr_'))
            y = -self.title_height
            self.tw.canvas.setxy(x, y, pendown=False)
            self._prim_show(media2.replace('media_', 'descr_'))
            x = -(self.tw.canvas.width / 2) + xo
            self.tw.canvas.setxy(x, y, pendown=False)
            self._prim_show(media2)
        # restore text size
        self.tw.canvas.settextsize(save_text_size)

    def _prim_t2x2(self, title, media1, media2, media3, media4):
        """ title and four images """
        xo = self.tw.calc_position('t2x2')[2]
        x = -(self.tw.canvas.width / 2) + xo
        y = self.tw.canvas.height / 2
        self.tw.canvas.setxy(x, y, pendown=False)
        # save the text size so we can restore it later
        save_text_size = self.tw.canvas.textsize
        # set title text
        self.tw.canvas.settextsize(self.title_height)
        self._prim_show(title)
        # calculate and set scale for media blocks
        myscale = 45 * (self.tw.canvas.height - self.title_height * 2) / \
                  self.tw.canvas.height
        self._prim_setscale(myscale)
        # set body text size
        self.tw.canvas.settextsize(self.tw.lc.body_height)
        # render four quadrents
        # leave some space below the title
        y -= int(self.title_height * 2 * self.tw.lead)
        self.tw.canvas.setxy(x, y, pendown=False)
        self._prim_show(media1)
        x = 0
        self.tw.canvas.setxy(x, y, pendown=False)
        self._prim_show(media2)
        y = -self.title_height
        self.tw.canvas.setxy(x, y, pendown=False)
        self._prim_show(media4)
        x = -(self.tw.canvas.width / 2) + xo
        self.tw.canvas.setxy(x, y, pendown=False)
        self._prim_show(media3)
        # restore text size
        self.tw.canvas.settextsize(save_text_size)

    def _prim_t1x1a(self, title, media1):
        """ title, one media object """
        xo = self.tw.calc_position('t1x1a')[2]
        x = -(self.tw.canvas.width / 2) + xo
        y = self.tw.canvas.height / 2
        self.tw.canvas.setxy(x, y, pendown=False)
        # save the text size so we can restore it later
        save_text_size = self.tw.canvas.textsize
        # set title text
        self.tw.canvas.settextsize(self.title_height)
        self._prim_show(title)
        # calculate and set scale for media blocks
        myscale = 90 * (self.tw.canvas.height - self.title_height * 2) / \
                       self.tw.canvas.height
        self._prim_setscale(myscale)
        # set body text size
        self.tw.canvas.settextsize(self.tw.lc.body_height)
        # render media object
        # leave some space below the title
        y -= int(self.title_height * 2 * self.tw.lead)
        self.tw.canvas.setxy(x, y, pendown=False)
        self._prim_show(media1)
        # restore text size
        self.tw.canvas.settextsize(save_text_size)

    def _prim_write(self, string, fsize):
        """ Write string at size """
        x = self.tw.canvas.width / 2 + int(self.tw.canvas.xcor)
        y = self.tw.canvas.height / 2 - int(self.tw.canvas.ycor)
        self.tw.canvas.draw_text(string, x, y - 15, int(fsize),
                                 self.tw.canvas.width)
