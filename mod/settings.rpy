define persistent._fom_saysomething_show_code = False

screen fom_saysomething_settings:
    $ tooltip = renpy.get_screen("submods", "screens").scope["tooltip"]

    if config.developer:
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