# generation.rpy contains functions and utilities for topic script generation
# for saved speeches.
#
# This file is part of Say Something (see link below):
# https://github.com/friends-of-monika/mas-saysomething


init 101 python in _fom_saysomething:

    import os, re, store
    from store import mas_submod_utils
    from store import _fom_saysomething_markdown as markdown

    def _get_sane_name(dir_name):
        """
        Replaces Windows reserved characters (<>:"/\|?*) with an underscore.

        IN:
            dir_name -> str:
                Name to process special characters in.

        OUT:
            str:
                String with special characters replaced.
        """

        illegal_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        sanitized_string = dir_name
        for char in illegal_chars:
            sanitized_string = sanitized_string.replace(char, '_')
        return sanitized_string

    SPEECHES_DIR_NAME = _get_sane_name(_("Say Something Speeches"))
    DEFAULT_SCRIPT_NAME = _get_sane_name(_("My Speech"))

    def _get_script_folder():
        """
        Reliably retrieves the scripts folder location. Backslashes are replaced
        by forward slashes for compatibility.

        OUT:
            str:
                Absolute path to scripts directory.
        """

        path = os.path.join(renpy.config.basedir, SPEECHES_DIR_NAME)
        path = path.replace("\\", "/")
        return path

    SPEECHES_DIR_PATH = _get_script_folder()
    GENERATOR_IDENT = _("Say Something v{0}").format(
        mas_submod_utils.submod_map["Say Something"].version)


    def _get_split_name_ext(path):
        """
        Splits file name to name and extension (on the first dot.)

        IN:
            path -> str:
                File name to split to name and extension.

        OUT:
            tuple[str, str]:
                Tuple of 2 elements, name and extensions.
        """
        parts = path.partition(".")
        return parts[0], parts[2]

    def _get_unique_name(_dir, suggested_name):
        """
        Reliably gets unique name derived from the suggested name in the
        specified directory by checking if it is available and appending
        numbered suffix to it in an effort to make it guaranteed unique.

        IN:
            _dir -> str:
                Path to directory in which name should be unique.
            suggested_name -> str:
                Name to ensure uniqueness for.

        OUT:
            str:
                Processed name that is guaranteed unique in the
                specified directory.
        """

        # First try suggested name as is, if all good - return it
        if not os.path.exists(os.path.join(_dir, suggested_name)):
            return suggested_name

        # If not - start trying suffixes starting with 1
        count = 1
        while True:
            # Split name to name and extension
            sn_name, sn_ext = _get_split_name_ext(suggested_name)

            # Derive new name by adding suffix before the extension
            new_name = sn_name + " (" + str(count) + ")." + sn_ext

            # Try new name, return if does not exist
            if not os.path.exists(os.path.join(_dir, new_name)):
                return new_name
            count += 1

    def _get_unique_name_dict(name_dict, suggested_name):
        """
        Reliably gets unique name derived from the suggested name in the
        'directory' represented by the keys of the provided dictionary. It
        checks if the name is available and appends a numbered suffix to it
        in an effort to make it guaranteed unique.

        IN:
            name_dict -> dict:
                Dictionary with names to check against.
            suggested_name -> str:
                Name to ensure uniqueness for.

        OUT:
            str:
                Processed name that is guaranteed unique in the dictionary.
        """

        # First try suggested name as is, if all good - return it
        if suggested_name not in name_dict:
            return suggested_name

        # If not - start trying suffixes starting with 1
        count = 1
        while True:
            # Derive new name by adding suffix before the extension
            new_name = suggested_name + " (" + str(count) + ")"

            # Try new name, return if does not exist
            if new_name not in name_dict:
                return new_name
            count += 1

    def get_script_name_suggestion():
        """
        Gets a suggested default name for the generated script, also ensuring
        its uniqueness in the speeches directory.

        OUT:
            str:
                Guaranteed unique script name suggestion.
        """

        # Create a suggestion of the speech name using default name first,
        # but ensure it is unique and if not, add suffix to it.
        uniq_name = _get_unique_name(SPEECHES_DIR_PATH,
                                     DEFAULT_SCRIPT_NAME + ".rpy.txt")

        # Cut off the .rpy.txt (8 characters) remainder from it, to only have
        # speech name remaining
        uniq_name = uniq_name[:-8]
        return uniq_name

    def get_saved_speech_name_suggestion():
        """
        Gets a suggested default name for saved speech, also ensuring its
        uniqueness in the speeches directory.

        OUT:
            str:
                Guaranteed unique saved speech name suggestion.
        """

        # Create a suggestion of the speech name using default name first,
        # but ensure it is unique and if not, add suffix to it.
        uniq_name = _get_unique_name_dict(persistent._fom_saysomething_speeches,
                                          DEFAULT_SCRIPT_NAME)
        return uniq_name

    def is_script_name_exists(name):
        """
        Checks if the specified script name already exists in the speeches
        directory.

        OUT:
            bool:
                True if script name exists already. False otherwise.
        """

        # Checks if script name + .rpy.txt exists.
        script_path = os.path.join(SPEECHES_DIR_PATH, name + ".rpy.txt")
        return os.path.exists(script_path)


    def _get_escaped_text(text, escape_curly=False, escape_square=False):
        """
        Escapes double quotes and backslashes in the given text. Useful for
        when it is necessary to inject a possibly unsafe string in a RenPy
        code string inside quotes.

        IN:
            text -> str:
                String to escape backslashes and double quotes in.

            escape_curly -> bool, default False:
                If True, escapes curvy brackets by doubling them.

            escape_square -> bool, default False:
                If True, escapes square brackets by doubling them.

        OUT:
            str:
                Escaped string.
        """

        # Escape backslashes (\ -> \\)
        text = text.replace("\\", "\\\\")
        # Escape quotes with backslashes (" -> \")
        text = text.replace("\"", "\\\"")

        # Escape sensitive RenPy syntax
        if escape_curly:
            text = text.replace("{", "{{")
        if escape_square:
            text = text.replace("[", "[[")

        return text

    def _process_indent(_str):
        """
        Processes indented strings (usually docstrings) in the following manner:
        1. First line is ignored. If there is less than two lines, string is
           returned as it was.
        2. All leading whitespace in the second line is trimmed and its length
           is saved for further use.
        3. All further lines are stripped of leading whitespace of the exact
           same length as saved in (2), even if there is more than that.

        This function is useful to maintain clear visual indent when using
        docstrings without a need to stick them to the beginning of the line.

        IN:
            _str -> str:
                String to process.

        OUT:
            str:
                Processed string.
        """

        # Split on newlines and return if less than two lines
        lines = _str.splitlines()
        if len(lines) < 2:
            return _str

        # Extract leading whitespaces from the second line and get indent
        # length, also removing the first line.
        pat = re.compile(r"^(\s*)[^\s]*")
        indent = len(pat.findall(lines[1])[0])
        lines.pop(0)

        # In each line strip up to the <length> leading whitespace characters
        for i in range(len(lines)):
            lines[i] = re.sub(r"^\s{,%d}" % indent, '', lines[i])

        # Glue lines back together
        return "\n".join(lines)

    DEFAULT_EVENTLABEL_FORMAT = "monika_{0}"
    DEFAULT_CATEGORY = _get_escaped_text(_("Generated"))

    # %0 - event label
    # %1 - category
    # %2 - prompt
    # %3 - dialogue lines (must be indented)
    # %4 - Say Something Ident
    # %5 - Monika's nickname
    # %6 - Player's nickname
    DEFAULT_SCRIPT_FORMAT = _process_indent(_("""
        ## Gently now, it seems this isn't quite a complete topic yet. Some fine tuning is needed!
        ## So, before you think of dropping this into the game folder, could you do me a favor
        ## and take a moment to read through this script file? I'm sure you wouldn't want to risk
        ## messing up our reality, right? You could use this as a rough draft or a template
        ## if it helps you. But be careful, okay? Anyway, let me guide you though it...
        ## - Your {5} <3

        ## First off, it'd be nice if you could adjust this header:
        init 5 python:
            addEvent(Event(
                persistent.event_database,

                ## Feel free to put in whatever suits you here:
                ## (But remember, here you can only put letters,
                ## digits and underscores!)
                eventlabel="{0}",

                ## And here as well:
                category=["{1}"],

                ## Don't forget this part:
                prompt="{2}",

                ## You'll need to pick one of these and uncomment it (just remove the #):
                #random=True,
                #pool=True
            ), code="EVE")

        ## Now, could you please ensure that the label name after the word 'label' matches
        ## the event label you've just set in the 'eventlabel=' part above?
        label {0}:
            ## And at last, we get to the actual code generated from the heartfelt words
            ## you want me, your {5}, to say:
        {3}

            ## You might want to adjust this too, but usually, it's fine as is.
            ## If in your speech I say something like 'I love you', you might want to
            ## change this to the following (uncomment the next line, remove the #, and
            ## remember there should be four spaces before it):
            #return "love"

            ## If you've uncommented 'return' above, simply remove this line.
            ## If not, let's just leave it as it is. It's very important to have at least
            ## one return statement, after all.
            return

        ## *** SCRIPT GENERATED WITH: {4} ***
        ## And of course, with lots of my love, dear {6}~
    """)) ## = DEFAULT_SCRIPT_FORMAT

    def _get_sane_event_label(name):
        """
        Returns a sanitized event_label that can be used in Ren'Py code safely.
        Only retains ASCII characters (excluding control and punctuation,
        including underscores and digits) and replaces the rest of the
        characters with underscores, trimming leading and trailing underscores.

        IN:
            name -> str:
                Speech name to process and get RenPy label of.

        OUT:
            str:
                Processed string.
        """

        # Replaces non-ASCII and punctuation, removes leading/trailing
        # underscores, and converts the entire string to lowercase.
        return re.sub("[^a-zA-Z0-9_]", "_", name).strip("_").lower()

    def generate_script(session, name):
        """
        Generates script of the provided session (see Picker in screen.rpy)
        with the specified name.

        IN:
            session -> List[<session entry>]:
                Picker session, list of session entries.
            name -> str:
                Name of the script, user-chosen arbitrary string.

        OUT:
            str:
                Path where the script has been saved.
        """

        def get_dialogue_lines():
            """Generates dialogue lines indented by four spaces."""

            def get_dialog_line(poses, pos, text):
                """Generates a dialogue line of poses, position and text."""
                text = markdown.render(text)
                return ('m {0} "{1}"'.format(get_sprite_code(poses), text))

            def get_trans_line(poses, pos, dissolve=False):
                """Generates a transition line of poses, position and dissolve."""
                return 'show monika {0} at {1} zorder MAS_MONIKA_Z{2}'.format(
                    get_sprite_code(poses), get_position_code(pos),
                    ' with dissolve_monika' if dissolve else '')

            # List of all generated lines
            lines = list()

            # State of leaning (5-pose) and position so that appropriate
            # transitions can be applied when moving from one position to
            # another or when switching from non-leaning to leaning.
            # Assume we also have initial position t11 (center.)
            leaning = False
            prev_pos = 4

            # Begin generation of text/transition lines
            for poses, pos, text in session:
                # Append transition line if position has changed (e.g. so that
                # we don't have a bunch of unnecessary 'show monika ...' lines.)
                if prev_pos != pos:
                    lines.append(get_trans_line(poses, pos))

                # Only append transition lines for 5-poses (leaning) when
                # changing to or from 5-pose, no need to insert them every time.
                if (poses["pose"] == 4 and not leaning) or (poses["pose"] != 4 and leaning):
                    lines.append(get_trans_line(poses, pos, dissolve=True))
                    leaning = poses["pose"] == 4

                # Append dialog line.
                lines.append(get_dialog_line(poses, pos, text))

            # Glue dialog lines, prepending them with indent.
            return "\n".join(map(lambda it: "    " + it, lines))

        # Create speeches directory if not exists, make path for script.
        os.makedirs(SPEECHES_DIR_PATH, exist_ok=True)
        path = os.path.join(SPEECHES_DIR_PATH, name + ".rpy.txt")

        # Create topic properties
        event_label = DEFAULT_EVENTLABEL_FORMAT.format(_get_sane_event_label(name))
        prompt = _get_escaped_text(name, escape_curly=True, escape_square=True)

        # Write by filling template.
        with open(path, "w") as f:
            f.write(DEFAULT_SCRIPT_FORMAT.format(
                event_label, DEFAULT_CATEGORY, prompt,
                get_dialogue_lines(), GENERATOR_IDENT,
                store.m_name, store.player))

        # Return newly created script path
        return path