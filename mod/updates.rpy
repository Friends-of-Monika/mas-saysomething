label friends_of_monika_say_something_v1_5_0(version="v1_5_0"):
    return

label friends_of_monika_say_something_v1_5_1(version="v1_5_1"):
    python:
        for name in list(persistent._fom_saysomething_presets.keys()):
            sel, pos, text, buttons = persistent._fom_saysomething_presets[name]
            for sel_key in list(sel.keys()):
                sel[sel_key.lower()] = sel.pop(sel_key)
            persistent._fom_saysomething_presets[name] = (sel, pos, text, buttons)
    return