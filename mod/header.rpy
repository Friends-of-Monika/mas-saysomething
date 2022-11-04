# header.rpy contains MAS submod header as well as Submod Updater header.
#
# This file is part of Say Something (see link below):
# https://github.com/friends-of-monika/mas-saysomething


init -990 python in mas_submod_utils:

    Submod(
        author="Friends of Monika",
        name="Say Something",
        description="Ask your Monika to say something and pose for you~",
        version="1.5.1",
        settings_pane="fom_saysomething_settings",
        version_updates={
            "friends_of_monika_say_something_v1_5_0": "friends_of_monika_say_something_v1_5_1"
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