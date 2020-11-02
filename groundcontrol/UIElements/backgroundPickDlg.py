from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
from kivy.vector import Vector


class BackgroundPickDlg(GridLayout, MakesmithInitFuncs):
    instructionText = StringProperty("Drag bounding box to frame edges")
    texture = ObjectProperty(None)
    tex_coords = ListProperty([0, 0, 1, 0, 1, 1, 0, 1])
    tex_selection = ListProperty([0, 0, 100, 0, 100, 100, 0, 100])

    def __init__(self, data, **kwargs):
        super(BackgroundPickDlg, self).__init__(**kwargs)
        self.data = data
        # Load the texture
        self.texture = self.data.backgroundTexture
        # Window is not set up yet, wait for size.update
        self.imWidg.bind(size=self.update)
        self.update()

    def update(self, *args):
        if self.imWidg.size[0] is not 100 and self.imWidg.size[1] is not 100:
            # Widget is stable, update the textures bounds
            self.w, self.h = self.imWidg.size
            self.coeff_size = [self.w, self.h, self.w, self.h,
                               self.w, self.h, self.w, self.h]
            # Place selection box
            self.tex_selection = [self.w * 0.2, self.h * 0.3,
                                  self.w * 0.9, self.h * 0.3,
                                  self.w * 0.9, self.h * 0.9,
                                  self.w * 0.2, self.h * 0.9]
            # Why??!!...
            self.resize_texture()
            self.reset_image()
        else:
            pass  # Wait for widget to resize properly

    def reset_image(self):
        self.tex_coords = [0, 0, 1, 0, 1, 1, 0, 1]

    def resize_texture(self):
        coeffs = []
        padOffx, padOffy = self.imWidg.pos
        i = 0
        for (p, s) in zip(self.coeff_size, self.tex_selection):
            if i % 2:  # y coord
                if p is not 0:
                    coeffs.append(float(s - padOffy) / float(p))
                else:
                    coeffs.append(0.0 - padOffy)
            else:  # x coord
                if p is not 0:
                    coeffs.append(float(s - padOffx) / float(p))
                else:
                    coeffs.append(0.0 - padOffx)
            i += 1
        self.tex_coords = coeffs

    def accept_texture(self):
        self.accepted = True
        self.close(self)

    def on_touch_down(self, touch):
        for i in range(4):
            x, y = self.tex_selection[i*2:i*2+2]
            if Vector(x - touch.x, y - touch.y).length() < 10:
                touch.grab(self)
                touch.ud['tex'] = i
                return True

        return super(BackgroundPickDlg, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return super(BackgroundPickDlg, self).on_touch_move(touch)

        tex = touch.ud.get('tex')

        if tex is not None:
            self.tex_selection[tex * 2] = touch.x
            self.tex_selection[tex * 2 + 1] = touch.y

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
        else:
            return super(BackgroundPickDlg, self).on_touch_up(touch)
