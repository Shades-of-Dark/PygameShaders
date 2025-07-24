#version 330 core
uniform sampler2D Texture;

in vec2 v_text;
out vec4 color;

uniform float brightness;
uniform float contrast;
void main() {
    // Range: brightness [-1, 1], contrast [0, 2]
    vec4 baseColor = texture(Texture, v_text);
    vec4 color_adj = (baseColor - 0.5) * contrast + 0.5 + brightness;
    color = color_adj;
}
