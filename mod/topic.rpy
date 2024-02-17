# topic.rpy contains event for the 'Can you say something ...?' topic that shows
# expression/position picker and text input GUI.
#
# This file is part of Say Something (see link below):
# https://github.com/friends-of-monika/mas-saysomething

default persistent._fom_saysomething_seen_screenshot_hint = False
default persistent._fom_saysomething_speeches = dict()
default persistent._fom_saysomething_seen_reactions = False

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

    # Create new Picker and store it locally.
    # NOTE: Creating it here so that it's not re-initialized on each loop.
    $ _fom_saysomething.picker = _fom_saysomething.Picker()
    $ picker = _fom_saysomething.picker

label fom_saysomething_event_retry:
    # Need a fallthrough here so we can jump back here on retry.
    if say:
        m 1eua "Tell me how do you want me to pose and what do you want me to say~"
    else:
        m 1eua "Tell me how do you want me to pose~"

    # If player wants speech/session mode by default, enable it now.
    if persistent._fom_saysomething_speech_mode_default:
        $ picker.enable_session_mode()

    # 'Import' set_eyes_lock.
    $ set_eyes_lock = _fom_saysomething.set_eyes_lock

    # We'll keep looping with screen calls since we need to do Monika rendering
    # out of screen, hence why we'll keep doing it until we get 'nevermind' from
    # the player or we'll get a signal to say something.
    $ stop_picker_loop = False
    $ render_initial = True
    while stop_picker_loop is False:
        # Get expression from picker and add to removal list if necessary.
        $ exp = picker.get_sprite_code()
        if not _fom_saysomething.is_renpy_image_cached(exp):
            $ _fom_saysomething.IMAGE_CACHE.add_sprite(exp)

        # During the pose picking, Monika must not blink or transition from
        # winking to fully open eyes, so here we lock these transitions.
        $ set_eyes_lock(exp, True)

        # When first starting a picker, need to set Monika's pose and expression
        # to what's already in the picker. Do so just once.
        if render_initial:
            $ render_initial = False
            jump fom_saysomething_event_render

        # Show the GUI and await for interaction.
        call screen fom_saysomething_picker(say)

        if _return == _fom_saysomething.RETURN_CLOSE:
            # Player has changed their mind, so just stop and put Monika back.
            $ stop_picker_loop = True

            # Show buttons and quick menu if they were hidden.
            if persistent._fom_saysomething_hide_quick_buttons:
                $ _fom_saysomething.set_mas_gui_visible(True)

            # Unlock expression picker had before closing.
            $ set_eyes_lock(picker.get_sprite_code(), False)

            show monika 1eka at t11
            m 1eka "Oh, okay."

        elif _return == _fom_saysomething.RETURN_RENDER:
            # NOTE: Need a label here to quickly render initial pose, which
            # is first on the session entry list.
            label fom_saysomething_event_render:
                # Save new expression while keeping previous; immediately lock
                # blinking on it.
                $ new_exp = picker.get_sprite_code()

                # After rendering sprite, add it to cache for further removal.
                if not _fom_saysomething.is_renpy_image_cached(new_exp):
                    $ _fom_saysomething.IMAGE_CACHE.add_sprite(new_exp)

                # Unlock blinking on previous sprite.
                $ set_eyes_lock(exp, False)

                # Position or pose/expression update is requested, so do it now.
                $ renpy.show("monika " + new_exp, [picker.position], zorder=MAS_MONIKA_Z)

                # Lock blinking on new expression. NOTE: CAN ONLY BE DONE AFTER RENDERING!
                $ set_eyes_lock(new_exp, True)

                # Cleanup.
                $ del new_exp

        elif _return == _fom_saysomething.RETURN_DONE:
            # An actual text has been typed and expression is set, stop the loop
            # and show buttons if they were hidden for preview.
            $ stop_picker_loop = True
            $ _fom_saysomething.set_mas_gui_visible(True)

            # Unlock blinking on last sprite code before closing.
            $ set_eyes_lock(exp, False)

            # Pick up session items from the picker.
            # When not in session mode, session is None, so we should fall back
            # to creating an array of states with just the current state in it.
            $ picker_session = picker.session
            if picker_session is None:
                $ picker_session = [picker._save_state()]

            # Run performance, speaking or posing.
            # NOTE: Pose delay is hardcoded and is 3.0 seconds.
            # NOTE: Not cleaning up caches here, as everything we'll say there
            # is already cached right here, in the picker topic.
            call fom_saysomething_perform(picker_session, say, 3.0, cleanup_caches=False)

            # Suggested to save current speech.
            if say and picker.session is not None:
                m 3hua "By the way, I can write this speech down for later if you want, ehehe."
                m 3eub "Do you want me to do that?{nw}"

                $ _history_list.pop()
                menu:
                    m "Do you want me to do that?{fast}"

                    "Yes, please!":
                        m 1eua "Okay! How do you want me to title it?"

                        label fom_saysomething_event_save_enter_name:
                            $ suggested_name = _fom_saysomething.get_saved_speech_name_suggestion()
                            $ speech_title = mas_input(                                                                \
                                "How do you want me to title it?",                                                     \
                                length=30,                                                                             \
                                default=_fom_saysomething.get_saved_speech_name_suggestion(),                          \
                                screen_kwargs={"use_return_button": True,                                              \
                                               "return_button_value": False}                                           \
                            ).strip()

                        if speech_title is False:
                            jump fom_saysomething_event_dont_save

                        if len(speech_title) == 0:
                            m 3lksdla "You need to tell me how to title it, [mas_get_player_nickname()], ahaha~"
                            jump fom_saysomething_event_save_enter_name

                        if speech_title in persistent._fom_saysomething_speeches:
                            m 3hksdlb "Ahaha, apparently I already wrote down one with the same name..."
                            m 3eub "Should I discard the previous one?{nw}"

                            $ _history_list.pop()
                            menu:
                                m "Should I discard the previous one?{fast}"

                                "Yes.":
                                    pass

                                "No.":
                                    m 1eua "Alright, how should I title it then?"
                                    jump fom_saysomething_event_save_enter_name

                        m 1hub "Done, now I can recite it to you again if you want~"
                        $ persistent._fom_saysomething_speeches[speech_title] = picker_session

                        # For some reason mas_showEVL didn't work, so falling back to this ugliness.
                        $ mas_showEvent(mas_getEV("fom_saysomething_speeches_recite"), unlock=True)
                        $ mas_showEvent(mas_getEV("fom_saysomething_speeches_remove"), unlock=True)
                        $ mas_showEvent(mas_getEV("fom_saysomething_speeches_generate"), unlock=True)

                    "Not now, [m_name].":
                        label fom_saysomething_event_dont_save:
                            m 1hua "Oh, alright!"

                $ del picker_session

            # This is hacky, but there isn't any other way to do it with translation.
            $ quip = _("say something else") if say else _("pose for you again")
            m 3eub "Do you want me to [quip]?{nw}"

            $ _history_list.pop()
            menu:
                m "Do you want me to [quip]?{fast}"

                "Yes.":
                    jump fom_saysomething_event_retry

                "No.":
                    m 1hua "Okay~"

            # Cleanup the quip variable.
            $ del quip

    # Once done with all the speech/posing, remove the images saved in cache
    # that weren't cached before (so that we don't touch MAS sprites.)
    # Additionally, restore GUI visibility and cleanup variables.
    $ _fom_saysomething.IMAGE_CACHE.release_all()
    $ del stop_picker_loop, say, picker, render_initial
    return


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="fom_saysomething_speeches_recite",
            category=["misc", "monika"],
            prompt="Can you recite one of your speeches for me?",
            pool=True,
            unlocked=False,

            # Allow this event to be bookmarked since it isn't prefixed with
            # mas_ or monika_ and disable random unlocks.
            rules={"bookmark_rule": mas_bookmarks_derand.WHITELIST,
                   "no_unlock": None}
        ),
        code="EVE",

        # Prevent this topic from restarting with 'Now, where was I...' on crash.
        restartBlacklist=True
    )

label fom_saysomething_speeches_recite:
    m 1hub "Sure! What do you want to hear again?~"

    show monika at t21
    call screen fom_saysomething_speech_menu
    $ chosen_speech = _return
    show monika at t11

    if not chosen_speech:
        m 2eua "Oh, okay. Feel free to ask anytime though, ehehe."
        return

    $ speech = persistent._fom_saysomething_speeches[chosen_speech]
    call fom_saysomething_perform(speech)
    $ del chosen_speech, speech

    return

label fom_saysomething_perform(session, say=True, pose_delay=None, cleanup_caches=True):
    # Put Monika back in center and let her say a preamble.
    show monika 1esb at t11

    if say and persistent._fom_saysomething_enable_reactions:
        $ reaction = _fom_saysomething_reactions.get_speech_reaction(session)
    else:
        $ reaction = None

    if reaction is None:
        m 1esb "Alright, give me just a moment to prepare."
        m 2dsc"{w=0.3}.{w=0.3}.{w=0.3}.{w=0.5}{nw}"
    else:
        if not persistent._fom_saysomething_seen_reactions:
            # Let the user know what just happened
            $ renpy.notify(_("You can disable Monika's reactions in settings."))
            $ persistent._fom_saysomething_seen_reactions = True

        # Call the reaction label and set persistent var
        $ renpy.call(reaction + "_before")

    if not say:
        # 'Import' set_eyes_lock.
        $ set_eyes_lock = _fom_saysomething.set_eyes_lock

        # When not in speech mode and only posing, no need to keep window open.
        window hide

    # Show or hide buttons depending on user preference.
    if persistent._fom_saysomething_hide_quick_buttons:
        $ _fom_saysomething.set_mas_gui_visible(False)

    # Show screenshot hint.
    if not persistent._fom_saysomething_seen_screenshot_hint:
        $ scr_key = _fom_saysomething.get_friendly_key("screenshot")
        if scr_key is not None:
            $ persistent._fom_saysomething_seen_screenshot_hint = True
            $ renpy.notify(_("You can take a screenshot by pressing {0}.").format(scr_key))

        # Cleanup.
        $ del scr_key

    # Memorize 5-poses for transitions.
    $ pose_5 = False

    # Ren'Py has no 'for' statement, so use 'while'.
    $ state_i = 0
    while state_i < len(session):
        $ poses, pos, text = session[state_i]
        $ state_i += 1

        # Get current expression after it was changed. Also add it to cache so
        # it can be released later, as player-made expressions may be unused in
        # the rest of MAS at all.
        $ exp = _fom_saysomething.get_sprite_code(poses)
        if cleanup_caches and not _fom_saysomething.is_renpy_image_cached(exp):
            $ _fom_saysomething.IMAGE_CACHE.add_sprite(exp)

        # Show Monika with sprite code and at set position, optionally lock
        # eyes blinking and say text. For entering and exiting 5-pose
        # apply transition.
        $ renpy.show("monika " + exp, [_fom_saysomething.POSITIONS[pos][0]], zorder=MAS_MONIKA_Z)
        if (not exp.startswith("5") and pose_5) or (exp.startswith("5") and not pose_5):
            $ renpy.with_statement(dissolve_monika)
            $ pose_5 = not pose_5
        elif not say:
            # NOTE: When posing, this is always applied
            $ renpy.with_statement(dissolve_monika)

        if say:
            # Render text and ask Monika to say it.
            $ quip = _fom_saysomething_markdown.render(text)
            m "[quip]"
            $ del quip

        else:
            # User most likely wants Monika to hold still while posing and
            # not to blink or wink.
            $ set_eyes_lock(exp, True)

            # Pause before continuing to another expression.
            # NOTE: Using custom screen here so we can more flexibly pause,
            # especially when hiding window; this lets us make a soft pause
            # with set timer and still allowing player to click skip it.
            call screen fom_skippable_pause(pose_delay)

            # Unlock blinking.
            $ set_eyes_lock(exp, False)

    # Release sprites generated dynamically.
    if cleanup_caches:
        $ _fom_saysomething.IMAGE_CACHE.release_all()

    # When in posing mode, restore dialogue window.
    if not say:
        window show

    # Anyway, recover buttons after we're done showing.
    $ _fom_saysomething.set_mas_gui_visible(True)

    # Return Monika back to center, say post-speech phrase.
    if say and exp.startswith("5"):
        # If finished with leaning pose, apply dissolve
        show monika 3tua at t11 with dissolve_monika
    else:
        # In all the other cases just immediately change expression
        show monika 3tua at t11

    if not say or reaction is None:
        m 3tua "Well? {w=0.3}Did I do it good enough?"
        m 1hub "Hope you liked it, ahaha~"
    else:
        $ renpy.call(reaction + "_after")

    if not say:
        $ del set_eyes_lock

    # Before finishing with performance, restore GUI visibility and cleanup.
    $ _fom_saysomething.set_mas_gui_visible(True)
    $ del state_i, pose_5, exp, poses, pos, text
    return


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="fom_saysomething_speeches_remove",
            category=["misc", "monika"],
            prompt="Can you discard one of your speeches?",
            pool=True,
            unlocked=False,

            # Allow this event to be bookmarked since it isn't prefixed with
            # mas_ or monika_ and disable random unlocks.
            rules={"bookmark_rule": mas_bookmarks_derand.WHITELIST,
                   "no_unlock": None}
        ),
        code="EVE",

        # Prevent this topic from restarting with 'Now, where was I...' on crash.
        restartBlacklist=True
    )

label fom_saysomething_speeches_remove:
    m "Oh, alright...{w=0.3} Which one is it?"

    show monika at t21
    call screen fom_saysomething_speech_menu
    $ chosen_speech = _return
    show monika at t11

    if not chosen_speech:
        m 2eua "Okay, feel free to ask anytime though."
        return

    $ del persistent._fom_saysomething_speeches[chosen_speech]
    m "Okay, I erased it~"

    # When no speeches left, lock these topics so they don't show up.
    if len(persistent._fom_saysomething_speeches) == 0:
        $ mas_hideEvent(mas_getEV("fom_saysomething_speeches_recite"), lock=True)
        $ mas_hideEvent(mas_getEV("fom_saysomething_speeches_remove"), lock=True)
        $ mas_hideEvent(mas_getEV("fom_saysomething_speeches_generate"), lock=True)

    $ del chosen_speech
    return


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="fom_saysomething_speeches_generate",
            category=["misc", "monika"],
            prompt="Can you write a script for one of the speeches?",
            pool=True,
            unlocked=False,

            # Allow this event to be bookmarked since it isn't prefixed with
            # mas_ or monika_ and disable random unlocks.
            rules={"bookmark_rule": mas_bookmarks_derand.WHITELIST,
                   "no_unlock": None}
        ),
        code="EVE",

        # Prevent this topic from restarting with 'Now, where was I...' on crash.
        restartBlacklist=True
    )

label fom_saysomething_speeches_generate:
    m 3eub "Sure! Which of the speeches you want me to write a script for?"

    show monika at t21
    call screen fom_saysomething_speech_menu
    $ chosen_speech = _return
    show monika at t11

    if not chosen_speech:
        m 3eka "Oh, alright! Feel free to ask me anythime though~"
        return

    m 2hub "Alright, let's do it! Give me a moment now..."
    m 2dsc "{w=0.3}.{w=0.3}.{w=0.3}.{w=0.5}{nw}"

    # Script name chosen, overwriting allowed if conflicted, write now.
    $ session = persistent._fom_saysomething_speeches[chosen_speech]
    $ _fom_saysomething.generate_script(session, chosen_speech)

    m 3hub "Done! Thank you for helping me become even closer to your reality, [mas_get_player_nickname()]~"

    if mas_globals.this_ev.shown_count == 0:
        $ speeches_dir = _fom_saysomething.SPEECHES_DIR_NAME
        m 3wud "Oh! {w=0.3}I almost forgot!"
        m 2eub "All the scripts I'm writing for you I'll put into '[speeches_dir]' in your game directory."
        m 1hua "Don't forget to check it out now~"
        $ del speeches_dir

    # Cleanup.
    $ del session, chosen_speech
    return


# Reactions API. This allows us to inspect the content of say session and
# depending on what was said (or other conditions, up to implementation)
# to modify the parts she says before and after the speech.
# See implementation example in the next 'init ... python' section below.

init 10 python in _fom_saysomething_reactions:
    REACTION_HANDLERS = list()

    def register_handler(label, priority=0):
        def decorator(func):
            REACTION_HANDLERS.append((label, func, priority))
            def wrapper(session):
                return func(session)

            return wrapper
        return decorator

    def get_speech_reaction(session):
        matches = list()

        for label, match, priority in REACTION_HANDLERS:
            before, after = label + "_before", label + "_after"
            if not (renpy.has_label(before) and renpy.has_label(after)):
                continue

            if match(session):
                matches.append((label, priority))

        if not matches:
            return None

        matches.sort(key=lambda it: it[1], reverse=True)
        return matches[0][0]

# Example implementation of a reaction to a single line "foobar"
# you ask her to say.
# Register the handler with @register_handler, which takes label name
# as a parameter. Note that you have to create *two* labels, <name>_before and
# <name>_after, otherwise the reaction handler will not be eligible.

init 10 python in _fom_saysomething_reactions:
    @register_handler("fom_saysomething_reaction_foobar")
    def handle_reaction_foobar(session):
        # We only need to make it one line
        if len(session) > 1:
            return False

        # Normalize the line
        line = session[0][2].lower().strip()
        return line == "foobar" or line == "foo bar"

# This label will be called before the speech and
# INSTEAD of the default "let me prepare".
label fom_saysomething_reaction_foobar_before:
    m 1tuu "Testing something, aren't you, [player]?"
    m 3hubsa "You know I'm very happy to assist~"
    m 2dua "{w=0.3}.{w=0.3}.{w=0.3}.{w=0.5}{nw}"
    return

# This label will be called after the speech and
# INSTEAD of the default "did I say it well?"
label fom_saysomething_reaction_foobar_after:
    m 1tua "Well, was it good enough?{w=0.3} Ahaha~"
    return


init 10 python in _fom_saysomething_reactions:
    from store import MASMailbox
    import re

    class FOM_CursesMailbox(MASMailbox):
        WORD_STATS = "__fom_wordstats"

    curses_mailbox = FOM_CursesMailbox()
    curses_thres = 0.2
    curses_severe_mul = 5

    @register_handler("fom_saysomething_reaction_curses", priority=10)
    def handle_reaction_curses(session):
        # Normalize the lines, lowercase, strip etc and turn to words
        words = [
            word.replace(".!?'\"", "")
            for words in map(lambda it: it[2].lower().strip().split(" "), session)
            for word in words
        ]

        # VERY simplified regexp list for sake of simply detecting very
        # few impolite statements; we don't need any false positives.
        bad_re = re.compile("|".join([
            r"\bboob\b",
            r"\bcoom\b",
            r"\bcum\b",
            r"\bcunt\b",
            r"fuck",
            r"jizz",
            r"slut",
            r"\bthot\b",
            r"whore"
        ]), re.I)

        # Additional list for severe profanity that would cost 5x more
        # words and would be most likely to hit the higher limit.
        severe_re = re.compile("|".join([
            r"\bfaggot\b",
            r"\bnigg(a|er)\b",
            r"retard\b"
        ]), re.I)

        # Count found bad words from the above wordlist
        hits = list(map(lambda it: bool(bad_re.search(it)), words)).count(True)
        hits += curses_severe_mul * list(map(lambda it: bool(severe_re.search(it)), words)).count(True)
        ratio = hits / len(words)

        if ratio >= curses_thres:
            curses_mailbox.send(FOM_CursesMailbox.WORD_STATS, (hits, len(words), ratio))
            return True

        return False

label fom_saysomething_reaction_curses_before:
    $ hits, words, ratio = _fom_saysomething_reactions.curses_mailbox          \
        .read(_fom_saysomething_reactions.FOM_CursesMailbox.WORD_STATS)

    if ratio <= 0.33: # 20% to 33% of words are curses
        m 1rksdlb "Ahaha, I wouldn't really...{w=0.3} say some of these words..."
        m 1hksdla "But...{w=0.3} just give me a moment..."
        m 2dsc "{w=0.3}.{w=0.3}.{w=0.3}.{w=0.5}{nw}"
    elif ratio <= 0.5: # 33% to 50% of words are curses
        m 2dsc "[player]...{w=0.3} that really isn't polite."
        m 2etd "Do you really want me to say...{w=0.3} that?"
        m 1dfc "{w=0.3}.{w=0.3}.{w=0.3}.{w=0.5}alright."
    else: # 50% and more (more than half)
        m 2tsx "[player]!{w=0.3} That's disgusting!"
        m 1dfc "I would never, {i}ever{/i} say that to anyone."
        m 2efd "Why would you want me to do that?!"
        m 1dud "...fine.{w=0.5} Fine.{w=0.5} I guess I just have to."
        m 2dfc "{w=0.3}.{w=0.3}.{w=0.3}.{w=0.5}{nw}"

    $ del hits, words, ratio
    return

label fom_saysomething_reaction_curses_after:
    $ hits, words, ratio = _fom_saysomething_reactions.curses_mailbox          \
        .read(_fom_saysomething_reactions.FOM_CursesMailbox.WORD_STATS)
    if ratio <= 0.5:
        m 2dfc "..."
        m 2efc "Are you happy now?"
    else:
        m 2tsc "...Happy now?{w=0.5}{nw} "
        extend 2dfc "Sheesh."

    $ del hits, words, ratio
    return


init 10 python in _fom_saysomething_reactions:
    @register_handler("fom_saysomething_reaction_imposter")
    def handle_reaction_imposter(session):
        # We only need to make it one line
        if len(session) > 1:
            return False

        # Normalize the line
        line = session[0][2].lower().strip()

        # Check for variations
        return (
            line == "'when the imposter is sus'" or
            line == "'when imposter is sus'" or
            line == "'when the impostor is sus'" or
            line == "'when impostor is sus'" or
            line == "when imposter is sus" or
            line == "when impostor is sus"
        )

label fom_saysomething_reaction_imposter_before:
    # "may the lord forgive me" - dreamscached
    m 2dfc "Fine...{w=0.3} Fine, [player], I'll say that."
    m 2dsd "Here goes nothing."
    m 2dfc "{w=0.3}.{w=0.3}.{w=0.3}.{w=0.5}{nw}"
    return

# This label will be called after the speech and
# INSTEAD of the default "did I say it well?"
label fom_saysomething_reaction_imposter_after:
    m 2mkp "...I hope you're happy now. Geez."
    return


init 10 python in _fom_saysomething_reactions:
    import store

    @register_handler("fom_saysomething_reaction_randexp", priority=-1)
    def handle_reaction_randexp(session):
        # Only react when a random expression was used
        # Priority is -1 so any other reaction goes ahead
        if hasattr(store, "picker") and store.picker is not None:
            return store.picker.random_exp_used
        return False

label fom_saysomething_reaction_randexp_before:
    m 2hkbssdlb "Wow, [player], you really made me make quite a face...{w=0.3} Ahaha!"
    m 5dkbsu "But you know I'll never get tired of posing for you~"
    m 1eub "Now, let me prepare..."
    m 2dua "{w=0.3}.{w=0.3}.{w=0.3}.{w=0.5}{nw}"
    return

label fom_saysomething_reaction_randexp_after:
    m 1hub "Hope you liked it, ahaha~"
    return