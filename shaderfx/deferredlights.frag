#version 330 core

struct PointLight {
    vec2 pos;
    vec2 _pad0;

    vec3 color;
    float intensity;

    float radius;
    float directionAngle;  // degrees
    float coneHalfAngle;   // degrees

    float volumetricIntensity;
    float _pad1;
    float _pad2;
    float _pad3;
};

layout(std140) uniform LightBlock {
    int numLights;
    int _pad0;
    int _pad1;
    int _pad2;

    PointLight lights[32];
};

uniform sampler2D gAlbedo;
uniform sampler2D gNormalXYZ;

in vec2 v_text;
out vec4 FragColor;

void main() {
    vec4 albedo = texture(gAlbedo, v_text);

    vec3 baseColor = albedo.rgb;
    vec4 normalSample = texture(gNormalXYZ, v_text);

    vec3 normalXYZ = normalSample.xyz * 2.0 - 1.0;
    vec3 normal = normalize(normalXYZ);
    float ambient = 0.01;
    vec3 finalColor = albedo.rgb * ambient;

    for (int i = 0; i < min(numLights, 32); i++) {
        vec2 lightPos = lights[i].pos;
        vec3 lightTint = lights[i].color;
        float lightIntensity = lights[i].intensity;
        float lightRadius = lights[i].radius;
        float volumetricIntensity = lights[i].volumetricIntensity;
        float coneHalfAngleDeg = lights[i].coneHalfAngle;

        // Light direction vector (where the light points)
        float directionRad = radians(lights[i].directionAngle);
        vec2 lightDirection = vec2(cos(directionRad), sin(directionRad));

        // Vector from light to fragment
        vec2 toFragment = v_text - lightPos;
        float distance = length(toFragment);


        vec2 toFragmentNorm = normalize(toFragment);
                // Cosine of angle between light direction and fragment direction
        float cosAngle = clamp(dot(lightDirection, toFragmentNorm), 0.0, 1.0);
        // Radial falloff
        float radialFalloff = clamp(1.0 - (distance)/lightRadius, 0.0, 1.0);
        radialFalloff *= radialFalloff;

        float softness = 0.8; // 0.0 = hard edge, 1.0 = very soft
        float innerAngle = coneHalfAngleDeg * (1.0 - softness);
        float outerAngle = coneHalfAngleDeg * (1.0 + softness);

        innerAngle = max(innerAngle, 0.0);

        float cosInner = cos(radians(innerAngle));
        float cosOuter = cos(radians(outerAngle));

        float angularFalloff = smoothstep(cosOuter, cosInner, cosAngle);


        // Normal-based lighting
        vec2 lightDir2D = -toFragment / distance; // Direction from fragment to light
        vec3 lightDir3D = normalize(vec3(lightDir2D, 0.9));
        float normalFalloff = clamp(dot(lightDir3D, normal), 0.0, 1.0);

        // Combine all falloffs
        // --- surface lighting (needs normals & albedo)
        float surfI = lightIntensity * normalFalloff * radialFalloff * angularFalloff;
        vec3 surfColor = baseColor * (surfI * lightTint);

        // --- volumetric lighting (NO albedo, NO normal)
        float fogI = lightIntensity * radialFalloff * angularFalloff;
        vec3 fogColor = (fogI * volumetricIntensity) * lightTint;

        finalColor += surfColor + fogColor;

    }

    FragColor = vec4(finalColor, 1.0);

}