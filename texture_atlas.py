import pygame
import uuid
from utils import pack_rectangles
class AtlasEntry():
    def __init__(self, name, w, h, uv):
        self.name = name
        self.w = w
        self.h = h
        self.area = w * h
        self.uv = uv


class TextureAtlas:
    def __init__(self, ctx):
        self.ctx = ctx
        self.MAX_TEXTURE_SIZE = ctx.info["GL_MAX_TEXTURE_SIZE"]
        self._texture_atlas = ctx.texture((512, 512), components=4)
        self._tex_at_surf = pygame.Surface((512, 512), pygame.SRCALPHA)
        self._texture_atlas_contents = {}
        self.stored_surfaces = {}  # Keep original surfaces for repacking

    @property
    def usage_stats(self):
        """stats"""
        total_pixels = self._tex_at_surf.get_width() * self._tex_at_surf.get_height()
        used_pixels = sum(entry.area for entry in self._texture_atlas_contents.values())
        return {
            'utilization': used_pixels / total_pixels,
            'sprite_count': len(self._texture_atlas_contents),
            'atlas_size': (self._tex_at_surf.get_width(), self._tex_at_surf.get_height())
        }

    @property
    def sprite_names(self):
        """list of loaded sprites"""
        return list(self._texture_atlas_contents.keys())
    
    def get_sprite_surface(self, name):
        """Extract a sprite from the atlas and return as pygame Surface"""
        if name not in self._texture_atlas_contents:
            return None

        entry = self._texture_atlas_contents[name]
        atlas_size = self.tex_at_surf.get_width()

        # Convert UV coordinates back to pixel coordinates
        u1, v1, u2, v2 = entry.uv
        x = int(u1 * atlas_size)
        y = int(v1 * atlas_size)
        w = entry.w
        h = entry.h

        # Extract the subsurface from the atlas
        sprite_rect = pygame.Rect(x, y, w, h)
        extracted_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        extracted_surface.blit(self.tex_at_surf, (0, 0), sprite_rect)

        return extracted_surface

    def get_sprite_texture(self, name):
        """Extract a sprite from the atlas and return as ModernGL texture"""
        if name not in self._texture_atlas_contents:
            return None

        # Get the surface first
        sprite_surface = self.get_sprite_surface(name)
        if sprite_surface is None:
            return None

        # Convert to ModernGL texture
        w, h = sprite_surface.get_size()
        texture_data = pygame.image.tostring(sprite_surface, 'RGBA')
        sprite_texture = self.ctx.texture((w, h), components=4)
        sprite_texture.write(texture_data)

        return sprite_texture

    def get_sprite_texture_data(self, name):
        """Extract sprite as raw texture data (for manual texture creation)"""
        if name not in self._texture_atlas_contents:
            return None

        sprite_surface = self.get_sprite_surface(name)
        if sprite_surface is None:
            return None

        return {
            'data': pygame.image.tostring(sprite_surface, 'RGBA'),
            'size': sprite_surface.get_size(),
            'components': 4
        }

    def submit_sprite(self, surf: pygame.Surface, name=None):
        """Submit a singular sprite into the texture atlas
         (***NOT RECOMMENDED*** using this method & opting for
         batching with the submit_sprites_batch method"""
        if name is None:
            name = str(uuid.uuid4())

        # Store the surface for future repacking
        self.stored_surfaces[name] = surf.copy()

        # Collect all rectangles for packing
        rectangles = []
        surface_order = []

        for surface_name, surface in self.stored_surfaces.items():
            w, h = surface.get_size()
            rectangles.append((w, h))
            surface_order.append(surface_name)

        # Try packing with resize if needed
        results = self._pack_with_resize(rectangles)

        if results is None:
            # Remove the surface we just added since packing failed
            del self.stored_surfaces[name]
            print("Could not fit sprite even at maximum atlas size")
            return None

        # Rebuild atlas with new packing
        self._rebuild_atlas(surface_order, results)
        return name

    def submit_sprites_batch(self, surfaces_dict):
        """
        Submit multiple sprites at once for efficient packing.

        Args:
            surfaces_dict: Dict of {name: surface} or list of surfaces (auto-named)

        Returns:
            Dict of {name: success_bool} or list of success bools if input was list
        """
        # Handle list input by creating names
        return_list = isinstance(surfaces_dict, list)
        if return_list:
            surfaces_dict = {str(uuid.uuid4()): surf for surf in surfaces_dict}

        # Store all new surfaces
        for name, surf in surfaces_dict.items():
            self.stored_surfaces[name] = surf.copy()

        # Collect all rectangles for packing
        rectangles = []
        surface_order = []

        for name, surf in self.stored_surfaces.items():
            w, h = surf.get_size()
            rectangles.append((w, h))
            surface_order.append(name)

        # Try packing, resize if needed
        results = self._pack_with_resize(rectangles)

        if results is None:
            # Remove the surfaces we just added since packing failed
            for name in surfaces_dict.keys():
                if name in self.stored_surfaces:
                    del self.stored_surfaces[name]

            failed_result = {name: False for name in surfaces_dict.keys()}
            return list(failed_result.values()) if return_list else failed_result

        # Rebuild atlas with new packing
        self._rebuild_atlas(surface_order, results)

        success_result = {name: True for name in surfaces_dict.keys()}
        return list(success_result.values()) if return_list else success_result

    def _pack_with_resize(self, rectangles):
        """Try packing, resizing atlas if needed"""
        current_size = self.tex_at_surf.get_width()

        while current_size <= self.MAX_TEXTURE_SIZE:
            results = pack_rectangles(current_size, current_size, rectangles)

            if None not in results:
                # Resize atlas if needed
                if current_size > self.tex_at_surf.get_width():
                    self.tex_at_surf = pygame.Surface((current_size, current_size), pygame.SRCALPHA)
                    self._texture_atlas = self.ctx.texture((current_size, current_size), components=4)
                return results

            # Double size and try again
            current_size *= 2

        return None  # Couldn't fit even at max size

    def _rebuild_atlas(self, surface_order, results):
        """Rebuild the atlas texture with new packing"""
        self.tex_at_surf.fill((0, 0, 0, 0))
        self._texture_atlas_contents.clear()

        atlas_size = self.tex_at_surf.get_width()

        for surface_name, result in zip(surface_order, results):
            x, y, w, h = result
            surface = self.stored_surfaces[surface_name]

            # Blit to atlas
            self.tex_at_surf.blit(surface, (x, y))

            # Store UV coords
            u1, v1 = x / atlas_size, y / atlas_size
            u2, v2 = (x + w) / atlas_size, (y + h) / atlas_size
            self._texture_atlas_contents[surface_name] = AtlasEntry(surface_name, w, h, (u1, v1, u2, v2))

        # Update GPU texture
        self._texture_atlas.write(pygame.image.tostring(self.tex_at_surf, 'RGBA'))

    def get_sprite_uv(self, name):
        """Get UV coordinates for a sprite"""
        if name in self._texture_atlas_contents:
            return self._texture_atlas_contents[name].uv
        return None

    def remove_sprite(self, name):
        """Remove a sprite and repack the atlas"""
        if name not in self.stored_surfaces:
            return False

        del self.stored_surfaces[name]

        # Repack remaining sprites if any exist
        if self.stored_surfaces:
            rectangles = []
            surface_order = []

            for surface_name, surface in self.stored_surfaces.items():
                w, h = surface.get_size()
                rectangles.append((w, h))
                surface_order.append(surface_name)

            results = self._pack_with_resize(rectangles)
            if results:
                self._rebuild_atlas(surface_order, results)
        else:
            # Clear everything if no sprites left
            self.tex_at_surf.fill((0, 0, 0, 0))
            self._texture_atlas_contents.clear()
            self._texture_atlas.write(pygame.image.tostring(self.tex_at_surf, 'RGBA'))

        return True
