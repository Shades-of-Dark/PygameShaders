#version 330 core
in vec2 v_text;
out vec4 color;
#define MAX_ELEMENTS 81
uniform sampler2D Texture;
uniform float weights[MAX_ELEMENTS]; // size must match kernel
uniform float radius;
uniform vec2 direction;    // (1,0)=horizontal, (0,1)=vertical
uniform vec2 texelSize;    // 1.0 / resolution

void main() {
    vec3 blur = texture(Texture, v_text).rgb * weights[0];
    for (int i = 1; i <= radius; ++i) {
        vec2 offset = direction * texelSize * float(i);
        blur += texture(Texture, v_text + offset).rgb * weights[i];
        blur += texture(Texture, v_text - offset).rgb * weights[i];
    }
    color = vec4(blur, 1.0);
}
