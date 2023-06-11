init 101 python in _fom_saysomething:

    import os, re
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


    def _get_escaped_text(text):
        """
        Escapes double quotes and backslashes in the given text. Useful for
        when it is necessary to inject a possibly unsafe string in a RenPy
        code string inside quotes.

        IN:
            text -> str:
                String to escape backslashes and double quotes in.

        OUT:
            str:
                Escaped string.
        """

        # Escape backslashes (\ -> \\)
        text = text.replace("\\", "\\\\")
        # Escape quotes with backslashes (" -> \")
        text = text.replace("\"", "\\\"")

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
    DEFAULT_SCRIPT_FORMAT = _process_indent(_("""
        ## WARNING! WARNING! WARNING! WARNING! WARNING! WARNING! WARNING!
        ## This isn't a complete topic, it actually needs adjustment!
        ## Before you simply drop this into game folder, take your time
        ## to read and understand what's inside this script file, please.
        ## IDEALLY you'd only use this as a sketch or template at best;
        ## if it works for you, please do so, if not - please be CAREFUL.

        ## First of, you'll have to adjust this header:
        init 5 python:
            addEvent(Event(
                persistent.event_database,

                ## Adjust this to your own preference:
                eventlabel="{0}",

                ## This, too:
                category=["{1}"],

                ## And this:
                prompt="{2}",

                ## Pick JUST ONE of them and uncomment (remove leading #):
                #random=True,
                #pool=True
            ), code="EVE")

        ## Then, MAKE SURE the label name AFTER the world 'label' matches
        ## the event label you've set in 'eventlabel=' bit up there:
        label {0}:
            ## And FINALLY, here is the actual code generated from the speech
            ## you've asked your Monika to say:
        {3}

            ## You may want to adjust this too, but GENERALLY you don't have to.
            ## If in your speech Monika says something like 'I love you', you
            ## may want to change this to this (uncomment the next line, remove
            ## the leading #, MAKE SURE there are EXACTLY FOUR SPACES before it):
            #return "love"

            ## If you have uncommented 'return' above, simply remove this line.
            ## If not, LEAVE IT AS IS! It's critical to have AT LEAST ONE return.
            return

        ## *** THIS SCRIPT WAS GENERATED BY: {4}
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
                text = markdown.render(_get_escaped_text(text))
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
            # another or when switching from non-leaning to leaning
            leaning = False
            prev_pos = None

            # Begin generation of text/transition lines
            for poses, pos, text in session:
                # Save state if not memorized yet, append transition line
                # if position has changed (e.g. so that we don't have a bunch
                # of unnecessary 'show monika ...' lines.)
                if prev_pos is None:
                    prev_pos = pos
                elif prev_pos != pos:
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

        # Write by filling template.
        with open(path, "w") as f:
            f.write(DEFAULT_SCRIPT_FORMAT.format(
                DEFAULT_EVENTLABEL_FORMAT.format(_get_sane_event_label(name)),
                DEFAULT_CATEGORY,
                _get_escaped_text(name),
                get_dialogue_lines(),
                GENERATOR_IDENT))

        # Return newly created script path
        return path