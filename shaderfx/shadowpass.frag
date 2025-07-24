#version 330 core
in vec2 v_text;
out float fragShadow;  // Just write brightness or alpha

uniform sampler2D Texture;
uniform vec2 lightPos;
uniform float lightRadius;

void main() {
    vec4 texColor = texture(Texture, v_text);

    float brightness = dot(texColor.rgb, vec3(0.299, 0.587, 0.114));
    float visibility = 1.0 - smoothstep(0.0, lightRadius, distance(v_text, lightPos));

    // Use brightness * visibility or alpha if using alpha-based shadows
    fragShadow = brightness * visibility;
}
