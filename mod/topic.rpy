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
    m 1eub "Of course!"

    show monika 1eua at t11
    $ HKBHideButtons()
    $ mas_RaiseShield_core()

    $ stop_picker_loop = False
    while stop_picker_loop is False:
        call screen fom_saysomething_picker
        if _return is False:
            $ stop_picker_loop = True
        elif _return is 0:
            $ renpy.show("monika "  + _fom_saysomething._get_sprite_code(), [_fom_saysomething._position])
        else:
            $ renpy.show("monika "  + _fom_saysomething._get_sprite_code(), [_fom_saysomething._position])
            $ renpy.say(m, _fom_saysomething._text)
            $ stop_picker_loop = True

    show monika at t11
    $ mas_DropShield_core()
    $ HKBShowButtons()
    return