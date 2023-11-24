# MenuTitle: Centering Tools
# -*- coding: utf-8 -*-

__doc__ = """
GUI for various centering tools: horizontally, vertically in x-height, ascender height, and cap height.
"""

import vanilla
from Foundation import NSPoint


class CenteringToolUI:
    def __init__(self):
        self.font = Glyphs.font
        horizontal_padding = 16
        top_padding = 14
        bottom_padding = 16
        button_height = 20
        button_spacing = 8
        button_titles = [
            "Horizontally center",
            "Vertically center in x-height",
            "Vertically center in capheight",
            "Vertically center in ascender height",
        ]
        actions = [
            self.centerHorizontally,
            self.centerXHeight,
            self.centerCapHeight,
            self.centerAscenderHeight,
        ]

        total_height = (
            top_padding
            + bottom_padding
            + button_height * len(button_titles)
            + button_spacing * (len(button_titles) - 1)
        )

        self.w = vanilla.FloatingWindow((300, total_height), "Centering Tool")

        y = top_padding

        for title, action in zip(button_titles, actions):
            setattr(
                self.w,
                title,
                vanilla.Button(
                    (horizontal_padding, y, -horizontal_padding, button_height),
                    title,
                    callback=action,
                ),
            )
            y += button_height + button_spacing

        self.w.open()

    def get_combined_bounds(self, selected_paths, selected_components, selected_anchors):
        combined_min_x, combined_max_x = float('inf'), float('-inf')
        combined_min_y, combined_max_y = float('inf'), float('-inf')

        for item in selected_paths + selected_components:
            min_x = item.bounds.origin.x
            max_x = item.bounds.origin.x + item.bounds.size.width
            min_y = item.bounds.origin.y
            max_y = item.bounds.origin.y + item.bounds.size.height

            combined_min_x = min(combined_min_x, min_x)
            combined_max_x = max(combined_max_x, max_x)
            combined_min_y = min(combined_min_y, min_y)
            combined_max_y = max(combined_max_y, max_y)

        for anchor in selected_anchors:
            anchor_x = anchor.position.x
            anchor_y = anchor.position.y

            combined_min_x = min(combined_min_x, anchor_x)
            combined_max_x = max(combined_max_x, anchor_x)
            combined_min_y = min(combined_min_y, anchor_y)
            combined_max_y = max(combined_max_y, anchor_y)

        return combined_min_x, combined_max_x, combined_min_y, combined_max_y

    def center_selection(self, horizontal=False, vertical=False, height=None):
        selected_paths = [path for path in self.font.selectedLayers[0].paths if path.selected]
        selected_components = [comp for comp in self.font.selectedLayers[0].components if comp.selected]
        selected_anchors = [anchor for anchor in self.font.selectedLayers[0].anchors if anchor.selected]

        if not selected_paths and not selected_components and not selected_anchors:
            print("No paths, components, or anchors selected.")
            return

        include_anchors_in_bounds = not selected_paths and not selected_components
        combined_min_x, combined_max_x, combined_min_y, combined_max_y = self.get_combined_bounds(
            selected_paths, selected_components, selected_anchors if include_anchors_in_bounds else []
        )

        move_x = (self.font.selectedLayers[0].width / 2 - (combined_max_x + combined_min_x) / 2) if horizontal and combined_min_x is not None else 0
        move_y = (height / 2 - (combined_max_y + combined_min_y) / 2) if vertical and combined_min_y is not None else 0

        for item in selected_paths + selected_components:
            item.applyTransform((1.0, 0.0, 0.0, 1.0, move_x, move_y))

        for anchor in selected_anchors:
            anchor.position = NSPoint(anchor.position.x + move_x, anchor.position.y + move_y)

    def centerHorizontally(self, sender):
        self.center_selection(horizontal=True)

    def centerXHeight(self, sender):
        self.center_selection(
            vertical=True, height=self.font.selectedLayers[0].master.xHeight
        )

    def centerAscenderHeight(self, sender):
        self.center_selection(
            vertical=True, height=self.font.selectedLayers[0].master.ascender
        )

    def centerCapHeight(self, sender):
        self.center_selection(
            vertical=True, height=self.font.selectedLayers[0].master.capHeight
        )

CenteringToolUI()