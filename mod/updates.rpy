# updates.rpy contains labels for version update data migration logic.
#
# This file is part of Say Something (see link below):
# https://github.com/friends-of-monika/mas-saysomething


## From v1.4.0 to v1.5.0 (empty update, first label)
label friends_of_monika_say_something_v1_5_0(version="v1_5_0"):
    return


## From v1.5.0 to v1.5.1 (change of presets structure)
label friends_of_monika_say_something_v1_5_1(version="v1_5_1"):
    python:
        for name in list(persistent._fom_saysomething_presets.keys()):
            sel, pos, text, buttons = persistent._fom_saysomething_presets[name]
            for sel_key in list(sel.keys()):
                sel[sel_key.lower()] = sel.pop(sel_key)
            persistent._fom_saysomething_presets[name] = (sel, pos, text, buttons)
    return


## From v1.6.0 to v1.7.0 (change of presets structure)
label friends_of_monika_say_something_v1_7_0(version="v1_7_0"):
    python:
        for name in list(persistent._fom_saysomething_presets.keys()):
            persistent._fom_saysomething_presets[name] = persistent._fom_saysomething_presets[name][:-1]
    return


## From v1.7.0 to v1.8.0 (removal of some config options)
label friends_of_monika_say_something_v1_8_0(version="v1_8_0"):
    $ persistent.__dict__.pop("_fom_saysomething_allow_winking", None)
    $ persistent.__dict__.pop("_fom_saysomething_pose_pause", None)
    return