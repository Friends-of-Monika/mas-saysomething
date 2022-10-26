init 100 python in _fom_saysomething:

    import store
    from store import ui

    import math
    from collections import OrderedDict


    # Pose input

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
            ("tu", "Tearing up"),
            ("tl", "Tearing up, left"),
            ("tr", "Tearing up, right")
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
    _pose_cursors = {key: (0, __POSE_MAP[key][0][1]) for key in __POSE_MAP.keys()}

    def _switch_pose(key, forward):
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
        curr = _pose_cursors[key][0]
        return __POSE_MAP[key][curr][1]

    def _get_sprite_code():
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
        global _position
        _position = __POSITIONS[math.ceil(value * (len(__POSITIONS) - 1))]

        global _picker_flip
        _picker_flip = value > 0.5

    _position = __POSITIONS[4]
    _position_adjustment = ui.adjustment(
        range=1.0,
        value=0.4,
        adjustable=True,
        changed=_position_changed
    )

    _picker_flip = False


    # Text input

    def _text_changed(value):
        global _text
        _text = value

    _text = ""


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

screen fom_saysomething_picker:
    style_prefix "fom_saysomething_picker"

    vbox:
        if not _fom_saysomething._picker_flip:
            align (0.95, 0.3)
        else:
            align (0.05, 0.3)
        spacing 10

        vbox:
            spacing 10

            frame:
                padding (30, 30)

                vbox:
                    spacing 10

                    for key, value in _fom_saysomething.__POSE_MAP.items():
                        hbox:
                            xmaximum 350
                            xfill True

                            text key
                            textbutton "<" action [Function(_fom_saysomething._switch_pose, key, forward=False), Return(0)] xalign 0.0
                            text _fom_saysomething._pose_label(key) xalign 0.5
                            textbutton ">" action [Function(_fom_saysomething._switch_pose, key, forward=True), Return(0)] xalign 1.0

            frame:
                padding (30, 0)

                vbox:
                    spacing 10

                    hbox:
                        xmaximum 350
                        xfill True

                        text "Position"
                        bar:
                            xalign 1.0
                            yalign 0.5
                            adjustment _fom_saysomething._position_adjustment
                            released Return(0)

        frame:
            background None
            padding (30, 15)

            hbox:
                align (0.5, 0.5)

                xmaximum 250
                xfill True
                spacing 10

                style_prefix "fom_saysomething_confirm"

                textbutton "Say" action Return(_fom_saysomething._text)
                textbutton "Close" action Return(False)

    window:
        align (0.5, 0.98)

        vbox:
            align (0.5, 0.5)
            spacing 30

            text "What do you want me to say?~" style "input_prompt"
            input changed _fom_saysomething._text_changed