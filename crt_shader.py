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


class GraphicEngine:
    def __init__(self, screen, VIRTUAL_RES=(800, 600), style=1, cpu_only=False, fullscreen=False):

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
            # shader style : 0, no shader. 1, vignette. 2, flat_crt.
            self.prog = self.ctx.program(
            vertex_shader='''
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
            
            
            in vec2 v_text; // coords of pixel
            uniform int mode;
            
            out vec4 color;
            void main() {
              vec4 baseColor = texture(Texture, v_text);
              if (mode == 0){
                color = vec4(baseColor.rgb, 1.0);
              }
              else if (mode==1){
                 float centerDis = distance(v_text, vec2(0.5, 0.5));
                 float grayColor = (baseColor.r + baseColor.g + baseColor.b) * 0.333;
                 float grayness = max((centerDis - 0.33) * 2.0, 0.0);
                 grayColor *= (1.0 - grayness* 0.9);
                 color = vec4(mix(baseColor.r, grayColor, grayness), 
                            mix(baseColor.g, grayColor, grayness),
                            mix(baseColor.b, grayColor, grayness),
                            baseColor.a);
                 
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
            self.display = pygame.display.get_surface()

    def change_shader(self):
        if not self.cpu_only:
            self.style = (self.style + 1) % 3
            self.prog['mode'] = self.style
            print(f"Shader mode changed to: {self.style}")

    def render(self):
        if not (self.cpu_only):
            texture_data = self.screen.get_view('1')

            self.screen_texture.write(texture_data)
            self.ctx.clear(14 / 255, 40 / 255, 66 / 255)
            self.screen_texture.use()
            self.vao.render()
            pygame.display.flip()
        else:
            self.display.blit(self.screen, (0, 0))
            pygame.display.update()

    def full_screen(self, REAL_RES):
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
