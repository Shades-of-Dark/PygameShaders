#version 330 core

in vec2 v_text;          // Original UV coords
out vec4 color;

uniform sampler2D Texture;

// Distortion strength (positive value causes barrel distortion)
uniform float distortion_strength;

void main() {
    // Center UV coordinates around (0.0, 0.0)
    vec2 centeredUV = v_text - 0.5;

    // Calculate radius squared from center
    float radius = length(centeredUV);

    // Apply barrel distortion formula:
    // distortedRadius = radius * (1.0 + distortion_strength * radius^2)
    float distortedRadius = radius * (1.0 + distortion_strength * radius * radius);

    // Calculate distorted UV coordinates direction (normalized)
    vec2 distortedUV = (distortedRadius / radius) * centeredUV;

    // Move UVs back to [0,1] range
    distortedUV += 0.5;

    // If distorted UV is outside [0,1], can either clamp or discard
    if (distortedUV.x < 0.0 || distortedUV.x > 1.0 || distortedUV.y < 0.0 || distortedUV.y > 1.0) {
        // Optional: discard pixels outside the screen after distortion
        color = vec4(0.0);
        return;
    }

    // Sample the texture with distorted UV coordinates
    color = texture(Texture, distortedUV);
}
