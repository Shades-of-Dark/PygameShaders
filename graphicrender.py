import pygame, moderngl, struct
from array import array
import numpy as np


def generate_gaussian_kernel_1d(radius, sigma):
    """
    Generates a 1D Gaussian kernel for separable blur.
    Returns weights from center (index 0) to radius.

    Args:
        radius (int): Half-width of the kernel
        sigma (float): Standard deviation of the Gaussian function

    Returns:
        numpy.ndarray: 1D Gaussian kernel weights [center, +1, +2, ..., +radius]
    """
    weights = []

    # Calculate weights from center (0) to radius
    for i in range(int(radius + 1)):
        weight = np.exp(-(i ** 2) / (2 * sigma ** 2))
        weights.append(weight)

    # Normalize: center weight + 2 * sum of offset weights = 1
    total = weights[0] + 2 * sum(weights[1:])
    weights = [w / total for w in weights]

    return np.array(weights)


class GraphicsEngine():
    texture_id = 0

    def __init__(self, screen: pygame.Surface, style: int, display_size=None, ui_scale=1.0):
        self.screen = screen
        self.display_size = display_size or pygame.display.get_surface().get_size()
        self.ui_scale = ui_scale
        self.ctx = moderngl.create_context()
        self.style = style

        # Load common vertex shader source
        vert_shader = open("shaderfx/vertex_shader.vert").read()

        # List of effect fragment shader filenames keyed by effect name
        effects = {
            "bright_pass": "shaderfx/bright_pass.frag",
            "blur_pass": "shaderfx/blur_pass.frag",
            "bloom": "shaderfx/bloom.frag",
            "vignette": "shaderfx/vignette.frag",
            "saturation": "shaderfx/saturation.frag",
            "chromatic_aberration": "shaderfx/chromatic_abberation.frag",
            "point_light": "shaderfx/pointlight.frag",
            "shadow_pass": "shaderfx/shadowpass.frag",
            "scanline": "shaderfx/scanline.frag",
            "distortion": "shaderfx/distortion.frag",
            "flicker": "shaderfx/flicker.frag",
            "phosphormask": "shaderfx/phosphormask.frag",
            "gaussianblur": "shaderfx/gaussianblur.frag",
            "pulse": "shaderfx/pulse.frag",
            "contrast": "shaderfx/constrast.frag",
            # Add more shader filenames here as needed
        }

        # Dictionaries to hold compiled shader programs and VAOs
        self.progs = {}
        self.vaos = {}

        # Load each shader program and create VAO for fullscreen quad
        consistent_quad_buffer = array('f', [
            -1.0, 1.0, 0.0, 1.0,  # top-left (flipped Y)
            1.0, 1.0, 1.0, 1.0,  # top-right
            -1.0, -1.0, 0.0, 0.0,  # bottom-left
            1.0, -1.0, 1.0, 0.0,  # bottom-right
        ])

        self.fullscreen_vbo = self.ctx.buffer(consistent_quad_buffer)
        self.position_vbo = self.ctx.buffer(consistent_quad_buffer)  # Will
        self.ibo = self.ctx.buffer(struct.pack('6I', 0, 1, 2, 1, 2, 3))

        for effect_name, frag_path in effects.items():
            frag_shader_source = open(frag_path, "r").read()
            program = self.ctx.program(vertex_shader=vert_shader, fragment_shader=frag_shader_source)
            vao = self.ctx.vertex_array(program, [(self.fullscreen_vbo, '2f 2f', 'vert', 'in_text')],
                                        index_buffer=self.ibo)
            self.progs[effect_name] = program
            self.vaos[effect_name] = vao
        self.phosphortex1 = pygame.image.load("textures/phosphordot.png").convert()
        self.phosphortex2 = pygame.image.load("textures/phosphormask.png").convert()
        self.phosphortex3 = pygame.image.load("textures/slotmask.png").convert()
        # First texture (dots)

        texture_data = pygame.image.tostring(self.phosphortex1, "RGB", True)
        width1, height1 = self.phosphortex1.get_size()
        phosphordot = self.ctx.texture((width1, height1), 3, texture_data)
        phosphordot.repeat_x = True
        phosphordot.repeat_y = True
        phosphordot.filter = (moderngl.NEAREST, moderngl.NEAREST)
        phosphordot.use(location=3)

        # Second texture (lines)
        lin_data = pygame.image.tostring(self.phosphortex2, "RGB", True)
        width2, height2 = self.phosphortex2.get_size()
        phosphorlin = self.ctx.texture((width2, height2), 3, lin_data)
        phosphorlin.repeat_x = True
        phosphorlin.repeat_y = True
        phosphorlin.filter = (moderngl.NEAREST, moderngl.NEAREST)
        phosphorlin.use(location=4)

        # third texture (slots)
        slot_data = pygame.image.tostring(self.phosphortex3, "RGB", True)
        width3, height3 = self.phosphortex3.get_size()
        phosphorslot = self.ctx.texture((width3, height3), 3, slot_data)
        phosphorslot.repeat_x = True
        phosphorslot.repeat_y = True
        phosphorslot.filter = (moderngl.NEAREST, moderngl.NEAREST)
        phosphorslot.use(location=5)
        # You'll need to handle phosphorSize differently now since textures have different sizes
        self.progs["phosphormask"]["screenResolution"] = self.screen.get_size()

        # Base rendering shader (could also be included in effects if you want)
        base_frag_shader = '''
            #version 330 core
            precision mediump float;
            uniform sampler2D Texture;
            in vec2 v_text;
            out vec4 color;
            void main() {
                vec4 baseColor = texture(Texture, v_text);
                color = baseColor;
            }
        '''
        self.progs["base"] = self.ctx.program(vertex_shader=vert_shader, fragment_shader=base_frag_shader)
        self.vaos["base"] = self.ctx.vertex_array(self.progs["base"],
                                                  [(self.fullscreen_vbo, '2f 2f', 'vert', 'in_text')],
                                                  index_buffer=self.ibo)
        self.vaos["pos"] = self.ctx.vertex_array(self.progs["base"],
                                                 [(self.position_vbo, '2f 2f', 'vert', 'in_text')],
                                                 index_buffer=self.ibo)
        # Rectangle rendering program
        self.rect_prog = self.ctx.program(
            vertex_shader='''
                #version 330 core
                in vec2 vert;
                void main() {
                    gl_Position = vec4(vert, 0.0, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330 core
                precision mediump float;
                uniform vec3 color;
                out vec4 fragColor;
                void main() {
                    fragColor = vec4(color, 1.0);
                }
            '''
        )

        # Initialize textures and framebuffers
        screen_size = self.screen.get_size()
        self.textures = [
            self.ctx.texture(screen_size, components=4),
            self.ctx.texture(screen_size, components=4)
        ]

        # Add a third texture to store the original scene for bloom
        self.original_texture = self.ctx.texture(screen_size, components=4)

        black_data = bytes([0, 0, 0, 255] * (screen_size[0] * screen_size[1]))
        for tex in self.textures:
            tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
            tex.repeat_x = False
            tex.repeat_y = False
            tex.write(black_data)

        self.original_texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.original_texture.repeat_x = False
        self.original_texture.repeat_y = False
        self.original_texture.write(black_data)

        self.framebuffers = [
            self.ctx.framebuffer(color_attachments=[self.textures[0]]),
            self.ctx.framebuffer(color_attachments=[self.textures[1]])
        ]

        self.read_idx = 0
        self.write_idx = 1

        # Initialize with screen texture
        self.update_screen_texture(screen)

    @property
    def read_texture(self):
        return self.textures[self.read_idx]

    @property
    def write_framebuffer(self):
        return self.framebuffers[self.write_idx]

    def swap(self):
        self.read_idx, self.write_idx = self.write_idx, self.read_idx

    def clear(self):
        self.framebuffers[0].clear()
        self.framebuffers[1].clear()

    def apply_point_light(self, lightPosition, lightColor, intensity, radius):

        uniforms = {"lightColor": lightColor, "lightPosition": lightPosition, "intensity": intensity, "radius": radius}
        self.render_effect("point_light", uniforms)

    def chromatic_aberration(self, mouseFocusPoint, redOffset, greenOffset, blueOffset):
        uniforms = {"mouseFocusPoint": mouseFocusPoint, "redOffset": redOffset, "greenOffset": greenOffset,
                    "blueOffset": blueOffset}
        self.render_effect("chromatic_aberration", uniforms=uniforms)

    def vignette_pass(self, defaultIntensity, defaultRadius):
        """Apply vignette effect - ONLY applies the effect, doesn't render to screen"""
        uniforms = {
            'defaultIntensity': defaultIntensity,
            'defaultRadius': defaultRadius
        }
        self.render_effect("vignette", uniforms=uniforms)

    def vignette(self, defaultIntensity, defaultRadius):
        """Apply vignette effect (FIXED - no longer renders to screen automatically)"""
        self.vignette_pass(defaultIntensity, defaultRadius)

    def apply_saturation(self, maxSaturation, focusPoint, radius):
        self.render_effect("saturation",
                           {"maxSaturation": maxSaturation, "focusPoint": focusPoint, "radius": radius})

    def bright_pass(self, threshold):
        """Extract bright areas from the image"""
        uniforms = {"threshold": threshold}
        # Check if threshold uniform exists in shader

        self.render_effect("bright_pass", uniforms=uniforms)

    def blur_pass(self, radius, horizontal=True):
        """Apply blur in specified direction"""
        # Ensure radius is at least 1 and convert to int
        radius = max(1, int(radius))

        # Check shader limits
        MAX_ELEMENTS = 81
        if radius >= MAX_ELEMENTS:
            print(f"Warning: Radius {radius} exceeds shader limit. Clamping to {MAX_ELEMENTS - 1}")
            radius = MAX_ELEMENTS - 1

        # Generate 1D Gaussian weights (center to radius)
        sigma = max(0.5, radius / 3.0)  # Adaptive sigma
        weights = generate_gaussian_kernel_1d(radius, sigma)

        # Convert to list and pad with zeros up to MAX_ELEMENTS
        padded_weights = weights.tolist()
        while len(padded_weights) < MAX_ELEMENTS:
            padded_weights.append(0.0)

        screen_size = self.screen.get_size()
        uniforms = {
            "direction": (1.0, 0.0) if horizontal else (0.0, 1.0),
            "texelSize": (1.0 / screen_size[0], 1.0 / screen_size[1]),
            'weights': padded_weights,  # Use padded weights, not sliced
            'radius': float(radius)  # Pass actual radius as float
        }

        self.render_effect("blur_pass", uniforms=uniforms)

    def bloom_pass(self, bloom_strength=1.0):
        """Combine bloom with original image - renders to write framebuffer, not screen"""

        # Render to write framebuffer instead of screen
        self.write_framebuffer.use()
        self.ctx.viewport = (0, 0, *self.screen.get_size())
        self.write_framebuffer.clear()

        # Bind original scene texture to unit 0
        self.original_texture.use(location=0)
        self.progs["bloom"]['Texture'] = 0

        # Bind bloom texture (blurred bright areas) to unit 1
        self.read_texture.use(location=1)
        self.progs["bloom"]['bloom'] = 1

        # Set bloom strength
        self.progs["bloom"]['bloom_strength'] = bloom_strength

        # Render fullscreen quad
        self.vaos["bloom"].render()

        # Swap buffers so result becomes the read texture
        self.swap()

    def apply_bloom(self, threshold, blurRadius, intensity):
        """Apply full bloom effect in multiple passes.

            Args:
                threshold (float): Brightness threshold for extracting bright areas.
                blurRadius (float): Controls blur amount, converted to iterations.
                intensity (float): Strength of the bloom effect.
            """
        # Step 0: Save original scene to a separate texture (self.original_texture)
        self.write_framebuffer.use()
        self.write_framebuffer.clear()

        # Render current read texture (the full scene) into write framebuffer
        self.read_texture.use(location=0)
        self.progs["base"]['Texture'] = 0
        self.vaos["base"].render()

        # Read pixels from the write framebuffer and copy into original_texture
        # This stores the original scene so bloom can later be combined with it
        data = self.write_framebuffer.read(components=4)
        self.original_texture.write(data)

        # Determine how many blur passes based on blurRadius
        blur_iterations = 1

        # Step 1: Bright pass - extract bright spots (highlights)
        # This writes bright areas into the write framebuffer, swapping ping-pong buffers
        self.bright_pass(threshold)  # calls render_effect, which calls swap()

        # Step 2: Blur passes - repeatedly blur horizontally and vertically
        # Each pass calls render_effect and swaps buffers automatically
        for _ in range(blur_iterations):
            self.blur_pass(blurRadius, horizontal=True)
            self.blur_pass(blurRadius, horizontal=False)

        self.bloom_pass(intensity)

        # At this point, the final bloom combined texture is in read_texture ready for rendering

    def apply_vignette(self, intensity, radius):
        """Apply vignette effect - FIXED version"""
        self.vignette_pass(intensity, radius)

    def apply_scanline(self, intensity, frequency):
        self.render_effect("scanline", uniforms={"intensity": intensity, "frequency": frequency})

    def render_effect(self, effect_name, uniforms=None):
        """Render effect by name, applying uniforms dynamically."""
        program = self.progs.get(effect_name)
        vao = self.vaos.get(effect_name)
        if not program or not vao:
            raise ValueError(f"Effect '{effect_name}' not found")

        self.write_framebuffer.use()
        self.ctx.viewport = (0, 0, *self.screen.get_size())
        self.write_framebuffer.clear()

        # Bind read texture
        self.read_texture.use(location=0)
        program['Texture'] = 0

        if uniforms:
            for name, value in uniforms.items():
                try:
                    program[name] = value
                except KeyError:
                    # Uniform doesn't exist, ignore or log warning
                    pass

        vao.render()
        self.swap()

    def update_screen_texture(self, surface):
        """Update the read texture with pygame surface data"""
        # Make sure we're updating with the correct surface data
        data = pygame.image.tostring(surface, "RGBA", True)
        self.read_texture.write(data)

    def render_to_screen(self):
        """Render the current read texture to screen at the specified position"""
        self.ctx.screen.use()
        self.ctx.viewport = (0, 0, *self.display_size)
        self.ctx.clear(26 / 255.0, 26 / 255.0, 26 / 255.0, 1.0)

        self.read_texture.use(location=0)
        self.progs["base"]["Texture"] = 0

        # Use positioned VAO for screen output
        self.vaos["pos"].render()

    def surf_to_texture(self, surf):
        tex = self.ctx.texture(surf.get_size(), 4)
        tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        tex.swizzle = "BGRA"
        tex.write(surf.get_view("1"))
        return tex

    def set_position_and_size(self, x, y, width, height):
        """Update the position buffer for rendering at specific screen coordinates"""
        display_width, display_height = self.display_size

        left = (x / display_width) * 2 - 1
        right = ((x + width) / display_width) * 2 - 1
        bottom = ((display_height - y - height) / display_height) * 2 - 1
        top = ((display_height - y) / display_height) * 2 - 1

        quad_data = [
            left, top, 0.0, 1.0,  # Keep flipped Y texture coordinates
            right, top, 1.0, 1.0,
            left, bottom, 0.0, 0.0,
            right, bottom, 1.0, 0.0,
        ]

        # Update only the position buffer, not the fullscreen buffer
        self.position_vbo.write(struct.pack('16f', *quad_data))

    def render_screen_rect_outline(self, x, y, width, height, color, thickness=1.0):
        """Render an outlined rectangle to screen with given thickness"""
        display_width, display_height = self.display_size

        left = (x / display_width) * 2 - 1
        right = ((x + width) / display_width) * 2 - 1
        bottom = ((display_height - y - height) / display_height) * 2 - 1
        top = ((display_height - y) / display_height) * 2 - 1

        # Vertices in order: bottom-left, bottom-right, top-right, top-left
        vertices = [left, bottom, right, bottom, right, top, left, top]

        vbo = self.ctx.buffer(struct.pack('8f', *vertices))
        vao = self.ctx.vertex_array(self.rect_prog, [(vbo, '2f', 'vert')])

        self.rect_prog['color'] = (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)
        self.ctx.line_width = thickness
        vao.render(mode=self.ctx.LINE_LOOP)

        vbo.release()
        vao.release()

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
        ui_data = pygame.image.tostring(ui_surface, "RGBA", False)
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

    def render_screen_rect(self, x, y, width, height, color):
        """Render a colored rectangle to screen"""
        display_width, display_height = self.display_size

        left = (x / display_width) * 2 - 1
        right = ((x + width) / display_width) * 2 - 1
        bottom = ((display_height - y - height) / display_height) * 2 - 1
        top = ((display_height - y) / display_height) * 2 - 1

        vertices = [left, bottom, right, bottom, left, top, right, top]
        indices = [0, 1, 2, 1, 2, 3]

        vbo = self.ctx.buffer(struct.pack('8f', *vertices))
        ibo = self.ctx.buffer(struct.pack('6I', *indices))
        vao = self.ctx.vertex_array(self.rect_prog, [(vbo, '2f', 'vert')], index_buffer=ibo)

        self.rect_prog['color'] = (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)
        self.ctx.line_width = 1.0
        vao.render()

        vbo.release()
        ibo.release()
        vao.release()

    def draw_line(self, start, end, color, thickness=1.0):
        """Draw a line between two points"""
        display_width, display_height = self.display_size

        x1 = (start[0] / display_width) * 2 - 1
        y1 = ((display_height - start[1]) / display_height) * 2 - 1
        x2 = (end[0] / display_width) * 2 - 1
        y2 = ((display_height - end[1]) / display_height) * 2 - 1

        vertices = [x1, y1, x2, y2]

        vbo = self.ctx.buffer(struct.pack('4f', *vertices))
        vao = self.ctx.vertex_array(self.rect_prog, [(vbo, '2f', 'vert')])

        self.rect_prog['color'] = (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)
        self.ctx.line_width = thickness
        vao.render(mode=moderngl.LINES)

        vbo.release()
        vao.release()

    def render_surface_at_position(self, surface, x, y):
        """Render a pygame surface at screen coordinates"""
        surface_width = surface.get_width()
        surface_height = surface.get_height()
        surface_data = pygame.image.tostring(surface, "RGBA", False)

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

    def apply_contrast(self, brightness, contrast):
        self.render_effect("contrast", {"brightness": brightness, "contrast": contrast})

    def apply_distortion(self, distortionStrength):
        self.render_effect("distortion", {"distortion_strength": distortionStrength})

    def apply_flicker(self, noiseIntensity, noiseScale, noiseSpeed):
        self.render_effect("flicker",
                           {"noiseIntensity": noiseIntensity, "noiseScale": noiseScale, "noiseSpeed": noiseSpeed})

    def apply_phosphor_mask(self, phosphorScale, blendStrength, pattern):
        texture_unit = 3
        offset = (0.5, 0.0)
        match pattern:
            case "aperture grille":
                texture_unit = 4
                # Row offset: floor(scaledPos.y) * 0.5, no column offset
                offset = (0.0, 0.0)
            case "slot mask":
                texture_unit = 5
                offset = (0.0, 0.5)

        size = self.phosphortex1.get_size()

        match texture_unit:
            case 3:
                size = self.phosphortex1.get_size()
            case 4:
                size = self.phosphortex2.get_size()
            case 5:
                size = self.phosphortex3.get_size()

        self.render_effect("phosphormask", {
            "phosphorScale": phosphorScale,
            "phosphorSize": size,
            "blendStrength": blendStrength,
            "phosphorTex": texture_unit,
            "offset": offset,
        })

    def apply_pulsing(self, pulseSpeed, pulseStrength):
        self.render_effect("pulse", {"pulseSpeed": pulseSpeed, "pulseStrength": pulseStrength})

    def apply_blur(self, blurRadius):
        """Apply blur with dynamic radius"""
        # Ensure radius is at least 1 and convert to int
        radius = max(1, int(blurRadius))

        # Check shader limits
        MAX_ELEMENTS = 81
        if radius >= MAX_ELEMENTS:
            radius = MAX_ELEMENTS - 1

        # Generate 1D Gaussian weights (center to radius)
        sigma = max(0.5, radius / 3.0)  # Adaptive sigma
        weights = generate_gaussian_kernel_1d(radius, sigma)

        # Convert to list and pad with zeros up to MAX_ELEMENTS
        padded_weights = weights.tolist()
        while len(padded_weights) < MAX_ELEMENTS:
            padded_weights.append(0.0)

        screen_size = self.screen.get_size()

        # Apply horizontal and vertical passes
        for direction in [(1.0, 0.0), (0.0, 1.0)]:
            uniforms = {
                "direction": direction,
                "texelSize": (1.0 / screen_size[0], 1.0 / screen_size[1]),
                'weights': padded_weights,
                'radius': float(radius)
            }

            self.render_effect("gaussianblur", uniforms=uniforms)

    def render_text(self, text, x, y, font, color=(255, 255, 255)):
        """Render text at screen coordinates"""
        text_surface = font.render(text, True, color)
        self.render_surface_at_position(text_surface, x, y)

    def render(self):
        """Basic render method - just displays current texture"""
        self.render_to_screen()

    def __call__(self):
        return self.render()
