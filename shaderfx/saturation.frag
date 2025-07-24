#version 330 core
uniform sampler2D Texture;
uniform float maxSaturation;
uniform vec2 focusPoint;
uniform float radius;     // usually (0.5, 0.5) for center
in vec2 v_text;
out vec4 color;
void main() {


vec4 baseColor = texture(Texture, v_text);
vec3 grayscale = vec3(dot(baseColor.rgb, vec3(0.2126, 0.7152, 0.0722)));

float dist = distance(v_text, focusPoint);

// fade = how far along we are from full color → grayscale
// smoothstep gives a softer transition than clamp()
float fade = smoothstep(radius, 0.707, dist);  // 0.707 = max distance in unit square

// fade: 0.0 near center, 1.0 at edge → mix saturation accordingly
float saturation = mix(maxSaturation, 0.0, fade);

vec3 rawColor = mix(grayscale, baseColor.rgb, saturation);
vec3 finalColor = clamp(rawColor, 0.0, 1.0);

color = vec4(finalColor, baseColor.a);




}
