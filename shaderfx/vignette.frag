#version 330 core

uniform float defaultIntensity;
uniform float defaultRadius;
uniform sampler2D Texture;

in vec2 v_text;

out vec4 color;

vec4 applyVignette(vec2 uv, vec4 baseColor, float intensity, float radius)
{
    float dist = distance(uv, vec2(0.5, 0.5));

    // Calculate vignette factor: 0.0 at center, 1.0 at edge (after radius)
    float vignette = smoothstep(radius, 0.707, dist); // 0.707 = max dist in a unit square

    // Apply intensity to control darkness
    float fade = 1.0 - vignette * intensity;

    return vec4(baseColor.rgb * fade, baseColor.a);
}

vec4 applyVignette(vec2 uv, vec4 baseColor, float radius)
{
    return applyVignette(uv, baseColor, defaultIntensity, radius);
}

vec4 applyVignette(vec2 uv, vec4 baseColor)
{
    return applyVignette(uv, baseColor, defaultIntensity, defaultRadius);
}

void main()
{
    vec4 baseColor = texture(Texture, v_text);
    color = applyVignette(v_text, baseColor);
}
