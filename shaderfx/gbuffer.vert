#version 330 core
layout (location = 0) in vec2 in_pos;   // local quad coords (-1..1)
layout (location = 1) in vec2 in_text;  // UV coords (0..1)

out vec2 v_text;

uniform vec2 spritePos;   // top-left in pixels
uniform vec2 spriteSize;  // size in pixels
uniform vec2 screenSize;  // screen size in pixels

void main() {
    // Convert [-1..1] to [0..1] local space
    vec2 local01 = (in_pos * 0.5) + 0.5;

    // Convert to pixel coords in screen space
    vec2 posPixels = spritePos + local01 * spriteSize;

    // Pixel coords → NDC [-1..1]
    vec2 ndcPos = posPixels / screenSize * 2.0 - 1.0;

    // Flip Y so top-left is (0,0)
    ndcPos.y = -ndcPos.y;

    v_text = in_text;
    gl_Position = vec4(ndcPos, 0.0, 1.0);
}
