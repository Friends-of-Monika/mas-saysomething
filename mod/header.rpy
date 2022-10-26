# header.rpy contains MAS submod header as well as Submod Updater header.
#
# This file is part of Say Something (see link below):
# https://github.com/friends-of-monika/mas-saysomething


init -990 python in mas_submod_utils:

    Submod(
        author="Friends of Monika",
        name="Say Something",
        description="Ask your Monika to say something and pose for you~",
        version="0.0.0"
    )


init -989 python:

    if store.mas_submod_utils.isSubmodInstalled("Submod Updater Plugin"):
        store.sup_utils.SubmodUpdater(
            submod="Say Something",
            user_name="friends-of-monika",
            repository_name="mas-saysomething",
            extraction_depth=3
        )