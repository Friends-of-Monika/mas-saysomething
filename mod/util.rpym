# util.rpy contains various utility methods, classes, etc. used in Say Something
# submod codebase.
#
# This file is part of Say Something (see link below):
# https://github.com/friends-of-monika/mas-saysomething

init -200 python in _fom_saysomething:

    import pygame
    from collections import OrderedDict

    def set_eyes_lock(exp, lock):
        """
        Locks or unlocks winking (closing then opening left/right eye for
        one second) and blinking (quickly closing and opening both eyes
        randomly).

        IN:
            exp -> str:
                Expression code for which winking/blinking has to be locked.
                Unfortunately due to MAS implementation of this mechanism,
                only can be applied to certain expression.

            lock -> bool:
                True to lock, False to unlock. Locking when locked and
                unlocking when not locked has no effect.
        """

        disp = renpy.display.image.images[("monika", exp)]

        if lock:
            if isinstance(disp, MASMoniBlinkTransform):
                disp.transform_map[MASMoniBlinkTransform.STEP_START].old_widget = disp.open_eyes_img
                disp.transform_map[MASMoniBlinkTransform.STEP_END].new_widget = disp.open_eyes_img
                disp.transform_map[MASMoniBlinkTransform.STEP_DB_START].old_widget = disp.open_eyes_img
                disp.transform_map[MASMoniBlinkTransform.STEP_DB_END].new_widget = disp.open_eyes_img

            elif isinstance(disp, MASMoniWinkTransform):
                disp.wink_into_open_eyes_dis.new_widget = disp.wink_img

        else:
            if isinstance(disp, MASMoniBlinkTransform):
                disp.transform_map[MASMoniBlinkTransform.STEP_START].old_widget = disp.closed_eyes_img
                disp.transform_map[MASMoniBlinkTransform.STEP_END].new_widget = disp.closed_eyes_img
                disp.transform_map[MASMoniBlinkTransform.STEP_DB_START].old_widget = disp.closed_eyes_img
                disp.transform_map[MASMoniBlinkTransform.STEP_DB_END].new_widget = disp.closed_eyes_img

            elif isinstance(disp, MASMoniWinkTransform):
                disp.wink_into_open_eyes_dis.new_widget = disp.open_eyes_img

    def is_renpy_image_cached(exp):
        """
        Checks if a specified image is present in the Ren'Py image cache.

        IN:
            exp -> str:
                Expression code of the image to be checked. The image is identified
                by a tuple ("monika", exp).

        OUT:
            bool:
                True if the image is present in the cache, False otherwise.
        """
        return ("monika", exp) in renpy.display.image.images

    def remove_renpy_images_bulk(exps):
        """
        Removes multiple images from the Ren'Py image cache in a single call.

        IN:
            exps -> list of str:
                A list of expression codes for the images to be removed from the
                cache. Each image is identified by a tuple ("monika", exp).
        """

        for exp in exps:
            remove_renpy_image(exp)

    def remove_renpy_image(exp):
        """
        Removes a specified image from the Ren'Py image cache. No-op if the
        spritecode does not exist in Ren'Py cache. Static images
        (i.e. "1eua_static")

        IN:
            exp -> str:
                Expression code of the image to be removed from the cache. The
                image is identified by a tuple ("monika", exp).
        """

        for cur_exp in [exp, exp + "_static"]:
            tup = ("monika", cur_exp)
            if tup in renpy.display.image.images:
                del renpy.display.image.images[tup]

    def get_friendly_key(action):
        """
        Retrieves user-friendly key combination for a given action.
        If keymap is not configured for this action, returns None.

        OUT:
            str:
                User-friendly key combination.

            None:
                If keymap is not configured.
        """

        # May be not set or be empty here.
        key = renpy.config.keymap.get(action)
        if key is None or len(key) == 0:
            return None

        # Take first key.
        key = key[0]

        # May have PyGame K_-constant.
        if "K_" in key:
            # Extract constant and check if it exists.
            sym = key[key.index("K_"):]
            if not hasattr(pygame, sym):
                return None

            # Fetch name of key from PyGame by constant and extract modifiers.
            sym = pygame.key.name(getattr(pygame, sym)).decode()
            mod = key[:key.index("K_") - 1].split("_")

        else:
            # Split key name into keysym and modifiers.
            sym = key.split("_")[-1]
            mod = key.split("_")[:-1]

        # Ignore noshift.
        if "noshift" in mod:
            mod.remove("noshift")

        # Construct combination of keysym and optionally modifiers, all
        # converted to title case.
        name = sym.title()
        if len(mod) > 0:
            name = "+".join(map(str.title, mod)) + "+" + name

        return name

    def get_script_file(fallback=None, relative=False):
        """
        Uses internal Ren'Py function renpy.get_filename_line() to locate
        current script file and get its location, accounting for potential
        erroneous outputs produced by this function.
        IN:
            fallback -> str, default None:
                Path to use as a fallback in case this function fails to find
                appropriate current script location.
            relative -> bool, default False:
                True if function should omit "game/" from detected path to make
                it relative to "game/" folder.
        OUT:
            str:
                Relative (to DDLC directory) path to the .rpy script file that
                is currently being executed, or fallback value (or None if not
                provided) if this function is unable to find appropriate path.
        RAISES:
            ValueError:
                If fallback does not start with "game/" and relative is set to
                False.
        NOTE:
            For consistency between platforms (and further usage in Ren'Py
            functions and related things) paths returned always have "/" as
            folder separator, even on Windows.
            Also note that even though it is possible for script file to be
            located not in "game/" folder for somewhere else, this function
            assumes it is located in "game/" and uses this assumption in its
            path correction logic.
            Proper functionality of this function cannot be guaranteed if called
            from eval() and alike dynamic code execution contexts.
        """

        if (
            fallback is not None and not fallback.startswith("game/") and
            not relative
        ):
            raise ValueError(
                "fallback path does not start with \"game/\" "
                "and relative is not True"
            )

        import os

        # Use renpy's developer function get_filename_line() to get current
        # script location. WARNING: THIS IS EXTREMELY UNSTABLE, THE FOLLOWING
        # CODE IS THE WORKAROUND THAT MAKES IT SOMEWHAT RELIABLE! Also replace
        # Windows \ (backslash) folder separators with / (slash) character
        # for consistency.
        path = renpy.get_filename_line()[0].replace("\\", "/")
        if os.path.isabs(path):
            # Returned path may be absolute, relativize it.
            path = os.path.relpath(path, renpy.config.renpy_base)

        # Split current file path into components. Our strategy here:
        # 1. Get path components.
        # 2. Check if path starts with game/ folder.
        # 3. While it does not, drop first i+1 (initially i=0) parts from it
        #    and prepend it with game/.
        # 4a. If new path from 3. exists, we most likely have got the right path.
        # 4b. If new path from 3. doesn't exist, increment i by 1 and drop more
        #     path components from the original path and repeat 3.
        parts = path.split("/")  # (1.)
        if parts[0] != "game":  # (2.)
            for n in range(1, len(parts)):  # (3.)
                parts_proc = parts[n:]
                parts_proc.insert(0, "game")

                rel_path = "/".join(parts_proc)
                if os.path.exists(os.path.join(renpy.config.renpy_base, rel_path)):
                    result = rel_path.replace("\\", "/")  # (4a.)
                    if relative:
                        # Omit "game/" prefix (5 chars.)
                        return result[5:]
                    return result

                # else (4b.)

            if fallback is not None and relative:
                return fallback[5:]  # Omit game/ prefix, its presence is checked above.
            return fallback.replace("\\", "/") if fallback is not None else None

        else:
            if relative:
                # Simply remove leading "game" item frm path parts.
                parts.pop(0)
            return "/".join(parts)

    def set_mas_gui_visible(visible):
        """
        Shows or hides MAS GUI (left buttons and quick menu.)

        IN:
            visible -> bool:
                True to show, False to hide.
        """

        store.quick_menu = visible
        if visible:
            store.HKBShowButtons()
        else:
            store.HKBHideButtons()

    class MoniSpriteCache(object):
        """
        Simple OrderedDict-based LRU cache for Monika sprites. When capacity
        is reached, oldest sprites get removed from both this cache and Ren'Py
        images list.
        """

        def __init__(self, capacity):
            """
            Creates MoniSpriteCache with given capacity.

            IN:
                capacity -> int:
                    Capacity of this cache.
            """

            self.cache = OrderedDict()
            self.capacity = capacity

        def add_sprite(self, sprite):
            """
            Adds sprite code to cache. NOTE: in order NOT to accidentally
            release and remove EXISTING sprite that is already loaded, caller
            must check if it is already in Ren'Py cache itself!

            If added sprite caused excess count of cache contents, oldest
            sprite is removed both from cache and Ren'Py images list.

            IN:
                sprite -> str:
                    Sprite code to add to cache.
            """

            if sprite in self.cache:
                self.cache.move_to_end(sprite)

            self.cache[sprite] = None
            if len(self.cache) > self.capacity:
                exp, _ = self.cache.popitem(last=False)
                remove_renpy_image(exp)

        def release_all(self):
            """
            Removes all images from this cache and from Ren'Py images list.
            """

            remove_renpy_images_bulk(list(self.cache.keys()))
            self.cache.clear()