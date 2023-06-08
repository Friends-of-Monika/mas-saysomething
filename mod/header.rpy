# header.rpy contains MAS submod header as well as Submod Updater header.
# It also contains logic for libraries injection.
#
# This file is part of Say Something (see link below):
# https://github.com/friends-of-monika/mas-saysomething


init -990 python in mas_submod_utils:

    Submod(
        author="Friends of Monika",
        name="Say Something",
        description=_("Ask your Monika to say something and pose for you~"),
        version="1.7.0",
        settings_pane="fom_saysomething_settings",
        version_updates={
            "friends_of_monika_say_something_v1_5_0": "friends_of_monika_say_something_v1_5_1",
            "friends_of_monika_say_something_v1_6_0": "friends_of_monika_say_something_v1_7_0"
        }
    )


init -989 python:

    if store.mas_submod_utils.isSubmodInstalled("Submod Updater Plugin"):
        store.sup_utils.SubmodUpdater(
            submod="Say Something",
            user_name="friends-of-monika",
            repository_name="mas-saysomething",
            extraction_depth=3
        )


## Setting up lib/ directory for custom libraries location

init -199 python in _fom_saysomething:

    import store, os
    from store import _fom_saysomething
    basedir = os.path.join(renpy.config.basedir, *_fom_saysomething.get_script_file(
        fallback="game/Submods/Say Something/header.rpy").split("/")[:-1])

init -99 python in _fom_saysomething_lib:

    import store, os, sys
    from store import _fom_saysomething

    if sys.version_info.major == 2:
        sys.path.append(os.path.join(_fom_saysomething.basedir, "lib", "py2"))