from utils import generate_gaussian_kernel_1d
import pygame
import moderngl
import struct
from array import array
import math as m


class ShaderManager:
    def __init__(self, ctx, screen, display_size=None):
        self.ctx = ctx
        self.screen = screen
        # Load common vertex shader source
        vert_shader = open("shaderfx/vertex_shader.vert").read()
        self.width = screen.get_width()
        self.height = screen.get_height()
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
            "directional_light": "shaderfx/directionallight.frag",
            "gbuffer": "shaderfx/gbuffer.frag",
            "normal_map": "shaderfx/normalgen.frag",
            "deferredlighting": "shaderfx/deferredlights.frag",
            "pixelation": "shaderfx/quantizedrendering.glsl",
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

        # Initialize textures and framebuffers
        screen_size = self.screen.get_size()
        self.textures = [
            self.ctx.texture(screen_size, components=4),
            self.ctx.texture(screen_size, components=4)
        ]

        black_data = bytes([0, 0, 0, 0] * (screen_size[0] * screen_size[1]))
        # Add a third texture to store the original scene for bloom
        self.original_texture = self.ctx.texture(screen_size, components=4)
        self.original_texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.original_texture.repeat_x = False
        self.original_texture.repeat_y = False
        self.original_texture.write(black_data)

        for tex in self.textures:
            tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
            tex.repeat_x = False
            tex.repeat_y = False
            tex.write(black_data)

        self.framebuffers = [
            self.ctx.framebuffer(color_attachments=[self.textures[0]]),
            self.ctx.framebuffer(color_attachments=[self.textures[1]])
        ]

        self.read_idx = 0
        self.write_idx = 1

        for effect_name, frag_path in effects.items():
            frag_shader_source = open(frag_path, "r").read()
            program = self.ctx.program(vertex_shader=vert_shader, fragment_shader=frag_shader_source)

            if effect_name == "gbuffer":
                with  open("shaderfx/gbuffer.vert", "r") as f:
                    vert_shader_buffer = f.read()
                program = self.ctx.program(vertex_shader=vert_shader_buffer, fragment_shader=frag_shader_source)
                vao = self.ctx.vertex_array(program, [(self.fullscreen_vbo, '2f 2f', 0, 1)],
                                            index_buffer=self.ibo)
            else:
                vao = self.ctx.vertex_array(program, [(self.fullscreen_vbo, '2f 2f', 'vert', 'in_text')],
                                            index_buffer=self.ibo)

            self.progs[effect_name] = program
            self.vaos[effect_name] = vao
        self.phosphortex1 = pygame.image.load("textures/phosphordot.png").convert()
        self.phosphortex2 = pygame.image.load("textures/phosphormask.png").convert()
        self.phosphortex3 = pygame.image.load("textures/slotmask.png").convert()
        # First texture (dots)

        texture_data = pygame.image.tobytes(self.phosphortex1, "RGB", True)
        width1, height1 = self.phosphortex1.get_size()
        phosphordot = self.ctx.texture((width1, height1), 3, texture_data)
        phosphordot.repeat_x = True
        phosphordot.repeat_y = True
        phosphordot.filter = (moderngl.NEAREST, moderngl.NEAREST)
        phosphordot.use(location=3)
        self.display_size = display_size or pygame.display.get_surface().get_size()

        # Second texture (lines)
        lin_data = pygame.image.tobytes(self.phosphortex2, "RGB", True)
        width2, height2 = self.phosphortex2.get_size()
        phosphorlin = self.ctx.texture((width2, height2), 3, lin_data)
        phosphorlin.repeat_x = True
        phosphorlin.repeat_y = True
        phosphorlin.filter = (moderngl.NEAREST, moderngl.NEAREST)
        phosphorlin.use(location=4)

        # third texture (slots)
        slot_data = pygame.image.tobytes(self.phosphortex3, "RGB", True)
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

        # Initialize with screen texture
        self.update_screen_texture(screen)

        self.surface_texture_cache = {}
        self.gbuffer_albedo = self.ctx.texture(self.screen.get_size(), components=4, dtype="f1")
        self.gbuffer_normal = self.ctx.texture(self.screen.get_size(), components=4, dtype="f1")
        self.gbuffer_albedo.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.gbuffer_normal.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.gbuffer_albedo.repeat_x = False
        self.gbuffer_albedo.repeat_y = False
        self.gbuffer_normal.repeat_x = False
        self.gbuffer_normal.repeat_y = False
        self.gbuffer_fbo = self.ctx.framebuffer(color_attachments=[self.gbuffer_albedo, self.gbuffer_normal])
        print(self.gbuffer_fbo.color_attachments)
        print(self.gbuffer_albedo.glo)
        print(self.gbuffer_normal.glo)

        # Framebuffer for normal map generation

        # Rectangle rendering program

    def update_screen_texture(self, surface):
        """Update the read texture with pygame surface data"""
        # Make sure we're updating with the correct surface data
        data = pygame.image.tobytes(surface, "RGBA", True)
        self.read_texture.write(data)

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

    def apply_pixelation(self, pixelSize=320.0):
        """Apply base pixelation effect when needed"""
        uniforms = {"pixelSize": 1.0 / pixelSize}
        self.render_effect("pixelation", uniforms)

    def render_to_screen(self):
        """Render the current read texture to screen at the specified position"""
        self.ctx.screen.use()
        self.ctx.viewport = (0, 0, *self.display_size)
        self.ctx.clear(26 / 255.0, 26 / 255.0, 26 / 255.0, 0.0)

        self.read_texture.use(location=0)
        self.progs["base"]["Texture"] = 0

        # Use positioned VAO for screen output
        self.vaos["pos"].render()

    def apply_point_light(self, lightPosition, lightColor, intensity, radius, lightAngle,
                          minAngle=20.0, maxAngle=90.0, volumetricIntensity=0.2):

        uniforms = {
            "lightPosition": lightPosition,
            "lightColor": lightColor,
            "lightAngle": lightAngle,
            "intensity": intensity,
            "radius": radius,
            "minAngle": minAngle,
            "maxAngle": maxAngle,
            "volumetricIntensity": volumetricIntensity
        }

        self.render_effect("point_light", uniforms)

    def geometry_pass(self, scene_sprites):
        self.gbuffer_fbo.use()
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)

        gbuffer_prog = self.progs["gbuffer"]
        gbuffer_prog["screenSize"] = (self.width, self.height)
        for sprite, pos, sprite_type in scene_sprites:  # Add sprite_type parameter
            sprite_tex = self.surf_to_texture(sprite)
            sprite_tex.use(location=0)
            gbuffer_prog["Texture"] = 0

            gbuffer_prog["spritePos"].value = pos
            gbuffer_prog["spriteSize"].value = sprite.get_size()

            # Laightr-style parameters

            # Enhance controls (inner surface detail)
            gbuffer_prog["enhanceHeight"] = 2.0  # Height control (0.0-1.0+)
            gbuffer_prog["enhanceSoft"] = 1.0  # Blur amount for enhance (0.0-1.0)

            # Bump controls (edge volume from distance transform)
            gbuffer_prog["bumpHeight"] = 5.0  # Height control for bump (0.0-1.0+)
            gbuffer_prog["bumpDistance"] = 6.0  # Distance from edge (0.0-1.0)
            gbuffer_prog["bumpSoft"] = 1.5  # Blur amount for bump (0.0-1.0)
            gbuffer_prog["bumpSoftRadio"] = True  # True=soft/spherical, False=abrupt/linear

            # Axis controls (for different engines)
            gbuffer_prog["invertX"] = False  # Invert X component
            gbuffer_prog["invertY"] = False  # Set to True for Godot engine
            # Set normal generation based on sprite type
            if sprite_type == "sky":
                gbuffer_prog["useNormalMap"] = False
                gbuffer_prog["generateSphericalNormals"] = False
                gbuffer_prog["normalType"] = 3  # Custom normals for sky
            elif sprite_type == "ground":

                gbuffer_prog["useNormalMap"] = False
                gbuffer_prog["generateSphericalNormals"] = False
                gbuffer_prog["normalType"] = 0  # Flat normals
            elif sprite_type == "object":
                gbuffer_prog["useNormalMap"] = False
                gbuffer_prog["generateSphericalNormals"] = True
                gbuffer_prog["normalType"] = 4  # Spherical for round objects

            else:
                gbuffer_prog["useNormalMap"] = False
                gbuffer_prog["generateSphericalNormals"] = False
                gbuffer_prog["normalType"] = 0  # Flat normals

            self.vaos["gbuffer"].render()

    def render(self):
        """Basic render method - just displays current texture"""
        self.render_to_screen()

    def surf_to_texture(self, surf, small=False) -> moderngl.Texture:
        # Create a cache key based on surface properties and small flag
        cache_key = (id(surf), small)

        # Check if this surface was already converted with these settings
        if cache_key in self.surface_texture_cache:
            return self.surface_texture_cache[cache_key]

        # Convert and create texture as before
        if surf.get_bitsize() != 32:
            surf = surf.convert_alpha()  # This makes it 32-bit RGBA

        tex = self.ctx.texture(surf.get_size(), 4)
        if not small:
            tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        else:
            tex.filter = (moderngl.LINEAR, moderngl.LINEAR)

        # Fix color channel ordering - pygame is BGRA, OpenGL expects RGBA
        tex.swizzle = "BGRA"  # This tells OpenGL how to interpret the data
        tex.write(surf.get_view("1"))

        # Cache the texture
        self.surface_texture_cache[cache_key] = tex

        return tex

    def apply_deferred_lighting(self, lights):

        debug_lights = False

        if debug_lights:

            num_lights = 3
        else:
            num_lights = min(len(lights), 32)

        data = bytearray()

        # Header: numLights + padding
        data += struct.pack('4i', num_lights, 0, 0, 0)

        if debug_lights:
            test_lights = [
                {
                    'pos': (0.5, 0.5),
                    'color': (1.0, 0.0, 0.0),
                    'intensity': 1.0,
                    'radius': 0.3,
                    'directionAngle': 0.0,  # pointing right
                    'coneHalfAngle': 30.0,
                    'volumetricIntensity': 0.2
                },
                {
                    'pos': (0.2, 0.8),
                    'color': (0.0, 1.0, 0.0),
                    'intensity': 1.0,
                    'radius': 0.25,
                    'directionAngle': 90.0,  # pointing up
                    'coneHalfAngle': 20.0,
                    'volumetricIntensity': 0.3
                },
                {
                    'pos': (0.8, 0.2),
                    'color': (0.0, 0.0, 1.0),
                    'intensity': 1.0,
                    'radius': 0.2,
                    'directionAngle': 270.0,  # pointing down
                    'coneHalfAngle': 25.0,
                    'volumetricIntensity': 0.15
                }
            ]
            for i, light in enumerate(test_lights):
                pos_x, pos_y = light['pos']
                r, g, b = light['color']
                intensity = light['intensity']
                radius = light['radius']
                directionAngle = light.get('directionAngle', 0.0)
                coneHalfAngle = light.get('coneHalfAngle', 30.0)
                volumetricIntensity = light.get('volumetricIntensity', 0.0)

                # Pack vec2 pos + padding
                data += struct.pack('4f', pos_x, pos_y, 0.0, 0.0)
                # Pack vec3 color + intensity
                data += struct.pack('4f', r, g, b, intensity)
                # Pack radius, directionAngle, coneHalfAngle, padding
                data += struct.pack('4f', radius, directionAngle, coneHalfAngle, 0.0)
                # Pack volumetricIntensity + padding
                data += struct.pack('4f', volumetricIntensity, 0.0, 0.0, 0.0)

                print(f"Light {i}: pos=({pos_x:.2f},{pos_y:.2f}), color=({r:.1f},{g:.1f},{b:.1f}), "
                      f"intensity={intensity:.1f}, radius={radius:.2f}, "
                      f"directionAngle={directionAngle:.1f}, coneHalfAngle={coneHalfAngle:.1f}, "
                      f"volumetricIntensity={volumetricIntensity:.2f}")
        else:
            for i, light in enumerate(lights[:32]):
                pos_x, pos_y = getattr(light, 'pos', (0.5, 0.5))
                r, g, b = getattr(light, 'color', (1.0, 1.0, 1.0))
                intensity = getattr(light, 'intensity', 1.0)
                radius = getattr(light, 'radius', 0.3)
                directionAngle = getattr(light, 'directionAngle', 0.0)
                coneHalfAngle = getattr(light, 'coneHalfAngle', 30.0)
                volumetricIntensity = getattr(light, 'volumetricIntensity', 0.0)

                data += struct.pack('4f', pos_x, pos_y, 0.0, 0.0)
                data += struct.pack('4f', r, g, b, intensity)
                data += struct.pack('4f', radius, directionAngle, coneHalfAngle, 0.0)
                data += struct.pack('4f', volumetricIntensity, 0.0, 0.0, 0.0)

        # Pad remaining lights
        remaining_lights = 32 - num_lights
        if remaining_lights > 0:
            data += bytes(remaining_lights * 64)

        if hasattr(self, 'ubo_lights'):
            self.ubo_lights.release()
            delattr(self, 'ubo_lights')

        self.ubo_lights = self.ctx.buffer(data)
        self.ubo_lights.bind_to_uniform_block(2)
        uniform_block = self.progs["deferredlighting"]['LightBlock']

        uniform_block.binding = 2


        self.render_deferred_lighting()

    def render_deferred_lighting(self, uniforms=None):
        """Render deferred lighting pass using G-buffer textures."""
        program = self.progs.get("deferredlighting")
        vao = self.vaos.get("deferredlighting")
        if not program or not vao:
            print("Error: Deferred lighting shader or VAO not found")
            return

        self.write_framebuffer.use()
        self.ctx.viewport = (0, 0, *self.screen.get_size())
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        # === MAIN DEFERRED LIGHTING PASS ===

        # Bind G-buffer textures
        self.gbuffer_albedo.use(location=0)  # Contains albedo data
        self.gbuffer_normal.use(location=1)  # Contains normal data

        # Set G-buffer texture uniforms for main lighting
        try:
            program["gAlbedo"] = 0  # Points to albedo data
            program["gNormalXYZ"] = 1  # Points to normal data

        except KeyError as e:
            print(f"Warning: G-buffer uniform not found in shader: {e}")

        # Set additional uniforms if provided
        if uniforms:
            for name, value in uniforms.items():
                try:
                    program[name] = value
                except KeyError:
                    print(f"Warning: Uniform '{name}' not found in deferred lighting shader")

        # Render main deferred lighting
        vao.render()

        # Swap buffers (following your architecture)
        self.swap()



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

    def render_effect(self, effect_name, uniforms=None, additional_textures=None):
        """Render effect by name, applying uniforms dynamically."""
        program = self.progs.get(effect_name)
        vao = self.vaos.get(effect_name)
        if not program or not vao:
            raise ValueError(f"Effect '{effect_name}' not found")

        # Bind main texture to location 0
        if effect_name != "deferredlighting":
            self.write_framebuffer.use()
            self.ctx.viewport = (0, 0, *self.screen.get_size())
            self.write_framebuffer.clear()
            self.read_texture.use(location=0)
            program['Texture'] = 0

        # Bind additional textures to subsequent locations
        if additional_textures:
            for i, (uniform_name, texture) in enumerate(additional_textures.items(), 6):

                try:
                    texture.use(location=i)
                    program[uniform_name] = i

                except KeyError:
                    # Uniform doesn't exist, ignore or log warning
                    pass

        # Set other uniforms
        if uniforms:
            for name, value in uniforms.items():
                try:
                    program[name] = value
                except KeyError:
                    # Uniform doesn't exist, ignore or log warning
                    pass

        vao.render()
        self.swap()

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

    def apply_contrast(self, brightness, contrast):
        self.render_effect("contrast", {"brightness": brightness, "contrast": contrast})

    def apply_distortion(self, distortionStrength):
        self.render_effect("distortion", {"distortion_strength": distortionStrength})

    def apply_flicker(self, inputs, noiseIntensity, noiseScale, noiseSpeed):
        # Update the base texture with the main image

        additional_textures = {}
        if inputs[1] is not None:
            noise_texture = self.surf_to_texture(inputs[1], small=True)
            additional_textures["NoiseTexture"] = noise_texture

            self.render_effect("flicker",
                               {"noiseIntensity": noiseIntensity,
                                "noiseScale": noiseScale,
                                "noiseSpeed": noiseSpeed},
                               additional_textures)

    def apply_directional_light(self, lightDirection, lightColor, intensity):
        self.render_effect("directional_light",
                           {"lightDirection": lightDirection, "lightColor": lightColor, "intensity": intensity})

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
