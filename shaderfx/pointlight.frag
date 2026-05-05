#version 330 core

uniform sampler2D Texture;

in vec2 v_text;
out vec4 color;

uniform vec2 lightPosition;
uniform vec3 lightColor;
uniform float intensity;
uniform float radius;
uniform float minAngle;
uniform float maxAngle;
uniform float volumetricIntensity;
uniform float lightAngle;
void main()
{
    vec4 baseColor = texture(Texture, v_text);

    // Direction to pixel
    vec2 toPixel = v_text - lightPosition;
    float dist = length(toPixel);

    // ---- Radial falloff ----
    float radialFalloff = pow(1.0 - clamp(dist / radius, 0.0, 1.0), 2.0);

    // ---- Angular falloff ----
    vec2 dirToPixel = normalize(toPixel);
    vec2 lightDir = vec2(cos(radians(lightAngle)), sin(radians(lightAngle)));

    float angleCos = dot(lightDir, dirToPixel);
    float minCos = cos(radians(minAngle * 0.5));
    float maxCos = cos(radians(maxAngle * 0.5));
    float angularFalloff = smoothstep(maxCos, minCos, angleCos);



    // ---- Combine attenuation ----
    float totalAttenuation = radialFalloff * angularFalloff;

    // ---- Volumetric glow ----
    float volumetric = volumetricIntensity * (radialFalloff * angularFalloff);

    // ---- Final lighting ----
    vec3 litColor = baseColor.rgb * (lightColor * intensity * totalAttenuation + volumetric);

    color = vec4(litColor, baseColor.a);
}
