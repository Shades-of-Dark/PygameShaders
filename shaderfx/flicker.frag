#version 330 core
in vec2 v_text;
out vec4 color;

uniform sampler2D Texture;
uniform float u_time;
uniform float noiseIntensity; // e.g., 0.1
uniform float noiseScale;     // e.g., 0.02
uniform float noiseSpeed;     // e.g., 1.0

// Pseudo-random noise function
float rand(vec2 co) {
    return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

void main() {
    vec3 baseColor = texture(Texture, v_text).rgb;

    // Animate UV based on time
    vec2 noiseUV = v_text * noiseScale + vec2(u_time * noiseSpeed, 0.0);

    // Centered noise in [-0.5, 0.5]
    float n = rand(noiseUV) - 0.5;

    // Flicker as a brightness multiplier around 1.0
    float flicker = 1.0 + n * noiseIntensity;

    vec3 flickeredColor = baseColor * flicker;

    // Optional: gamma correction
    //flickeredColor = pow(flickeredColor, vec3(1.0 / 2.2));

    color = vec4(clamp(flickeredColor, 0.0, 1.0), 1.0);
}
