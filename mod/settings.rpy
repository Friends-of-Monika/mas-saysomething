# settings.rpy contains settings pane (and persistent variables) for the submod.
#
# This file is part of Say Something (see link below):
# https://github.com/friends-of-monika/mas-saysomething

define persistent._fom_saysomething_show_code = False
define persistent._fom_saysomething_hide_quick_buttons = False
define persistent._fom_saysomething_speech_mode_default = False
define persistent._fom_saysomething_pose_pause = 5.0
define persistent._fom_saysomething_enable_codegen = False

screen fom_saysomething_settings:
    $ tooltip = renpy.get_screen("submods", "screens").scope["tooltip"]
    $ pose_delay = "{:.2f}".format(persistent._fom_saysomething_pose_pause)

    vbox:
        style_prefix "check"

        box_wrap False
        xfill True
        xmaximum 800

        grid 2 2:
            textbutton _("Show expression code"):
                selected persistent._fom_saysomething_show_code
                action ToggleField(persistent, "_fom_saysomething_show_code")
                hovered SetField(tooltip, "value", _("Enable display of expression code."))
                unhovered SetField(tooltip, "value", tooltip.default)

            textbutton _("Show buttons and quick menu"):
                selected not persistent._fom_saysomething_hide_quick_buttons
                action ToggleField(persistent, "_fom_saysomething_hide_quick_buttons")
                hovered SetField(tooltip, "value", _("Show quick menu and menu buttons (can be only toggled when in say/pose menu)."))
                unhovered SetField(tooltip, "value", tooltip.default)

            textbutton _("Enable speech/session mode by default"):
                selected persistent._fom_saysomething_speech_mode_default
                action ToggleField(persistent, "_fom_saysomething_speech_mode_default")
                hovered SetField(tooltip, "value", _("Always enable speech/session mode without asking."))
                unhovered SetField(tooltip, "value", tooltip.default)

            textbutton _("Enable code generation"):
                selected persistent._fom_saysomething_enable_codegen
                action ToggleField(persistent, "_fom_saysomething_enable_codegen")
                hovered SetField(tooltip, "value", _("Enable Ren'Py script file generation for said speeches."))
                unhovered SetField(tooltip, "value", tooltip.default)

        hbox:
            text _("Pose delay: [pose_delay]"):
                style "slider_label"

            bar:
                style "slider_slider"
                value FieldValue(persistent, "_fom_saysomething_pose_pause",
                                 offset=1.0, range=4.0, step=0.5, force_step=True)
                hovered SetField(tooltip, "value", _("Delay between changing poses when asking Monika to pose."))
                unhovered SetField(tooltip, "value", tooltip.default)