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
            unlocked=True
        ),
        code="EVE"
    )

label fom_saysomething_event:
    m 1hub "Of course!"
    m 1eua "Tell me how do you want me to pose and what do you want me to say~"

    # Disable game menu and hide textbox buttons.
    $ HKBHideButtons()
    $ mas_RaiseShield_core()

    # Create new Picker and store it locally.
    $ _fom_saysomething.picker = _fom_saysomething.Picker()
    $ picker = _fom_saysomething.picker

    # We'll keep looping with screen calls since we need to do Monika rendering
    # out of screen, hence why we'll keep doing it until we get 'nevermind' from
    # the player or we'll get a signal to say something.
    $ stop_picker_loop = False
    while stop_picker_loop is False:
        call screen fom_saysomething_picker

        if _return is False:
            # Player has changed their mind, so just stop and put Monika back.
            $ stop_picker_loop = True

            show monika 1eka at t11
            m 1eka "Oh, okay."

        elif _return is 0:
            # Position or pose/expression update is requested, so do it now.
            $ renpy.show("monika " + picker.get_sprite_code(), [picker.position])

        else:
            # An actual text has been typed and expression is set, ready to go.
            $ stop_picker_loop = True

            show monika 1esb at t11
            m 1esb "Alright, give me just a moment to prepare."
            m 2dsc"{w=0.3}.{w=0.3}.{w=0.3}.{w=0.5}{nw}"

            # Show Monika with sprite code and at set position and say text.
            $ renpy.show("monika " + picker.get_sprite_code(), [picker.position])
            $ renpy.say(m, picker.text)

            # Enable textbox buttons and put Monika back on the middle.
            $ mas_DropShield_core()

            show monika 3tua at t11
            m 3tua "Well? {w=0.3}Did I do it good enough?"
            m 1hub "Hope you liked it, ahaha~"

    # Enable textbox buttons (again) and show left-bottom buttons.
    $ mas_DropShield_core()
    $ HKBShowButtons()

    return