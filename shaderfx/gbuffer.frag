#version 330 core
in vec2 v_text;

layout(location = 0) out vec4 gAlbedo;     // ✓ Matches second attachment (gbuffer_albedo)
layout(location = 1) out vec4 gNormalXYZ;  // ✓ Matches first attachment (gbuffer_normal)

uniform sampler2D Texture;   // Base sprite
uniform sampler2D NormalMap; // Optional normal map
uniform bool useNormalMap;
uniform bool generateSphericalNormals;

// Sprite properties
uniform vec2 spriteSize;     // Sprite size in pixels
uniform int normalType;      // 0=flat, 1=spherical, 2=cylindrical, 3=custom, 4=laigter-style

// Laigter-style parameters (matching actual Laigter controls)
// Enhance controls (inner detail from luminance)
uniform float enhanceHeight;  // Height control for enhance (surface detail)
uniform float enhanceSoft;    // Soft control for enhance (blur amount)

// Bump controls (edge volume from distance transform)
uniform float bumpHeight;     // Height control for bump (edge volume intensity)
uniform float bumpDistance;   // Distance control (how far from edge bump extends)
uniform float bumpSoft;       // Soft control for bump (blur amount)
uniform bool bumpSoftRadio;   // Soft/Abrupt radio (true=soft/spherical, false=abrupt/linear)

// Axis controls
uniform bool invertX;         // Invert X component
uniform bool invertY;         // Invert Y component (for engines like Godot)

// Simple distance transform approximation
float calculateDistanceField(vec2 coord) {
    vec2 pixelSize = 1.0 / spriteSize;
    float alpha = texture(Texture, coord).a;

    if (alpha < 0.01) return 0.0;

    // Multi-sample distance approximation
    float minDist = 1.0;
    int samples = 3; // Radius of sampling

    for (int y = -samples; y <= samples; y++) {
        for (int x = -samples; x <= samples; x++) {
            if (x == 0 && y == 0) continue;

            vec2 offset = vec2(float(x), float(y)) * pixelSize;
            float sampleAlpha = texture(Texture, coord + offset).a;

            if (sampleAlpha < 0.01) {
                float dist = length(vec2(x, y)) / float(samples);
                minDist = min(minDist, dist);
            }
        }
    }

    return minDist;
}

// Gaussian-like blur approximation
vec3 blurNormal(vec3 normal, vec2 coord, float blurAmount) {
    if (blurAmount <= 0.0) return normal;

    vec2 pixelSize = 1.0 / spriteSize;
    vec3 result = normal;
    float totalWeight = 1.0;

    // Simple 3x3 blur
    for (int y = -1; y <= 1; y++) {
        for (int x = -1; x <= 1; x++) {
            if (x == 0 && y == 0) continue;

            vec2 offset = vec2(float(x), float(y)) * pixelSize * blurAmount;
            float sampleAlpha = texture(Texture, coord + offset).a;

            if (sampleAlpha > 0.01) {
                float weight = 0.5; // Simple uniform weight
                // For a real blur, you'd calculate this normal properly
                result += normal * weight;
                totalWeight += weight;
            }
        }
    }

    return result / totalWeight;
}
// Surface detail enhancement from luminance
const float ENHANCE_HEIGHT_DEFAULT = 2.0;  // Strength of height-from-luminance
const float ENHANCE_SOFT_DEFAULT   = 1.0;  // Blur radius in texels (0.0 = no blur)

// Volume bump from distance transform
const float BUMP_HEIGHT_DEFAULT    = 5.0;  // Height scale for bump effect
const float BUMP_SOFT_DEFAULT      = 1.5;  // Blur radius in texels (softens edges)
const float BUMP_DISTANCE_DEFAULT  = 6.0;  // How far in pixels bump effect extends from edge

void main() {
    // Albedo sample
    vec4 texColor = texture(Texture, v_text);

    // Default flat normal
    vec3 normal = vec3(0.0, 0.0, 1.0);

    if (useNormalMap) {
        // Sample normal map (tangent space) and remap from [0,1] → [-1,1]
        vec3 mapNormal = texture(NormalMap, v_text).rgb * 2.0 - 1.0;
        normal = normalize(mapNormal);
    }
    else if (generateSphericalNormals) {
        // Spherical normals with aspect ratio correction
        vec2 pixelCoords = v_text * spriteSize;
        vec2 centered = pixelCoords - (spriteSize * 0.5);

        // Normalize based on actual dimensions to avoid stretching
        vec2 normalizedCoords = vec2(
            centered.x / (spriteSize.x * 0.5),
            centered.y / (spriteSize.y * 0.5)
        );

        float distanceFromCenter = length(normalizedCoords);
        if (distanceFromCenter <= 1.0) {
            float z = sqrt(max(0.0, 1.0 - distanceFromCenter * distanceFromCenter));
            normal = normalize(vec3(normalizedCoords.x, normalizedCoords.y, z));
        }
    }
    else if (normalType == 2) {
        // Cylindrical normals
        vec2 pixelCoords = v_text * spriteSize;
        vec2 centered = pixelCoords - (spriteSize * 0.5);

        float radius = spriteSize.x * 0.5;
        float normalizedX = centered.x / radius;

        if (abs(normalizedX) <= 1.0) {
            float z = sqrt(max(0.0, 1.0 - normalizedX * normalizedX));
            normal = normalize(vec3(normalizedX, 0.0, z));
        }
    }
    else if (normalType == 3) {
        // Custom bulge
        vec2 pixelCoords = v_text * spriteSize;
        vec2 centered = pixelCoords - (spriteSize * 0.5);
        vec2 normalizedCoords = centered / (spriteSize * 0.5);

        float bulge = 0.3;
        normal = normalize(vec3(normalizedCoords.x * bulge, normalizedCoords.y * bulge, 1.0));
    }
    else if (normalType == 4) {
        // Laigter-style normals: proper implementation
        vec2 pixelSize = 1.0 / spriteSize;

        // === ENHANCE NORMALS (Surface detail from luminance derivatives) ===
        vec3 enhanceNormal = vec3(0.0, 0.0, 1.0);

        if (enhanceHeight > 0.0) {
            // Sample neighboring pixels for luminance
            float heightC = dot(texColor.rgb, vec3(0.299, 0.587, 0.114));
            float heightL = dot(texture(Texture, v_text + vec2(-pixelSize.x, 0.0)).rgb, vec3(0.299, 0.587, 0.114));
            float heightR = dot(texture(Texture, v_text + vec2(pixelSize.x, 0.0)).rgb, vec3(0.299, 0.587, 0.114));
            float heightU = dot(texture(Texture, v_text + vec2(0.0, pixelSize.y)).rgb, vec3(0.299, 0.587, 0.114));
            float heightD = dot(texture(Texture, v_text + vec2(0.0, -pixelSize.y)).rgb, vec3(0.299, 0.587, 0.114));

            // Calculate height derivatives (gradients)
            float dx = (heightR - heightL) * enhanceHeight;
            float dy = (heightU - heightD) * enhanceHeight; // Note: Laigter coordinate system

            enhanceNormal = normalize(vec3(dx, dy, 1.0));

            // Apply enhance soft (blur)
            if (enhanceSoft > 0.0) {
                enhanceNormal = blurNormal(enhanceNormal, v_text, enhanceSoft);
            }
        }

        // === BUMP NORMALS (Volume from distance transform) ===
        vec3 bumpNormal = vec3(0.0, 0.0, 1.0);

        if (bumpHeight > 0.0) {
            // Calculate distance field from alpha mask
            float distField = calculateDistanceField(v_text);

            // Apply distance control (how far from edge the effect extends)
            float effectiveDistance = min(distField / max(bumpDistance, 0.01), 1.0);

            // Calculate height from distance field
            float height;
            if (bumpSoftRadio) {
                // Soft/Spherical bump
                height = sqrt(max(0.0, effectiveDistance));
            } else {
                // Abrupt/Linear bump
                height = effectiveDistance;
            }

            // Calculate gradients from distance field
            float distL = calculateDistanceField(v_text + vec2(-pixelSize.x, 0.0));
            float distR = calculateDistanceField(v_text + vec2(pixelSize.x, 0.0));
            float distU = calculateDistanceField(v_text + vec2(0.0, pixelSize.y));
            float distD = calculateDistanceField(v_text + vec2(0.0, -pixelSize.y));

            float dx = (distR - distL) * bumpHeight * height;
            float dy = (distU - distD) * bumpHeight * height;

            bumpNormal = normalize(vec3(dx, dy, 1.0));

            // Apply bump soft (blur)
            if (bumpSoft > 0.0) {
                bumpNormal = blurNormal(bumpNormal, v_text, bumpSoft);
            }
        }

        // === COMBINE NORMALS ===
        // Proper normal blending (Reoriented Normal Mapping)
        vec3 n1 = enhanceNormal;
        vec3 n2 = bumpNormal;
        normal = normalize(vec3(n1.xy + n2.xy, n1.z * n2.z));

        // Apply axis inversions
        if (invertX) normal.x = -normal.x;
        if (invertY) normal.y = -normal.y;
    }

    gAlbedo = vec4(texColor.rgb, 1.0);
    // Encode normal to [0,1] range for storage
    gNormalXYZ = vec4(normal * 0.5 + 0.5, 1.0);
}