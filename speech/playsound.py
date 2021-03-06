from platform import system
from abc import ABC, abstractmethod

operating_system = system()

if operating_system == 'Windows':
    from ctypes import c_buffer, windll
    from random import random
    from time import sleep
    from sys import getfilesystemencoding
elif operating_system == 'Darwin':
    from AppKit import NSSound
    from Foundation import NSURL
    from time import sleep
elif operating_system == 'Linux':
    # pathname2url escapes non-URL-safe characters
    import os

    try:
        from urllib.request import pathname2url
    except ImportError:
        # python 2
        from urllib import pathname2url
    import gi

    gi.require_version('Gst', '1.0')
    from gi.repository import Gst


class PlaysoundException(Exception):
    pass


class playsoundBase(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def play(self, sound, block):
        raise NotImplemented

    @abstractmethod
    def stop(self):
        raise NotImplemented


class playsoundWin(playsoundBase):
    alias = ''

    def winCommand(self, *command):
        buf = c_buffer(255)
        command = ' '.join(command).encode(getfilesystemencoding())
        errorCode = int(windll.winmm.mciSendStringA(command, buf, 254, 0))
        if errorCode:
            errorBuffer = c_buffer(255)
            windll.winmm.mciGetErrorStringA(errorCode, errorBuffer, 254)
            exceptionMessage = (
                    '\n    Error ' + str(errorCode) + ' for command:\n'
                    + command.decode() + '\n    ' + errorBuffer.value.decode())
            raise PlaysoundException(exceptionMessage)
        return buf.value


    def play(self, sound, block=True):
        self.alias = 'playsound_' + str(random())
        self.winCommand('open "' + sound + '" alias', self.alias)
        self.winCommand('set', self.alias, 'time format milliseconds')
        durationInMS = self.winCommand('status', self.alias, 'length')
        self.winCommand('play', self.alias, 'from 0 to', durationInMS.decode())

        if block:
            sleep(float(durationInMS) / 1000.0)

    def stop(self):
        self.winCommand('stop', self.alias)

    def close(self):
        self.winCommand('close', self.alias)


class playsoundOSX(playsoundBase):
    def play(self, sound, block=True):
        '''
        Utilizes AppKit.NSSound. Tested and known to work with MP3 and WAVE on
        OS X 10.11 with Python 2.7. Probably works with anything QuickTime supports.
        Probably works on OS X 10.5 and newer. Probably works with all versions of
        Python.
        Inspired by (but not copied from) Aaron's Stack Overflow answer here:
        http://stackoverflow.com/a/34568298/901641
        I never would have tried using AppKit.NSSound without seeing his code.
        '''

        if '://' not in sound:
            if not sound.startswith('/'):
                from os import getcwd
                sound = getcwd() + '/' + sound
            sound = 'file://' + sound
        url = NSURL.URLWithString_(sound)
        nssound = NSSound.alloc().initWithContentsOfURL_byReference_(url, True)
        if not nssound:
            raise IOError('Unable to load sound named: ' + sound)
        nssound.play()

        if block:
            sleep(nssound.duration())

    def stop(self):
        raise NotImplemented


class playsoundNix(playsoundBase):
    def play(self, sound, block=True):
        """Play a sound using GStreamer.
        Inspired by this:
        https://gstreamer.freedesktop.org/documentation/tutorials/playback/playbin-usage.html
        """
        if not block:
            raise NotImplementedError(
                "block=False cannot be used on this platform yet")

        Gst.init(None)

        playbin = Gst.ElementFactory.make('playbin', 'playbin')
        if sound.startswith(('http://', 'https://')):
            playbin.props.uri = sound
        else:
            playbin.props.uri = 'file://' + pathname2url(
                os.path.abspath(sound))

        set_result = playbin.set_state(Gst.State.PLAYING)
        if set_result != Gst.StateChangeReturn.ASYNC:
            raise PlaysoundException(
                "playbin.set_state returned " + repr(set_result))

        # FIXME: use some other bus method than poll() with block=False
        # https://lazka.github.io/pgi-docs/#Gst-1.0/classes/Bus.html
        bus = playbin.get_bus()
        bus.poll(Gst.MessageType.EOS, Gst.CLOCK_TIME_NONE)
        playbin.set_state(Gst.State.NULL)

    def stop(self):
        raise NotImplemented

operating_system = 'Windows'
if operating_system == 'Windows':
    playsound = playsoundWin
elif operating_system == 'Darwin':
    playsound = playsoundOSX
elif operating_system == 'Linux':
    playsound = playsoundNix

del operating_system

#how to use?
'''
form playsound import playsound
p=playsound()
p.play("/your music path")
p.stop()#pause
p.close()#close
'''
