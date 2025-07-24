#version 330 core

in vec2 v_text;
out vec4 color;

uniform sampler2D Texture;
uniform float intensity;     // e.g., 0.2 = 20% darkening
uniform float frequency;     // e.g., 240.0 for 240 scanlines per screen height

void main() {
    vec4 baseColor = texture(Texture, v_text);

    // Scanline darkness based on sine wave
    float line = sin(v_text.y * frequency * 3.14159); // frequency controls number of lines
    float brightness = 1.0 - intensity * (0.5 * (1.0 - line)); // scale to [1-intensity, 1]
    color = vec4(baseColor.rgb * brightness, baseColor.a);

}
