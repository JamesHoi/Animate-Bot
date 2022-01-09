import math
import numpy as np
from psd_tools import PSDImage
import glfw
import time
from OpenGL.GL import *

import render.matrix as matrix
from render.init import render_init, get_all_layers

IS_MOVING = False

def body_rotate(layer, a):
    rotation = 0;
    part_name = layer['name'].split("/")[0]
    if part_name != "体" and part_name != "右腕A" and part_name != "左腕A" and part_name != "首":
        rotation = math.sin(time.time() * 5) / 30
    a = a @ matrix.translate(0, 0, -1) \
        @ matrix.rotate_ax(rotation, axis=(0, 2)) \
        @ matrix.translate(0, 0, 1)
    return a


def opengl_loop(all_layers, window, psd_size):
    while not glfw.window_should_close(window):
        glfw.poll_events()
        glClearColor(0,0,0,0)
        glClear(GL_COLOR_BUFFER_BIT)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        for layer in all_layers:
            a, b, c, d = layer['pos']
            q, w = layer['axis']
            z = layer['depth']
            p1 = np.array([a, b, z, 1, 0, 0])
            p2 = np.array([a, d, z, 1, w, 0])
            p3 = np.array([c, d, z, 1, w, q])
            p4 = np.array([c, b, z, 1, 0, q])

            model = matrix.scale(2 / psd_size[0], 2 / psd_size[1], 1) @ \
                matrix.translate(-1, -1, 0) @ \
                matrix.rotate_ax(-math.pi / 2, axis=(0, 1))

            glBindTexture(GL_TEXTURE_2D, layer['texture_num'])
            glColor4f(1, 1, 1, 1)
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            glBegin(GL_QUADS)
            for p in [p1, p2, p3, p4]:
                a = p[:4]
                b = p[4:6]
                a = a @ model
                if IS_MOVING: a = body_rotate(layer,a)
                glTexCoord2f(*b)
                glVertex4f(*a)
            glEnd()
        glfw.swap_buffers(window)
        
def render_loop():
    psd = PSDImage.open('render/resources/cgjoy.psd')
    layers, size = get_all_layers(psd)
    window = render_init(layers)
    opengl_loop(layers, window, size)