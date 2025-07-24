#version 330 core
in vec2 v_text;
out vec4 color;

uniform sampler2D Texture;
uniform float threshold;

void main() {
    vec3 col = texture(Texture, v_text).rgb;
    float brightness = dot(col, vec3(0.2126, 0.7152, 0.0722));
    if (brightness > threshold)
        color = vec4(col, 1.0);
    else
        color = vec4(0.0);
}
