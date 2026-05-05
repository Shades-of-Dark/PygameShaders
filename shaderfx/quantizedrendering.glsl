#version 330 core
precision mediump float;
uniform sampler2D Texture;

in vec2 v_text;
out vec4 color;
uniform float pixelSize;
void main() {

    vec2 scaledCoord = floor(v_text / pixelSize + 0.5) * pixelSize; // pixelates the screen
    vec4 baseColor = texture(Texture, scaledCoord);
    color = baseColor;
}