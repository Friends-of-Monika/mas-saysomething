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


    # Pose input

    # Orderect dictionary is used to preserve order when rendering a table of
    # selectors. This dictionary contains key (human readable name of expression
    # part) to list of 2-tuples of the following elements:
    #  [0]: expression code/mnemonic
    #  [1]: expression human readable description
    __POSE_MAP = OrderedDict([
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

    # This dictionary contains key to 2-tuple of:
    #  [0]: current expression cursor index
    #  [1]: current expression human readable name
    # Initially all cursors are at zero (with corresponding expression names.)
    _pose_cursors = {key: (0, __POSE_MAP[key][0][1]) for key in __POSE_MAP.keys()}

    def _switch_pose(key, forward):
        """
        Switches pose for selector by the specified key, forward or backward. If
        cursor is zero/max value and is requested to increment/decrement
        correspondingly, the value is wrapped.

        IN:
            key -> str:
                Key of selector to switch. See __POSE_MAP above.

            forward -> bool:
                True if need to increment cursor, False to decrement.
        """

        curr = _pose_cursors[key][0]
        _max = len(__POSE_MAP[key]) - 1

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

        _pose_cursors[key] = (new, __POSE_MAP[key][new][1])

    def _pose_label(key):
        """
        Returns label for the current value of the specified selector key (see
        __POSE_MAP above.)

        IN:
            key -> str:
                Selector key to return human readable name for.

        OUT:
            str:
                Human readable selector item name.
        """

        curr = _pose_cursors[key][0]
        return __POSE_MAP[key][curr][1]

    def _get_sprite_code():
        """
        Builds sprite code for the current selectors configuration.

        OUT:
            str:
                Sprite code for use in renpy.show(...)
        """

        code = list()
        for key, values in __POSE_MAP.items():
            value = values[_pose_cursors[key][0]][0]
            if value is not None:
                code.append(value)
        return "".join(code)


    # Position input

    __POSITIONS = [
        store.t41, #0
        store.t31, #1
        store.t21, #2
        store.t42, #3

        store.t11, #4
        store.t32, #5
        store.t43, #6

        store.t22, #7
        store.t33, #8

        store.t44  #9
    ]

    def _position_changed(value):
        """
        Callback function for position bar.

        If value is greater than 5 the GUI is flipped to left side.

        IN:
            value -> float:
                New value of position bar slider.
        """

        global _position
        _position = __POSITIONS[value]

        global _picker_flip
        _picker_flip = value > 5

    _position = __POSITIONS[4]
    _position_adjustment = ui.adjustment(
        range=9,
        value=4,
        adjustable=True,
        changed=_position_changed
    )

    _picker_flip = False


    # Text input

    def _text_changed(value):
        """
        Callback for text input prompt. Restarts interaction on every
        alteration.

        IN:
            value -> str:
                New input field value.
        """

        global _text
        _text = value
        renpy.restart_interaction()

    _text = ""


    # Key callback functions

    def _enter_pressed():
        # Need one more check since key press isn't covered by 'Say' button
        # sensitive expression.
        if len(_text.strip()) > 0:
            # This is equivalent to using Return(0) action.
            # https://lemmasoft.renai.us/forums/viewtopic.php?p=536626#p536626
            return _text


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

screen fom_saysomething_picker:
    style_prefix "fom_saysomething_picker"

    vbox:
        # Flip GUI to prevent hiding Monika behind it.
        if not _fom_saysomething._picker_flip:
            align (0.95, 0.3)
        else:
            align (0.05, 0.3)

        spacing 10

        vbox:
            spacing 10

            frame:
                padding (30, 30)

                # Selectors panel.

                vbox:
                    spacing 10

                    for key, value in _fom_saysomething.__POSE_MAP.items():
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

                                textbutton "<" action [Function(_fom_saysomething._switch_pose, key, forward=False), Return(0)] xalign 0.0
                                text _fom_saysomething._pose_label(key) xalign 0.5
                                textbutton ">" action [Function(_fom_saysomething._switch_pose, key, forward=True), Return(0)] xalign 1.0

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
                        adjustment _fom_saysomething._position_adjustment
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
                    action Return(_fom_saysomething._text)
                    sensitive len(_fom_saysomething._text.strip()) > 0
                textbutton "Close" action Return(False) xalign 1.0

    # Text input area styled as textbox and key capture so that Enter key press
    # is the same as pressing 'Say' button.

    key "K_RETURN" action Function(_fom_saysomething._enter_pressed) capture True

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
                changed _fom_saysomething._text_changed
                pixel_width gui.text_width