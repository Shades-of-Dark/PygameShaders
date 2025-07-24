#version 330 core

in vec2 v_text;
out vec4 color;

uniform sampler2D Texture;
uniform sampler2D phosphorTex;
uniform vec2 screenResolution; // Screen resolution (width, height)
uniform vec2 phosphorSize;
uniform float phosphorScale; // scale factor for size of each texture
uniform float blendStrength;
uniform vec2 offset; // Pre-calculated offset multipliers (rowOffset, columnOffset)

void main() {
    vec2 uv = v_text;

    // Convert UV coordinates to screen pixel coordinates
    vec2 screenPos = uv * screenResolution;

    // Scale the coordinates
    vec2 scaledPos = screenPos / phosphorSize / phosphorScale;

    // Calculate offset using pre-calculated multipliers
    // offset.x is applied to floor(scaledPos.x) for column offset
    // offset.y is applied to floor(scaledPos.y) for row offset
    vec2 dynamicOffset = vec2(
        floor(scaledPos.y) * offset.x,  // Column offset
        floor(scaledPos.x) * offset.y   // Row offset
    );

    // Apply the offset to create the phosphor pattern
    vec2 phosphorUV = fract(scaledPos + dynamicOffset);

    vec3 baseColor = texture(Texture, uv).rgb;
    vec3 maskColor = texture(phosphorTex, phosphorUV).rgb;
    vec3 result = mix(baseColor, baseColor * maskColor, pow(blendStrength, 1.5));
    color = vec4(result, 1.0);
}