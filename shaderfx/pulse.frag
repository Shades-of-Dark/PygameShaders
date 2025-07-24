#version 330 core
uniform float u_time;
uniform float pulseSpeed;   // 1.0 to 10.0
uniform float pulseStrength; // 0.0 to 0.2
uniform sampler2D Texture;

in vec2 v_text;
out vec4 color;
void main() {
    vec4 baseColor = texture(Texture, v_text);
    float pulse = 1.0 + sin(u_time * pulseSpeed) * pulseStrength;
    color = vec4(baseColor.rgb * pulse, baseColor.a);
}

