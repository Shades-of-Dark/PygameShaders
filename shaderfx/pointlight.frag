#version 330 core

uniform sampler2D Texture;

in vec2 v_text;
out vec4 color;

uniform vec2 lightPosition;   // light center in UV space (0–1)
uniform vec3 lightColor;      // RGB light tint
uniform float intensity;      // how strong the light is
uniform float radius;         // how far it reaches

void main()
{
    vec4 baseColor = texture(Texture, v_text);

    float dist = distance(v_text, lightPosition);
float attenuation = clamp(1.0 - dist / radius, 0.0, 1.0);

// When attenuation is 0 (outside radius), color = base color
// When attenuation > 0 (inside radius), color blends towards lit color

vec3 ambient = vec3(0.0); // or some ambient if you want

vec3 litColor = baseColor.rgb * (ambient + lightColor * intensity * attenuation);

// Blend: if attenuation=0 -> baseColor; if attenuation=1 -> litColor
vec3 finalColor = mix(baseColor.rgb, litColor, attenuation);

color = vec4(finalColor, baseColor.a);

}
