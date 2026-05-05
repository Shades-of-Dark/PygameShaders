#version 330 core
in vec2 v_text;
out vec4 color;

uniform sampler2D Texture;
uniform sampler2D bloom;
uniform float bloom_strength;  // e.g., 0.7

void main() {
    vec4 sceneColor = texture(Texture, v_text);
    vec3 bloomColor = texture(bloom, v_text).rgb;

    vec3 result = sceneColor.rgb + clamp(bloom_strength * bloomColor, vec3(0.0), vec3(1.0));

    color = vec4(result, sceneColor.a);
}
