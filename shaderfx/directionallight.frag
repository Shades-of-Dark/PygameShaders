#version 330 core

uniform sampler2D Texture;

in vec2 v_text;
out vec4 color;

uniform vec2 lightDirection;  // normalized direction (optional for normal-based lighting)
uniform vec3 lightColor;      // RGB tint
uniform float intensity;      // overall brightness

void main()
{
    // Sample the base texture
    vec4 baseColor = texture(Texture, v_text);

    // For flat 2D shading without normals, direction is constant
    // If you have normals, replace with dot(normal, -lightDirection)
    vec3 litColor = baseColor.rgb * lightColor * intensity;

    color = vec4(litColor, baseColor.a);
}
