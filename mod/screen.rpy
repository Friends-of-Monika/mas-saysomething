init 100 python in _fom_saysomething:

    import store
    from store import ui

    import math


    __POSITIONS = [
        store.t41, #0
        store.t31, #1
        store.t21, #2
        store.t42, #4

        store.t11, #3
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
        _picker_flip = value > 0.55

        renpy.show("monika", [_position])
        renpy.call("spaceroom")

    _position = None
    _position_adjustment = ui.adjustment(
        range=1.0,
        value=0.3,
        adjustable=True,
        changed=_position_changed
    )

    _picker_flip = False


style fom_saysomething_picker_frame is gui_frame:
    background Frame(["gui/confirm_frame.png", "gui/frame.png"], gui.confirm_frame_borders, tile=gui.frame_tile)

style fom_saysomething_picker_frame_dark is gui_frame:
    background Frame(["gui/confirm_frame.png", "gui/frame_d.png"], gui.confirm_frame_borders, tile=gui.frame_tile)

style fom_saysomething_confirm_button is generic_button_light:
    xysize (115, None)
    padding (10, 5, 10, 5)

style fom_saysomething_confirm_button_dark is generic_button_dark:
    xysize (115, None)
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
            align (0.95, 0.5)
        else:
            align (0.05, 0.5)
        spacing 10

        vbox:
            frame:
                padding (30, 30)

                vbox:
                    spacing 10

                    hbox:
                        xmaximum 250
                        xfill True

                        text "Pose:"
                        textbutton "<" action NullAction() xalign 1.0
                        text "Resting on hands" xalign 1.0
                        textbutton ">" action NullAction() xalign 1.0

                    hbox:
                        xmaximum 250
                        xfill True

                        text "Eyes:"
                        textbutton "<" action NullAction() xalign 1.0
                        text "Normal" xalign 1.0
                        textbutton ">" action NullAction() xalign 1.0

        frame:
            background None
            padding (30, 15)

            hbox:
                align (0.5, 0.5)

                xmaximum 250
                xfill True
                spacing 10

                style_prefix "fom_saysomething_confirm"

                textbutton "Say" action Return("say")
                textbutton "Close" action Return("close")

    vbox:
        align(0.5, 0.95)

        frame:
            padding (30, 15)

            vbox:
                spacing 10

                hbox:
                    xmaximum 700
                    xfill True

                    text "Position:"
                    bar:
                        xalign 1.0
                        yalign 0.5
                        adjustment _fom_saysomething._position_adjustment
