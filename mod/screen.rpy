# screen.rpy contains custom text GUI that shows up when Monika is asked to
# say something.
#
# This file is part of Say Something (see link below):
# https://github.com/friends-of-monika/mas-saysomething



## PRESETS DICTIONARY DEFINITION ----------------------------------------------------------------------------------------------------------

# Presets dictionary with premade presets. Structure is the following:
# String key (warning: shown to user!), tuple value.
# Tuple contains three items:
# 1. Pose selectors dictionary (scroll to poses dictionary for more info)
# 2. Position ID (again, scroll down to see positions)
# 3. Text she says (always present and non None)

default persistent._fom_saysomething_presets = {
    # Presets by dreamscached
    "Hey, everyone!":           ({"pose": 3, "eyes": 0, "eyebrows": 0, "blush": 0, "tears": 0, "sweat": 0, "mouth": 1}, 4, "Hey, everyone!"),
    "Sparkly pretty eyes":      ({"pose": 0, "eyes": 2, "eyebrows": 0, "blush": 0, "tears": 0, "sweat": 0, "mouth": 1}, 4, "Is this... Is this for me?"),
    "Daydreaming":              ({"pose": 4, "eyes": 8, "eyebrows": 3, "blush": 0, "tears": 0, "sweat": 0, "mouth": 0}, 4, "..."),
    "Fact of the day":          ({"pose": 6, "eyes": 7, "eyebrows": 0, "blush": 0, "tears": 0, "sweat": 0, "mouth": 1}, 4, "Here's another fun fact of the day!"),
    "Angry Monika":             ({"pose": 1, "eyes": 3, "eyebrows": 1, "blush": 0, "tears": 0, "sweat": 0, "mouth": 2}, 4, "You should not have done that..."),
    "I love you":               ({"pose": 4, "eyes": 0, "eyebrows": 2, "blush": 2, "tears": 0, "sweat": 0, "mouth": 0}, 4, "I... I love you so much..."),
    "How embarrassing":         ({"pose": 1, "eyes": 6, "eyebrows": 2, "blush": 0, "tears": 0, "sweat": 1, "mouth": 1}, 4, "I really hope you didn't mind that, ahaha..."),
    "Asking you out":           ({"pose": 2, "eyes": 7, "eyebrows": 0, "blush": 2, "tears": 0, "sweat": 0, "mouth": 0}, 4, "Got any plans for this evening?~"),
    "Feeling singy":            ({"pose": 0, "eyes": 8, "eyebrows": 0, "blush": 0, "tears": 0, "sweat": 0, "mouth": 1}, 4, "Every day, I imagine a future where I can be with you~"),
    "Cutest smug in existence": ({"pose": 0, "eyes": 9, "eyebrows": 0, "blush": 2, "tears": 0, "sweat": 0, "mouth": 5}, 4, "If you know what I mean, ehehe~"),

    # Contributed by Sevi (u/lost_localcat) with small edits by dreamscached
    "Sulks to you":        ({"eyebrows": 3, "eyes": 12, "blush": 2, "mouth": 8, "sweat": 0, "pose": 4, "tears": 0}, 4, "Hmph..."),
    "Thinking deep":       ({"eyebrows": 4, "eyes": 5,  "blush": 0, "mouth": 2, "sweat": 0, "pose": 4, "tears": 0}, 4, "Hmm, I wonder..."),
    "Bringing up a topic": ({"eyebrows": 0, "eyes": 0,  "blush": 0, "mouth": 3, "sweat": 0, "pose": 0, "tears": 0}, 4, "Darling, have you ever thought of..."),
    "In loving worries":   ({"eyebrows": 2, "eyes": 0,  "blush": 0, "mouth": 2, "sweat": 0, "pose": 1, "tears": 0}, 4, "Honey, is everything alright?..")
}

## END PRESETS DICTIONARY DEFINITION ------------------------------------------------------------------------------------------------------



## PICKER CLASS, CONSTANTS, POSES/POSITIONS -----------------------------------------------------------------------------------------------

init -200 python in mas_ui:
    import store

    if not hasattr(store.mas_ui, "TEXT_FIELD_BG"):
        TEXT_FIELD_BG = "#ffaa99aa"


init 100 python in _fom_saysomething:

    import store
    from store import ui, persistent
    from store import FieldInputValue
    from store import MASMoniBlinkTransform, MASMoniWinkTransform
    from store import pygame

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


    ## POSE SELECTORS DICTIONARY ----------------------------------------------------------------------------------------------------------

    # Orderect dictionary is used to preserve order when rendering a table of
    # selectors. This dictionary has the following structure:
    #  [key] -> tuple:
    #    [0]: human-readable selector name
    #    [1] -> tuple:
    #      [0]: expression code/mnemonic
    #      [1]: expression human readable description

    EXPR_MAP = OrderedDict([
        ("pose", (_("Pose"), [
            ("1", _("Rest on hands")),
            ("2", _("Cross")),
            ("3", _("Point right, rest")),
            ("4", _("Point right")),
            ("5", _("Lean")),
            ("6", _("Down")),
            ("7", _("Point right, down"))
        ])),
        ("eyes", (_("Eyes"), [
            ("e", _("Normal")),
            ("w", _("Wide")),
            ("s", _("Sparkle")),
            ("t", _("Smug")),
            ("c", _("Crazy")),
            ("r", _("Look right")),
            ("l", _("Look left")),
            ("h", _("Closed, happy")),
            ("d", _("Closed, sad")),
            ("k", _("Wink left")),
            ("n", _("Wink right")),
            ("f", _("Soft")),
            ("m", _("Smug, left")),
            ("g", _("Smug, right"))
        ])),
        ("eyebrows", (_("Eyebrows"), [
            ("u", _("Up")),
            ("f", _("Furrowed")),
            ("k", _("Knit")),
            ("s", _("Straight")),
            ("t", _("Thinking"))
        ])),
        ("blush", (_("Blush"), [
            (None, _("None")),
            ("bl", _("Line")),
            ("bs", _("Shade")),
            ("bf", _("Full"))
        ])),
        ("tears", (_("Tears"), [
            (None, _("None")),
            ("ts", _("Streaming")),
            ("td", _("Dried")),
            ("tp", _("Pooled")),
            ("tu", _("Tearing up"))
        ])),
        ("sweat", (_("Sweat"), [
            (None, _("None")),
            ("sdl", _("Left cheek")),
            ("sdr", _("Right cheek")),
        ])),
        ("mouth", (_("Mouth"), [
            ("a", _("Smile, closed")),
            ("b", _("Smile, open")),
            ("c", _("Straight")),
            ("d", _("Open")),
            ("o", _("Gasp")),
            ("u", _("Smug")),
            ("w", _("Wide")),
            ("x", _("Grit teeth")),
            ("p", _("Pout")),
            ("t", _("Triangle"))
        ]))
    ])


    def get_sprite_code(pose_cursors):
        """
        Generate sprite code for a dictionary of pose cursors (see above for
        detailed declaration of keys and IDs.)

        IN:
            post_cursors -> dict[str, int]:
                Pose cursor dictionary.

        OUT:
            str:
                MAS sprite code for Monika's pose.
        """

        code = list()
        for key, data in EXPR_MAP.items():
            _, values = data
            cursor = pose_cursors[key]
            if isinstance(cursor, tuple):
                cursor = cursor[0]
            value = values[cursor][0]
            if value is not None:
                code.append(value)
        return "".join(code)

    def get_pose_cursors(sprite_code):
        """
        Generate pose cursors for a sprite code.

        IN:
            sprite_code -> str:
                MAS sprite code for Monika's pose.

        OUT:
            pose_cursors -> dict[str, int]:
                Pose cursor dictionary.
        """
        # Flatten the EXPR_MAP into a dictionary for easier search
        flat_map = {}
        for key, data in EXPR_MAP.items():
            _, values = data
            for i, (code, _) in enumerate(values):
                if code is not None:
                    flat_map[code] = (key, i)

        # Sort the codes by length in descending order for greedy matching
        sorted_codes = sorted(flat_map.keys(), key=len, reverse=True)

        # Initialize pose_cursors with all keys from EXPR_MAP set to 0
        pose_cursors = {key: 0 for key in EXPR_MAP.keys()}

        while sprite_code:
            for code in sorted_codes:
                if sprite_code.startswith(code):
                    key, cursor = flat_map[code]
                    pose_cursors[key] = cursor
                    sprite_code = sprite_code[len(code):]
                    break
            else:
                raise ValueError(sprite_code)

        return pose_cursors

    ## END POSE SELECTORS DICTIONARY ------------------------------------------------------------------------------------------------------



    ## POSITIONS LIST ---------------------------------------------------------------------------------------------------------------------

    # Positions list containing Monika table positions from leftmost [0] to
    # rightmost [9]. Items are usable with renpy.show(..., at=list[...]) call.
    POSITIONS = [
        (store.t41, "t41"), #0
        (store.t31, "t31"), #1
        (store.t21, "t21"), #2, usually used in talk menu and scrollable choices
        (store.t42, "t42"), #3

        (store.t11, "t11"), #4, default middle screen position
       #(store.t32, "t32"), # formerly #5, same as #4 so no need to keep it here
        (store.t43, "t43"), #5

        (store.t22, "t22"), #6
        (store.t33, "t33"), #7

        (store.t44, "t44")  #8
    ]

    def get_position_code(position_cursor):
        """
        Gets position identifier for given Monika's position (see above for IDs
        and naming of the positions.)

        IN:
            position_cursor -> int:
                ID of the position Monika is at.

        OUT:
            str:
                Name of Monika's position.
        """

        return POSITIONS[position_cursor][1]

    ## END POSITIONS LIST -----------------------------------------------------------------------------------------------------------------



    ## SESSION FUNCTIONS/CONSTANTS --------------------------------------------------------------------------------------------------------

    def get_session_expressions(session):
        """
        Returns set of unique expressions used in the given session.

        IN:
            session -> <Picker session>:
                Session to extract sprite codes from.

        OUT:
            set[str]:
                Set of spritecodes.
        """

        return set(map(lambda it: get_sprite_code(it[0]), session))


    # Need this limitation because else we'll quickly run out of memory.
    MAX_SESSION_SIZE = 100

    # How many images can we allow Ren'Py to keep in memory before we
    # clean them up to reduce memory consumption?
    MAX_CACHED_IMAGES = 64

    # Cache object to track and release images.
    IMAGE_CACHE = MoniSpriteCache(MAX_CACHED_IMAGES)

    # Maximum length of processable clipboard content.
    MAX_CLIP_INPUT = 32

    ## END SESSION FUNCTIONS/CONSTANTS ----------------------------------------------------------------------------------------------------



    ## PICKER OBJECT AND METHODS ----------------------------------------------------------------------------------------------------------

    class Picker(object):
        """
        Picker represents pose, position and GUI configuration screen with data
        stored in this object.
        """

        def __init__(self):
            """
            Creates a new Picker instance.
            """

            self._reset_state()

            # Flag value for flipping selectors/position GUI to left side of
            # screen if it would mean Monika is behind the GUI and not in user's
            # sight.
            self.gui_flip = False

            # Flag value for showing presets menu instead of selectors panel.
            self.presets_menu = False

            # Adjustment object to keep scroll state for preset list and prevent
            # jumping on re-render.
            self.presets_list_adjustment = ui.adjustment()

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

            # Session states and current state cursor.
            self.session = None
            self.session_cursor = 0

            # Flag to indicate that any changes were made to ask for confirmation
            self.changed = False


        ## PICKER STATE MANAGEMENT FUNCTIONS ----------------------------------------------------------------------------------------------

        def _reset_state(self, reset_pose=True, reset_text=True):
            if reset_pose:
                # This dictionary contains key to 2-tuple of:
                #  [0]: current expression cursor index
                #  [1]: current expression human readable name
                # Initially all cursors are at zero (with corresponding expression names.)
                self.pose_cursors = {key: (0, EXPR_MAP[key][1][0][1]) for key in EXPR_MAP.keys()}

                # Position object to use when showing Monika at her table. By
                # default, her usual middle screen position.
                self.position = POSITIONS[4][0]

                # Position cursor, an index to POSITIONS list to pick position by.
                self.position_cursor = 4

                # Set GUI flip.
                self.gui_flip = self.position_cursor > 4

            if reset_text:
                # Variable that stores entered user text prompt.
                self.text = ""

                # Ren'Py input value to allow disabling text input when needed.
                self.text_value = FieldInputValue(self, "text", returnable=False)

            return RETURN_RENDER

        def _save_state(self):
            return (
                {key: value[0] for key, value in self.pose_cursors.items()},  #0 - pose cursors
                self.position_cursor,  #1 - position
                self.text  #2 - text
            )

        def _load_state(self, state):
            pose_cur, pos, text = state

            # Load selectors
            self._load_pose_cursors(pose_cur)

            # Load position
            self.position_cursor = pos
            self.on_position_change(pos)

            # Load text
            self.text = text
            self.on_text_change(text)

            self.changed = True
            return RETURN_RENDER

        def _load_pose_cursors(self, pose_cursors):
            self.pose_cursors = {key: (cur, EXPR_MAP[key][1][cur][1]) for key, cur in pose_cursors.items()}

        ## END PICKER STATE MANAGEMENT FUNCTIONS ------------------------------------------------------------------------------------------



        ## POSE/EXPRESSION SELECTOR FUNCTIONS ---------------------------------------------------------------------------------------------

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
            _max = len(EXPR_MAP[key][1]) - 1

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

            self.pose_cursors[key] = (new, EXPR_MAP[key][1][new][1])

            # This is equivalent to using Return(RETURN_RENDER) action.
            # https://lemmasoft.renai.us/forums/viewtopic.php?p=536626#p536626
            self.changed = True
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
            return EXPR_MAP[key][1][curr][1]

        def position_switch_selector(self, forward):
            """
            Switches position forward or backward. If cursor reaches zero or max
            value, prevents it from going further.

            IN:
                forward -> bool:
                    True if to increment, False to decrement.

            NOTE:
                This function (and entire position selector as selector) exists
                only to provide support for RenPy 6. It will be removed as soon
                as MAS migrates to RenPy 8.
            """

            curr = self.position_cursor
            _max = len(POSITIONS) - 1

            new = curr
            if forward:
                if curr != _max:
                    new = curr + 1
            else:
                if curr != 0:
                    new = curr - 1

            self.position_cursor = new
            self.position = POSITIONS[self.position_cursor][0]
            self.gui_flip = self.position_cursor > 4
            return RETURN_RENDER

        def get_position_label(self):
            """
            Returns human readable (cursor + 1 or tXX notation depending on
            user preferences) position label for position.

            OUT:
                str:
                    Position label.
            """

            if self.is_show_code():
                return POSITIONS[self.position_cursor][1]
            return "#" + str(self.position_cursor + 1)

        def position_switch_usable(self, forward):
            """
            Returns if position switch (backward or forward) is usable and
            should be sensitive.

            IN:
                forward -> bool:
                    True if forward, False if backward.

            OUT:
                True:
                    True if can increment/decrement, False otherwise.

            NOTE:
                This function (and entire position selector as selector) exists
                only to provide support for RenPy 6. It will be removed as soon
                as MAS migrates to RenPy 8.
            """

            curr = self.position_cursor
            _max = len(POSITIONS) - 1
            if forward:
                return curr < _max
            else:
                return curr > 0

        def get_sprite_code(self):
            """
            Builds sprite code for the current selectors configuration.

            OUT:
                str:
                    Sprite code for use in renpy.show(...)
            """

            return get_sprite_code(self.pose_cursors)

        def get_position_label(self):
            """
            Returns human readable (cursor + 1 or tXX notation depending on
            user preferences) position label for position.

            OUT:
                str:
                    Position label.
            """

            if self.is_show_code():
                return POSITIONS[self.position_cursor][1]
            return "#" + str(self.position_cursor + 1)

        def position_switch_usable(self, forward):
            """
            Returns if position switch (backward or forward) is usable and
            should be sensitive.

            IN:
                forward -> bool:
                    True if forward, False if backward.

            OUT:
                True:
                    True if can increment/decrement, False otherwise.

            NOTE:
                This function (and entire position selector as selector) exists
                only to provide support for RenPy 6. It will be removed as soon
                as MAS migrates to RenPy 8.
            """

            curr = self.position_cursor
            _max = len(POSITIONS) - 1
            if forward:
                return curr < _max
            else:
                return curr > 0

        def position_switch_selector(self, forward):
            """
            Switches position forward or backward. If cursor reaches zero or max
            value, prevents it from going further.

            IN:
                forward -> bool:
                    True if to increment, False to decrement.

            NOTE:
                This function (and entire position selector as selector) exists
                only to provide support for RenPy 6. It will be removed as soon
                as MAS migrates to RenPy 8.
            """

            curr = self.position_cursor
            _max = len(POSITIONS) - 1

            new = curr
            if forward:
                if curr != _max:
                    new = curr + 1
            else:
                if curr != 0:
                    new = curr - 1

            self.position_cursor = new
            self.position = POSITIONS[self.position_cursor][0]
            self.gui_flip = self.position_cursor > 4
            self.changed = True
            return RETURN_RENDER

        def select_from_clipboard(self):
            """
            Receives text from clipboard and parses expression code from it.
            If text is longer than MAX_CLIP_INPUT, returns None.
            If syntax is incorrect, returns None.

            OUT:
                None:
                    Returns None on failure.
                RETURN_RENDER:
                    Returns RETURN_RENDER on success.
            """

            clip = pygame.scrap.get(pygame.SCRAP_TEXT)
            if len(clip) > MAX_CLIP_INPUT:
                return

            clip = clip.decode("utf-8")

            try:
                cursors = get_pose_cursors(clip)
                if not cursors:
                    return
            except ValueError:
                return

            self._load_pose_cursors(cursors)
            self.changed = True
            return RETURN_RENDER

        def copy_to_clipboard(self):
            """
            Retrieves sprite code from pickers state and saves it to clipboard.

            OUT:
                RETURN_RENDER:
                    Always returns RETURN_RENDER.
            """

            code = get_sprite_code(self.pose_cursors)
            pygame.scrap.put(pygame.SCRAP_TEXT, code.encode("utf-8"))
            return RETURN_RENDER

        ## END POSE/EXPRESSION SELECTOR FUNCTIONS -----------------------------------------------------------------------------------------



        ## VARIOUS CHECK FUNCTIONS --------------------------------------------------------------------------------------------------------

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
            Checks if player has requested code display.

            OUT:
                True:
                    If player has ticked "Show expression code" option in settings.

                False:
                    False otherwise.
            """

            return persistent._fom_saysomething_show_code

        ## END VARIOUS CHECK FUNCTIONS ----------------------------------------------------------------------------------------------------



        ## PRESET RELATED FUNCTION --------------------------------------------------------------------------------------------------------

        def get_presets(self, query):
            """
            Returns list of preset names matching query sorted lexicographically.

            IN:
                query -> str:
                    String to find in presets.

            OUT:
                list of str:
                    List of presets matching query.
            """

            query = query.lower()
            return [
                key for key in sorted(persistent._fom_saysomething_presets.keys())
                if query in key.lower()
            ]

        def is_preset_exists(self, name):
            """
            Checks if preset by the provided name exists.

            IN:
                name -> str:
                    Name of a preset to check.

            OUT:
                True:
                    If exists.

                False:
                    If does not.
            """

            return name in persistent._fom_saysomething_presets

        def _save_state(self):
            return (
                {key: value[0] for key, value in self.pose_cursors.items()},  #0 - pose cursors
                self.position_cursor,  #1 - position
                self.text  #2 - text
            )

        def _load_state(self, state):
            pose_cur, pos, text = state

            # Load selectors
            self.pose_cursors = {key: (cur, EXPR_MAP[key][1][cur][1]) for key, cur in pose_cur.items()}

            # Load position
            self.position_cursor = pos
            self.on_position_change(pos)

            # Load text
            self.text = text
            self.on_text_change(text)

            return RETURN_RENDER

        def save_preset(self, name):
            """
            Saves current state of a picker into a preset with the provided
            name. Also sets current preset cursor to this preset.

            IN:
                name -> str:
                    Name to save this preset with.
            """

            persistent._fom_saysomething_presets[name] = self._save_state()

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

            # Set preset name (for easier overwriting) and cursor (to keep
            # visual track of current preset.)
            self.preset_name = name
            self.preset_cursor = name
            return self._load_state(persistent._fom_saysomething_presets[name])

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

        ## END PRESET RELATED FUNCTION ----------------------------------------------------------------------------------------------------



        ## SESSION MODE RELATED FUNCTIONS -------------------------------------------------------------------------------------------------

        def enable_session_mode(self):
            """
            Activates session mode and sets session list. This action should be
            irreversible for the current picker interaction.
            """

            self.session = list()

        def session_switch_usable(self, forward):
            """
            Checks if session state switch is usable for backward/forward
            movement.

            IN:
                forward -> bool:
                    True if moving forward, False if backward.

            OUT:
                True if allowed to navigate to previous/next session state,
                False otherwise.
            """

            if forward:
                return self.session is not None and self.session_cursor < len(self.session)
            else:
                return self.session is not None and self.session_cursor > 0

        def session_switch_cursor(self, forward):
            """
            Switches current session state to previous/next one.

            IN:
                forward -> bool:
                    True if moving forward, False if backward.

            OUT:
                RETURN_RENDER:
                    Returned always.
            """

            if forward:
                if self.session_cursor + 1 < len(self.session):
                    self.session_cursor += 1
                    self._load_state(self.session[self.session_cursor])
                else:
                    self.session_cursor = len(self.session)
                    self._reset_state(reset_pose=False, reset_text=True)
                return RETURN_RENDER
            else:
                if self.session_cursor > 0:
                    self.session_cursor -= 1
                else:
                    self.session_cursor = 0
                self._load_state(self.session[self.session_cursor])
                return RETURN_RENDER

        def add_session_item(self):
            """
            Saves current session state and appends it to session.

            OUT:
                RETURN_RENDER:
                    Always returns RETURN_RENDER.

            RAISES:
                ValueError:
                    If session entries count is too big.
            """

            if self.is_session_maximum_reached():
                raise ValueError("Maximum count of session entries reached.")

            self.session.append(self._save_state())
            self.session_cursor += 1

            # NOTE: reset just text, not pose
            self._reset_state(reset_pose=False, reset_text=True)
            self.changed = True
            return RETURN_RENDER

        def edit_session_item(self):
            """
            Changes current session state and saves it to session.
            """

            self.session[self.session_cursor] = self._save_state()

        def remove_session_item(self):
            """
            Removes current session state.

            OUT:
                RETURN_RENDER:
                    Always returned.
            """

            if self.session_cursor > len(self.session) - 1:
                self.session.pop(len(self.session) - 1)
                self.session_cursor = len(self.session)
                self._load_state(self.session[self.session_cursor])

            elif self.session_cursor < 0:
                self.session.pop(0)
                self.session_cursor = 0

            else:
                self.session.pop(self.session_cursor)

            if self.session_cursor < len(self.session):
                self._load_state(self.session[self.session_cursor])
            else:
                self._reset_state()
            return RETURN_RENDER

        def can_remove_session(self):
            """
            Checks if it is possible to remove currently showing session state.

            OUT:
                True:
                    If possible to remove current session state.

                False:
                    If not.
            """

            return self.session_cursor >= 0 and self.session_cursor < len(self.session)

        def is_editing_session_item(self):
            """
            Checks if session cursor is currently behind its head.

            OUT:
                True:
                    If user is editing previous state and not adding new one.

                False:
                    If user is adding new state.
            """

            if self.session_cursor == 0 and len(self.session) == 0:
                return False
            return self.session_cursor != len(self.session)

        def is_session_maximum_reached(self):
            """
            Checks if the session has reached its maximum capacity.

            OUT:
                True:
                    If the session is full and has reached the maximum size.

                False:
                    If the session has not yet reached the maximum size.
            """

            return not (len(self.session) < MAX_SESSION_SIZE)

        ## END SESSION MODE RELATED FUNCTIONS -------------------------------------------------------------------------------------------------



        ## GUI CALLBACK FUNCTIONS ---------------------------------------------------------------------------------------------------------

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
            self.changed = True

        def on_text_change(self, value):
            """
            Callback for text input prompt. Restarts interaction on every
            alteration.

            IN:
                value -> str:
                    New input field value.
            """

            self.text = value
            if len(self.text) > 0:
                self.changed = True
            renpy.restart_interaction()

        def on_shift_enter_press(self, say):
            """
            Callback for Shift+Enter key press. Only returns text value when it
            is not empty (see is_text_empty(...))

            IN:
                say -> bool:
                    True if in say mode, False if in pose mode.

            OUT:
                str:
                    Text if it is not empty.

                None:
                    If text is empty.
            """

            if say:
                # Need one more check since key press isn't covered by 'Say' button
                # sensitive expression.
                if not self.is_text_empty():
                    # When in session mode, save session state and re-render.
                    if self.session is not None:
                        self.add_session_item()
                        return RETURN_RENDER

                    # Say something.
                    else:
                        return RETURN_DONE

            else:
                # If in session mode, add session state and re-render.
                if self.session is not None:
                    self.add_session_item()
                    return RETURN_RENDER

                # If not, just pose.
                else:
                    return RETURN_DONE

        def on_enter_press(self):
            """
            Callback for Enter key press (without Shift.) Adds a line break if
            there are less than two line breaks in the line already.
            """

            if self.text.count("\n") < 2:
                self.text += "\n"
            self.changed = True
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

        ## END GUI CALLBACK FUNCTIONS -----------------------------------------------------------------------------------------------------

    # Declare picker as a variable.
    picker = None

    ## END PICKER OBJECT AND METHODS ------------------------------------------------------------------------------------------------------



## STYLE CUSTOMIZATIONS/BACKPORTS ---------------------------------------------------------------------------------------------------------

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

## END STYLE CUSTOMIZATIONS/BACKPORTS -----------------------------------------------------------------------------------------------------



## PICKER GUI LAYOUT AND DEFINITIONS ------------------------------------------------------------------------------------------------------

# Expression/pose, location and say text picker GUI screen.
# NOTE: in this screen, picker is referenced directly as it is implied that it
# is set in fom_saysomething_event event.

screen fom_saysomething_picker(say=True):
    style_prefix "fom_saysomething_picker"

    # NOTE: This is placed here because in Ren'Py 6 key object affects spacing.
    if picker.preset_cursor is not None:
        key "K_DELETE" action Show("fom_saysomething_preset_confirm_modal",
                                    title="Delete this preset?",
                                    message=picker.preset_name,
                                    ok_button="Delete",
                                    ok_action=Function(picker.delete_preset, picker.preset_name))

    vbox:



        ## GUI FLIP LOGIC -----------------------------------------------------------------------------------------------------------------

        # Based on Monika's position, it's necessary to flip GUI
        # to let user fully see Monika's pose and face.

        if not picker.gui_flip:
            if picker.is_show_code():
                align (0.99, 0.07)
            else:
                align (0.99, 0.2)
        else:
            if picker.is_show_code():
                align (0.01, 0.07)
            else:
                align (0.01, 0.2)

        ## END GUI FLIP LOGIC -------------------------------------------------------------------------------------------------------------



        ## POSE/EXRESSION SELECTORS PANEL -------------------------------------------------------------------------------------------------

        vbox:
            spacing 10

            if not picker.presets_menu:

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
                                    text _("Expression")

                                hbox:
                                    xmaximum 240
                                    xfill True
                                    xalign 1.0

                                    if picker.is_show_code():
                                        text _("{0} at {1}").format(picker.get_sprite_code(), picker.get_position_label()) xalign 0.5
                                    else:
                                        text picker.get_sprite_code() xalign 0.5

                        for key, data in _fom_saysomething.EXPR_MAP.items():
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
                                    text data[0]

                                hbox:
                                    xmaximum 240
                                    xfill True
                                    xalign 1.0

                                    textbutton "<" action Function(picker.pose_switch_selector, key, forward=False) xalign 0.0
                                    text picker.get_pose_label(key) xalign 0.5
                                    textbutton ">" action Function(picker.pose_switch_selector, key, forward=True) xalign 1.0

                ## END POSE/EXPRESSION SELECTORS PANEL ------------------------------------------------------------------------------------



                ## POSITION SLIDER/SELECTOR -----------------------------------------------------------------------------------------------

                frame:
                    padding (10, 10)

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
                            text "Position"

                        hbox:
                            xmaximum 240
                            xfill True
                            xalign 1.0

                            textbutton "<":
                                xalign 0.0
                                action Function(picker.position_switch_selector, forward=False)
                                sensitive picker.position_switch_usable(forward=False)
                            text picker.get_position_label() xalign 0.5
                            textbutton ">":
                                xalign 1.0
                                action Function(picker.position_switch_selector, forward=True)
                                sensitive picker.position_switch_usable(forward=True)

                ## END POSITION SLIDER/SELECTOR -------------------------------------------------------------------------------------------



                ## ENABLE SPEECH MODE BUTTON/SESSION CONTROL RACK -------------------------------------------------------------------------

                frame:
                    background None
                    padding (0, 0)

                    hbox:
                        style_prefix "fom_saysomething_confirm"

                        xmaximum 350
                        xfill True
                        spacing 10


                        ## ENABLE SPEECH MODE BUTTON --------------------------------------------------------------------------------------

                        if picker.session is None:
                            textbutton _("Enable {0} mode").format(_("speech") if say else _("session")):
                                xysize (370, None)
                                action Show("fom_saysomething_confirm_modal",
                                            message=_("You will be able to save up to {2} {0} for Monika to do them one after another in a row. When done,\n"
                                                      "click on {{i}}{1}{{/i}} button.\n\n"
                                                      "{{i}}You can enable {1} mode by default in submod settings.{{/i}}")
                                                      .format(_("sentences") if say else _("poses"), _("Say") if say else _("Pose"),
                                                              _fom_saysomething.MAX_SESSION_SIZE),
                                            ok_button=_("Yes"),
                                            ok_action=Function(picker.enable_session_mode))

                        ## END ENABLE SPEECH MODE BUTTON ----------------------------------------------------------------------------------



                        ## SESSION MODE RACK ----------------------------------------------------------------------------------------------

                        else:
                            textbutton (_("Add") if not picker.is_editing_session_item() else _("Edit")):
                                sensitive not say or not picker.is_text_empty()
                                if picker.is_editing_session_item():
                                    action Function(picker.edit_session_item)

                                else:
                                    if not picker.is_session_maximum_reached():
                                        # While limit is not reached, keep adding iteams
                                        action Function(picker.add_session_item)

                                    else:
                                        # When reached, show a nice message about it.
                                        action Show("dialog",
                                                    message=_("You have reached the maximum amount\nof {0}.")
                                                            .format(_("phrases for Monika to say") if say else _("poses for Monika to do")),
                                                    ok_action=Hide("dialog"))

                            textbutton _("Remove"):
                                sensitive picker.can_remove_session()
                                action Function(picker.remove_session_item)

                            textbutton "<":
                                xysize (54, None)
                                sensitive picker.session_switch_usable(forward=False)
                                action Function(picker.session_switch_cursor, forward=False)

                            textbutton ">":
                                xysize (54, None)
                                sensitive picker.session_switch_usable(forward=True)
                                action Function(picker.session_switch_cursor, forward=True)

                        ## END SESSION MODE RACK ------------------------------------------------------------------------------------------


                ## END ENABLE SPEECH MODE BUTTON/SESSION CONTROL RACK ---------------------------------------------------------------------

            else:

                ## PRESETS MENU -----------------------------------------------------------------------------------------------------------

                frame:
                    xsize 370
                    ysize 40

                    # Text input.

                    background Solid(mas_ui.TEXT_FIELD_BG)

                    viewport:
                        draggable False
                        arrowkeys False
                        mousewheel "horizontal"
                        xsize 370
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
                        text _("Search for a preset..."):
                            text_align 0.0
                            layout "nobreak"
                            color "#EEEEEEB2"
                            first_indent 10
                            line_leading 1
                            outlines []

                # List of presets.

                fixed:
                    xsize 370

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

                            yadjustment picker.presets_list_adjustment

                            vbox:
                                spacing 10

                                # Preset buttons; highlit when selected.

                                for _key in sorted(picker.get_presets(picker.presets_search)):
                                    textbutton _key:
                                        style "twopane_scrollable_menu_button"
                                        xysize (370, None)

                                        action Function(picker.load_preset, _key)
                                        selected picker.preset_cursor == _key

                    # Scrollbar used by list of presets above.

                    bar:
                        style "classroom_vscrollbar"
                        value YScrollValue("viewport")
                        xalign -0.07

                ## END PRESETS MENU -------------------------------------------------------------------------------------------------------

        # Confirmation buttons area.

        frame:
            background None
            padding (0, 10, 0, 0)

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
                        textbutton _("Say"):
                            action Return(_fom_saysomething.RETURN_DONE)
                            sensitive picker.session is None and not picker.is_text_empty() or picker.session is not None and len(picker.session) > 0

                    else:
                        textbutton _("Pose"):
                            action Return(_fom_saysomething.RETURN_DONE)
                            sensitive picker.session is None or len(picker.session) > 0

                    textbutton _("Presets"):
                        # NOTE: DisableAllInputValues will re-focus on search
                        # text input.
                        action [SetField(picker, "presets_menu", True),
                                DisableAllInputValues()]

                # Presets panel buttons.
                # NOTE: selected False because buttons tend to be stuck in
                # selected state which is unwanted.

                else:
                    textbutton _("Save"):
                        action [Show("fom_saysomething_preset_name_input_modal"),
                                picker.presets_search_value.Disable()]
                        selected False
                    textbutton _("Delete"):
                        action Show("fom_saysomething_confirm_modal",
                                    title=_("Delete this preset?"),
                                    message=picker.preset_name,
                                    ok_button=_("Delete"),
                                    ok_action=Function(picker.delete_preset, picker.preset_name))
                        sensitive picker.preset_cursor is not None
                        selected False

                # 'Close' or 'back' is the same for both panels and can share
                # the logic. For selectors panel it will close the GUI
                # altogether, for presets it will take back to selectors.

                textbutton (_("Close") if not picker.presets_menu else _("Back")):
                    xysize (118, None)
                    if not picker.presets_menu:
                        if picker.changed:
                            action Show("fom_saysomething_confirm_modal",
                                        message=_("You're going to lose any unsaved changes. Continue?"),
                                        ok_action=Return(_fom_saysomething.RETURN_CLOSE),
                                        no_action=None)
                        else:
                            action Return(_fom_saysomething.RETURN_CLOSE)
                    else:
                        # NOTE: DisableAllInputValues will re-focus on say text
                        # input (in the textbox) again.
                        action [SetField(picker, "presets_menu", False),
                                DisableAllInputValues()]

    # Additional buttons, such as menu hiding, etc.

    vbox:
        align (0.99, 0.977)
        xsize 210
        spacing 10

        # Have to use this to make buttons 'togglable.'
        style_prefix "check_scrollable_menu"

        hbox:
            style_prefix "fom_saysomething_confirm"
            xysize (210, None)
            spacing 10

            textbutton _("Copy"):
                xysize(100, None)
                action Function(picker.copy_to_clipboard)

            textbutton _("Paste"):
                xysize(100, None)
                action Function(picker.select_from_clipboard)

        hbox:
            style_prefix "fom_saysomething_confirm"

            textbutton _("Reset Pose"):
                xysize (210, None)
                action Function(picker._reset_state)

        hbox:
            # Have to use this to make buttons 'togglable.'
            style_prefix "check_scrollable_menu"

            textbutton _("Show Q. Menu"):
                xysize (210, None)

                # Make this persist, so player doesn't have to always toggle it
                selected not persistent._fom_saysomething_hide_quick_buttons

                action [ToggleField(persistent, "_fom_saysomething_hide_quick_buttons"),
                        Function(_fom_saysomething.set_mas_gui_visible,
                                 persistent._fom_saysomething_hide_quick_buttons)]

        # textbutton _("Lock Blinking"):
        #     xysize (210, None)
        #     selected not persistent._fom_saysomething_allow_winking
        #     action ToggleField(persistent, "_fom_saysomething_allow_winking")

        # vbox:
        #     style_prefix "fom_saysomething_confirm"
        #     textbutton _("Markdown Help"):
        #         xysize (210, None)
        #         selected not persistent._fom_saysomething_markdown_enabled
        #         action ToggleField(persistent, "_fom_saysomething_markdown_enabled")

    # Text input area styled as textbox and key capture so that Shift+Enter key
    # press is the same as pressing 'Say' button. For posing, it is equivalent
    # of pressing 'Pose'. When in session mode, this will add current state to
    # the session.

    key "shift_K_RETURN" action Function(picker.on_shift_enter_press, say)

    ## It's necessary to put keys *here* and not where they're actually used...
    ## Because thanks to Ren'Py, keys somehow affect spacing.

    if picker.presets_menu and picker.preset_cursor is not None:
        key "K_DELETE" action Show("fom_saysomething_confirm_modal",
                                    title=_("Delete this preset?"),
                                    message=picker.preset_name,
                                    ok_button=_("Delete"),
                                    ok_action=Function(picker.delete_preset, picker.preset_name))

    if say:
        # This handles Enter key press and adds a new line.
        key "noshift_K_RETURN" action Function(picker.on_enter_press)

        window:
            align (0.5, 0.99)

            # This split into two components to prevent title sliding as user keeps
            # typing the input text.

            window:
                style "fom_saysomething_titlebox"
                align (0.5, 0.0)

                text _("What do you want me to say?~")

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

    # This is here because 'key' somehow affects spacing.

    if picker.preset_cursor is not None:
        key "K_DELETE" action Show("fom_saysomething_confirm_modal",
                                    title="Delete this preset?",
                                    message=picker.preset_name,
                                    ok_button="Delete",
                                    ok_action=Function(picker.delete_preset, picker.preset_name))

## END PICKER GUI LAYOUT AND DEFINITIONS --------------------------------------------------------------------------------------------------



## CUSTOM SCREENS/MODALS ------------------------------------------------------------------------------------------------------------------

# Modal screen used for entering new preset name.
# NOTE: same as main screen refers to picker directly, in global scope.

screen fom_saysomething_preset_name_input_modal:
    if not picker.is_preset_exists(picker.preset_name):
        $ ok_action = [Play("sound", gui.activate_sound),
                       Function(picker.save_preset, picker.preset_name),
                       Hide("fom_saysomething_preset_name_input_modal")]
    else:
        $ ok_action = [Play("sound", gui.activate_sound),
                       Show("fom_saysomething_confirm_modal",
                            title=_("Overwrite this preset?"),
                            message=picker.preset_cursor,
                            ok_button=_("Overwrite"),
                            ok_action=Function(picker.save_preset, picker.preset_cursor)),
                       Hide("fom_saysomething_preset_name_input_modal")]
    $ cancel_action = [Play("sound", gui.activate_sound),
                       Hide("fom_saysomething_preset_name_input_modal")]

    # Force enable preset name value (doesn't work otherwise) on show.
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
            action ok_action

    # Allow pressing Esc to cancel.
    key "K_ESCAPE":
        action cancel_action

    frame:
        vbox:
            xmaximum 300
            xfill True

            align (0.5, 0.5)
            spacing 30

            # Title.

            text _("Save this preset as:"):
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
                textbutton _("Save"):
                    action ok_action
                    sensitive not picker.is_preset_name_empty()
                textbutton _("Cancel"):
                    action cancel_action


# Modal screen shared between confirming preset deletion and overwrite confirmation.
# NOTE: same as main screen refers to picker directly, in global scope.

screen fom_saysomething_confirm_modal(message, ok_button=_("Yes"), ok_action=Return(True), no_button=_("No"), no_action=Return(False), title=None):
    $ ok_action = [Play("sound", gui.activate_sound),
                   ok_action,
                   Hide("fom_saysomething_confirm_modal")]
    $ no_action = [Play("sound", gui.activate_sound),
                       no_action or NullAction(),
                       Hide("fom_saysomething_confirm_modal")]

    style_prefix "confirm"

    modal True
    zorder 200

    add mas_getTimeFile("gui/overlay/confirm.png")

    # Keybinds alternative to button clicks, pressing Enter will confirm
    # and Esc will cancel.

    key "K_RETURN":
        action ok_action

    key "K_ESCAPE":
        action no_action

    frame:
        vbox:
            xmaximum 650

            align (0.5, 0.5)
            spacing 30

            # Title.

            if title:
                text title:
                    style "confirm_prompt"
                    xalign 0.5

            # Text.

            text message:
                xalign 0.5
                text_align 0.5

            # Confirmation and cancellation buttons.

            hbox:
                xalign 0.5
                spacing 10

                textbutton ok_button:
                    action ok_action
                textbutton no_button:
                    action no_action

## END CUSTOM SCREENS/MODALS --------------------------------------------------------------------------------------------------------------



## CUSTOM SCROLLABLE MENU WITH SEARCH BAR -------------------------------------------------------------------------------------------------

init -10 python in _fom_saysomething_gui:

    from store import persistent

    def on_search_adjustment_range(adjustment):
        """
        Callback for presets menu search input to adjust cursor so it's
        visible to the user.

        IN:
            adjustment -> ui.adjustment:
                Adjustment that has changed.
        """

        widget = renpy.get_widget("fom_saysomething_speech_menu", "search_input", "screens")
        caret_relative_pos = 1.0
        if widget is not None:
            caret_pos = widget.caret_pos
            content_len = len(widget.content)

            if content_len > 0:
                caret_relative_pos = caret_pos / float(content_len)

        # This ensures that the caret is always visible (close enough) to the user
        # when they enter text
        adjustment.change(adjustment.range * caret_relative_pos)

    speech_menu_query = ""

    def on_search_input_change(query):
        global speech_menu_query
        speech_menu_query = query.lower()
        renpy.restart_interaction()

    def reset_search_input():
        global speech_menu_query
        speech_menu_query = ""


screen fom_saysomething_speech_menu:

    $ matching_speeches = list(filter(lambda it: _fom_saysomething_gui.speech_menu_query in it.lower(),
                                      persistent._fom_saysomething_speeches.keys()))

    on "hide" action Function(_fom_saysomething_gui.reset_search_input)

    # Speeches list menu.

    frame:
        pos (evhand.LEFT_AREA[0], evhand.LEFT_AREA[1] - 55)
        xsize evhand.RIGHT_AREA[0] - evhand.LEFT_AREA[0] + evhand.RIGHT_AREA[2]
        ysize 40

        # Text input.

        background Solid(mas_ui.TEXT_FIELD_BG)

        viewport:
            draggable False
            arrowkeys False
            mousewheel "horizontal"
            xsize 520
            ysize 38
            xadjustment ui.adjustment(ranged=_fom_saysomething_gui.on_search_adjustment_range)

            input:
                id "search_input"
                style_prefix "input"
                length 50
                xalign 0.0
                layout "nobreak"
                changed _fom_saysomething_gui.on_search_input_change

        # Hint text in search box visible if no text is entered.

        if len(_fom_saysomething_gui.speech_menu_query) == 0:
            text _("Search for a speech..."):
                text_align 0.0
                layout "nobreak"
                color "#EEEEEEB2"
                first_indent 10
                line_leading 1
                outlines []

    # List of presets.

    fixed:
        pos (evhand.LEFT_AREA[0], evhand.LEFT_AREA[1])
        xsize evhand.RIGHT_AREA[0] - evhand.LEFT_AREA[0] + evhand.RIGHT_AREA[2]
        ysize evhand.LEFT_AREA[3]

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

                    # Speech choice buttons; highlit when selected.

                    for _key in sorted(matching_speeches):
                        textbutton _key:
                            style "scrollable_menu_button"
                            xysize (530, None)
                            action Return(_key)

            null height 20

            textbutton _("Nevermind."):
                style "scrollable_menu_button"
                xsize evhand.RIGHT_AREA[0] - evhand.LEFT_AREA[0] + evhand.RIGHT_AREA[2]
                action Return(False)

        # Scrollbar used by list of speeches above.

        bar:
            style "classroom_vscrollbar"
            value YScrollValue("viewport")
            xalign evhand.LEFT_XALIGN / 2 + 0.005

## END CUSTOM SCROLLABLE MENU WITH SEARCH BAR ---------------------------------------------------------------------------------------------



## PAUSE SCREEN IMPLEMENTATION ------------------------------------------------------------------------------------------------------------

# We're using custom-made "pause" (which is basically just a screen with timer
# and key handlers) because Ren'Py provides no ability to use pause statement
# and let player click and skip it. This screen does what we need pause to do,
# when called with 'call screen', it waits for the specified duration and
# returns, optionally can be interrupted by pressing any key from 'dismiss'
# key mapping (e.g. left click, enter, space, etc.)
screen fom_skippable_pause(duration=1.0):

    # NOTE: For reference, here's zorders of other screens used in MAS.
    # When deciding zorder, these were taken into account (must be able to click
    # other things on the screen when pausing.)
    # - Music selector  zorder: 200 modal
    # - Textbox screen  zorder: 60  not modal
    # - Hotkey buttons  zorder: 50  not modal
    # - Calendar screen zorder: 6   not modal

    # Since out pause screen must be clickable, but must not interfere with
    # other UI elements, let it have the lowest z-order.
    zorder -100

    # Wait for timer and return True, since pause went uninterrupted.
    timer duration action Return(True)

    # Add an invisible button to react on clicking.
    # -- Actually, we don't need that anymore. `key` section below handles it.
    # button action Return(False):
    #     xsize config.screen_width
    #     ysize config.screen_height

    # Listen to dismiss keypresses and return False, since pause
    # was interrupted by player keypress.
    for _key in config.keymap["dismiss"]:
        key _key action Return(False)

## END PAUSE SCREEN IMPLEMENTATION --------------------------------------------------------------------------------------------------------