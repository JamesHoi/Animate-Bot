import math
import yaml
import numpy as np
import glfw
from OpenGL.GL import *


def get_all_layers(psd):
    layers = []

    def dfs(layer, path=''):
        if layer.is_group():
            for i in layer: dfs(i, path + layer.name + '/')
        else:
            a, b, c, d = layer.bbox
            np_data = layer.numpy()
            if np_data is None: return
            np_data[:, :, 0], np_data[:, :, 2] = np_data[:, :, 2].copy(), np_data[:, :, 0].copy()
            layers.append({'name': path + layer.name, 'pos': (b, a, d, c), 'np_data': np_data})

    for layer in psd: dfs(layer)
    return layers, psd.size


def add_depth_data(all_layers):
    with open('render/resources/depth.yaml', encoding='utf8') as f:
        data = yaml.load(f,Loader=yaml.FullLoader)
    for info in all_layers:
        if info['name'] in data:
            info['depth'] = data[info['name']]


def gen_texture(img):
    w, h = img.shape[:2]
    d = 2**int(max(math.log2(w), math.log2(h)) + 1)
    texture = np.zeros([d, d, 4], dtype=img.dtype)
    texture[:w, :h] = img
    return texture, (w / d, h / d)


def add_texture(all_layers):
    for layer in all_layers:
        texture_num = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_num)
        texture, axis = gen_texture(layer['np_data'])
        width, height = texture.shape[:2]
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_BGRA, GL_FLOAT, texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glGenerateMipmap(GL_TEXTURE_2D)
        layer['texture_num'] = texture_num
        layer['axis'] = axis


def opengl_init(size):
    glfw.init()
    glfw.window_hint(glfw.RESIZABLE, False)
    glfw.window_hint(glfw.DECORATED, False)
    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, True)
    glfw.window_hint(glfw.FLOATING, True)
    window = glfw.create_window(*size, 'Animate-Bot', None, None)
    glfw.make_context_current(window)
    glViewport(0, 0, *size)

    glClearColor(0, 0, 0, 0)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    monitor_size = glfw.get_video_mode(glfw.get_primary_monitor()).size
    glfw.set_window_pos(window, monitor_size.width - size[0], monitor_size.height - size[1]-150)
    return window


def render_init(all_layers):
    SIZE = 512, 512
    # SIZE = 1024, 1024
    window = opengl_init(SIZE)
    add_texture(all_layers)
    add_depth_data(all_layers)
    return window
