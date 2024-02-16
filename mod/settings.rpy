# settings.rpy contains settings pane (and persistent variables) for the submod.
#
# This file is part of Say Something (see link below):
# https://github.com/friends-of-monika/mas-saysomething

define persistent._fom_saysomething_show_code = False
define persistent._fom_saysomething_hide_quick_buttons = False
define persistent._fom_saysomething_speech_mode_default = False
define persistent._fom_saysomething_enable_reactions = True

screen fom_saysomething_settings:
    $ tooltip = renpy.get_screen("submods", "screens").scope["tooltip"]

    vbox:
        style_prefix "check"

        box_wrap False
        xfill True
        xmaximum 800

        hbox:
            textbutton _("Show expression code"):
                selected persistent._fom_saysomething_show_code
                action ToggleField(persistent, "_fom_saysomething_show_code")
                hovered SetField(tooltip, "value", _("Enable display of expression code."))
                unhovered SetField(tooltip, "value", tooltip.default)

            textbutton _("Enable speech/session mode by default"):
                selected persistent._fom_saysomething_speech_mode_default
                action ToggleField(persistent, "_fom_saysomething_speech_mode_default")
                hovered SetField(tooltip, "value", _("Always enable speech/session mode without asking."))
                unhovered SetField(tooltip, "value", tooltip.default)

        if persistent._fom_saysomething_seen_reactions:
            hbox:
                textbutton _("Enable Monika's reactions"):
                    selected persistent._fom_saysomething_enable_reactions
                    action ToggleField(persistent, "_fom_saysomething_enable_reactions")
                    hovered SetField(tooltip, "value", _("Allow Monika to react to things you ask her to say."))
                    unhovered SetField(tooltip, "value", tooltip.default)