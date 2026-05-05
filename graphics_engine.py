import pygame, moderngl
import struct
from shader_manager import ShaderManager
from texture_atlas import TextureAtlas
from instance_renderer import InstanceRenderer


class GraphicsEngine():
    texture_id = 0

    def __init__(self, screen: pygame.Surface, style: int, display_size=None):
        self.screen = screen
        self.display_size = display_size or pygame.display.get_surface().get_size()

        self.ctx = moderngl.create_context()
        self.style = style

        self.textureAtlas = TextureAtlas(self.ctx)
        self.shaderManager = ShaderManager(self.ctx, self.screen, self.display_size)
        self.instanceRenderer = InstanceRenderer(self.ctx)
        self.instanceRenderer.set_atlas(self.textureAtlas)
        self.lights = []

    def add_light(self, light):
        self.lights.append(light)

    def clear_lights(self):
        self.lights.clear()

    # Texture atlas methods
    def load_sprite(self, surface, name=None):
        self.textureAtlas.submit_sprite(surface, name)

    def load_sprites_batch(self, surfaces):
        return self.textureAtlas.submit_sprites_batch(surfaces)

    def add_sprite_instance(self, sprite_name, pos, rotation=0, scale=(1, 1), color=(1, 1, 1, 1)):
        self.instanceRenderer.add_sprite_instance(sprite_name, pos, rotation, scale, color)

    def clear_instances(self):
        self.instanceRenderer.clear_instances()

    def get_instance_count(self):
        return self.instanceRenderer.instance_count

    def is_instance_buffer_full(self):
        return self.instanceRenderer.max_instances < self.instanceRenderer.instance_count

    def apply_effects_and_render(self):
        self.shaderManager.render_to_screen()

    def render_instances(self):
        # Render instances to ShaderManager's write framebuffer
        target_texture = self.shaderManager.write_framebuffer.color_attachments[0]
        self.instanceRenderer.render(
            self.screen.get_width(),
            self.screen.get_height(),
            target_texture  # Render TO the shader manager's framebuffer
        )

    # Add this to your main.py after execute_node_chain:
    # engine.debug_texture_alpha()
    def render_ui_to_gldisplay(self, ui_surface, dest_x=0, dest_y=0, dest_width=None, dest_height=None,
                               source_x=0, source_y=0, source_width=None, source_height=None):
        """
        Render a UI surface to the GL display at specified coordinates and size.

        Args:
            ui_surface: pygame.Surface to render
            dest_x, dest_y: Destination coordinates on GL display (top-left)
            dest_width, dest_height: Destination size (None = use source size)
            source_x, source_y: Source region start coordinates
            source_width, source_height: Source region size (None = full surface)
        """
        # Get source dimensions
        surf_width = ui_surface.get_width()
        surf_height = ui_surface.get_height()

        # Set default source region to full surface
        if source_width is None:
            source_width = surf_width - source_x
        if source_height is None:
            source_height = surf_height - source_y

        # Set default destination size to source size
        if dest_width is None:
            dest_width = source_width
        if dest_height is None:
            dest_height = source_height

        # Create texture from UI surface
        ui_data = pygame.image.tobytes(ui_surface, "RGBA", False)
        ui_texture = self.ctx.texture((surf_width, surf_height), 4, ui_data)
        ui_texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        ui_texture.repeat_x = False
        ui_texture.repeat_y = False

        # Calculate normalized texture coordinates for source region
        tex_left = source_x / surf_width
        tex_right = (source_x + source_width) / surf_width
        tex_top = source_y / surf_height
        tex_bottom = (source_y + source_height) / surf_height

        # Calculate normalized device coordinates for destination
        display_width, display_height = self.display_size

        ndc_left = (dest_x / display_width) * 2 - 1
        ndc_right = ((dest_x + dest_width) / display_width) * 2 - 1
        ndc_bottom = ((display_height - dest_y - dest_height) / display_height) * 2 - 1
        ndc_top = ((display_height - dest_y) / display_height) * 2 - 1

        # Create vertex data (position + texture coordinates)
        vertices = [
            ndc_left, ndc_top, tex_left, tex_top,  # top-left
            ndc_right, ndc_top, tex_right, tex_top,  # top-right
            ndc_left, ndc_bottom, tex_left, tex_bottom,  # bottom-left
            ndc_right, ndc_bottom, tex_right, tex_bottom,  # bottom-right
        ]
        indices = [0, 1, 2, 1, 2, 3]

        # Create shader program if it doesn't exist
        if not hasattr(self, 'ui_render_prog'):
            self.ui_render_prog = self.ctx.program(
                vertex_shader='''
                    #version 330 core
                    in vec2 vert;
                    in vec2 texCoord;
                    out vec2 v_texCoord;
                    void main() {
                        gl_Position = vec4(vert, 0.0, 1.0);
                        v_texCoord = texCoord;
                    }
                ''',
                fragment_shader='''
                    #version 330 core
                    precision mediump float;
                    uniform sampler2D uiTexture;
                    in vec2 v_texCoord;
                    out vec4 fragColor;
                    void main() {
                        vec4 texColor = texture(uiTexture, v_texCoord);
                        // Handle transparency - you can modify this blending as needed
                        fragColor = texColor;
                    }
                '''
            )

        # Create buffers and VAO
        vbo = self.ctx.buffer(struct.pack('16f', *vertices))
        ibo = self.ctx.buffer(struct.pack('6I', *indices))
        vao = self.ctx.vertex_array(self.ui_render_prog,
                                    [(vbo, '2f 2f', 'vert', 'texCoord')],
                                    index_buffer=ibo)

        # Use screen framebuffer (GL display)
        self.ctx.screen.use()

        # Enable blending for transparency support
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        # Bind texture and render
        ui_texture.use(location=0)
        self.ui_render_prog['uiTexture'] = 0
        vao.render()

        # Clean up
        self.ctx.disable(moderngl.BLEND)
        ui_texture.release()
        vbo.release()
        ibo.release()
        vao.release()

    def render_surface_at_position(self, surface, x, y):
        """Render a pygame surface at screen coordinates"""
        surface_width = surface.get_width()
        surface_height = surface.get_height()
        surface_data = pygame.image.tobytes(surface, "RGBA", False)

        surface_texture = self.ctx.texture((surface_width, surface_height), 4, surface_data)
        surface_texture.repeat_x = False
        surface_texture.repeat_y = False

        if not hasattr(self, 'surface_prog'):
            self.surface_prog = self.ctx.program(
                vertex_shader='''
                        #version 330 core
                        in vec2 vert;
                        in vec2 texCoord;
                        out vec2 v_texCoord;
                        void main() {
                            gl_Position = vec4(vert, 0.0, 1.0);
                            v_texCoord = texCoord;
                        }
                    ''',
                fragment_shader='''
                        #version 330 core
                        precision mediump float;
                        uniform sampler2D surfaceTexture;
                        in vec2 v_texCoord;
                        out vec4 fragColor;
                        void main() {
                            vec4 texColor = texture(surfaceTexture, v_texCoord);
                            if (texColor.a < 0.1) discard;
                            fragColor = texColor;
                        }
                    '''
            )

        display_width, display_height = self.display_size

        left = (x / display_width) * 2 - 1
        right = ((x + surface_width) / display_width) * 2 - 1
        bottom = ((display_height - y - surface_height) / display_height) * 2 - 1
        top = ((display_height - y) / display_height) * 2 - 1

        vertices = [
            left, top, 0.0, 0.0,
            right, top, 1.0, 0.0,
            left, bottom, 0.0, 1.0,
            right, bottom, 1.0, 1.0,
        ]
        indices = [0, 1, 2, 1, 2, 3]

        vbo = self.ctx.buffer(struct.pack('16f', *vertices))
        ibo = self.ctx.buffer(struct.pack('6I', *indices))
        vao = self.ctx.vertex_array(self.surface_prog, [(vbo, '2f 2f', 'vert', 'texCoord')], index_buffer=ibo)

        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        surface_texture.use()
        vao.render()

        self.ctx.disable(moderngl.BLEND)

        surface_texture.release()
        vbo.release()
        ibo.release()
        vao.release()
