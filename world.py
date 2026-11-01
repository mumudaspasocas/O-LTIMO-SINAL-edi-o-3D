from ursina import Entity, Vec3, color, PointLight, scene, Sky, destroy
import math
import random


class WorldBuilder:
    """Cria os cenários usando geometria simples, sem arquivos de arte externos."""

    def __init__(self):
        self.entities = []
        self.lights = []
        self.items = []
        self.exit_entity = None
        self.level_index = 0

    def clear(self):
        for entity in self.entities:
            destroy(entity)
        for light in self.lights:
            destroy(light)
        self.entities.clear()
        self.lights.clear()
        self.items.clear()
        self.exit_entity = None

    def add(self, **kwargs):
        entity = Entity(**kwargs)
        self.entities.append(entity)
        return entity

    def wall(self, x, z, sx, sz, level, y=2.0):
        palettes = [
            color.rgb(48, 51, 58),
            color.rgb(47, 51, 57),
            color.rgb(39, 40, 48),
        ]
        return self.add(
            model="cube",
            position=(x, y, z),
            scale=(sx, 4.0, sz),
            color=palettes[level],
            texture="white_cube",
            collider="box",
        )

    def floor_tile(self, x, z, level):
        colors = [
            color.rgb(37, 36, 38),
            color.rgb(32, 36, 40),
            color.rgb(27, 27, 33),
        ]
        return self.add(
            model="cube",
            position=(x, -0.12, z),
            scale=(1, 0.2, 1),
            color=colors[level] if (int(x + z) % 2 == 0) else colors[level] * 0.8,
            texture="white_cube",
            collider=None,
        )

    def lamp(self, x, z, tint=None, intensity=1.0):
        tint = tint or color.rgb(150, 190, 205)
        fixture = self.add(
            model="cube",
            position=(x, 3.82, z),
            scale=(0.65, 0.08, 0.18),
            color=tint,
            unlit=True,
        )
        light = PointLight(
            parent=scene,
            position=Vec3(x, 3.35, z),
            color=tint,
        )
        light.range = 9 * intensity
        self.lights.append(light)
        return fixture

    def pillar(self, x, z, level):
        shades = [color.rgb(64, 63, 60), color.rgb(57, 62, 66), color.rgb(48, 47, 56)]
        self.add(
            model="cube",
            position=(x, 1.5, z),
            scale=(0.35, 3.0, 0.35),
            color=shades[level],
            texture="white_cube",
            collider="box",
        )

    def crate(self, x, z, scale=1):
        self.add(
            model="cube",
            position=(x, 0.48 * scale, z),
            scale=(0.9 * scale, 0.9 * scale, 0.9 * scale),
            color=color.rgb(66, 49, 39),
            texture="white_cube",
            collider="box",
            rotation_y=random.randint(-8, 8),
        )

    def build(self, level_index, notes_data):
        self.clear()
        self.level_index = level_index

        # Ambient palette changes by chapter.
        fog_colors = [
            color.rgb(9, 13, 20),
            color.rgb(8, 15, 20),
            color.rgb(15, 9, 18),
        ]
        scene.fog_color = fog_colors[level_index]
        scene.fog_density = (7, 27 if level_index == 0 else 23)

        # A 28x28 building shell.
        self.add(
            model="cube", position=(0, -0.22, 0),
            scale=(28, 0.4, 28),
            color=color.rgb(29, 29, 32),
            texture="white_cube", collider="box",
        )
        self.add(
            model="cube", position=(0, 4.25, 0),
            scale=(28, 0.3, 28),
            color=color.rgb(18, 19, 23),
            texture="white_cube", collider="box",
        )

        self.wall(0, -14, 28, 0.5, level_index)
        self.wall(0, 14, 28, 0.5, level_index)
        self.wall(-14, 0, 0.5, 28, level_index)
        self.wall(14, 0, 0.5, 28, level_index)

        # A small maze with gaps. All coordinates are intentionally walkable.
        if level_index == 0:
            segments = [
                (-7, -7, 12, .35), (5, -7, 10, .35),
                (-7, 0, .35, 9), (2, 2, 12, .35),
                (8, 7, .35, 9), (-5, 8, 11, .35),
                (-1, -1, .35, 5),
            ]
            lamps = [(-9, -9), (0, -9), (9, -3), (-9, 5), (4, 10)]
            crates = [(-10, -3), (5, -10), (-9, 10)]
        elif level_index == 1:
            segments = [
                (-8, -7, 10, .35), (4, -7, 12, .35),
                (-4, -2, .35, 10), (5, 1, 11, .35),
                (9, 7, .35, 9), (-7, 8, 11, .35),
                (1, 8, .35, 6),
            ]
            lamps = [(-10, -10), (7, -10), (-8, 2), (8, 4), (-1, 11)]
            crates = [(-10, 4), (3, -4), (10, 10)]
        else:
            segments = [
                (-8, -8, 11, .35), (5, -8, 10, .35),
                (-7, -1, .35, 11), (2, -2, 12, .35),
                (8, 4, .35, 9), (-2, 8, 12, .35),
                (2, 5, .35, 6),
            ]
            lamps = [(-10, -10), (9, -10), (-10, 5), (5, 5), (0, 11)]
            crates = [(-10, -4), (5, -5), (10, 10)]

        for x, z, sx, sz in segments:
            self.wall(x, z, sx, sz, level_index)

        for x, z in lamps:
            tint = color.rgb(165, 190, 205)
            if level_index == 2 and random.random() < 0.5:
                tint = color.rgb(175, 65, 75)
            self.lamp(x, z, tint, 0.8)

        for x, z in crates:
            self.crate(x, z, random.choice([0.8, 1.0, 1.15]))

        for x, z in [(-12, -12), (12, -12), (-12, 12), (12, 12)]:
            self.pillar(x, z, level_index)

        # Glowing memory objects. Each one can be read once.
        note_positions = [
            (-9.5, -3.5), (3.5, -10), (9.5, 10),
        ]
        if level_index == 1:
            note_positions = [(-10, 3), (0, -10), (10, 8)]
        elif level_index == 2:
            note_positions = [(-10, -4), (5, -5), (10, 10)]

        for i, note in enumerate(notes_data):
            x, z = note_positions[i]
            pedestal = self.add(
                model="cube",
                position=(x, 0.16, z),
                scale=(0.8, 0.25, 0.8),
                color=color.rgb(42, 46, 54),
                texture="white_cube",
                collider=None,
            )
            orb_color = color.rgb(80, 205, 220) if level_index < 2 else color.rgb(215, 95, 115)
            orb = self.add(
                model="sphere",
                position=(x, 0.85, z),
                scale=0.28,
                color=orb_color,
                unlit=True,
                collider=None,
            )
            halo = self.add(
                model="sphere",
                position=(x, 0.85, z),
                scale=0.48,
                color=color.rgba(60, 180, 210, 45),
                unlit=True,
                collider=None,
            )
            self.items.append({
                "type": "note",
                "title": note["title"],
                "text": note["text"],
                "position": Vec3(x, 0.85, z),
                "entities": [pedestal, orb, halo],
            })

        # Exit beacon: visible from a distance, but usable only after all memories.
        exit_x, exit_z = (10.5, -10.5) if level_index == 0 else ((-10.5, 10.5) if level_index == 1 else (10.5, -10.5))
        gate = self.add(
            model="cube",
            position=(exit_x, 1.35, exit_z),
            scale=(1.0, 2.7, 0.25),
            color=color.rgb(110, 34, 43),
            unlit=True,
            collider=None,
        )
        self.add(
            model="cube",
            position=(exit_x, 2.75, exit_z),
            scale=(1.35, 0.12, 0.35),
            color=color.rgb(185, 65, 75),
            unlit=True,
            collider=None,
        )
        self.exit_entity = {
            "type": "exit",
            "position": Vec3(exit_x, 1, exit_z),
            "entity": gate,
        }

        # The exit is also a subtle light source.
        exit_light = PointLight(
            parent=scene,
            position=Vec3(exit_x, 2, exit_z),
            color=color.rgb(170, 40, 55),
        )
        exit_light.range = 7
        self.lights.append(exit_light)
