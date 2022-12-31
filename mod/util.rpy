# util.rpy contains various utility methods, classes, etc. used in Say Something
# submod codebase.
#
# This file is part of Say Something (see link below):
# https://github.com/friends-of-monika/mas-saysomething

init python in _fom_saysomething:
    def set_eyes_lock(self, exp, lock):
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