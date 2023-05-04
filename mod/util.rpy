# util.rpy contains various utility methods, classes, etc. used in Say Something
# submod codebase.
#
# This file is part of Say Something (see link below):
# https://github.com/friends-of-monika/mas-saysomething

init python in _fom_saysomething:
    import pygame

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

    def get_screenshot_key():
        """
        Retrieves user-friendly key combination for a screenshot.
        If keymap is not configured for screenshots, returns None.

        OUT:
            str:
                User-friendly key combination.

            None:
                If keymap is not configured for taking screenshots.
        """

        # May be not set or be empty here.
        key = renpy.config.keymap.get("screenshot")
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