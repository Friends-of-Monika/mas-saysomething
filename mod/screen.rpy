# screen.rpy contains custom text GUI that shows up when Monika is asked to
# say something.
#
# This file is part of Say Something (see link below):
# https://github.com/friends-of-monika/mas-saysomething


init 100 python in _fom_saysomething:

    import store
    from store import ui

    import math
    from collections import OrderedDict


    # Orderect dictionary is used to preserve order when rendering a table of
    # selectors. This dictionary contains key (human readable name of expression
    # part) to list of 2-tuples of the following elements:
    #  [0]: expression code/mnemonic
    #  [1]: expression human readable description
    EXPR_MAP = OrderedDict([
        ("Pose", [
            ("1", "Rest on hands"),
            ("2", "Cross"),
            ("3", "Point right, rest"),
            ("4", "Point right"),
            ("5", "Lean"),
            ("6", "Down"),
            ("7", "Point right, down")
        ]),
        ("Eyes", [
            ("e", "Normal"),
            ("w", "Wide"),
            ("s", "Sparkle"),
            ("t", "Smug"),
            ("c", "Crazy"),
            ("r", "Look right"),
            ("l", "Look left"),
            ("h", "Closed, happy"),
            ("d", "Closed, sad"),
            ("k", "Wink left"),
            ("n", "Wink right"),
            ("f", "Soft"),
            ("m", "Smug, left"),
            ("g", "Smug, right")
        ]),
        ("Eyebrows", [
            ("u", "Up"),
            ("f", "Furrowed"),
            ("k", "Knit"),
            ("s", "Straight"),
            ("t", "Thinking")
        ]),
        ("Blush", [
            (None, "None"),
            ("bl", "Line"),
            ("bs", "Shade"),
            ("bf", "Full")
        ]),
        ("Tears", [
            (None, "None"),
            ("ts", "Streaming"),
            ("td", "Dried"),
            ("tp", "Pooled"),
            ("tu", "Tearing up")
        ]),
        ("Sweat", [
            (None, "None"),
            ("sdl", "Left cheek"),
            ("sdr", "Right cheek"),
        ]),
        ("Mouth", [
            ("a", "Smile, closed"),
            ("b", "Smile, open"),
            ("c", "Straight"),
            ("d", "Open"),
            ("o", "Gasp"),
            ("w", "Wide"),
            ("x", "Grit teeth"),
            ("p", "Pout"),
            ("t", "Triangle")
        ])
    ])


    # Positions list containing Monika table positions from leftmost [0] to
    # rightmost [9]. Items are usable with renpy.show(..., at=list[...]) call.
    POSITIONS = [
        store.t41, #0
        store.t31, #1
        store.t21, #2, usually used in talk menu and scrollable choices
        store.t42, #3

        store.t11, #4, default middle screen position
        #store.t32, formerly #5, same as #4 so no need to keep it here
        store.t43, #5

        store.t22, #6
        store.t33, #7

        store.t44  #8
    ]


    class Picker(object):

        def __init__(self):
            # This dictionary contains key to 2-tuple of:
            #  [0]: current expression cursor index
            #  [1]: current expression human readable name
            # Initially all cursors are at zero (with corresponding expression names.)
            self.pose_cursors = {key: (0, EXPR_MAP[key][0][1]) for key in EXPR_MAP.keys()}

            # Position object to use when showing Monika at her table. By
            # default, her usual middle screen position.
            self.position = POSITIONS[4]

            # Adjustment object to define slider properties for position slider
            # and handle value changes.
            self.position_adjustment = ui.adjustment(
                range=9,
                value=4,
                adjustable=True,
                changed=self.on_position_change
            )

            # Flag value for flipping selectors/position GUI to left side of
            # screen if it would mean Monika is behind the GUI and not in user's
            # sight.
            self.gui_flip = False

            # Variable that stores entered user text prompt.
            self.text = ""

        def pose_switch_selector(self, key, forward):
            """
            Switches pose for selector by the specified key, forward or backward. If
            cursor is zero/max value and is requested to increment/decrement
            correspondingly, the value is wrapped.

            IN:
                key -> str:
                    Key of selector to switch. See __EXPR_MAP above.

                forward -> bool:
                    True if need to increment cursor, False to decrement.
            """

            curr = self.pose_cursors[key][0]
            _max = len(EXPR_MAP[key]) - 1

            if forward:
                if curr == _max:
                    new = 0
                else:
                    new = curr + 1
            else:
                if curr == 0:
                    new = _max
                else:
                    new = curr - 1

            self.pose_cursors[key] = (new, EXPR_MAP[key][new][1])
            return 0

        def get_pose_label(self, key):
            """
            Returns label for the current value of the specified selector key (see
            __EXPR_MAP in this module.)

            IN:
                key -> str:
                    Selector key to return human readable name for.

            OUT:
                str:
                    Human readable selector item name.
            """

            curr = self.pose_cursors[key][0]
            return EXPR_MAP[key][curr][1]

        def get_sprite_code(self):
            """
            Builds sprite code for the current selectors configuration.

            OUT:
                str:
                    Sprite code for use in renpy.show(...)
            """

            code = list()
            for key, values in EXPR_MAP.items():
                value = values[self.pose_cursors[key][0]][0]
                if value is not None:
                    code.append(value)
            return "".join(code)

        def is_text_empty(self):
            """
            Checks if stored text is empty (e.g. length is zero not including
            leading or trailing whitespace.)

            OUT:
            """

            return len(self.text.strip()) > 0

        def on_position_change(self, value):
            """
            Callback function for position bar.

            If value is greater than 5 the GUI is flipped to left side.

            IN:
                value -> float:
                    New value of position bar slider.
            """

            self.position = POSITIONS[value]
            self.gui_flip = value > 5

        def on_text_change(self, value):
            """
            Callback for text input prompt. Restarts interaction on every
            alteration.

            IN:
                value -> str:
                    New input field value.
            """

            self.text = value
            renpy.restart_interaction()

        def on_enter_press(self):
            """
            Callback for Enter key press. Only returns text value when it is not
            empty (see is_text_empty(...))

            OUT:
                str:
                    Text if it is not empty.

                None:
                    If text is empty.
            """

            # Need one more check since key press isn't covered by 'Say' button
            # sensitive expression.
            if self.is_text_empty():
                # This is equivalent to using Return(0) action.
                # https://lemmasoft.renai.us/forums/viewtopic.php?p=536626#p536626
                return self.text

    picker = None


# GUI elements styling, mostly reused to keep up with MAS theme and style.
# Some elements have been adjusted for design of this submod's GUI.

style fom_saysomething_picker_frame is gui_frame:
    background Frame(["gui/confirm_frame.png", "gui/frame.png"], gui.confirm_frame_borders, tile=gui.frame_tile)

style fom_saysomething_picker_frame_dark is gui_frame:
    background Frame(["gui/confirm_frame.png", "gui/frame_d.png"], gui.confirm_frame_borders, tile=gui.frame_tile)

style fom_saysomething_confirm_button is generic_button_light:
    xysize (175, None)
    padding (10, 5, 10, 5)

style fom_saysomething_confirm_button_dark is generic_button_dark:
    xysize (175, None)
    padding (10, 5, 10, 5)

style fom_saysomething_confirm_button_text is generic_button_text_light:
    text_align 0.5
    layout "subtitle"

style fom_saysomething_confirm_button_text_dark is generic_button_text_dark:
    text_align 0.5
    layout "subtitle"


# Expression/pose, location and say text picker GUI screen.
# NOTE: in this screen, picker is referenced directly as it is implied that it
# is set in fom_saysomething_event event.

screen fom_saysomething_picker:
    style_prefix "fom_saysomething_picker"

    vbox:
        # Flip GUI to prevent hiding Monika behind it.
        if not picker.gui_flip:
            align (0.95, 0.3)
        else:
            align (0.05, 0.3)

        spacing 10

        vbox:
            spacing 10

            # Selectors panel.

            frame:
                padding (30, 30)

                vbox:
                    spacing 10

                    for key, value in _fom_saysomething.EXPR_MAP.items():
                        hbox:
                            xmaximum 350
                            xfill True

                            # Split into two hboxes to align arrows and labels
                            # properly, so that one can click them without
                            # missing if label is too big; this layout preserves
                            # space for big labels.

                            hbox:
                                xfill True
                                xmaximum 110
                                text key

                            hbox:
                                xmaximum 240
                                xfill True
                                xalign 1.0

                                textbutton "<" action Function(picker.pose_switch_selector, key, forward=False) xalign 0.0
                                text picker.get_pose_label(key) xalign 0.5
                                textbutton ">" action Function(picker.pose_switch_selector, key, forward=True) xalign 1.0

            # Position slider panel.

            frame:
                padding (30, 5)

                hbox:
                    xmaximum 350
                    xfill True
                    spacing 25

                    text "Position"
                    bar:
                        xalign 1.0
                        yalign 0.5
                        adjustment picker.position_adjustment
                        released Return(0)

        # Confirmation buttons area.

        frame:
            background None
            padding (30, 15)

            hbox:
                align (0.5, 0.5)

                xmaximum 250
                xfill True
                spacing 10

                style_prefix "fom_saysomething_confirm"

                # Note: this button sensitivity relies on Ren'Py interaction
                # restart that is done in text input field callback.
                textbutton "Say":
                    action Return(picker.text)
                    sensitive picker.is_text_empty()
                textbutton "Close" action Return(False) xalign 1.0

    # Text input area styled as textbox and key capture so that Enter key press
    # is the same as pressing 'Say' button.

    key "K_RETURN" action Function(picker.on_enter_press) capture True

    window:
        align (0.5, 0.98)

        vbox:
            align (0.5, 0.5)
            spacing 30

            text "What do you want me to say?~" style "input_prompt"
            input:
                # Note: in order to always have the most up to date text this
                # callback updates it internally in _fom_saysomething store
                # and restarts Ren'Py interaction in order for 'Say' button
                # to gray out when no text is provided.
                changed picker.on_text_change
                pixel_width gui.text_width