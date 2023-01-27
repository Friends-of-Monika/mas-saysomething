# topic.rpy contains event for the 'Can you say something ...?' topic that shows
# expression/position picker and text input GUI.
#
# This file is part of Say Something (see link below):
# https://github.com/friends-of-monika/mas-saysomething


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="fom_saysomething_event",
            category=["misc", "monika"],
            prompt="Can you say something for me?",
            pool=True,
            unlocked=True,

            # Allow this event to be bookmarked since it isn't prefixed with
            # mas_ or monika_.
            rules={"bookmark_rule": mas_bookmarks_derand.WHITELIST}
        ),
        code="EVE",

        # Prevent this topic from restarting with 'Now, where was I...' on crash.
        restartBlacklist=True
    )

label fom_saysomething_event:
    call fom_saysomething_event_entry(say=True)
    return _return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="fom_saysomething_event_pose",
            category=["misc", "monika"],
            prompt="Can you pose for me?",
            pool=True,
            unlocked=True,

            # Allow this event to be bookmarked since it isn't prefixed with
            # mas_ or monika_.
            rules={"bookmark_rule": mas_bookmarks_derand.WHITELIST}
        ),
        code="EVE",

        # Prevent this topic from restarting with 'Now, where was I...' on crash.
        restartBlacklist=True
    )

label fom_saysomething_event_pose:
    call fom_saysomething_event_entry(say=False)
    return _return

label fom_saysomething_event_entry(say=True):
    m 1hub "Of course!"

label fom_saysomething_event_retry:
    # Need a fallthrough here so we can jump back here on retry.
    if say:
        m 1eua "Tell me how do you want me to pose and what do you want me to say~"
    else:
        m 1eua "Tell me how do you want me to pose~"

    # Create new Picker and store it locally.
    $ _fom_saysomething.picker = _fom_saysomething.Picker()
    $ picker = _fom_saysomething.picker

    # 'Import' set_eyes_lock.
    $ set_eyes_lock = _fom_saysomething.set_eyes_lock

    # We'll keep looping with screen calls since we need to do Monika rendering
    # out of screen, hence why we'll keep doing it until we get 'nevermind' from
    # the player or we'll get a signal to say something.
    $ stop_picker_loop = False
    while stop_picker_loop is False:
        # During the pose picking, Monika must not blink or transition from
        # winking to fully open eyes, so here we lock these transitions.
        if not persistent._fom_saysomething_allow_winking:
            $ exp = picker.get_sprite_code()
            $ set_eyes_lock(exp, True)

        # Show the GUI and await for interaction.
        $ _fom_saysomething.posing = True
        call screen fom_saysomething_picker(say)
        $ _fom_saysomething.posing = False

        if _return == _fom_saysomething.RETURN_CLOSE:
            # Player has changed their mind, so just stop and put Monika back.
            $ stop_picker_loop = True

            # Show buttons and quick menu if they were hidden.
            if not picker.show_buttons:
                call fom_saysomething_event_buttons(_show=True)

            if not persistent._fom_saysomething_allow_winking:
                # Here it's safe to just take a sprite code as it's already
                # rendered and respective image is loaded into memory.
                $ set_eyes_lock(picker.get_sprite_code(), False)

            show monika 1eka at t11
            m 1eka "Oh, okay."

        elif _return == _fom_saysomething.RETURN_RENDER:
            $ new_exp = picker.get_sprite_code()

            # Position or pose/expression update is requested, so do it now.
            $ renpy.show("monika " + new_exp, [picker.position])

            # Lock winking/blinking on the new image.
            if not persistent._fom_saysomething_allow_winking:
                $ set_eyes_lock(new_exp, True)

            if not persistent._fom_saysomething_allow_winking and "exp" in globals():
                # Once out of GUI, unlock the winking/blinking on the previous
                # sprite, but ONLY if it was previously locked (exp variable is
                # declared) as it could be locked from menu by unselecting
                # 'allow winking' option.
                $ set_eyes_lock(exp, False)

            # Hide or show buttons and quick menu.
            call fom_saysomething_event_buttons(_show=picker.show_buttons)

        elif _return == _fom_saysomething.RETURN_DONE:
            # An actual text has been typed and expression is set, stop the loop
            # and show buttons if they were hidden for preview.
            $ stop_picker_loop = True
            call fom_saysomething_event_buttons(_show=True)

            if not persistent._fom_saysomething_allow_winking:
                # Here it's safe to just take a sprite code as it's already
                # rendered and respective image is loaded into memory.
                $ set_eyes_lock(picker.get_sprite_code(), False)

            show monika 1esb at t11
            m 1esb "Alright, give me just a moment to prepare."
            m 2dsc"{w=0.3}.{w=0.3}.{w=0.3}.{w=0.5}{nw}"

            # Show or hide buttons depending on user preference.
            if not picker.show_buttons:
                call fom_saysomething_event_buttons(_show=False)

            # Lock winking/blinking for the current sprite code.
            if not persistent._fom_saysomething_allow_winking:
                $ exp = picker.get_sprite_code()
                $ set_eyes_lock(exp, True)

            # Set flag as posing.
            $ _fom_saysomething.posing = True

            # Show screenshot hint.
            if not persistent._fom_saysomething_seen_screenshot_hint:
                $ scr_key = _fom_saysomething.get_screenshot_key()
                if scr_key is not None:
                    $ persistent._fom_saysomething_seen_screenshot_hint = True
                    $ renpy.notify("You can take a screenshot by pressing " + scr_key + ".")
                $ del scr_key

            # Show Monika with sprite code and at set position, optionally lock
            # eyes blinking and say text.
            $ renpy.show("monika " + exp, [picker.position])
            if not persistent._fom_saysomething_allow_winking:
                $ set_eyes_lock(exp, True)
            if say:
                $ quip = picker.text
                m "[quip!q]"
            else:
                window hide
                pause 5.0
                window show

            # No longer posing.
            $ _fom_saysomething.posing = False

            # Unlock winking/blinking.
            if not picker.show_buttons:
                $ set_eyes_lock(exp, False)

            # Anyway, recover buttons after we're done showing.
            if not picker.show_buttons:
                call fom_saysomething_event_buttons(_show=True)

            show monika 3tua at t11
            m 3tua "Well? {w=0.3}Did I do it good enough?"
            m 1hub "Hope you liked it, ahaha~"

            if say:
                $ quip = "say something else"
            else:
                $ quip = "pose for you again"

            m 3eub "Do you want me to [quip]?{nw}"
            $ _history_list.pop()
            menu:
                m "Do you want me to [quip]?{fast}"

                "Yes.":
                    jump fom_saysomething_event_retry

                "No.":
                    m 1hua "Okay~"

    call fom_saysomething_event_buttons(_show=True)
    return

label fom_saysomething_event_buttons(_show=True):
    # Here we're recovering (since show=True when not called) buttons after
    # player chose to hide them.
    $ quick_menu = _show
    if _show:
        $ HKBShowButtons()
    else:
        $ HKBHideButtons()
    return