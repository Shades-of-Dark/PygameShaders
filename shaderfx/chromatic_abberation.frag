#version 330 core

uniform sampler2D Texture;

in vec2 v_text;
out vec4 color;

uniform float redOffset   =  0.009;
uniform  float greenOffset =  0.006;
uniform  float blueOffset  = -0.006;
uniform vec2 mouseFocusPoint;
void main() {

    vec2 direction = v_text - mouseFocusPoint;

    color.r = texture(Texture, v_text + (direction * vec2(redOffset))).r;
    color.g = texture(Texture, v_text + (direction * vec2(greenOffset))).g;
    color.ba = texture(Texture, v_text + (direction * vec2(blueOffset))).ba;
}
