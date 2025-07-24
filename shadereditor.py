import sys
import pygame
from graphicrender import GraphicsEngine
from components.node import Node
from components.connections import Connection
import pygame_widgets
from pygame_widgets.slider import Slider
from ui.colorpicker import ColorPicker
from ui.textinput import TextInput
from ui.pointpicker import PointPicker
from ui.selectbox import SelectBox
import json
import os

import pygame_gui

pygame.init()
gldisplay = pygame.display.set_mode((1920, 1080), pygame.OPENGL | pygame.DOUBLEBUF)
uisurface = pygame.Surface((1920, 1080)).convert_alpha()
ui_s = 1 / 1.875

output_window = pygame.Surface(
    (int(gldisplay.get_width() * ui_s), int(gldisplay.get_height() * ui_s))
).convert((255, 65282, 16711681, 0))

engine = GraphicsEngine(output_window, 1, gldisplay.get_size(), ui_s)

screen_width, screen_height = gldisplay.get_size()
texture_width = output_window.get_width()
texture_height = output_window.get_height()

padding = 0.1 * screen_height
x_pos, y_pos = (screen_width - texture_width) / 2, 0.05 * screen_height

rect_x = 0
rect_y = padding + texture_height
rect_width = screen_width * 0.8
rect_height = screen_height - padding - texture_height

pygame.display.set_caption("Lumos")

# Create a simple test image if testimg.jpg doesn't exist
try:
    testimg = pygame.image.load("textures/testimg.jpg").convert()
except pygame.error:
    testimg = pygame.Surface((texture_width, texture_height))
    testimg.fill((255, 0, 0))  # Red background
    pygame.draw.circle(testimg, (0, 255, 0), (texture_width // 2, texture_height // 2), 50)  # Green circle
testimg = pygame.transform.scale(testimg, output_window.get_size())

nodes = []
connects = []

nodes.append(Node("input", screen_width * 0.2, screen_height * 0.8))
font = pygame.font.SysFont("Arial", 16)

greysquare = pygame.Surface((8, 8))
greysquare.fill((255, 255, 255))

# Create a simple arrow if arrow.png doesn't exist
arrow = pygame.image.load("arrow.png").convert()
arrow.set_colorkey((39, 39, 45))

outlinesquare = pygame.Surface((greysquare.get_width() + 2, greysquare.get_height() + 2))

uim = pygame_gui.UIManager(uisurface.get_size())

# Separate shader functions mapping
shader_functions = {
    "Contrast": engine.apply_contrast,
    "Pulse": engine.apply_pulsing,
    "Blur": engine.apply_blur,
    "Flicker": engine.apply_flicker,
    "Vignette": engine.apply_vignette,
    "Saturation": engine.apply_saturation,
    "Point Light": engine.apply_point_light,
    "Distortion": engine.apply_distortion,
    "Scan Line": engine.apply_scanline,
    "Phosphor Mask": engine.apply_phosphor_mask,
    "Bloom": engine.apply_bloom,
    "Chromatic Aberration": engine.chromatic_aberration,
}

# Effect settings without shader functions
with open("node_configs/settings.json", 'r') as f:
    effect_settings = json.load(f)
'''
effect_settings =    {
    "Contrast": {
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
    "Blur": {
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
        "uniforms": {
            "noiseIntensity": {
                "type": "float",
                "value": 0.1,
                "min": 0.0,
                "max": 0.3,
                "step": 0.01
            },
            "noiseScale": {
                "type": "float",
                "value": 0.02,
                "min": 0.001,
                "max": 0.1,
                "step": 0.001
            },
            "noiseSpeed": {
                "type": "float",
                "value": 10,
                "min": 0.1,
                "max": 30.0,
                "step": 0.1
            }
        }
    },
    "Vignette": {
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
        "uniforms": {
            "lightPosition": {
                "type": "vec2",
                "value": (0.5, 0.5),
            },
            "radius": {
                "type": "float",
                "value": 0.4,
                "min": 0.0,
                "max": 1.5,
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
                "value": (255.0, 255.0, 255.0)
            }
        }
    },
    "Distortion": {
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
with open("node_configs/settings.json", "w") as f:
    json.dump(effect_settings, f, indent=4)
'''


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
        "nodes": [export_node(node) for node in nodes],
        "connections": [export_connection(conn) for conn in connections]
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
            connections.append(Connection(node_lookup[inp_id], node_lookup[out_id]))
        else:
            print(f"Skipping invalid connection: {conn_data}")

    return nodes, connections


def import_node(data):
    node = Node(data["type"], data["x"], data["y"])
    node.id = data["id"]
    if node.type != "input":
        node.widgets = []

        settings = effect_settings[node.type]["uniforms"]
        for key, default in data["uniforms"].items():
            uniform = settings[key]
            # Just reuse your create_widgets_for_node logic, but inject the `default` value
            uniform["value"] = default  # temporarily override for widget creation

        node.widgets = create_widgets_for_node(node)
    return node


def import_connection(data):
    inp = data["input"]
    out = data["output"]
    conn = Connection(Node(inp["type"], inp["x"], inp["y"]), Node(out["type"], out["x"], out["y"]))
    return conn


def export_node(node: Node):
    return {
        "id": node.id,
        "type": node.type,
        "x": node.x,
        "y": node.y,
        "uniforms": {
            key: widget.getValue()
            for key, widget in node.widgets
        }
    }


def export_connection(conn: Connection):
    return {
        "input": conn.inp.id,
        "output": conn.out.id,
    }


def create_widgets_for_node(node):
    widgets = []
    settings = effect_settings[node.type]["uniforms"]
    for k, (uniform_key, uniform) in enumerate(settings.items(), start=4):
        ui_x = int(gldisplay.get_width() * 0.87)
        ui_y = int(gldisplay.get_height() * 0.04 * k)
        ui_w = int(gldisplay.get_width() * 0.1)
        ui_h = int(gldisplay.get_height() * 0.015)

        if uniform["type"] == "float":
            widget = Slider(
                uisurface,
                ui_x,
                ui_y,
                ui_w,
                3,
                min=uniform["min"],
                max=uniform["max"],
                step=uniform["step"],
                initial=uniform["value"],
                handleRadius=12
            )
        elif uniform["type"] == "vec2":
            widget = PointPicker(ui_x - 10, ui_y, ui_w, ui_h, uniform_key, default=uniform["value"])
        elif uniform["type"] == "vec3":
            widget = ColorPicker(ui_x - 10, ui_y, ui_w, ui_h, uniform_key, default=uniform["value"])
        elif uniform["type"] == "choice":
            widget = SelectBox(ui_x - 10, ui_y, ui_w, ui_h, uniform_key, uniform["choices"], default=uniform["value"])
        else:
            continue  # Unknown widget type
        widgets.append((uniform_key, widget))
    return widgets


def execute_node_chain():
    executed_list = []
    visited = set()

    def dfs(node):
        if node in visited:
            return
        visited.add(node)
        executed_list.append(node)
        node.color = (47, 48, 54)

        for con in connects:
            if con.inp == node:
                dfs(con.out)

    # Start from the input node
    if nodes and nodes[0].type == "input":
        # Clear output window and blit test image
        output_window.fill((0, 0, 0))  # Clear first
        output_window.blit(testimg, (0, 0))
        engine.update_screen_texture(output_window)
        # Reset the original stored flag so original texture gets updated
        if hasattr(engine, '_original_stored'):
            delattr(engine, '_original_stored')
        dfs(nodes[0])

    return executed_list


def apply_post_effects(executed_nodes):
    for node in executed_nodes:
        if node.type in effect_settings and node.type in shader_functions:
            # Get the shader function from the separate mapping
            shader_func = shader_functions[node.type]

            if hasattr(node, "widgets"):
                kwargs = {}
                for uniform_key, widget in node.widgets:
                    if isinstance(widget, Slider):
                        kwargs[uniform_key] = widget.getValue()
                    elif isinstance(widget, PointPicker):
                        kwargs[uniform_key] = widget.point
                    elif isinstance(widget, ColorPicker):
                        kwargs[uniform_key] = widget.color
                    elif isinstance(widget, SelectBox):
                        kwargs[uniform_key] = widget.value

                shader_func(**kwargs)


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
menu_position = (screen_width // 2, screen_height * 5 / 7)
filtered_nodes = []
clock = pygame.time.Clock()
node_input = TextInput(font)
selected_index = 0
FIRST_RESULT = 0
SEARCH_MAX_ENTRIES = int(8 * gldisplay.get_width() / 1920)
menu_option_rects = []

fileName = ""
fileNameInput = TextInput(font, screen_width * 0.1)
fileNameInput.disable()
fileNameRect = pygame.Rect(screen_width * 0.5, screen_height * 0.01, screen_width * 0.1, screen_height * 0.02)
result = ""
filePath = ""
ignore_mouse_hover = False
ignore_mouse_timer = 0

while True:
    dt = clock.tick(60)/1000.0
    left, middle, right = pygame.mouse.get_pressed(3)
    mx, my = pygame.mouse.get_pos()
    events = pygame.event.get()
    pygame_widgets.update(events)

    # Clear UI surface at start of frame
    uisurface.fill((0, 0, 0, 0))  # Transparent fill

    # Handle events (same as before)
    for node in nodes:
        if hasattr(node, "widgets"):
            for uniform_key, widget in node.widgets:
                if isinstance(widget, PointPicker):
                    widget.handle_event(events, texture_width, texture_height, x_pos, y_pos, font)
                elif isinstance(widget, ColorPicker):
                    widget.handle_event(events, font)
                elif isinstance(widget, SelectBox):
                    widget.handle_event(events)

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
                filePath = event.text
                chosenFile = filePath
                fileName = chosenFile.replace(os.getcwd() + "\\", "")
                fileNameInput.set_text(fileName.replace(".json", ""))

                nodes, connects = load_graph_from_file(chosenFile)
                uifiledialog.kill()

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
                filtered_nodes = [n for n in node_types if node_input.get_text().lower() in n.lower()]

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
                filtered_nodes = [n for n in node_types if node_input.get_text().lower() in n.lower()]
                if filtered_nodes and selected_index < len(filtered_nodes):
                    new_node = Node(filtered_nodes[selected_index], x=mx, y=my)
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
                filtered_nodes = [n for n in node_types if node_input.get_text().lower() in n.lower()]
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
                            new_node = Node(node_type, x=mx, y=my)
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
                    connects = [con for con in connects if con.inp != node and con.out != node]
                    node.delete_cons = False

    # Clamp values to valid ranges
    if show_node_menu:
        filtered_nodes = [n for n in node_types if node_input.get_text().lower() in n.lower()]
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
    executed_nodes = execute_node_chain()
    engine.set_position_and_size(x_pos, y_pos, texture_width, texture_height)

    if delete and currentnode is not None and currentnode.type != "input":
        connects = [con for con in connects if con.inp != currentnode and con.out != currentnode]
        nodes.remove(currentnode)
        currentnode = None
        pygame.mouse.set_visible(True)
        delete = False

    apply_post_effects(executed_nodes)
    engine.render()

    # ============ START UI DRAWING TO UI SURFACE ============

    # Draw main workspace background
    draw_ui_rect(uisurface, rect_x, rect_y, rect_width, rect_height, (38, 38, 44))

    # Draw sidebar separator and background
    draw_ui_line(uisurface,
                 (gldisplay.get_width() * 0.8, 0),
                 (gldisplay.get_width() * 0.8, gldisplay.get_height()),
                 (9, 9, 9))
    draw_ui_rect(uisurface,
                 gldisplay.get_width() * 0.8, 0,
                 gldisplay.get_width() * 0.2, gldisplay.get_height(),
                 (40, 40, 46))

    # Draw horizontal separator
    draw_ui_rect(uisurface, 0, rect_y, rect_width, 2, (9, 9, 9))

    # Draw current node title
    if currentnode is not None:
        draw_ui_text(uisurface,
                     currentnode.type.title().replace("_", " "),
                     gldisplay.get_width() * 0.9,
                     gldisplay.get_height() * 0.01,
                     font, (255, 255, 255))

    # Draw connections
    for connect in connects:
        start = connect.inp.out.midright
        end = connect.out.inp.midleft

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
    if currentnode is not None and currentnode.type != "input":
        for uniform_key, widget in currentnode.widgets:
            widget.enable()
            if isinstance(widget, Slider):
                # Draw slider background
                draw_ui_rect(uisurface,
                             widget.getX(), widget.getY(),
                             widget.getWidth(), int(gldisplay.get_height() * 0.006),
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
                             widget.getX() - gldisplay.get_width() * 0.05,
                             widget.getY() - gldisplay.get_height() * 0.01,
                             font, (255, 255, 255))

            elif isinstance(widget, PointPicker):
                widget.draw_button(uisurface, font)
            elif isinstance(widget, ColorPicker):
                widget.draw(font, uisurface)
            elif isinstance(widget, SelectBox):
                widget.draw(uisurface, font)

    # Draw nodes
    for o, node in enumerate(nodes):
        # Node outline and body
        draw_ui_rect(uisurface, node.x - 1, node.y - 1, node.width + 2, node.height + 2, node.outline_c)
        draw_ui_rect(uisurface, node.x, node.y, node.width, node.height, node.color)
        draw_ui_rect(uisurface, node.x + 1, node.y + node.height - 2, node.width, 2, (121, 168, 208))

        # Handle time-based effects
        if node.type in ["Flicker", "Pulse"]:
            current_time = pygame.time.get_ticks() / 1000.0
            engine.progs[node.type.lower()]["u_time"] = current_time

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

        # Handle node connections
        if left:
            if node.connecting:
                innode = [(k, n) for k, n in enumerate(nodes) if
                          (n.rect.collidepoint(mx, my) or n.inp.collidepoint(mx, my)) and k != o]
                if innode:
                    new_connection = Connection(node, innode[0][1])
                    if new_connection not in connects and Connection(innode[0][1], node) not in connects:
                        connects.append(new_connection)
                draw_ui_line(uisurface, node.out.midright, (mx, my), (255, 255, 255), 1)

            if node.out.collidepoint(mx, my):
                node.connecting = True
        else:
            node.connecting = False

        node.update(mx, my)

        # Disable widgets for non-current nodes
        for uniform_key, slider in node.widgets:
            slider.disable()
            if currentnode is not None:
                if currentnode == node:
                    slider.enable()

    # Handle file name input
    fileNameInput.update(dt)

    # Draw node menu if active
    if show_node_menu:
        node_input.enable()
        node_input.update(dt)
        menu_x, menu_y = menu_position
        box_w = screen_width * 0.15
        box_h = SEARCH_MAX_ENTRIES * 30 + screen_height * 0.0002
        # Menu background
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

        draw_ui_line(uisurface,
                     (menu_offset_x, menu_y - 1),
                     (menu_x + box_w / 2 + 12, menu_y - 1),
                     (9, 9, 9), 2)

        draw_ui_rect(uisurface,
                     menu_offset_x - 2, menu_y - 2 + SEARCH_MAX_ENTRIES * 30,
                     box_w + 16, screen_height * 0.03 + 12,
                     (230, 75, 61))

        # Draw input box
        node_input.draw(uisurface, menu_x - box_w / 2, menu_y + SEARCH_MAX_ENTRIES * 30, box_w,
                        screen_height * 0.03)

        filtered_nodes = [n for n in node_types if node_input.get_text().lower() in n.lower()]

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
        scrollbar_height = box_h
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

        # Alternative: Simple position indicator (just a dot)
        # if len(filtered_nodes) > 0:
        #     dot_y = scrollbar_y + (selected_index / max(1, len(filtered_nodes) - 1)) * scrollbar_height
        #     draw_ui_circle(uisurface, (scrollbar_x + scrollbar_width//2, dot_y), 4, scrollbar_thumb_color)
        # Optional: Add scrollbar end caps for better visual

        draw_ui_text(uisurface, "Select Effect", menu_x - box_w / 8, menu_y - 20, font, (255, 255, 255))
    else:
        node_input.disable()

    # Draw filename input
    fileNameInput.draw(uisurface, fileNameRect.x, fileNameRect.y, fileNameRect.width, fileNameRect.height)
    uim.update(dt)
    uim.draw_ui(uisurface)
    # ============ COMPOSITE UI SURFACE TO OPENGL DISPLAY ============

    # Convert UI surface to OpenGL texture and render it
    engine.render_ui_to_gldisplay(uisurface, 0, 0, uisurface.get_width(), uisurface.get_height())
    engine.update_screen_texture(output_window)

    pygame.display.flip()
