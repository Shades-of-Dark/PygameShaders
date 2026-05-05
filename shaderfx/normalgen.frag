#version 330 core
in vec2 v_text;
out vec4 color;

uniform sampler2D normalTex;
uniform float meshRad;
uniform vec2 textureSize;

void main() {
    vec4 baseColor = texture(normalTex, v_text);

    // If pixel is transparent, output no normal data
    if (baseColor.a < 0.01) {
        color = vec4(0.0, 0.0, 0.0, 0.0);
        return;
    }

    // Calculate spherical normal
    vec2 pixelCoords = (v_text * textureSize) - (textureSize * 0.5);
    float distanceSquared = dot(pixelCoords, pixelCoords);
    float radiusSquared = meshRad * meshRad;

    vec3 normal = vec3(0.0, 0.0, 1.0); // Default pointing up

    if (distanceSquared <= radiusSquared) {
        float z = sqrt(radiusSquared - distanceSquared);
        normal = normalize(vec3(pixelCoords, z));
    }

    // Pack only X,Y components of normal (Z can be reconstructed)
    // Store as normalized values (0-1 range)
    vec2 packedNormal = normal.xy * 0.5 + 0.5;

    // Output: RG = normal XY, B = unused, A = alpha from original
    color = vec4(packedNormal, 0.0, baseColor.a);
}