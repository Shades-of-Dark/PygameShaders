import numpy as np
def pack_rectangles(bin_width, bin_height, rectangles):
    """
    Pack rectangles using MaxRects algorithm with Best Short Side Fit.

    Args:
        bin_width, bin_height: Container dimensions
        rectangles: List of (width, height) tuples

    Returns:
        List of (x, y, width, height) tuples for placed rectangles,
        or None for rectangles that don't fit
    """
    free_rects = [(0, 0, bin_width, bin_height)]
    placed = []

    for w, h in rectangles:
        # Find best position
        best_rect = None
        best_short_side = float('inf')
        best_long_side = float('inf')

        for fx, fy, fw, fh in free_rects:
            if fw >= w and fh >= h:
                leftover_h = fw - w
                leftover_v = fh - h
                short_side = min(leftover_h, leftover_v)
                long_side = max(leftover_h, leftover_v)

                if short_side < best_short_side or \
                        (short_side == best_short_side and long_side < best_long_side):
                    best_rect = (fx, fy, w, h)
                    best_short_side = short_side
                    best_long_side = long_side

        if best_rect is None:
            placed.append(None)  # Doesn't fit
            continue

        x, y, w, h = best_rect
        placed.append(best_rect)

        # Split free rectangles
        new_free_rects = []
        for fx, fy, fw, fh in free_rects:
            # Check if this free rect intersects with placed rect
            if not (x >= fx + fw or x + w <= fx or y >= fy + fh or y + h <= fy):
                # Split into up to 4 new rectangles
                if fx < x:  # Left split
                    new_free_rects.append((fx, fy, x - fx, fh))
                if fx + fw > x + w:  # Right split
                    new_free_rects.append((x + w, fy, fx + fw - (x + w), fh))
                if fy < y:  # Bottom split
                    new_free_rects.append((fx, fy, fw, y - fy))
                if fy + fh > y + h:  # Top split
                    new_free_rects.append((fx, y + h, fw, fy + fh - (y + h)))
            else:
                # Keep non-intersecting free rects
                new_free_rects.append((fx, fy, fw, fh))

        # Remove contained rectangles (pruning)
        free_rects = []
        for i, rect1 in enumerate(new_free_rects):
            is_contained = False
            for j, rect2 in enumerate(new_free_rects):
                if i != j and rect_contains(rect2, rect1):
                    is_contained = True
                    break
            if not is_contained:
                free_rects.append(rect1)

    return placed


def rect_contains(outer, inner):
    ox, oy, ow, oh = outer
    ix, iy, iw, ih = inner
    return (ox <= ix and oy <= iy and
            ox + ow >= ix + iw and oy + oh >= iy + ih)


def generate_gaussian_kernel_1d(radius, sigma):
    """
    Generates a 1D Gaussian kernel for separable blur.
    Returns weights from center (index 0) to radius.

    Args:
        radius (int): Half-width of the kernel
        sigma (float): Standard deviation of the Gaussian function

    Returns:
        numpy.ndarray: 1D Gaussian kernel weights [center, +1, +2, ..., +radius]
    """
    weights = []

    # Calculate weights from center (0) to radius
    for i in range(int(radius + 1)):
        weight = np.exp(-(i ** 2) / (2 * sigma ** 2))
        weights.append(weight)

    # Normalize: center weight + 2 * sum of offset weights = 1
    total = weights[0] + 2 * sum(weights[1:])
    weights = [w / total for w in weights]

    return np.array(weights)