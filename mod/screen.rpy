# screen.rpy contains custom text GUI that shows up when Monika is asked to
# say something.
#
# This file is part of Say Something (see link below):
# https://github.com/friends-of-monika/mas-saysomething

define persistent._fom_saysomething_presets = dict()


init 100 python in _fom_saysomething:

    import store
    from store import ui, persistent
    from store import FieldInputValue

    import math
    from collections import OrderedDict


    # Value to return from picker screen to indicate that it has to be called
    # again after pose/position/UI change.
    RETURN_RENDER = -1

    # Value to return from picker screen to indicate that player wants to close
    # it without asking Monika to say anything.
    RETURN_CLOSE = -2

    # Value to return from picker screen to indicate player is done with picking
    # and typing and it is time to let Monika say and pose.
    RETURN_DONE = 1


    # Orderect dictionary is used to preserve order when rendering a table of
    # selectors. This dictionary contains key (human readable name of expression
    # part) to list of 2-tuples of the following elements:
    #  [0]: expression code/mnemonic
    #  [1]: expression human readable description
    EXPR_MAP = OrderedDict([
        ("Pose", [
            ("1", "Rest on hands"),
            ("2", "Cross"),
            ("3", "Point right, rest"),
            ("4", "Point right"),
            ("5", "Lean"),
            ("6", "Down"),
            ("7", "Point right, down")
        ]),
        ("Eyes", [
            ("e", "Normal"),
            ("w", "Wide"),
            ("s", "Sparkle"),
            ("t", "Smug"),
            ("c", "Crazy"),
            ("r", "Look right"),
            ("l", "Look left"),
            ("h", "Closed, happy"),
            ("d", "Closed, sad"),
            ("k", "Wink left"),
            ("n", "Wink right"),
            ("f", "Soft"),
            ("m", "Smug, left"),
            ("g", "Smug, right")
        ]),
        ("Eyebrows", [
            ("u", "Up"),
            ("f", "Furrowed"),
            ("k", "Knit"),
            ("s", "Straight"),
            ("t", "Thinking")
        ]),
        ("Blush", [
            (None, "None"),
            ("bl", "Line"),
            ("bs", "Shade"),
            ("bf", "Full")
        ]),
        ("Tears", [
            (None, "None"),
            ("ts", "Streaming"),
            ("td", "Dried"),
            ("tp", "Pooled"),
            ("tu", "Tearing up")
        ]),
        ("Sweat", [
            (None, "None"),
            ("sdl", "Left cheek"),
            ("sdr", "Right cheek"),
        ]),
        ("Mouth", [
            ("a", "Smile, closed"),
            ("b", "Smile, open"),
            ("c", "Straight"),
            ("d", "Open"),
            ("o", "Gasp"),
            ("u", "Smug"),
            ("w", "Wide"),
            ("x", "Grit teeth"),
            ("p", "Pout"),
            ("t", "Triangle")
        ])
    ])


    # Positions list containing Monika table positions from leftmost [0] to
    # rightmost [9]. Items are usable with renpy.show(..., at=list[...]) call.
    POSITIONS = [
        (store.t41, "t41"), #0
        (store.t31, "t31"), #1
        (store.t21, "t21"), #2, usually used in talk menu and scrollable choices
        (store.t42, "t42"), #3

        (store.t11, "t11"), #4, default middle screen position
#       (store.t32, "t32"), # formerly #5, same as #4 so no need to keep it here
        (store.t43, "t43"), #5

        (store.t22, "t22"), #6
        (store.t33, "t33"), #7

        (store.t44, "t44")  #8
    ]


    class Picker(object):
        """
        Picker represents pose, position and GUI configuration screen with data
        stored in this object.
        """

        def __init__(self):
            """
            Creates a new Picker instance.
            """

            # This dictionary contains key to 2-tuple of:
            #  [0]: current expression cursor index
            #  [1]: current expression human readable name
            # Initially all cursors are at zero (with corresponding expression names.)
            self.pose_cursors = {key: (0, EXPR_MAP[key][0][1]) for key in EXPR_MAP.keys()}

            # Position object to use when showing Monika at her table. By
            # default, her usual middle screen position.
            self.position = POSITIONS[4][0]

            # Adjustment object to define slider properties for position slider
            # and handle value changes.
            self.position_adjustment = ui.adjustment(
                range=len(POSITIONS) - 1,
                value=4,
                adjustable=True,
                changed=self.on_position_change
            )

            # Flag value for flipping selectors/position GUI to left side of
            # screen if it would mean Monika is behind the GUI and not in user's
            # sight.
            self.gui_flip = False

            # Flag value for showing or hiding buttons and quick menu.
            self.show_buttons = True

            # Variable that stores entered user text prompt.
            self.text = ""

            # Ren'Py input value to allow disabling text input when needed.
            self.text_value = FieldInputValue(self, "text", returnable=False)

            # Flag value for showing presets menu instead of selectors panel.
            self.presets_menu = False

            # Variable that stores entered preset search text prompt.
            self.presets_search = ""

            # Ren'Py input value to allow enabling search input when needed.
            self.presets_search_value = FieldInputValue(self, "presets_search", returnable=False)

            # Variable that stores entered preset name in modal.
            self.preset_name = ""

            # Ren'Py input value to handle text entering in modal (doesn't
            # work if it's used in screen.)
            self.preset_name_value = FieldInputValue(self, "preset_name")

            # Preset cursor keeps track of current preset chosen.
            self.preset_cursor = None

        def pose_switch_selector(self, key, forward):
            """
            Switches pose for selector by the specified key, forward or backward. If
            cursor is zero/max value and is requested to increment/decrement
            correspondingly, the value is wrapped.

            IN:
                key -> str:
                    Key of selector to switch. See __EXPR_MAP above.

                forward -> bool:
                    True if need to increment cursor, False to decrement.

            OUT:
                RETURN_RENDER:
                    Always returns RETURN_RENDER constant value.
            """

            curr = self.pose_cursors[key][0]
            _max = len(EXPR_MAP[key]) - 1

            if forward:
                if curr == _max:
                    new = 0
                else:
                    new = curr + 1
            else:
                if curr == 0:
                    new = _max
                else:
                    new = curr - 1

            self.pose_cursors[key] = (new, EXPR_MAP[key][new][1])

            # This is equivalent to using Return(RETURN_RENDER) action.
            # https://lemmasoft.renai.us/forums/viewtopic.php?p=536626#p536626
            return RETURN_RENDER

        def get_pose_label(self, key):
            """
            Returns label for the current value of the specified selector key (see
            __EXPR_MAP in this module.)

            IN:
                key -> str:
                    Selector key to return human readable name for.

            OUT:
                str:
                    Human readable selector item name.
            """

            curr = self.pose_cursors[key][0]
            return EXPR_MAP[key][curr][1]

        def get_sprite_code(self):
            """
            Builds sprite code for the current selectors configuration.

            OUT:
                str:
                    Sprite code for use in renpy.show(...)
            """

            code = list()
            for key, values in EXPR_MAP.items():
                value = values[self.pose_cursors[key][0]][0]
                if value is not None:
                    code.append(value)
            return "".join(code)

        def get_position_label(self):
            """
            Returns human readable (tXX notation) position label for position.

            OUT:
                str:
                    Position label if user wants to display expression codes.

                None:
                    If user does not need to display expression codes.
            """

            if self.is_show_code():
                return POSITIONS[self.position_adjustment.value][1]
            return None

        def is_text_empty(self):
            """
            Checks if stored text is empty (e.g. length is zero not including
            leading or trailing whitespace.)

            OUT:
                True:
                    If text is empty.

                False:
                    If text is not empty.
            """

            return len(self.text.strip()) == 0

        def is_preset_name_empty(self):
            """
            Checks if stored preset name is empty (e.g. length is zero not
            including leading or trailing whitespace.)

            OUT:
                True:
                    If preset name is empty.

                False:
                    If preset name is not empty.
            """

            return len(self.preset_name.strip()) == 0

        def is_show_code(self):
            """
            Checks if player is in developer mode and has requested code
            display.

            OUT:
                True:
                    If config.developer is set to True and player has ticked
                    "Show expression code" option in settings.

                False:
                    False otherwise.
            """

            return renpy.config.developer and persistent._fom_saysomething_show_code

        def get_presets(self, query):
            query = query.lower()
            return [
                key for key in sorted(persistent._fom_saysomething_presets.keys())
                if query in key.lower()
            ]


        def save_preset(self, name):
            """
            Saves current state of a picker into a preset with the provided
            name. Also sets current preset cursor to this preset.

            IN:
                name -> str:
                    Name to save this preset with.
            """

            persistent._fom_saysomething_presets[name] = (
                {key: value[0] for key, value in self.pose_cursors.items()},  #0 - pose cursors
                self.position_adjustment.value,  #1 - position
                self.text,  #2 - text
                self.show_buttons,  #3 - buttons
            )

            self.preset_name = name
            self.preset_cursor = name

        def load_preset(self, name):
            """
            Loads state of a picker from a preset with the provided name. Also
            sets current preset cursor to this preset.

            IN:
                name -> str:
                    Name to load preset with.

            OUT:
                RETURN_RENDER:
                    Always returns value of RETURN_RENDER constant.
            """

            pose_cur, pos, text, buttons = persistent._fom_saysomething_presets[name]

            # Load selectors
            self.pose_cursors = {key: (cur, EXPR_MAP[key][cur][1]) for key, cur in pose_cur.items()}

            # Load position
            self.position_adjustment.value = pos
            self.on_position_change(pos)

            # Load text
            self.text = text
            self.on_text_change(text)

            # Load buttons
            self.show_buttons = buttons

            # Set preset name (for easier overwriting) and cursor (to keep
            # visual track of current preset.)
            self.preset_name = name
            self.preset_cursor = name

            return RETURN_RENDER

        def delete_preset(self, name):
            """
            Deletes preset with the provided name. Resets preset cursor.

            IN:
                name -> str:
                    Name of a preset to delete.
            """

            persistent._fom_saysomething_presets.pop(name)

            self.preset_name = ""
            self.preset_cursor = None

        def on_position_change(self, value):
            """
            Callback function for position bar.

            If value is greater than 5 the GUI is flipped to left side.

            IN:
                value -> float:
                    New value of position bar slider.
            """

            self.position = POSITIONS[value][0]
            self.gui_flip = value > 5

        def on_text_change(self, value):
            """
            Callback for text input prompt. Restarts interaction on every
            alteration.

            IN:
                value -> str:
                    New input field value.
            """

            self.text = value
            renpy.restart_interaction()

        def on_shift_enter_press(self):
            """
            Callback for Shift+Enter key press. Only returns text value when it
            is not empty (see is_text_empty(...))

            OUT:
                str:
                    Text if it is not empty.

                None:
                    If text is empty.
            """

            # Need one more check since key press isn't covered by 'Say' button
            # sensitive expression.
            if not self.is_text_empty():
                return RETURN_DONE

        def on_enter_press(self):
            """
            Callback for Enter key press (without Shift.) Adds a line break if
            there are less than two line breaks in the line already.
            """
            if self.text.count("\n") < 2:
                self.text += "\n"

        def on_buttons_tick(self):
            """
            Callback for buttons/GUI tickbox button. Flips it and returns,
            ending interaction with screen and returning a value for
            re-rendering.

            OUT:
                RETURN_RENDER:
                    Always returns RETURN_RENDER constant.
            """

            self.show_buttons = not self.show_buttons
            return RETURN_RENDER

        def on_search_input_change(self, value):
            """
            Callback for presets menu search input prompt.

            IN:
                value -> str:
                    New input field value.
            """

            self.presets_search = value

        def on_search_adjustment_range(self, adjustment):
            """
            Callback for presets menu search input to adjust cursor so it's
            visible to the user.

            IN:
                adjustment -> ui.adjustment:
                    Adjustment that has changed.
            """

            widget = renpy.get_widget("fom_saysomething_picker", "search_input", "screens")
            caret_relative_pos = 1.0
            if widget is not None:
                caret_pos = widget.caret_pos
                content_len = len(widget.content)

                if content_len > 0:
                    caret_relative_pos = caret_pos / float(content_len)

            # This ensures that the caret is always visible (close enough) to the user
            # when they enter text
            adjustment.change(adjustment.range * caret_relative_pos)


    picker = None


# GUI elements styling, mostly reused to keep up with MAS theme and style.
# Some elements have been adjusted for design of this submod's GUI.

style fom_saysomething_picker_frame is gui_frame:
    background Frame(["gui/confirm_frame.png", "gui/frame.png"], gui.confirm_frame_borders, tile=gui.frame_tile)

style fom_saysomething_picker_frame_dark is gui_frame:
    background Frame(["gui/confirm_frame.png", "gui/frame_d.png"], gui.confirm_frame_borders, tile=gui.frame_tile)

style fom_saysomething_confirm_button is generic_button_light:
    xysize (116, None)
    padding (10, 5, 10, 5)

style fom_saysomething_confirm_button_dark is generic_button_dark:
    xysize (116, None)
    padding (10, 5, 10, 5)

style fom_saysomething_confirm_button_text is generic_button_text_light:
    text_align 0.5
    layout "subtitle"

style fom_saysomething_confirm_button_text_dark is generic_button_text_dark:
    text_align 0.5
    layout "subtitle"

style fom_saysomething_titlebox is default:
    background Frame("gui/namebox.png", gui.namebox_borders, tile=gui.namebox_tile, xalign=gui.name_xalign)
    padding gui.namebox_borders.padding
    ypos gui.name_ypos
    ysize gui.namebox_height

style fom_saysomething_titlebox_dark is default:
    background Frame("gui/namebox_d.png", gui.namebox_borders, tile=gui.namebox_tile, xalign=gui.name_xalign)
    padding gui.namebox_borders.padding
    ypos gui.name_ypos
    ysize gui.namebox_height


# Expression/pose, location and say text picker GUI screen.
# NOTE: in this screen, picker is referenced directly as it is implied that it
# is set in fom_saysomething_event event.

screen fom_saysomething_picker(say=True):
    style_prefix "fom_saysomething_picker"

    vbox:
        # Flip GUI to prevent hiding Monika behind it.
        if not picker.gui_flip:
            if picker.is_show_code():
                align (0.99, 0.07)
            else:
                align (0.97, 0.2)
        else:
            if picker.is_show_code():
                align (0.01, 0.07)
            else:
                align (0.03, 0.2)

        vbox:
            spacing 10

            if not picker.presets_menu:

                # Selectors panel.

                frame:
                    padding (10, 10)

                    vbox:
                        spacing 10

                        if picker.is_show_code():
                            hbox:
                                xmaximum 350
                                xfill True

                                # Split into two hboxes to align arrows and labels
                                # properly (similar to buttons with the selectors.)

                                hbox:
                                    xfill True
                                    xmaximum 110
                                    text "Expression"

                                hbox:
                                    xmaximum 240
                                    xfill True
                                    xalign 1.0

                                    if picker.is_show_code():
                                        text picker.get_sprite_code() + " at " + picker.get_position_label() xalign 0.5
                                    else:
                                        text picker.get_sprite_code() xalign 0.5

                        for key, value in _fom_saysomething.EXPR_MAP.items():
                            hbox:
                                xmaximum 350
                                xfill True

                                # Split into two hboxes to align arrows and labels
                                # properly, so that one can click them without
                                # missing if label is too big; this layout preserves
                                # space for big labels.

                                hbox:
                                    xfill True
                                    xmaximum 110
                                    text key

                                hbox:
                                    xmaximum 240
                                    xfill True
                                    xalign 1.0

                                    textbutton "<" action Function(picker.pose_switch_selector, key, forward=False) xalign 0.0
                                    text picker.get_pose_label(key) xalign 0.5
                                    textbutton ">" action Function(picker.pose_switch_selector, key, forward=True) xalign 1.0

                # Position slider panel.

                frame:
                    padding (10, 10)

                    hbox:
                        xmaximum 350
                        xfill True

                        text "Position"
                        bar:
                            xalign 1.0
                            yalign 0.5
                            adjustment picker.position_adjustment
                            released Return(_fom_saysomething.RETURN_RENDER)

                # Buttons tickbox.

                frame:
                    padding (10, 5)

                    hbox:
                        style_prefix "check"

                        xmaximum 350
                        xfill True
                        spacing 10

                        if say:
                            textbutton "Show buttons and quick menu":
                                selected picker.show_buttons
                                action Function(picker.on_buttons_tick)
                        else:
                            textbutton "Show buttons":
                                selected picker.show_buttons
                                action Function(picker.on_buttons_tick)

            else:

                # Presets menu.

                frame:
                    xsize 370
                    ysize 40

                    # Text input.

                    background Solid(mas_ui.TEXT_FIELD_BG)

                    viewport:
                        draggable False
                        arrowkeys False
                        mousewheel "horizontal"
                        xsize 360
                        ysize 38
                        xadjustment ui.adjustment(ranged=picker.on_search_adjustment_range)

                        input:
                            id "search_input"
                            style_prefix "input"
                            length 50
                            xalign 0.0
                            layout "nobreak"
                            changed picker.on_search_input_change
                            value picker.presets_search_value

                    # Hint text in search box visible if no text is entered.

                    if len(picker.presets_search) == 0:
                        text "Search for a preset...":
                            text_align 0.0
                            layout "nobreak"
                            color "#EEEEEEB2"
                            first_indent 10
                            line_leading 1
                            outlines []

                # List of presets.

                fixed:
                    xsize 350

                    if not picker.is_show_code():
                        ysize 420
                    else:
                        ysize 442

                    # Viewport wrapping long list.

                    vbox:
                        pos (0, 0)
                        anchor (0, 0)

                        viewport:
                            id "viewport"

                            yfill False
                            mousewheel True
                            arrowkeys True

                            vbox:
                                spacing 10

                                # Preset buttons; highlit when selected.

                                for _key in picker.get_presets(picker.presets_search):
                                    textbutton _key:
                                        style "twopane_scrollable_menu_button"
                                        xysize (350, None)

                                        action Function(picker.load_preset, _key)
                                        selected picker.preset_cursor == _key

                    # Scrollbar used by list of presets above.

                    bar:
                        style "classroom_vscrollbar"
                        value YScrollValue("viewport")
                        xalign 1.07

        # Confirmation buttons area.

        frame:
            padding(0, 10)
            background None

            hbox:
                style_prefix "fom_saysomething_confirm"

                xmaximum 350
                xfill True

                spacing 10

                # Selectors panel buttons.

                if not picker.presets_menu:
                    if say:
                        # Note: this button sensitivity relies on Ren'Py interaction
                        # restart that is done in text input field callback.
                        textbutton "Say":
                            action Return(_fom_saysomething.RETURN_DONE)
                            sensitive not picker.is_text_empty()

                    else:
                        textbutton "Pose":
                            action Return(_fom_saysomething.RETURN_DONE)

                    textbutton "Presets":
                        action [SetField(picker, "presets_menu", True),
                                DisableAllInputValues()]

                # Presets panel buttons.

                else:
                    textbutton "Save":
                        action Show("fom_saysomething_preset_name_input_modal")
                    textbutton "Delete":
                        action Show("fom_saysomething_preset_delete_confirm_modal")
                        sensitive picker.preset_cursor is not None
                    if picker.preset_cursor is not None:
                        key "K_DELETE" action Show("fom_saysomething_preset_delete_confirm_modal")

                # 'Close' or 'back' is the same for both panels and can share
                # the logic. For selectors panel it will close the GUI
                # altogether, for presets it will take back to selectors.

                textbutton ("Close" if not picker.presets_menu else "Back"):
                    if not picker.presets_menu:
                        action Return(_fom_saysomething.RETURN_CLOSE)
                    else:
                        action [SetField(picker, "presets_menu", False),
                                DisableAllInputValues()]

    if say:
        # Text input area styled as textbox and key capture so that Shift+Enter key
        # press is the same as pressing 'Say' button.

        key "shift_K_RETURN" action Function(picker.on_shift_enter_press) capture True

        # This handles Enter key press and adds a new line.
        key "noshift_K_RETURN" action Function(picker.on_enter_press) capture True

        window:
            align (0.5, 0.99)

            # This split into two components to prevent title sliding as user keeps
            # typing the input text.

            window:
                style "fom_saysomething_titlebox"
                align (0.5, 0.0)

                text "What do you want me to say?~"

            vbox:
                align (0.5, 0.58)

                hbox:
                    # This limits text input in height and width, preventing it from
                    # overflowing the container and getting out of box.
                    ymaximum 80
                    yfill True
                    xmaximum gui.text_width
                    xfill True

                    input:
                        # Prevent overflowing by limiting horizontal width of text.
                        pixel_width gui.text_width

                        # Align text to left side and prevent it from getting centered.
                        align (0.0, 0.0)
                        text_align 0.0

                        # Note: in order to always have the most up to date text this
                        # callback updates it internally in _fom_saysomething store
                        # and restarts Ren'Py interaction in order for 'Say' button
                        # to gray out when no text is provided.
                        changed picker.on_text_change
                        value picker.text_value

            hbox:
                align (0.5, 1.02)

                use quick_menu


# Modal screen used for entering new preset name.
# NOTE: same as main screen refers to picker directly, in global scope.

screen fom_saysomething_preset_name_input_modal:
    on "show" action picker.preset_name_value.Enable()

    style_prefix "confirm"

    modal True
    zorder 200

    add mas_getTimeFile("gui/overlay/confirm.png")

    # Button alternative keybinds.

    # If preset name is not empty, allow pressing Enter to confirm instead
    # of button click.
    if not picker.is_preset_name_empty():
        key "K_RETURN":
            action [Play("sound", gui.activate_sound),
                    Function(picker.save_preset, picker.preset_name),
                    Hide("fom_saysomething_preset_name_input_modal")]

    # Allow pressing Esc to cancel.
    key "K_ESCAPE":
        action [Play("sound", gui.activate_sound),
                Hide("fom_saysomething_preset_name_input_modal")]

    frame:
        vbox:
            xmaximum 300
            xfill True

            align (0.5, 0.5)
            spacing 30

            # Title.

            text "Save this preset as:":
                style "confirm_prompt"
                xalign 0.5

            # Input field.

            input:
                style_prefix "input"

                xalign 0.0
                layout "nobreak"

                length 30
                pixel_width 300

                # NOTE: for some reason this doesn't work if used with value
                # inside screen; for this reason it is in Picker instance.
                value picker.preset_name_value

            # Save/cancel buttons.

            hbox:
                xalign 0.5
                spacing 10

                # Sensitivity of this button relies on emptiness of entered
                # preset name.
                textbutton "Save":
                    action [Play("sound", gui.activate_sound),
                            Function(picker.save_preset, picker.preset_name),
                            Hide("fom_saysomething_preset_name_input_modal")]
                    sensitive not picker.is_preset_name_empty()
                textbutton "Cancel":
                    action [Play("sound", gui.activate_sound),
                            Hide("fom_saysomething_preset_name_input_modal")]


# Modal screen used for confirming preset deletion.
# NOTE: same as main screen refers to picker directly, in global scope.

screen fom_saysomething_preset_delete_confirm_modal:
    style_prefix "confirm"

    modal True
    zorder 200

    add mas_getTimeFile("gui/overlay/confirm.png")

    # Keybinds alternative to button clicks, pressing Enter will confirm
    # and Esc will cancel.

    key "K_RETURN":
        action [Play("sound", gui.activate_sound),
                Function(picker.delete_preset, picker.preset_name),
                Hide("fom_saysomething_preset_delete_confirm_modal")]

    key "K_ESCAPE":
        action [Play("sound", gui.activate_sound),
                Hide("fom_saysomething_preset_delete_confirm_modal")]

    frame:
        vbox:
            xmaximum 300
            xfill True

            align (0.5, 0.5)
            spacing 30

            # Title.

            text "Delete this preset?":
                style "confirm_prompt"
                xalign 0.5

            # Name of preset chosen for deletion.

            text picker.preset_cursor:
                xalign 0.5

            # Confirmation and cancellation buttons.

            hbox:
                xalign 0.5
                spacing 10

                textbutton "Delete":
                    action [Play("sound", gui.activate_sound),
                            Function(picker.delete_preset, picker.preset_cursor),
                            Hide("fom_saysomething_preset_delete_confirm_modal")]
                textbutton "Cancel":
                    action [Play("sound", gui.activate_sound),
                            Hide("fom_saysomething_preset_delete_confirm_modal")]