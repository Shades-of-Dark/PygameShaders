import struct
import pygame, os, sys
from pygame.locals import *

import moderngl


def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        absolute_path = os.path.join(sys._MEIPASS, relative)
    else:
        absolute_path = os.path.join(relative)
    return absolute_path


class Graphic_engine:
    def __init__(self, screen,  VIRTUAL_RES=(800, 600),  style=1,cpu_only=False, fullscreen=False):
        pygame.init()
        self.VIRTUAL_RES = VIRTUAL_RES
        self.cpu_only = cpu_only
        self.screen = screen
        self.fullscreen = fullscreen
        if not (self.cpu_only):
            self.ctx = moderngl.create_context()
            self.texture_coordinates = [0, 1, 1, 1,
                                        0, 0, 1, 0]
            self.world_coordinates = [-1, -1, 1, -1,
                                      -1, 1, 1, 1]
            self.render_indices = [0, 1, 2,
                                   1, 2, 3]

            self.style = style
            # shader style : 0, no shader. 1, crt. 2, flat_crt.
            self.prog = self.ctx.program(
                vertex_shader= '''
#version 300 es
in vec2 vert;
in vec2 in_text;
out vec2 v_text;
void main() {
   gl_Position = vec4(vert, 0.0, 1.0);
   v_text = in_text;
}
''',
                fragment_shader='''
#version 300 es
precision mediump float;
uniform sampler2D Texture;

out vec4 color;
in vec2 v_text;
uniform int mode;
void main() {
  if (mode == 0){
    color = vec4(texture(Texture, v_text).rgb, 1.0);
  }
  else{
    float flatness = 1.0;
    if (mode == 1)flatness = 2.7;
    else if(mode == 2)flatness = 10.0;
    vec2 center = vec2(0.5, 0.5);
    vec2 off_center = v_text - center;

    off_center *= 1.0 + 0.8 * pow(abs(off_center.yx), vec2(flatness));
    // 1.0 -> 1.5 make distance to screen
    // vec 2 -> screen flatness

    vec2 v_text2 = center+off_center;

    if (v_text2.x > 1.0 || v_text2.x < 0.0 ||
        v_text2.y > 1.0 || v_text2.y < 0.0){
      color=vec4(0.0, 0.0, 0.0, 1.0);
    } else {
      color = vec4(texture(Texture, v_text2).rgb, 1.0);
      float fv = fract(v_text2.y * float(textureSize(Texture,0).y));
      fv=min(1.0, 0.8+0.5*min(fv, 1.0-fv));
      color.rgb*=fv;
    }
  }
}
''',
            )
            self.prog['mode'] = self.style

            self.screen_texture = self.ctx.texture(
                self.VIRTUAL_RES, 3,
                pygame.image.tostring(screen, "RGB", 1)
            )

            self.screen_texture.repeat_x = False
            self.screen_texture.repeat_y = False

            self.vbo = self.ctx.buffer(struct.pack('8f', *self.world_coordinates))
            self.uvmap = self.ctx.buffer(struct.pack('8f', *self.texture_coordinates))
            self.ibo = self.ctx.buffer(struct.pack('6I', *self.render_indices))

            self.vao_content = [
                (self.vbo, '2f', 'vert'),
                (self.uvmap, '2f', 'in_text'),
            ]

            self.vao = self.ctx.vertex_array(self.prog, self.vao_content, index_buffer=self.ibo)
        else:
            self.diaplay = pygame.display.get_surface()

    def change_shader(self):
        if not self.cpu_only:
            self.__init__(self.screen, (self.style + 1) % 3, self.VIRTUAL_RES)

    def render(self):
        if not (self.cpu_only):
            texture_data = self.screen.get_view('1')

            self.screen_texture.write(texture_data)
            self.ctx.clear(14 / 255, 40 / 255, 66 / 255)
            self.screen_texture.use()
            self.vao.render()
            pygame.display.flip()
        else:
            self.diaplay.blit(self.screen, (0, 0))
            pygame.display.update()

    def Full_screen(self, REAL_RES):
        if not (self.cpu_only):
            if not (self.fullscreen):
                pygame.display.set_mode(REAL_RES, pygame.DOUBLEBUF | pygame.OPENGL)
            else:
                pygame.display.set_mode(REAL_RES, pygame.DOUBLEBUF | pygame.OPENGL | pygame.FULLSCREEN)
        else:
            if not (self.fullscreen):
                pygame.display.set_mode(self.VIRTUAL_RES)
            else:
                pygame.display.set_mode(self.VIRTUAL_RES, pygame.FULLSCREEN)

    def __call__(self):
        return self.render()