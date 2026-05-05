#version 330 core // Or whatever version you are targeting

in vec2 v_text; // Usually passed from the vertex shader

out vec4 color;

uniform sampler2D Texture;      // Base image (input 0)
uniform sampler2D NoiseTexture; // Noise/texture input (input 1)
uniform float u_time;
uniform float noiseIntensity;   // e.g., 0.85-0.95 (closer to 1.0 = less grain)
uniform float noiseScale;       // e.g., 3.0-8.0 for grain density
uniform float noiseSpeed;       // e.g., 8.0-15.0 for flicker rate

void main() {
    // Sample the base image
    vec4 baseColor = texture(Texture, v_text);

    // Calculate noise UV based on v_text, noiseScale, and u_time for animation
    vec2 noiseUV = v_text * noiseScale + u_time * noiseSpeed;

    // Sample the noise texture
    // We only need one component since it's typically grayscale noise
    float noise = texture(NoiseTexture, noiseUV).r;

    // Adjust noise to be in the range of -1 to 1 for adding and subtracting
    noise = noise * 2.0 - 1.0;

    // Apply intensity to the noise
    noise *= (1.0 - noiseIntensity);

    // Add the grain to the base color
    baseColor.rgb += noise;

    // Clamp the final color to ensure it stays within the valid range (0-1)
    color = clamp(baseColor, 0.0, 1.0);
}