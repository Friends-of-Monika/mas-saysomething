init 101 python in _fom_saysomething:

    import os, re
    from store import mas_submod_utils

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

        if not os.path.exists(os.path.join(_dir, suggested_name)):
            return suggested_name

        count = 1
        while True:
            sn_name, sn_ext = _get_split_name_ext(suggested_name)
            new_name = sn_name + " (" + str(count) + ")." + sn_ext
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

        uniq_name = _get_unique_name(SPEECHES_DIR_PATH, DEFAULT_SCRIPT_NAME + ".rpy.txt")
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

        text = text.replace("\\", "\\\\")
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

        lines = _str.splitlines()
        if len(lines) < 2:
            return _str

        pat = re.compile(r"^(\s*)[^\s]*")
        indent = len(pat.findall(lines[1])[0])
        lines.pop(0)

        for i in range(len(lines)):
            lines[i] = lines[i][indent:]
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
    """))

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

        return re.sub("[^a-zA-Z0-9_]", "_", name).strip("_")

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

        def get_dialog_line(poses, pos, text):
            return ('m {0} "{1}"'.format(get_sprite_code(poses),
                                         _get_escaped_text(text)))

        lines = list()
        for poses, pos, text in session:
            lines.append("    " + get_dialog_line(poses, pos, text))

        if not os.path.exists(SPEECHES_DIR_PATH):
            os.makedirs(SPEECHES_DIR_PATH)
        path = os.path.join(SPEECHES_DIR_PATH, name + ".rpy.txt")

        with open(path, "w") as f:
            f.write(DEFAULT_SCRIPT_FORMAT.format(
                DEFAULT_EVENTLABEL_FORMAT.format(_get_sane_event_label(name)),
                DEFAULT_CATEGORY,
                _get_escaped_text(name),
                "\n".join(lines),
                GENERATOR_IDENT))

        return path