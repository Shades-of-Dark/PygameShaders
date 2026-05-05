import sys
import pygame
from graphics_engine import GraphicsEngine
from components.node import Node
from components.connections import Connection
import pygame_widgets
from pygame_widgets.slider import Slider

from lights.pointlight import PointLight
from ui.colorpicker import ColorPicker
from ui.textinput import TextInput
from ui.pointpicker import PointPicker
from ui.selectbox import SelectBox
from ui.imagepicker import ImagePicker
from ui.plusbutton import PlusButton
import json
import os
from lights import *
import pygame_gui

pygame.init()
WIDTH, HEIGHT = 1920, 1080
gldisplay = pygame.display.set_mode((WIDTH, HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
uisurface = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
ui_s = 1 / 2

output_window = pygame.Surface(
    (int(WIDTH * ui_s), int(HEIGHT * ui_s)), pygame.SRCALPHA, 32
)

engine = GraphicsEngine(output_window, 1, gldisplay.get_size())

screen_width, screen_height = gldisplay.get_size()

pygame.display.set_caption("Lumos")

texture_width = output_window.get_width()
texture_height = output_window.get_height()


def main():
    padding = 0.1 * screen_height
    x_pos, y_pos = (screen_width - texture_width) / 2, 0.05 * screen_height

    rect_x = 0
    rect_y = padding + texture_height
    rect_width = screen_width * 0.8
    rect_height = screen_height - padding - texture_height

    testimg = pygame.image.load("textures/testimg.jpg").convert_alpha()

    #   testimg = pygame.transform.scale(testimg, (output_window.get_width(), 41))
    nodes = []
    connects = []

    nodes.append(Node("Image Input", screen_width * 0.2, screen_height * 0.8, num_inputs=0))

    font = pygame.font.SysFont("Arial", 16)

    greysquare = pygame.Surface((8, 8))
    greysquare.fill((146, 146, 146))

    # Create a simple arrow if arrow.png doesn't exist
    arrow = pygame.image.load("arrow.png").convert_alpha()
    arrow.set_colorkey((39, 39, 45))

    outlinesquare = pygame.Surface((greysquare.get_width() + 2, greysquare.get_height() + 2))

    uim = pygame_gui.UIManager(uisurface.get_size())
    cueBall = pygame.image.load("textures/cueball.png").convert_alpha()
    w, h = cueBall.get_size()

    cueBall = pygame.transform.scale(cueBall, (38 * 4, 38 * 4))

    # Separate shader functions mapping
    shader_functions = {
        "Contrast": engine.shaderManager.apply_contrast,
        "Pulse": engine.shaderManager.apply_pulsing,
        "Blur": engine.shaderManager.apply_blur,
        "Flicker": engine.shaderManager.apply_flicker,
        "Vignette": engine.shaderManager.apply_vignette,
        "Saturation": engine.shaderManager.apply_saturation,
        "Point Light": engine.shaderManager.apply_point_light,
        "Distortion": engine.shaderManager.apply_distortion,
        "Scan Line": engine.shaderManager.apply_scanline,
        "Phosphor Mask": engine.shaderManager.apply_phosphor_mask,
        "Bloom": engine.shaderManager.apply_bloom,
        "Chromatic Aberration": engine.shaderManager.chromatic_aberration,
        "Directional Light": engine.shaderManager.apply_directional_light,
        "Deferred Lighting": engine.shaderManager.apply_deferred_lighting,
        "Geometry Pass": engine.shaderManager.geometry_pass,
        "Pixelation": engine.shaderManager.apply_pixelation,

    }

    # Effect settings without shader functions
    with open("node_configs/settings.json", 'r') as f:
        effect_settings = json.load(f)

    effect_settings = {
        "Image Input": {
            "uniforms": {
                "Input Texture":
                    {
                        "type": "sampler2D",
                        "path": "textures/scene.png"
                    },
                "width": {
                    "type": "float",
                    "value": output_window.get_width(),
                    "min": 128,
                    "max": output_window.get_width(),
                    "step": 16,
                },
                "height":
                    {
                        "type": "float",
                        "value": 82,
                        "min": 128,
                        "max": output_window.get_height(),
                        "step": 16,
                    }

            }

        },
        "Pixelation": {
            "numInputs": 1,
            "uniforms": {
                "pixelSize": {
                    "type": "float",
                    "value": 320,
                    "min": 240,
                    "max": 800,
                    "default": 320,
                    "step": 1.0,

                }
            }
        },
        "Geometry Pass": {
            "numInputs": 1,
            "uniforms": {

            }
        },
        "Deferred Lighting": {
            "numInputs": 1,
            "uniforms": {
                "lights": {
                    "type": "light_array",
                    "struct": [
                        {
                            "name": "pos",
                            "type": "vec2",
                            "default": [0.5, 0.5],
                            "point": [0.5, 0.5]
                        },
                        {
                            "name": "color",
                            "type": "vec3",
                            "default": [255.0, 255.0, 255.0],
                            "color": [255.0, 255.0, 255.0]
                        },
                        {
                            "name": "intensity",
                            "type": "float",
                            "min": 0.0,
                            "max": 2.0,
                            "step": 0.01,
                            "default": 0.9,
                            "value": 0.9
                        },
                        {
                            "name": "radius",
                            "type": "float",
                            "min": 0.01,
                            "max": 5.0,
                            "step": 0.01,
                            "default": 0.1,
                            "value": 0.1
                        },
                        {
                            "name": "directionAngle",
                            "type": "float",
                            "min": 0.0,
                            "max": 359.0,
                            "step": 1.0,
                            "default": 0.0,
                            "value": 0.0
                        },
                        {
                            "name": "coneHalfAngle",
                            "type": "float",
                            "min": 1.0,
                            "max": 90.0,
                            "step": 1.0,
                            "default": 30.0,
                            "value": 30.0
                        },
                        {
                            "name": "volumetricIntensity",
                            "type": "float",
                            "min": 0.0,
                            "max": 5.0,
                            "step": 0.01,
                            "default": 0.2,
                            "value": 0.2
                        }
                    ]
                },

            }
        },
        "Texture Input": {
            "numInputs": 0,
            "uniforms": {
                "Lookup Texture":
                    {
                        "type": "sampler2D",
                        "path": "textures/noisetex.png"
                    },
                "width": {
                    "type": "float",
                    "value": 32,
                    "min": 16,
                    "max": output_window.get_width(),
                    "step": 16,
                },
                "height":
                    {
                        "type": "float",
                        "value": 32,
                        "min": 16,
                        "max": output_window.get_height(),
                        "step": 16,
                    }
            }
        },

        "Contrast": {
            "numInputs": 1,
            "uniforms": {
                "brightness": {
                    "type": "float",
                    "value": 0.0,
                    "step": 0.05,
                    "max": 0.5,
                    "min": -0.5,
                },
                "contrast": {
                    "type": "float",
                    "value": 1.0,
                    "step": 0.1,
                    "max": 2.0,
                    "min": 0.5,
                },
            }
        },
        "Pulse": {
            "numInputs": 1,
            "uniforms": {
                "pulseSpeed": {
                    "type": "float",
                    "value": 2.0,
                    "min": 0.5,
                    "max": 5.0,
                    "step": 0.5,
                },
                "pulseStrength": {
                    "type": "float",
                    "value": 0.1,
                    "min": 0.0,
                    "max": 0.3,
                    "step": 0.05
                }
            }
        },
        "Directional Light": {
            "numInputs": 1,
            "uniforms": {
                "lightDirection": {
                    "type": "vec2",
                    "value": (-0.2, -1.0)

                },
                "intensity":
                    {"type": "float",
                     "value": 1.0,
                     "min": 0.0,
                     "max": 5.0,
                     "step": 0.1},

                "lightColor":
                    {"type": "vec3",
                     "value": (255.0, 255.0, 255.0)}
            }
        },
        "Blur": {
            "numInputs": 1,
            "uniforms": {
                "blurRadius": {
                    "type": "float",
                    "value": 2.0,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.1
                },
            }
        },
        "Flicker": {
            "numInputs": 2,
            "uniforms": {
                "noiseIntensity": {
                    "type": "float",
                    "value": 0.84,
                    "min": 0.05,
                    "max": 0.9,
                    "step": 0.01
                },
                "noiseScale": {
                    "type": "float",
                    "value": 6.0,
                    "min": 2.0,
                    "max": 7.0,
                    "step": 0.1
                },
                "noiseSpeed": {
                    "type": "float",
                    "value": 12,
                    "min": 1,
                    "max": 15.0,
                    "step": 0.4
                }
            }
        },
        "Vignette": {
            "numInputs": 1,
            "uniforms": {
                "intensity": {
                    "type": "float",
                    "value": 1.0,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1
                },
                "radius": {
                    "type": "float",
                    "value": 0.33,
                    "min": 0.2,
                    "max": 0.7,
                    "step": 0.05
                }
            }
        },
        "Saturation": {
            "numInputs": 1,
            "uniforms": {
                "maxSaturation": {
                    "type": "float",
                    "value": 1.0,
                    "min": 0.0,
                    "max": 3.0,
                    "step": 0.05
                },
                "radius": {
                    "type": "float",
                    "value": 0.3,
                    "min": 0.0,
                    "max": 0.7,
                    "step": 0.01
                },
                "focusPoint": {
                    "type": "vec2",
                    "value": (0.5, 0.5)
                }
            }
        },
        "Point Light": {
            "numInputs": 1,
            "uniforms": {
                "lightPosition": {
                    "type": "vec2",
                    "value": [0.5, 0.5]
                },
                "radius": {
                    "type": "float",
                    "value": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01
                },
                "minAngle": {
                    "type": "float",
                    "value": 80,
                    "min": 0.0,
                    "max": 359.0,
                    "step": 1
                },
                "maxAngle": {
                    "type": "float",
                    "value": 120,
                    "min": 0.0,
                    "max": 359.0,
                    "step": 1
                },
                "lightAngle": {
                    "type": "float",
                    "value": 270,
                    "min": 0.0,
                    "max": 359.0,
                    "step": 1
                },
                "volumetricIntensity": {
                    "type": "float",
                    "value": 0.2,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.05
                },
                "intensity": {
                    "type": "float",
                    "value": 1.0,
                    "min": 0.0,
                    "max": 5.0,
                    "step": 0.1
                },
                "lightColor": {
                    "type": "vec3",
                    "value": [255.0, 255.0, 255.0]
                }
            }
        },
        "Distortion": {
            "numInputs": 1,
            "uniforms": {
                "distortionStrength": {
                    "type": "float",
                    "value": 0.1,
                    "min": -0.3,
                    "max": 0.5,
                    "step": 0.01
                }
            }
        },
        "Scan Line": {
            "numInputs": 1,
            "uniforms": {
                "intensity": {
                    "type": "float",
                    "value": 0.2,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01
                },
                "frequency": {
                    "type": "float",
                    "value": 240.0,
                    "min": 60.0,
                    "max": output_window.get_height(),
                    "step": 1.0
                }
            }
        },
        "Phosphor Mask": {
            "numInputs": 1,
            "uniforms": {
                "phosphorScale": {
                    "type": "float",
                    "value": 2.0,
                    "min": 0.2,
                    "max": 4.0,
                    "step": 0.1
                },
                "blendStrength": {
                    "type": "float",
                    "value": 0.3,
                    "min": 0.0,
                    "max": 0.5,
                    "step": 0.025
                },
                "pattern": {
                    "type": "choice",
                    "value": "shadow mask",
                    "choices": ["shadow mask", "aperture grille", "slot mask"],
                }
            }
        },
        "Bloom": {
            "numInputs": 1,
            "uniforms": {
                "threshold": {
                    "type": "float",
                    "value": 0.8,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01
                },
                "blurRadius": {
                    "type": "float",
                    "value": 5.0,
                    "min": 1.0,
                    "max": 32.0,
                    "step": 2.0
                },
                "intensity": {
                    "type": "float",
                    "value": 0.7,
                    "min": 0.0,
                    "max": 3.0,
                    "step": 0.1
                }
            }
        },
        "Chromatic Aberration": {
            "numInputs": 1,
            "uniforms": {
                "mouseFocusPoint": {
                    "type": "vec2",
                    "value": (0.5, 0.5)
                },
                "redOffset": {
                    "type": "float",
                    "value": 0.003,
                    "min": 0.000,
                    "max": 0.02,
                    "step": 0.001
                },
                "greenOffset": {
                    "type": "float",
                    "value": 0.002,
                    "min": -0.002,
                    "max": 0.015,
                    "step": 0.001
                },
                "blueOffset": {
                    "type": "float",
                    "value": -0.003,
                    "min": -0.02,
                    "max": 0.001,
                    "step": 0.001
                }
            }
        }
    }
    sky = pygame.Surface(output_window.get_size(), pygame.SRCALPHA).convert_alpha()

    sky.fill((1, 1, 1, 255))

    with open("node_configs/settings.json", "w") as f:
        json.dump(effect_settings, f, indent=4)

    def draw_ui_rect(surface, x, y, width, height, color):
        """Helper function to draw rectangles on UI surface"""
        pygame.draw.rect(surface, color, (x, y, width, height))

    def draw_ui_rect_outline(surface, x, y, width, height, color, thickness=1):
        """Helper function to draw rectangle outlines on UI surface"""
        pygame.draw.rect(surface, color, (x, y, width, height), thickness)

    def draw_ui_line(surface, start_pos, end_pos, color, width=1):
        """Helper function to draw lines on UI surface"""
        pygame.draw.line(surface, color, start_pos, end_pos, width)

    def draw_ui_text(surface, text, x, y, font, color=(255, 255, 255)):
        """Helper function to draw text on UI surface"""
        text_surf = font.render(str(text), True, color)
        surface.blit(text_surf, (x, y))

    def draw_ui_surface_at_position(surface, sprite, x, y):
        """Helper function to blit surfaces on UI surface"""
        surface.blit(sprite, (x, y))

    def save_graph_to_file(nodes, connections, filename):
        data = {
            "nodes": [export_node(node) for node in nodes],  # This will now include num_inputs
            "connections": [export_connection(conn) for conn in connections]  # This will now include input_index
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    def load_graph_from_file(filename):
        with open(filename, "r") as f:
            data = json.load(f)

        # Import nodes
        nodes = [import_node(n) for n in data["nodes"]]
        node_lookup = {n.id: n for n in nodes}

        # Import connections using existing node references
        connections = []
        for conn_data in data["connections"]:
            inp_id = conn_data["input"]
            out_id = conn_data["output"]
            if inp_id in node_lookup and out_id in node_lookup:
                input_node = node_lookup[inp_id]
                output_node = node_lookup[out_id]

                # Use saved input_index if available, otherwise get next available
                if "input_index" in conn_data:
                    input_index = conn_data["input_index"]
                else:
                    input_index = input_node.get_next_input_index(connections)

                connections.append(Connection(input_node, output_node, input_index))
                output_node.conns += 1
            else:
                print(f"Skipping invalid connection: {conn_data}")

        return nodes, connections

    def import_node(data):
        # Get num_inputs from data, default to 1 for backward compatibility
        num_inputs = data.get("num_inputs", 1)
        node = Node(data["type"], data["x"], data["y"], num_inputs)
        node.id = data["id"]

        node.widgets = []

        settings = effect_settings[node.type]["uniforms"]
        for key, default in data["uniforms"].items():
            uniform = settings[key]
            uniform["value"] = default  # temporarily override for widget creation

        node.widgets = create_widgets_for_node(node)
        return node

    def export_node(node: Node):
        return {
            "id": node.id,
            "type": node.type,
            "x": node.x,
            "y": node.y,
            "num_inputs": node.num_inputs,  # Add this line
            "uniforms": {
                key: widget.getValue()
                for key, widget in node.widgets
            }
        }

    def export_connection(conn: Connection):
        return {
            "input": conn.inp.id,
            "output": conn.out.id,
            "input_index": conn.input_index,  # Add this line
        }

    def create_widgets_for_node(node):
        widgets = []
        settings = effect_settings[node.type]["uniforms"]
        widget = None

        for k, (uniform_key, uniform) in enumerate(settings.items(), start=4):
            ui_x = int(WIDTH * 0.87)
            ui_y = int(HEIGHT * 0.04 * k)
            ui_w = int(WIDTH * 0.1)
            ui_h = int(HEIGHT * 0.015)

            if uniform["type"] == "light_array":
                # Add the PlusButton for adding/removing lights
                plus_button = PlusButton(ui_x - 10, ui_y, ui_w, ui_h, uniform_key, theme="node_configs/ui_theme.json")
                widgets.append((uniform_key, plus_button))

                # For each light, create widgets for each property
                for i, light in enumerate(engine.lights):
                    offset_y = ui_y + 40 + i * 150

                    for j, field in enumerate(uniform["struct"]):
                        field_name = field["name"]
                        field_type = field["type"]
                        widget_label = f"{uniform_key}_{field_name}_{i}"

                        # Skip widget with label exactly equal to uniform_key (to avoid duplicates)
                        if widget_label == uniform_key:
                            continue

                        widget_y = offset_y + j * 20
                        value = getattr(light, field_name, None)
                        if value is None:
                            # Use default from JSON struct if the attribute doesn't exist on light
                            if "default" in field:
                                value = field["default"]
                            elif "value" in field:
                                value = field["value"]
                            else:
                                continue

                        if field_type == "vec2":
                            # Use 'point' or 'default' value if available
                            default_val = field.get("point", value)
                            widget = PointPicker(ui_x - 10, widget_y, ui_w, height=ui_h, label=widget_label,
                                                 default=default_val,
                                                 theme="node_configs/ui_theme.json")
                        elif field_type == "vec3":
                            # Use 'color' or 'default' value if available
                            default_val = field.get("color", value)
                            widget = ColorPicker(ui_x - 10, widget_y, ui_w, height=ui_h, label=widget_label,
                                                 default=default_val,
                                                 theme="node_configs/ui_theme.json")
                        elif field_type == "float":
                            # Use min, max, step, and value/default for slider
                            min_val = field.get("min", 0.0)
                            max_val = field.get("max", 1.0)
                            step = field.get("step", 0.01)
                            initial_val = field.get("value", value)

                            widget = Slider(x=ui_x - 10, y=widget_y, width=ui_w, height=3,
                                            min=min_val, max=max_val, step=step,
                                            initial=initial_val,
                                            handleRadius=12, win=uisurface)
                        else:
                            continue  # unknown field type, skip

                        widgets.append((widget_label, widget))

            else:
                # For non-light_array uniforms, just use the usual way with min/max/step/value
                if uniform["type"] == "float":
                    widget = Slider(
                        uisurface,
                        ui_x,
                        ui_y,
                        ui_w,
                        3,
                        min=uniform.get("min", 0.0),
                        max=uniform.get("max", 1.0),
                        step=uniform.get("step", 0.01),
                        initial=uniform.get("value", 0.0),
                        handleRadius=12
                    )
                elif uniform["type"] == "vec2":
                    widget = PointPicker(ui_x - 10, ui_y, ui_w, ui_h, uniform_key, default=uniform.get("value"),
                                         theme="node_configs/ui_theme.json")
                elif uniform["type"] == "vec3":
                    widget = ColorPicker(ui_x - 10, ui_y, ui_w, ui_h, uniform_key, default=uniform.get("value"),
                                         theme="node_configs/ui_theme.json")
                elif uniform["type"] == "choice":
                    widget = SelectBox(ui_x - 10, ui_y, ui_w, ui_h, uniform_key, uniform["choices"],
                                       default=uniform.get("value"),
                                       theme="node_configs/ui_theme.json")
                elif uniform["type"] == "sampler2D":
                    widget = ImagePicker(ui_x - 10, ui_y, ui_w, ui_h, uniform_key, default=uniform.get("path"),
                                         theme="node_configs/ui_theme.json")
                if widget is not None:
                    widgets.append((uniform_key, widget))

        return widgets

    # Global cache dictionary keyed by (node, origin_type)
    _origin_cache = {}

    def originates_from_type(node, connects, origin_type, visited=None):
        """
        Recursively check if `node` originates from a node of type `origin_type`.
        Uses caching for efficiency.
        """
        cache_key = (node, origin_type)

        if visited is None:
            visited = set()
        if node in visited:
            _origin_cache[cache_key] = False
            return False
        visited.add(node)

        if node.type == origin_type:
            _origin_cache[cache_key] = True
            return True

        incoming_nodes = [conn.inp for conn in connects if conn.out == node]
        result = any(originates_from_type(n, connects, origin_type, visited) for n in incoming_nodes)

        _origin_cache[cache_key] = result
        return result

    def clear_origin_cache():
        _origin_cache.clear()

    def execute_node_chain(inputTex):
        executed_list = []
        visited = set()
        node_outputs = {}

        def get_node_inputs(node):
            inputs = [None] * node.num_inputs
            for conn in connects:
                if conn.out == node:
                    source_output = dfs(conn.inp)
                    inputs[conn.input_index] = source_output
            return inputs

        def apply_node_effect(node):
            if node.type == "Texture Input":
                if hasattr(node, 'widgets') and len(node.widgets) > 0:
                    image_picker = node.widgets[0][1]
                    if isinstance(image_picker, ImagePicker) and getattr(image_picker, 'img', None) is not None:
                        return image_picker.img
                return None

            if node.type in effect_settings and node.type in shader_functions:
                shader_func = shader_functions[node.type]
                inputs = get_node_inputs(node)

                # Skip effect if required inputs are missing
                if node.conns < node.num_inputs and any(inp is None for inp in inputs):
                    return None

                kwargs = {}
                light_widgets_data = {}

                if hasattr(node, "widgets"):
                    for uniform_key, widget in node.widgets:
                        if isinstance(widget, Slider):
                            kwargs[uniform_key] = widget.getValue()
                        elif isinstance(widget, PointPicker):
                            kwargs[uniform_key] = widget.point
                        elif isinstance(widget, ColorPicker):
                            kwargs[uniform_key] = widget.color
                        elif isinstance(widget, SelectBox):
                            kwargs[uniform_key] = widget.value
                        elif isinstance(widget, PlusButton):
                            kwargs[uniform_key] = engine.lights

                # Detect if this is the deferred lighting node
                if node.type == "Deferred Lighting":
                    # Gather all keys related to lights_* in kwargs
                    lights_data = {}
                    to_remove = []
                    for key in kwargs:
                        if key.startswith("lights_"):
                            # keys like 'lights_pos_0', 'lights_color_1', etc.
                            # Extract index and property name
                            parts = key.split("_")
                            if len(parts) >= 3:
                                prop = parts[1]  # e.g. pos, color, intensity
                                index = int(parts[2])  # e.g. 0, 1, 2
                                if index not in lights_data:
                                    lights_data[index] = {}
                                lights_data[index][prop] = kwargs[key]
                                to_remove.append(key)
                    # Remove these individual keys from kwargs
                    for key in to_remove:
                        del kwargs[key]

                    # Build list of PointLight from collected data, filling defaults if needed
                    # Iterate over the keys in lights_data, update corresponding engine.lights
                    for i, light in enumerate(engine.lights):
                        if i in lights_data:
                            d = lights_data[i]
                            # Update fields with new values if present, else keep current
                            light.pos = d.get("pos", light.pos)
                            light.color = d.get("color", light.color)
                            light.intensity = d.get("intensity", light.intensity)
                            light.radius = d.get("radius", light.radius)
                            light.directionAngle = d.get("directionAngle", light.directionAngle)
                            light.coneHalfAngle = d.get("coneHalfAngle", light.coneHalfAngle)
                            light.volumetricIntensity = d.get("volumetricIntensity", light.volumetricIntensity)

                    # If lights_data has more lights than engine.lights, you might want to add new PointLights
                    max_index = max(lights_data.keys()) if lights_data else -1
                    if max_index >= len(engine.lights):
                        for i in range(len(engine.lights), max_index + 1):
                            d = lights_data.get(i, {})
                            new_light = PointLight(
                                d.get("pos", (0.5, 0.5)),
                                d.get("color", (1.0, 1.0, 1.0)),
                                # Make sure color is normalized if your PointLight expects that
                                d.get("intensity", 1.0),
                                d.get("radius", 1.0),
                                d.get("directionAngle", 20.0),
                                d.get("coneHalfAngle", 30.0),
                                d.get("volumetricIntensity", 0.2)
                            )
                            engine.lights.append(new_light)

                    # Now use engine.lights directly in kwargs
                    kwargs["lights"] = engine.lights

                # Finally call shader_func with bundled kwargs
                if node.num_inputs > 1 or node.type == "Normal Map Generation":
                    return shader_func(inputs, **kwargs)
                else:
                    return shader_func(**kwargs)

            # Pass through first input
            if node.num_inputs > 0:
                inputs = get_node_inputs(node)

                return inputs[0] if inputs[0] is not None else None
            return None

        def dfs(node):
            if node in visited:
                return node_outputs.get(node)

            visited.add(node)
            executed_list.append(node)
            node.color = (47, 48, 54)

            if node.type == "Image Input":
                output_window.fill((0, 0, 0, 0))
                if use_geometry_pass:
                    engine.shaderManager.geometry_pass([
                        (sky, (0, 0), "sky"),
                        (inputTex, (0, 375), "ground"),
                        (cueBall, (600, 290), "object")
                    ])
                    node_outputs[node] = engine.shaderManager.read_texture
                else:
                    # Plain old rendering - just blit or draw textures directly
                    output_window.blit(inputTex, (0, 375))
                    output_window.blit(cueBall, (600, 290))
                    node_outputs[node] = output_window  # or however you track output
            else:
                if node.type != "Geometry Pass":
                    node_outputs[node] = apply_node_effect(node)

            for con in connects:
                if con.inp == node:
                    dfs(con.out)

            return node_outputs.get(node)

        #  Start DFS from input nodes only
        for node in nodes:
            if node.type == "Image Input":
                dfs(node)

        return executed_list

    # You can remove apply_post_effects since effects are now applied during DFS

    EDGE_THRESHOLD = 20  # Pixels from edge to activate resize

    def get_resize_edge(mouse_x, mouse_y, menu_x, menu_y, menu_width, menu_height):
        """Determine which edge of the menu the mouse is near"""
        menu_left = menu_x - menu_width / 2
        menu_right = menu_left + menu_width
        menu_top = menu_y - 20
        menu_bottom = menu_top + menu_height

        # Check distance from each edge
        near_left = abs(mouse_x - menu_left) <= EDGE_THRESHOLD and menu_top <= mouse_y <= menu_bottom
        near_right = abs(mouse_x - menu_right) <= EDGE_THRESHOLD and menu_top <= mouse_y <= menu_bottom
        near_top = abs(mouse_y - menu_top) <= EDGE_THRESHOLD and menu_left <= mouse_x <= menu_right
        near_bottom = abs(mouse_y - menu_bottom) <= EDGE_THRESHOLD and menu_left <= mouse_x <= menu_right

        # Check corners first (priority over edges)
        corner_threshold = EDGE_THRESHOLD * 1.5  # Slightly larger area for corners
        near_top_left = (abs(mouse_x - menu_left) <= corner_threshold and
                         abs(mouse_y - menu_top) <= corner_threshold)
        near_top_right = (abs(mouse_x - menu_right) <= corner_threshold and
                          abs(mouse_y - menu_top) <= corner_threshold)
        near_bottom_left = (abs(mouse_x - menu_left) <= corner_threshold and
                            abs(mouse_y - menu_bottom) <= corner_threshold)
        near_bottom_right = (abs(mouse_x - menu_right) <= corner_threshold and
                             abs(mouse_y - menu_bottom) <= corner_threshold)

        if near_top_left:
            return 'top-left'
        elif near_top_right:
            return 'top-right'
        elif near_bottom_left:
            return 'bottom-left'
        elif near_bottom_right:
            return 'bottom-right'
        elif near_left:
            return 'left'
        elif near_right:
            return 'right'
        elif near_top:
            return 'top'
        elif near_bottom:
            return 'bottom'
        return None

    def get_cursor_for_edge(edge):
        """Return appropriate cursor for each resize edge"""
        cursor_map = {
            'left': pygame.SYSTEM_CURSOR_SIZEWE,
            'right': pygame.SYSTEM_CURSOR_SIZEWE,
            'top': pygame.SYSTEM_CURSOR_SIZENS,
            'bottom': pygame.SYSTEM_CURSOR_SIZENS,
            'top-left': pygame.SYSTEM_CURSOR_SIZENWSE,
            'bottom-right': pygame.SYSTEM_CURSOR_SIZENWSE,
            'top-right': pygame.SYSTEM_CURSOR_SIZENESW,
            'bottom-left': pygame.SYSTEM_CURSOR_SIZENESW,
        }
        return cursor_map.get(edge, pygame.SYSTEM_CURSOR_ARROW)

    def input_node_search(connections):
        for connection in connections:
            if connection.inp.type == "Image Input":
                return connection.inp

    # Initialize sliders for existing effect nodes
    for node in nodes:
        if node.type in effect_settings:
            node.widgets = create_widgets_for_node(node)

    rad = 5
    greycircle = pygame.Surface((rad * 2, rad * 2))
    greycircle.set_colorkey((0, 0, 0))
    pygame.draw.circle(greycircle, (116, 116, 116), (rad, rad), rad)

    currentnode = None
    delete = False
    show_node_menu = False
    node_types = list(effect_settings.keys())
    node_types.remove("Image Input")
    menu_position = (screen_width // 2, screen_height * 5 / 7)
    filtered_nodes = []
    clock = pygame.time.Clock()
    node_input = TextInput(font)
    selected_index = 0
    FIRST_RESULT = 0
    SEARCH_MAX_ENTRIES = int(8 * WIDTH / 1920)
    menu_option_rects = []

    fileName = ""
    fileNameInput = TextInput(font, screen_width * 0.1)
    fileNameInput.disable()
    fileNameRect = pygame.Rect(screen_width * 0.5, screen_height * 0.01, screen_width * 0.1, screen_height * 0.02)
    result = ""
    filePath = ""
    ignore_mouse_hover = False
    ignore_mouse_timer = 0

    uifiledialog = None
    dialog = None
    noInputWindow = pygame.Surface(output_window.get_size())
    surf = pygame.image.load("textures/scene.png").convert_alpha()

    input_img = nodes[0].widgets[0][1].img

    menu_x, menu_y = menu_position
    menu_width = screen_width * 0.15  # Make this a variable instead of box_w
    menu_height = SEARCH_MAX_ENTRIES * 30 + screen_height * 0.0002
    min_menu_width = 150  # Minimum width
    max_menu_width = screen_width * 0.5  # Maximum width
    min_menu_height = 100  # Minimum height
    max_menu_height = screen_height * 0.8  # Maximum height

    # Resize state variables
    is_resizing = False
    resize_edge = None  # 'right', 'left', 'top', 'bottom', 'top-left', 'top-right', 'bottom-left', 'bottom-right'
    resize_start_pos = (0, 0)
    resize_start_size = (0, 0)
    resize_start_menu_pos = (0, 0)  # For tracking menu position during resize

    # Edge detection constants
    EDGE_THRESHOLD = 10  # Pixels from edge to activate resize
    dialogNodeType = None
    fileNameQueue = []
    use_geometry_pass = True
    while True:
        dt = clock.tick(60)

        left, middle, right = pygame.mouse.get_pressed(3)
        mx, my = pygame.mouse.get_pos()
        events = pygame.event.get()
        pygame_widgets.update(events)

        # Clear UI surface at start of frame
        uisurface.fill((0, 0, 0, 0))  # Transparent fill

        # Handle events (same as before)
        for node in nodes:
            if hasattr(node, "widgets"):

                lights = engine.lights  # This is now a direct reference

                for uniform_key, widget in node.widgets:
                    if isinstance(widget, PlusButton):
                        additionlight = widget.handle_event(events, font)
                        if additionlight is not None:
                            if additionlight == "add_light":
                                new_light = PointLight((0.5, 0.5), (1.0, 1.0, 1.0), 0.9, 0.1, 70,
                                                       volumetricintensity=0.65)
                                engine.lights.append(new_light)  # modifies node.lights directly

                                node.widgets = create_widgets_for_node(node)  # rebuild widgets
                            elif additionlight == "reset_light":
                                lights.clear()  # clears node.lights list
                                node.widgets = create_widgets_for_node(node)
                        continue

                    if len(lights) == 0:
                        continue

                    if isinstance(widget, PointPicker):
                        value = widget.handle_event(events, texture_width, texture_height, x_pos, y_pos, font)
                        if value is not None:
                            # Parse uniform_key to extract light index and property
                            # e.g. "lights_pos_0", "lights_pos_1", etc.
                            if uniform_key.startswith("lights_pos_"):
                                index = int(uniform_key.split("_")[-1])
                                if index < len(lights):
                                    lights[index].pos = value

                    elif isinstance(widget, ColorPicker):
                        value = widget.handle_event(events, font)
                        if value is not None:
                            if uniform_key.startswith("lights_color_"):
                                index = int(uniform_key.split("_")[-1])
                                if index < len(lights):
                                    lights[index].color = value

                    elif isinstance(widget, Slider):
                        value = widget.getValue()
                        if value is not None:
                            # Match slider to light property via uniform_key pattern
                            # e.g. "lights_intensity_0", "lights_radius_0", etc.
                            parts = uniform_key.split("_")
                            if len(parts) >= 3 and parts[0] == "lights":
                                prop = parts[1]  # e.g. intensity, radius, angle
                                index = int(parts[2])
                                if index < len(lights):
                                    setattr(lights[index], prop, value)

                    elif isinstance(widget, SelectBox):
                        widget.handle_event(events)
                    elif isinstance(widget, ImagePicker):
                        openFiledialog = widget.handle_event(events)
                        if openFiledialog == "confirm":
                            dialog = pygame_gui.windows.UIFileDialog(
                                pygame.Rect(uisurface.get_width() / 2 * 0.5, uisurface.get_height() / 2 * 0.5,
                                            uisurface.get_width() * 0.5, uisurface.get_height() * 0.5), uim,
                                initial_file_path=os.getcwd(), allowed_suffixes={".png", ".jpg", ".jpeg"},
                                allow_picking_directories=False,
                                allow_existing_files_only=True, window_title="Select a file")
                            dialogNodeType = node

        if show_node_menu:
            # CALCULATE ONCE - reuse everywhere else
            filtered_nodes = [n for n in node_types if
                              node_input.get_text().lower() in n.lower() and n != "Image Input"]

            # Clamp values to valid ranges using the calculated list
            selected_index = pygame.math.clamp(selected_index, 0, max(0, len(filtered_nodes) - 1))
            FIRST_RESULT = pygame.math.clamp(FIRST_RESULT, 0, max(0, len(filtered_nodes) - SEARCH_MAX_ENTRIES))

            # Initialize ignore_mouse_hover flag and timer if not set
            if 'ignore_mouse_hover' not in locals():
                ignore_mouse_hover = False
            if 'ignore_mouse_timer' not in locals():
                ignore_mouse_timer = 0

            # Decrement timer
            if ignore_mouse_timer > 0:
                ignore_mouse_timer -= dt
                ignore_mouse_hover = True
            else:
                ignore_mouse_hover = False

        for event in events:
            uim.process_events(event)
            filetyping = fileNameInput.handle_event(event)

            if filetyping == "confirm":
                fileName = fileNameInput.get_text()
                fileNameInput.disable()
            elif filetyping == "cancel":
                fileNameInput.reset()
                fileNameInput.disable()

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:

                if event.text:
                    if event.ui_element == uifiledialog and uifiledialog is not None:
                        filePath = event.text
                        chosenFile = filePath
                        fileName = chosenFile.replace(os.getcwd() + "\\", "")
                        fileNameInput.set_text(fileName.replace(".json", ""))

                        nodes, connects = load_graph_from_file(chosenFile)

                        uifiledialog.kill()
                    elif event.ui_element == dialog and dialog is not None:
                        aPath = event.text

                        imgpath = aPath.replace(os.getcwd() + "\\", "")
                        fileNameQueue.append((dialogNodeType, imgpath))

                else:
                    print("file not found")
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if fileNameInput.active != True and not show_node_menu:

                    if event.key == pygame.K_BACKSPACE:
                        delete = True

                else:  # show_node_menu is True
                    # Get filtered nodes first to work with current list

                    if event.key == pygame.K_UP:
                        if selected_index > 0:
                            selected_index -= 1
                            # Adjust scroll window if needed
                            if selected_index < FIRST_RESULT:
                                FIRST_RESULT = selected_index
                        node_input.typing = False
                        # Also ignore mouse hover briefly when using keyboard
                        ignore_mouse_timer = 200

                    elif event.key == pygame.K_DOWN:
                        if selected_index < len(filtered_nodes) - 1:
                            selected_index += 1
                            # Adjust scroll window if needed
                            if selected_index >= FIRST_RESULT + SEARCH_MAX_ENTRIES:
                                FIRST_RESULT = selected_index - SEARCH_MAX_ENTRIES + 1
                        node_input.typing = False
                        # Also ignore mouse hover briefly when using keyboard
                        ignore_mouse_timer = 200

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_BACKSPACE:
                    delete = False

            if show_node_menu:
                result = node_input.handle_event(event)
                if result == "confirm":

                    if filtered_nodes and selected_index < len(filtered_nodes):

                        new_node = Node(filtered_nodes[selected_index], x=mx, y=my,
                                        num_inputs=effect_settings[filtered_nodes[selected_index]]["numInputs"])

                        nodes.append(new_node)
                        if new_node.type in effect_settings:
                            new_node.widgets = create_widgets_for_node(new_node)

                    node_input.reset()
                    selected_index = 0
                    FIRST_RESULT = 0
                    menu_option_rects.clear()
                    show_node_menu = False
                elif result == "cancel":
                    node_input.reset()
                    selected_index = 0
                    FIRST_RESULT = 0
                    menu_option_rects.clear()
                    show_node_menu = False

                if event.type == pygame.MOUSEWHEEL:

                    if event.y < 0:  # Scroll down
                        if selected_index < len(filtered_nodes) - 1:
                            selected_index += 1
                            # Adjust scroll window if needed
                            if selected_index >= FIRST_RESULT + SEARCH_MAX_ENTRIES:
                                FIRST_RESULT = selected_index - SEARCH_MAX_ENTRIES + 1
                    elif event.y > 0:  # Scroll up
                        if selected_index > 0:
                            selected_index -= 1
                            # Adjust scroll window if needed
                            if selected_index < FIRST_RESULT:
                                FIRST_RESULT = selected_index
                    # Set timer to ignore mouse hover for a short period (200ms)
                    ignore_mouse_timer = 200

            if event.type == pygame.MOUSEBUTTONDOWN:
                done = False
                if event.button == 3:
                    show_node_menu = True
                    # Reset menu state when opening
                    selected_index = 0
                    FIRST_RESULT = 0
                    menu_option_rects.clear()
                elif event.button == 1:
                    if fileNameRect.collidepoint(mx, my):
                        fileNameInput.enable()
                    if show_node_menu:
                        # Handle clicking on menu options
                        for i, (rect, node_type) in enumerate(menu_option_rects):
                            if rect.collidepoint(mx, my):

                                new_node = Node(node_type, x=mx, y=my,
                                                num_inputs=effect_settings[node_type]["numInputs"])

                                nodes.append(new_node)
                                if new_node.type in effect_settings:
                                    new_node.widgets = create_widgets_for_node(new_node)
                                node_input.reset()
                                selected_index = 0
                                FIRST_RESULT = 0
                                menu_option_rects.clear()
                                show_node_menu = False

                                break

                    for node in nodes:
                        if rect_x + rect_width > mx > rect_x and rect_y + rect_height > my > rect_y:
                            node.touched = False
                            node.selected = False
                        if node.rect.collidepoint(mx, my) and not done:
                            currentnode = node
                            node.touched = True
                            node.selected = True
                            done = True
                        if not node.connecting:
                            if node.inp.collidepoint(mx, my):
                                node.delete_cons = True

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                for node in nodes:
                    if node.delete_cons:
                        cleaned = []
                        for con in connects:
                            if con.inp != node and con.out != node:
                                cleaned.append(con)
                            else:
                                con.out.conns -= 1
                        connects = cleaned

                        node.delete_cons = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_s] and (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
            if ".json" not in fileName:
                fileName += ".json"
            save_graph_to_file(nodes, connects, fileName)

        if keys[pygame.K_i] and (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
            if len(list(uim.get_root_container())) == 0:
                uifiledialog = pygame_gui.windows.UIFileDialog(
                    pygame.Rect(uisurface.get_width() / 2 * 0.5, uisurface.get_height() / 2 * 0.5,
                                uisurface.get_width() * 0.5, uisurface.get_height() * 0.5), uim,
                    initial_file_path=os.getcwd(), allowed_suffixes={".json"}, allow_picking_directories=False,
                    allow_existing_files_only=True, window_title="Select a file")

        # Execute the node chain and apply effects
        if nodes and nodes[0].type == "Image Input":
            image_widget = nodes[0].widgets[0][1]  # First widget is the ImagePicker
            width_widget = nodes[0].widgets[1][1]  # Second widget is width slider
            height_widget = nodes[0].widgets[2][1]  # Third widget is height slider

            current_path = image_widget.path
            current_width = int(width_widget.getValue())
            current_height = int(height_widget.getValue())

            # Initialize tracking variables if they don't exist
            if not hasattr(image_widget, '_last_path'):
                image_widget._last_path = current_path
                image_widget._last_width = current_width
                image_widget._last_height = current_height
                # Force initial load
                image_widget.path = current_path
                image_widget.img = pygame.image.load(current_path).convert_alpha()
                w = round(texture_width / image_widget.img.get_width())
                s = round(texture_height / image_widget.img.get_height())
                current_width = image_widget.img.get_width() * w
                current_height = image_widget.img.get_height() * s
                width_widget.setValue(current_width)
                height_widget.setValue(current_height)
                image_widget.img = pygame.transform.scale(image_widget.img, (current_width, current_height))
                input_img = image_widget.img
                image_widget.img = pygame.transform.scale(image_widget.img, (current_width, current_height))
                input_img = image_widget.img


            # Check if path changed - requires full reload
            elif image_widget._last_path != current_path:
                image_widget.path = current_path
                image_widget.img = pygame.image.load(current_path).convert_alpha()
                s = round(texture_height / image_widget.img.get_height())
                current_width = image_widget.img.get_width() * s
                current_height = image_widget.img.get_height() * s
                width_widget.setValue(current_width)
                height_widget.setValue(current_height)
                image_widget.img = pygame.transform.scale(image_widget.img, (current_width, current_height))
                input_img = image_widget.img

                # Update all tracking values
                image_widget._last_path = current_path
                image_widget._last_width = current_width
                image_widget._last_height = current_height

            # Check if only dimensions changed - just rescale existing image
            elif (image_widget._last_width != current_width or
                  image_widget._last_height != current_height):
                # Reload original image and scale to new dimensions
                original_img = pygame.image.load(image_widget.path).convert_alpha()
                image_widget.img = pygame.transform.scale(original_img, (current_width, current_height))
                input_img = image_widget.img

                # Update dimension tracking
                image_widget._last_width = current_width
                image_widget._last_height = current_height

        if delete and currentnode is not None and currentnode.type != "Image Input":
            connects = [con for con in connects if con.inp != currentnode and con.out != currentnode]
            nodes.remove(currentnode)
            currentnode = None
            pygame.mouse.set_visible(True)
            delete = False

        executed_nodes = execute_node_chain(input_img)

        engine.shaderManager.set_position_and_size(x_pos, y_pos, texture_width, texture_height)

        engine.shaderManager.render_to_screen()
        engine.shaderManager.update_screen_texture(output_window)

        # ============ START UI DRAWING TO UI SURFACE ============

        # Draw main workspace background
        draw_ui_rect(uisurface, rect_x, rect_y, rect_width, rect_height, (40, 40, 46))
        draw_ui_rect(uisurface,
                     WIDTH * 0.8, 0,
                     WIDTH * 0.2, HEIGHT,
                     (40, 40, 46))
        # Draw sidebar separator and background
        draw_ui_line(uisurface,
                     (WIDTH * 0.8, 0),
                     (WIDTH * 0.8, HEIGHT),
                     (9, 9, 9))
        pygame.draw.line(uisurface, (9, 9, 9), (WIDTH * 0.8, 0), (WIDTH * 0.8, HEIGHT), 2)

        # Draw horizontal separator
        draw_ui_rect(uisurface, 0, rect_y, rect_width, 2, (9, 9, 9))

        # Draw current node title
        if currentnode is not None:
            draw_ui_text(uisurface,
                         currentnode.type.title().replace("_", " "),
                         WIDTH * 0.9,
                         HEIGHT * 0.01,
                         font, (255, 255, 255))
        use_geometry_pass = False
        # Draw connections
        for connect in connects:
            start = connect.inp.out.midright
            end = connect.out.inp.midleft
            if connect.out.type == "Geometry Pass":
                use_geometry_pass = True
            if connect.out.rect.bottom > connect.inp.rect.y:
                start = connect.inp.rect.midbottom
                end = connect.out.rect.midtop
            elif connect.out.rect.y < connect.inp.rect.y:
                start = connect.inp.rect.midtop
                end = connect.out.rect.midbottom

            if connect.out.rect.x > connect.inp.rect.centerx:
                start = connect.inp.out.midright
                end = connect.out.inp.midleft

            draw_ui_line(uisurface, start, end, (248, 205, 28), 2)

        # Draw sliders for current node
        if currentnode is not None:
            for uniform_key, widget in currentnode.widgets:
                widget.enable()
                if isinstance(widget, Slider):
                    # Draw slider background
                    draw_ui_rect(uisurface,
                                 widget.getX(), widget.getY(),
                                 widget.getWidth(), int(HEIGHT * 0.006),
                                 (23, 23, 23))

                    # Draw slider handle
                    widget_value_normalized = (widget.getValue() - widget.min) / (widget.max - widget.min)
                    widget_pos_x = widget.getX() + widget_value_normalized * widget.getWidth()
                    pygame.draw.circle(uisurface, (116, 116, 116), (widget_pos_x - rad / 2, widget.getY()), rad)

                    # Draw value text
                    draw_ui_text(uisurface,
                                 str(round(widget.getValue(), 3)),
                                 widget.getX() + widget.getWidth() + 10, widget.getY(),
                                 font, (255, 255, 255))

                    # Draw uniform name
                    draw_ui_text(uisurface,
                                 uniform_key,
                                 widget.getX() - WIDTH * 0.05,
                                 widget.getY() - HEIGHT * 0.01,
                                 font, (255, 255, 255))

                elif isinstance(widget, PointPicker):
                    widget.draw_button(uisurface, font)
                elif isinstance(widget, ColorPicker):
                    widget.draw(font, uisurface)
                elif isinstance(widget, SelectBox):
                    widget.draw(uisurface, font)
                elif isinstance(widget, ImagePicker):
                    widget.draw_button(uisurface, font)
                elif isinstance(widget, PlusButton):
                    widget.draw_button(uisurface, font, engine.lights)

        # Draw nodes
        for o, node in enumerate(nodes):
            # Node outline and body
            draw_ui_rect(uisurface, node.x - 1, node.y - 1, node.width + 2, node.height + 2, node.outline_c)
            draw_ui_rect(uisurface, node.x, node.y, node.width, node.height, node.color)
            draw_ui_rect(uisurface, node.x + 1, node.y + node.height - 2, node.width, 2, (121, 168, 208))

            # Handle time-based effects
            if node.type in ["Flicker", "Pulse"]:
                current_time = pygame.time.get_ticks() / 1000.0
                engine.shaderManager.progs[node.type.lower()]["u_time"] = current_time

            if node.rect.collidepoint(mx, my) and left:
                node.selected = True
            else:
                node.selected = False

            # Draw node text
            text = node.type.replace("_", " ")
            text_size = font.size(text)
            text_x = node.x + (node.width - text_size[0]) // 2
            text_y = node.y + (node.height - text_size[1]) // 2 - 1
            draw_ui_text(uisurface, text, text_x, text_y, font, (255, 255, 255))

            # Draw node connection points
            draw_ui_surface_at_position(uisurface, outlinesquare, node.out.x, node.out.y)
            draw_ui_surface_at_position(uisurface, outlinesquare, node.rect.midtop[0] - 5, node.rect.midtop[1] - 10)
            draw_ui_surface_at_position(uisurface, greysquare, node.out.x + 1, node.out.y + 1)
            draw_ui_surface_at_position(uisurface, greysquare, node.rect.midtop[0] - 4, node.rect.midtop[1] - 9)
            draw_ui_surface_at_position(uisurface, arrow, node.inp.x, node.inp.y)

            if node.delete_cons:
                draw_ui_line(uisurface, node.inp.topleft, (mx, my), (230, 75, 61), 2)
            if node.num_inputs > 0:
                pygame.draw.rect(uisurface, (9, 9, 9),
                                 pygame.Rect(node.rect.bottomleft[0] + 3, node.rect.bottomleft[1] + 2, 23, 13))
                pygame.draw.rect(uisurface, (47, 48, 54),
                                 pygame.Rect(node.rect.bottomleft[0] + 4, node.rect.bottomleft[1] + 2, 21, 11))
                for j in range(node.num_inputs):
                    w = (255, 255, 255) if node.conns > j else (9, 9, 9)
                    radius = 3
                    pygame.draw.circle(uisurface, w, (
                        node.rect.x + 1 + (j + 1) * (radius + 1) * 2, node.rect.bottom + radius * 2 + 2), radius)
            # Handle node connections
            if left:
                if node.connecting:
                    innode = [(k, n) for k, n in enumerate(nodes) if
                              (n.rect.collidepoint(mx, my) or n.inp.collidepoint(mx, my)) and k != o]
                    if innode:
                        target_node = innode[0][1]

                        # Special case for Deferred Lighting node

                        # Existing logic for other nodes
                        if target_node.type != "Image Input" and target_node.type != "Texture Input":

                            is_main_chain = originates_from_type(node, connects, "Image Input")

                            used_indices = {conn.input_index for conn in connects if conn.out == target_node}

                            if is_main_chain:
                                if 0 not in used_indices:
                                    next_indice = 0
                                else:
                                    next_indice = next(
                                        (i for i in range(target_node.num_inputs) if i not in used_indices), None)
                            elif target_node.type == "Normal Map Generation":
                                next_indice = 0
                            else:
                                next_indice = next(
                                    (i for i in range(1, target_node.num_inputs) if i not in used_indices),
                                    None)
                        if next_indice is not None and next_indice < target_node.num_inputs:
                            # Check if this exact connection already exists
                            connection_already_exists = any(
                                conn.inp == node and conn.out == target_node
                                for conn in connects
                            )

                            # Also check if the target slot is already occupied by ANY connection
                            slot_already_occupied = any(
                                conn.out == target_node and conn.input_index == next_indice
                                for conn in connects
                            )

                            if not connection_already_exists and not slot_already_occupied:
                                target_node.conns += 1
                                new_connection = Connection(node, target_node, next_indice)
                                connects.append(new_connection)

                                print(f"Connection created: {node.type} -> {target_node.type} (slot {next_indice})")
                            else:
                                print(
                                    f"Connection blocked: exists={connection_already_exists}, slot_occupied={slot_already_occupied}")

                    draw_ui_line(uisurface, node.out.midright, (mx, my), (255, 255, 255), 1)

                if node.out.collidepoint(mx, my):
                    node.connecting = True
            else:
                node.connecting = False

            node.update(mx, my, rect_x, rect_y, rect_x + rect_width - node.width, rect_y + rect_height - node.height)

            # Disable widgets for non-current nodes
            for uniform_key, slider in node.widgets:
                slider.disable()
                if currentnode is not None:
                    if currentnode == node:
                        slider.enable()
            if fileNameQueue:
                if fileNameQueue[0][0] == node:
                    node.widgets[0][1].path = fileNameQueue[0][1]
                    fileNameQueue.pop(0)

        # Handle file name input
        fileNameInput.update(dt)

        # Draw node menu if active
        if show_node_menu:
            node_input.enable()
            node_input.update(dt)

            if not is_resizing:
                resize_edge = get_resize_edge(mx, my, menu_x, menu_y, menu_width, menu_height)
                if resize_edge and left:
                    is_resizing = True
                    resize_start_pos = (mx, my)
                    resize_start_size = (menu_width, menu_height)
                    resize_start_menu_pos = (menu_x, menu_y)
                    pygame.mouse.set_cursor(get_cursor_for_edge(resize_edge))
                elif resize_edge:
                    # Show resize cursor when hovering over edges
                    pygame.mouse.set_cursor(get_cursor_for_edge(resize_edge))
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

            # Handle active resizing
            if is_resizing:
                if left:
                    # Calculate mouse movement
                    dx = mx - resize_start_pos[0]
                    dy = my - resize_start_pos[1]

                    # Store original values
                    original_width = resize_start_size[0]
                    original_height = resize_start_size[1]
                    original_x = resize_start_menu_pos[0]
                    original_y = resize_start_menu_pos[1]

                    # Calculate new dimensions based on resize edge
                    new_width = original_width
                    new_height = original_height
                    new_x = original_x
                    new_y = original_y

                    # Handle width changes
                    if 'right' in resize_edge:
                        new_width = original_width + dx
                    elif 'left' in resize_edge:
                        new_width = original_width - dx
                        # When resizing from left, move the menu position to keep right edge fixed
                        if new_width >= min_menu_width and new_width <= max_menu_width:
                            new_x = original_x + dx / 2

                    # Handle height changes
                    if 'bottom' in resize_edge:
                        new_height = original_height + dy
                    elif 'top' in resize_edge:
                        new_height = original_height - dy
                        # When resizing from top, move the menu position to keep bottom edge fixed
                        if new_height >= min_menu_height and new_height <= max_menu_height:
                            new_y = original_y + dy / 2

                    # Apply size constraints
                    new_width = pygame.math.clamp(new_width, min_menu_width, max_menu_width)
                    new_height = pygame.math.clamp(new_height, min_menu_height, max_menu_height)

                    # Update menu properties
                    menu_width = new_width
                    menu_height = new_height
                    menu_x = new_x
                    menu_y = new_y

                    # Keep menu within screen bounds
                    half_width = menu_width / 2
                    half_height = menu_height / 2
                    menu_x = pygame.math.clamp(menu_x, half_width, WIDTH - half_width)
                    menu_y = pygame.math.clamp(menu_y, half_height + 20, HEIGHT - half_height)

                    # Update SEARCH_MAX_ENTRIES based on new height
                    SEARCH_MAX_ENTRIES = max(3, int((menu_height - screen_height * 0.0002) / 30))
                else:
                    # Stop resizing when mouse is released
                    is_resizing = False
                    resize_edge = None
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

            # Update your existing menu drawing code to use menu_width and menu_height
            box_w = menu_width
            box_h = menu_height

            # Handle dragging (your existing code with modification to avoid conflict with resizing)
            widt, heit = font.size("Select Effect")
            drag_area = pygame.Rect(menu_x - box_w / 8, menu_y - 20, widt, heit)
            if left and drag_area.collidepoint(mx, my) and not is_resizing and not get_resize_edge(mx, my, menu_x,
                                                                                                   menu_y,
                                                                                                   menu_width,
                                                                                                   menu_height):
                menu_x = pygame.math.clamp(pygame.mouse.get_pos()[0], 0, WIDTH - box_w / 2)
                menu_y = pygame.math.clamp(pygame.mouse.get_pos()[1] + 20, 0, HEIGHT - box_h / 2)

            menu_offset_x = menu_x - box_w / 2
            draw_ui_rect_outline(uisurface,
                                 menu_offset_x - 2, menu_y - 22,
                                 box_w + 18, box_h,
                                 (65, 65, 67))
            draw_ui_rect(uisurface,
                         menu_offset_x, menu_y - 20,
                         box_w + 14, box_h,
                         (40, 40, 46))
            draw_ui_rect(uisurface,
                         menu_offset_x, menu_y - 20,
                         box_w + 12, 20, (33, 33, 38))

            draw_ui_rect(uisurface,
                         menu_offset_x - 2, menu_y - 2 + SEARCH_MAX_ENTRIES * 30,
                         box_w + 16, screen_height * 0.03 + 14,
                         (230, 75, 61))

            # Draw input box
            node_input.draw(uisurface, menu_x - box_w / 2, menu_y + SEARCH_MAX_ENTRIES * 30 + 2, box_w,
                            screen_height * 0.03)

            # Clear menu option rects for this frame
            menu_option_rects.clear()

            # Draw menu options
            for i, node in enumerate(filtered_nodes[FIRST_RESULT:FIRST_RESULT + SEARCH_MAX_ENTRIES]):
                actual_index = FIRST_RESULT + i
                r = pygame.Rect(menu_x - box_w / 2, menu_y + 30 * i, box_w + 12, 30)
                menu_option_rects.append((r, node))

                # Update selected_index based on mouse hover only if scroll wheel wasn't used
                if actual_index == selected_index:

                    # Highlight selected option
                    color = (100, 100, 150)
                elif r.collidepoint(mx, my):
                    color = (55, 55, 55)
                else:
                    color = (40, 40, 46)
                draw_ui_rect(uisurface, r.x, r.y, r.width, r.height, color)

                draw_ui_text(uisurface, node.replace("_", " "), r.x + 5, r.y + 5, font, (255, 255, 255))

            # Scrollbar configuration
            scrollbar_x = menu_offset_x + box_w + 8  # Offset from your menu
            scrollbar_y = menu_y
            scrollbar_width = 8
            scrollbar_height = box_h - 2
            scrollbar_bg_color = (60, 60, 60)
            scrollbar_thumb_color = (160, 160, 160)

            # Draw scrollbar background (track)
            draw_ui_line(uisurface,
                         (scrollbar_x, scrollbar_y),
                         (scrollbar_x, scrollbar_y + scrollbar_height),
                         scrollbar_bg_color,
                         scrollbar_width)

            # Calculate thumb position and size
            if len(filtered_nodes) > 0:
                # How many items are visible at once (adjust based on your UI)
                visible_items = min(10, len(filtered_nodes))  # Assuming 10 visible items max

                # Thumb height represents the proportion of visible items to total items
                thumb_height = max(20, int(SEARCH_MAX_ENTRIES / len(filtered_nodes) * scrollbar_height))

                # Thumb position based on current selection
                # This creates a smooth scroll effect
                scroll_progress = selected_index / max(1, len(filtered_nodes) - 1)
                thumb_y = scrollbar_y + scroll_progress * (scrollbar_height - thumb_height)

                # Draw the scrollbar thumb
                draw_ui_line(uisurface,
                             (scrollbar_x, thumb_y),
                             (scrollbar_x, thumb_y + thumb_height),
                             scrollbar_thumb_color,
                             scrollbar_width)

            draw_ui_text(uisurface, "Select Effect", menu_x - box_w / 8, menu_y - 20, font, (255, 255, 255))


        else:

            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            node_input.disable()

        # Draw filename input
        fileNameInput.draw(uisurface, fileNameRect.x, fileNameRect.y, fileNameRect.width, fileNameRect.height)
        uim.update(dt)
        uim.draw_ui(uisurface)
        # ============ COMPOSITE UI SURFACE TO OPENGL DISPLAY ============

        # Convert UI surface to OpenGL texture and render it
        engine.render_ui_to_gldisplay(uisurface, 0, 0, uisurface.get_width(), uisurface.get_height())

        pygame.display.flip()


if __name__ == '__main__':
    main()
