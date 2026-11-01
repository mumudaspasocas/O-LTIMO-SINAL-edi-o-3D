from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from world import WorldBuilder
from story import LEVELS
import math
import random

app = Ursina()

window.title = "O ÚLTIMO SINAL — Terror 3D"
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False
window.fps_counter.enabled = True
window.color = color.rgb(5, 7, 12)

# Keep the UI readable even in dark areas.
camera.fov = 92
camera.clip_plane_far = 45

Sky(color=color.rgb(7, 10, 17))
AmbientLight(color=color.rgba(70, 78, 95, 0.55))
sun = DirectionalLight()
sun.look_at(Vec3(1, -2, -1))
sun.color = color.rgb(65, 68, 80)

builder = WorldBuilder()
current_level = 0
game_state = "menu"
active_interactable = None
toast_timer = 0.0
flash_timer = 0.0
collected = 0
story_log = []
intro_timer = 0.0

# UI
overlay = Entity(parent=camera.ui, model="quad", scale=(2, 2),
                 color=color.rgba(0, 0, 0, 0), z=1)
title_text = Text(
    parent=camera.ui, text="O ÚLTIMO SINAL",
    origin=(0, 0), y=0.20, scale=2.4, color=color.rgb(225, 230, 235),
    background=False,
)
subtitle_text = Text(
    parent=camera.ui, text="Uma experiência de terror psicológico",
    origin=(0, 0), y=0.09, scale=1.0, color=color.rgb(145, 160, 175),
)
start_text = Text(
    parent=camera.ui, text="ENTER  —  COMEÇAR",
    origin=(0, 0), y=-0.22, scale=1.2, color=color.rgb(100, 215, 225),
)
controls_text = Text(
    parent=camera.ui,
    text="WASD mover   •   Mouse olhar   •   E interagir   •   Shift correr",
    origin=(0, 0), y=-0.34, scale=0.75, color=color.rgb(140, 145, 155),
)
chapter_text = Text(
    parent=camera.ui, text="", x=-0.86, y=0.45, scale=0.9,
    color=color.rgb(175, 205, 215),
)
objective_text = Text(
    parent=camera.ui, text="", x=-0.86, y=0.39, scale=0.72,
    color=color.rgb(165, 170, 180),
)
prompt_text = Text(
    parent=camera.ui, text="", origin=(0, 0), y=-0.32, scale=1.0,
    color=color.rgb(120, 225, 230),
)
toast_text = Text(
    parent=camera.ui, text="", origin=(0, 0), y=-0.40, scale=0.9,
    color=color.rgb(230, 230, 220),
)
center_dot = Entity(
    parent=camera.ui, model="quad", scale=0.006,
    color=color.rgba(220, 230, 235, 190), z=-0.5,
)

# Full-screen chapter / ending cards.
card = Entity(parent=camera.ui, model="quad", scale=(2, 2),
              color=color.rgba(0, 0, 0, 235), z=-1)
card_title = Text(parent=camera.ui, text="", origin=(0, 0),
                  y=0.22, scale=1.65, color=color.rgb(225, 230, 235))
card_body = Text(parent=camera.ui, text="", origin=(0, 0),
                 y=0.02, scale=0.88, color=color.rgb(175, 185, 195))
card_continue = Text(parent=camera.ui, text="ENTER — CONTINUAR",
                     origin=(0, 0), y=-0.30, scale=0.85,
                     color=color.rgb(100, 215, 225))

player = FirstPersonController(
    position=(0, 2, 0),
    speed=3.4,
    origin_y=-0.5,
    mouse_sensitivity=Vec2(40, 40),
)
player.gravity = 0.65
player.jump_height = 0
player.cursor.visible = False
player.enabled = False
player.visible = False
mouse.locked = False

# Avoid falling below the floor in the deliberately simple maps.
def set_toast(text, duration=4.0):
    global toast_timer
    toast_text.text = text
    toast_timer = duration


def set_card(title, body, continue_text="ENTER — CONTINUAR"):
    global game_state
    game_state = "card"
    card.enabled = True
    card_title.enabled = True
    card_body.enabled = True
    card_continue.enabled = True
    card_title.text = title
    card_body.text = body
    card_continue.text = continue_text
    player.enabled = False
    mouse.locked = False
    mouse.visible = True
    prompt_text.text = ""


def hide_card():
    card.enabled = False
    card_title.enabled = False
    card_body.enabled = False
    card_continue.enabled = False


def update_hud():
    chapter_text.text = LEVELS[current_level]["name"]
    remaining = sum(1 for item in builder.items if item["type"] == "note")
    objective_text.text = f"LEMBRANÇAS: {3 - remaining}/3   |   ENCONTRE AS PISTAS"
    if active_interactable:
        if active_interactable["type"] == "note":
            prompt_text.text = "[E]  LER: " + active_interactable["title"]
        elif active_interactable["type"] == "exit":
            prompt_text.text = "[E]  INTERAGIR COM A PORTA"
    else:
        prompt_text.text = ""


def build_level(index):
    global current_level, collected, active_interactable
    current_level = index
    collected = 0
    active_interactable = None
    builder.build(index, LEVELS[index]["notes"])

    starts = [Vec3(-10.5, 2, -10.5), Vec3(-10.5, 2, -10.5), Vec3(-10.5, 2, -10.5)]
    player.position = starts[index]
    player.rotation_y = 0
    player.camera_pivot.rotation_x = 0
    player.enabled = True
    player.speed = 3.4
    hide_card()
    update_hud()


def begin_game():
    global game_state
    title_text.enabled = False
    subtitle_text.enabled = False
    start_text.enabled = False
    controls_text.enabled = False
    center_dot.enabled = True
    build_level(0)
    set_card(LEVELS[0]["name"], LEVELS[0]["intro"])


def nearest_interactable():
    candidates = []
    p = player.position
    for item in builder.items:
        d = math.sqrt((p.x - item["position"].x) ** 2 + (p.z - item["position"].z) ** 2)
        if d < 2.1:
            candidates.append((d, item))
    if builder.exit_entity:
        pos = builder.exit_entity["position"]
        d = math.sqrt((p.x - pos.x) ** 2 + (p.z - pos.z) ** 2)
        if d < 2.5:
            candidates.append((d, builder.exit_entity))
    return min(candidates, key=lambda pair: pair[0])[1] if candidates else None


def interact():
    global active_interactable, collected, game_state
    item = active_interactable
    if not item:
        set_toast("Não há nada ao alcance.", 1.5)
        return

    if item["type"] == "note":
        story_log.append((LEVELS[current_level]["name"], item["title"], item["text"]))
        for entity in item["entities"]:
            destroy(entity)
        builder.items.remove(item)
        collected += 1
        set_card(item["title"], item["text"], "ENTER — VOLTAR À EXPLORAÇÃO")
        update_hud()
        return

    remaining = sum(1 for obj in builder.items if obj["type"] == "note")
    if remaining:
        set_toast(f"A porta não responde. Ainda faltam {remaining} lembranças.", 3.0)
        return

    ending = LEVELS[current_level]["ending"]
    if current_level < len(LEVELS) - 1:
        next_level = current_level + 1
        build_level(next_level)
        set_card(LEVELS[next_level]["name"], LEVELS[next_level]["intro"])
    else:
        game_state = "ending"
        player.enabled = False
        mouse.locked = False
        mouse.visible = True
        card.enabled = True
        card_title.enabled = True
        card_body.enabled = True
        card_continue.enabled = True
        card_title.text = "O ÚLTIMO SINAL"
        card_body.text = (
            "A verdade não era que Daniel tinha perdido a irmã.\n\n"
            "Era que a lembrança dela era a única coisa que restava\n"
            "daquela noite — uma voz criada para que ele não precisasse\n"
            "encarar o próprio silêncio.\n\n"
            + ending
            + "\n\nA tela do telefone acende uma última vez:\n"
            "“Agora você pode ir.”"
        )
        card_continue.text = "ENTER — RECOMEÇAR     |     ESC — SAIR"


def input(key):
    global game_state
    if key == "escape":
        if game_state == "playing":
            set_card("PAUSADO", "Pressione ENTER para continuar.\nESC fecha o jogo.")
            game_state = "pause"
        elif game_state in ("menu", "ending"):
            application.quit()
        elif game_state in ("card", "pause"):
            if game_state == "pause":
                application.quit()
            else:
                resume_game()
    elif key == "enter":
        if game_state == "menu":
            begin_game()
        elif game_state in ("card", "pause"):
            resume_game()
        elif game_state == "ending":
            restart_game()
    elif key == "e" and game_state == "playing":
        interact()


def resume_game():
    global game_state
    hide_card()
    game_state = "playing"
    player.enabled = True
    mouse.locked = True
    mouse.visible = False


def restart_game():
    global game_state, story_log
    story_log = []
    hide_card()
    build_level(0)
    set_card(LEVELS[0]["name"], LEVELS[0]["intro"])


def update():
    global active_interactable, toast_timer, flash_timer, game_state

    if game_state == "playing":
        # Sprint while Shift is held.
        player.speed = 5.3 if held_keys["shift"] else 3.4

        # Gentle movement sway; subtle, not motion-sickness heavy.
        if held_keys["w"] or held_keys["a"] or held_keys["s"] or held_keys["d"]:
            camera.fov = lerp(camera.fov, 94, time.dt * 2)
        else:
            camera.fov = lerp(camera.fov, 91, time.dt * 2)

        active_interactable = nearest_interactable()
        update_hud()

        # Rare light flicker gives the halls a little life.
        if random.random() < 0.006:
            for light in builder.lights:
                if random.random() < 0.35:
                    light.enabled = False
                    invoke(setattr, light, "enabled", True, delay=0.07)

    if toast_timer > 0:
        toast_timer -= time.dt
        if toast_timer <= 0:
            toast_text.text = ""

# Start screen state.
game_state = "menu"
hide_card()
center_dot.enabled = False
chapter_text.enabled = False
objective_text.enabled = False
prompt_text.enabled = False
toast_text.enabled = False

# Enable HUD only after starting.
_original_update_hud = update_hud
def update_hud():
    _original_update_hud()
    visible = game_state == "playing"
    chapter_text.enabled = visible
    objective_text.enabled = visible
    prompt_text.enabled = visible
    toast_text.enabled = visible
    center_dot.enabled = visible

app.run()
