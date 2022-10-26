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
    while _return != "close":
        call screen fom_saysomething_picker

    show monika at t11
    return