# settings.rpy contains settings pane (and persistent variables) for the submod.
#
# This file is part of Say Something (see link below):
# https://github.com/friends-of-monika/mas-saysomething

define persistent._fom_saysomething_show_code = False
define persistent._fom_saysomething_allow_winking = False
define persistent._fom_saysomething_hide_quick_buttons = False
define persistent._fom_saysomething_seen_screenshot_hint = False
define persistent._fom_saysomething_speech_mode_default = False
define persistent._fom_saysomething_pose_pause = 5.0

screen fom_saysomething_settings:
    $ tooltip = renpy.get_screen("submods", "screens").scope["tooltip"]
    $ pose_delay = "{:.2f}".format(persistent._fom_saysomething_pose_pause)

    vbox:
        box_wrap False
        xfill True
        xmaximum 800

        style_prefix "check"

        grid 2 2:
            textbutton "Show expression code":
                selected persistent._fom_saysomething_show_code
                action ToggleField(persistent, "_fom_saysomething_show_code")
                hovered SetField(tooltip, "value", "Enable display of expression code.")
                unhovered SetField(tooltip, "value", tooltip.default)

            textbutton "Show buttons and quick menu":
                selected not persistent._fom_saysomething_hide_quick_buttons
                action ToggleField(persistent, "_fom_saysomething_hide_quick_buttons")
                hovered SetField(tooltip, "value", "Show quick menu and menu buttons (can be only toggled when in say/pose menu.)")
                unhovered SetField(tooltip, "value", tooltip.default)

            textbutton "Allow winking/blinking":
                selected persistent._fom_saysomething_allow_winking
                action [ToggleField(persistent, "_fom_saysomething_allow_winking"), Function(_fom_saysomething_allow_winking_callback)]
                hovered SetField(tooltip, "value", "Allow Monika to blink or wink when posing.")
                unhovered SetField(tooltip, "value", tooltip.default)

            textbutton "Show screenshot key hint":
                selected not persistent._fom_saysomething_seen_screenshot_hint
                action ToggleField(persistent, "_fom_saysomething_seen_screenshot_hint")
                hovered SetField(tooltip, "value", "Show a hint with screenshot key when saying or posing.")
                unhovered SetField(tooltip, "value", tooltip.default)

        textbutton "Enable speech/session mode by default":
            selected persistent._fom_saysomething_speech_mode_default
            action ToggleField(persistent, "_fom_saysomething_speech_mode_default")
            hovered SetField(tooltip, "value", "Always enable speech/session mode without asking.")
            unhovered SetField(tooltip, "value", tooltip.default)

        hbox:
            xfill True
            text "Pose delay: [pose_delay]":
                style "slider_label"

        bar:
            style "slider_slider"
            value FieldValue(persistent, "_fom_saysomething_pose_pause", offset=1.0, range=6.0, step=0.1)
            hovered SetField(tooltip, "value", "Delay between changing poses when asking Monika to pose.")
            unhovered SetField(tooltip, "value", tooltip.default)

init python:
    def _fom_saysomething_allow_winking_callback():
        from store._fom_saysomething import picker
        from store._fom_saysomething import posing
        from store._fom_saysomething import set_eyes_lock

        if picker is not None and posing:
            # Ensure that when Monika is posing allowing winking will unlock
            # eyes, and vice versa; disallowing winking will lock eyes.
            exp = picker.get_sprite_code()
            set_eyes_lock(exp, not persistent._fom_saysomething_allow_winking)