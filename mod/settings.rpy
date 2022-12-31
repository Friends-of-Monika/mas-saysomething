# settings.rpy contains settings pane (and persistent variables) for the submod.
#
# This file is part of Say Something (see link below):
# https://github.com/friends-of-monika/mas-saysomething

define persistent._fom_saysomething_show_code = False
define persistent._fom_saysomething_allow_winking = False

screen fom_saysomething_settings:
    $ tooltip = renpy.get_screen("submods", "screens").scope["tooltip"]

    vbox:
        box_wrap False
        xfill True
        xmaximum 800

    hbox:
        style_prefix "check"
        box_wrap False

        textbutton "Show expression code":
            selected persistent._fom_saysomething_show_code
            action ToggleField(persistent, "_fom_saysomething_show_code")
            hovered SetField(tooltip, "value", "Enable display of expression code.")
            unhovered SetField(tooltip, "value", tooltip.default)

        textbutton "Allow winking/blinking":
            selected persistent._fom_saysomething_allow_winking
            action [ToggleField(persistent, "_fom_saysomething_allow_winking"), Function(_fom_saysomething_allow_winking_callback)]
            hovered SetField(tooltip, "value", "Allow Monika to blink or wink when posing.")
            unhovered SetField(tooltip, "value", tooltip.default)

init python:
    def _fom_saysomething_allow_winking_callback():
        picker = _fom_saysomething.picker
        if picker is not None and picker.posing:
            # Ensure that when Monika is posing allowing winking will unlock
            # eyes, and vice versa; disallowing winking will lock eyes.
            exp = picker.get_sprite_code()
            picker.set_eyes_lock(exp, not persistent._fom_saysomething_allow_winking)