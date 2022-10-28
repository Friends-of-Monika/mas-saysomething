# topc.rpy contains event for the 'Can you say something ...?' topic that shows
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
    m 1hub "Of course!"

label fom_saysomething_event_retry:
    # Need a fallthrough here so we can jump back here on retry.
    m 1eua "Tell me how do you want me to pose and what do you want me to say~"

    # Create new Picker and store it locally.
    $ _fom_saysomething.picker = _fom_saysomething.Picker()
    $ picker = _fom_saysomething.picker

    # We'll keep looping with screen calls since we need to do Monika rendering
    # out of screen, hence why we'll keep doing it until we get 'nevermind' from
    # the player or we'll get a signal to say something.
    $ stop_picker_loop = False
    while stop_picker_loop is False:
        call screen fom_saysomething_picker

        if _return == _fom_saysomething.RETURN_CLOSE:
            # Player has changed their mind, so just stop and put Monika back.
            $ stop_picker_loop = True

            # Show buttons and quick menu if they were hidden.
            if not picker.show_buttons:
                call fom_saysomething_event_buttons(_show=True)

            show monika 1eka at t11
            m 1eka "Oh, okay."

        elif _return == _fom_saysomething.RETURN_RENDER:
            # Position or pose/expression update is requested, so do it now.
            $ renpy.show("monika " + picker.get_sprite_code(), [picker.position])

            # Hide or show buttons and quick menu.
            call fom_saysomething_event_buttons(_show=picker.show_buttons)

        elif _return == _fom_saysomething.RETURN_SAY:
            # An actual text has been typed and expression is set, stop the loop
            # and show buttons if they were hidden for preview.
            $ stop_picker_loop = True
            call fom_saysomething_event_buttons(_show=True)

            show monika 1esb at t11
            m 1esb "Alright, give me just a moment to prepare."
            m 2dsc"{w=0.3}.{w=0.3}.{w=0.3}.{w=0.5}{nw}"

            # Show or hide buttons depending on user preference.
            if not picker.show_buttons:
                call fom_saysomething_event_buttons(_show=False)

            # Show Monika with sprite code and at set position and say text.
            $ renpy.show("monika " + picker.get_sprite_code(), [picker.position])
            $ quip = picker.text
            m "[quip!q]"

            # Anyway, recover buttons after we're done showing.
            if not picker.show_buttons:
                call fom_saysomething_event_buttons(_show=True)

            show monika 3tua at t11
            m 3tua "Well? {w=0.3}Did I do it good enough?"
            m 1hub "Hope you liked it, ahaha~"

            m 3eub "Do you want me to say something else?{nw}"
            $ _history_list.pop()
            menu:
                m "Do you want me to say something else?{fast}"

                "Yes.":
                    jump fom_saysomething_event_retry

                "No.":
                    m 1hua "Okay~"

label fom_saysomething_event_buttons(_show=True):
    # Here we're recovering (since show=True when not called) buttons after
    # player chose to hide them. This is also a callable label we can reuse.
    if _show:
        $ quick_menu = True
        $ HKBShowButtons()
    else:
        $ quick_menu = False
        $ HKBHideButtons()

    # This return also returns from event.
    return