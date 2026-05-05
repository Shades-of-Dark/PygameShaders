import numpy as np


class InstanceRenderer:
    def __init__(self, ctx, max_instances=10000):
        # Public properties
        self.max_instances = max_instances

        # Internal state
        self._ctx = ctx
        self._atlas = None
        self._instances = []
        self._program = None
        self._vao = None
        self._instance_buffer = None
        self._vertex_buffer = None

        self._setup_buffers()
        self._setup_shaders()

    # === PUBLIC API ===
    def add_instance(self, pos, rotation=0.0, scale=(1.0, 1.0), color=(1.0, 1.0, 1.0, 1.0), uv=(0.0, 0.0, 1.0, 1.0)):
        """Add a raw instance with all parameters"""
        if len(self._instances) >= self.max_instances:
            return False

        instance_data = [
            pos[0], pos[1],  # position
            rotation,  # rotation in radians
            scale[0], scale[1],  # scale
            color[0], color[1], color[2], color[3],  # RGBA color
            uv[0], uv[1], uv[2], uv[3]  # UV coordinates (from atlas)
        ]
        self._instances.append(instance_data)
        return True

    def add_sprite_instance(self, sprite_name, pos, rotation=0.0, scale=(1.0, 1.0), color=(1.0, 1.0, 1.0, 1.0)):
        """Add instance using sprite name (requires atlas)"""
        if not self._atlas:
            raise ValueError("No atlas set - call set_atlas() first")

        uv = self._atlas.get_sprite_uv(sprite_name)
        if uv is None:
            return False

        return self.add_instance(pos, rotation, scale, color, uv)

    def render(self, screen_width, screen_height, texture):
        """Render all instances in one draw call"""
        if not self._instances:
            return

        self._upload_instance_data()
        self._bind_uniforms(screen_width, screen_height, texture)
        self._vao.render(instances=len(self._instances))

    def clear_instances(self):
        """Clear all instances for next frame"""
        self._instances.clear()

    def set_atlas(self, atlas):
        """Set the texture atlas reference"""
        self._atlas = atlas

    # === PROPERTIES ===
    @property
    def instance_count(self):
        """Number of instances queued for rendering"""
        return len(self._instances)

    @property
    def is_full(self):
        """Check if instance buffer is at capacity"""
        return len(self._instances) >= self.max_instances

    # === INTERNAL METHODS ===
    def _setup_buffers(self):
        """Initialize vertex and instance buffers"""
        # Quad vertices (shared by all instances)
        vertices = np.array([
            # x,    y,   u,   v
            -0.5, -0.5, 0.0, 0.0,  # bottom-left
            0.5, -0.5, 1.0, 0.0,  # bottom-right
            0.5, 0.5, 1.0, 1.0,  # top-right
            -0.5, 0.5, 0.0, 1.0,  # top-left
        ], dtype=np.float32)

        indices = np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)

        self._vertex_buffer = self._ctx.buffer(vertices.tobytes())
        self._index_buffer = self._ctx.buffer(indices.tobytes())

        # Instance buffer: 13 floats per instance
        instance_size = 13 * 4  # 13 floats * 4 bytes
        self._instance_buffer = self._ctx.buffer(reserve=instance_size * self.max_instances)

    def _setup_shaders(self):
        """Compile and link shader program"""
        vertex_shader = '''
        #version 330 core

        // Per-vertex attributes
        in vec2 in_position;
        in vec2 in_texcoord;

        // Per-instance attributes  
        in vec2 instance_pos;
        in float instance_rotation;
        in vec2 instance_scale;
        in vec4 instance_color;
        in vec4 instance_uv;

        out vec2 frag_texcoord;
        out vec4 frag_color;

        uniform float screen_width;
        uniform float screen_height;

        void main() {
            // Transform vertex by instance data
            float cos_rot = cos(instance_rotation);
            float sin_rot = sin(instance_rotation);

            vec2 scaled = in_position * instance_scale;
            vec2 rotated = vec2(
                scaled.x * cos_rot - scaled.y * sin_rot,
                scaled.x * sin_rot + scaled.y * cos_rot
            );
            vec2 world_pos = rotated + instance_pos;

            // Convert to normalized device coordinates manually
            vec2 ndc = vec2(
                (world_pos.x / screen_width) * 2.0 - 1.0,
                1.0 - (world_pos.y / screen_height) * 2.0  // Flip Y for screen coords
            );

            gl_Position = vec4(ndc, 0.0, 1.0);

            // Apply atlas UV transformation
            frag_texcoord = in_texcoord * instance_uv.zw + instance_uv.xy;
            frag_color = instance_color;
        }
        '''

        fragment_shader = '''
        #version 330 core

        in vec2 frag_texcoord;
        in vec4 frag_color;

        out vec4 color;

        uniform sampler2D atlas_texture;

        void main() {
            color = texture(atlas_texture, frag_texcoord) * frag_color;
        }
        '''

    def _upload_instance_data(self):
        """Upload instance data to GPU buffer"""
        if not self._instances:
            return

        data = np.array(self._instances, dtype=np.float32)
        self._instance_buffer.write(data.tobytes())

    def _bind_uniforms(self, texture, screen_width, screen_height):
        """Bind uniforms and textures"""
        texture.use(0)
        self._program['screen_width'] = screen_width
        self._program["screen_height"] = screen_height
        self._program['atlas_texture'] = 0
