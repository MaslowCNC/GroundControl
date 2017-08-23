'''A round menu that appears on a long touch
'''
from kivy.uix.widget                             import Widget
from kivy.uix.label                              import Label
from kivy.uix.behaviors                          import ButtonBehavior
from kivy.lang                                   import Builder
from kivy.clock                                  import Clock
from kivy.animation                              import Animation
from kivy.properties                             import (
    NumericProperty, ListProperty, ObjectProperty, DictProperty)
from kivy.app                                    import App

from functools                                   import partial
from copy                                        import copy


def dist((x1, y1), (x2, y2)):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 5


class ModernMenuLabel(ButtonBehavior, Label):
    index = NumericProperty(0)
    radius = NumericProperty(100)
    siblings = NumericProperty(1)
    callback = ObjectProperty(None)

    def on_parent(self, *args):
        if self.parent:
            self.parent.bind(children=self.update_siblings)

    def update_siblings(self, *args):
        if self.parent:
            self.siblings = max(0, len(self.parent.children))
        else:
            self.siblings = 1


class ModernMenu(Widget):
    radius = NumericProperty(50)
    circle_width = NumericProperty(5)
    line_width = NumericProperty(2)
    color = ListProperty([.3, .3, .3, 1])
    circle_progress = NumericProperty(0)
    creation_direction = NumericProperty(1)
    creation_timeout = NumericProperty(1)
    choices = ListProperty([])
    item_cls = ObjectProperty(ModernMenuLabel)
    item_args = DictProperty({'opacity': 0})
    animation = ObjectProperty(Animation(opacity=1, d=.5))
    choices_history = ListProperty([])

    def start_display(self, touch):
        touch.grab(self)
        a = Animation(circle_progress=1, d=self.creation_timeout)
        a.bind(on_complete=self.open_menu)
        touch.ud['animation'] = a
        a.start(self)

    def open_menu(self, *args):
        self.clear_widgets()
        for i in self.choices:
            kwargs = copy(self.item_args)
            kwargs.update(i)
            ml = self.item_cls(**kwargs)
            self.animation.start(ml)
            self.add_widget(ml)

    def open_submenu(self, choices, *args):
        self.choices_history.append(self.choices)
        self.choices = choices
        self.open_menu()

    def back(self, *args):
        self.choices = self.choices_history.pop()
        self.open_menu()

    def on_touch_move(self, touch, *args):
        if (
            touch.grab_current == self and
            dist(touch.pos, touch.opos) > self.radius and
            self.parent and
            self.circle_progress < 1
        ):
            self.parent.remove_widget(self)

        return super(ModernMenu, self).on_touch_move(touch, *args)

    def on_touch_up(self, touch, *args):
        print "other on touch up"
        if (
            touch.grab_current == self and
            self.parent and
            self.circle_progress < 1
        ):
            self.parent.remove_widget(self)
        return super(ModernMenu, self).on_touch_up(touch, *args)

    def dismiss(self):
        a = Animation(opacity=0)
        a.bind(on_complete=self._remove)
        a.start(self)

    def _remove(self, *args):
        if self.parent:
            self.parent.remove_widget(self)


class MenuSpawner(Widget):
    timeout = NumericProperty(0.1)
    menu_cls = ObjectProperty(ModernMenu)
    cancel_distance = NumericProperty(10)
    menu_args = DictProperty({})

    def on_touch_down(self, touch, *args):
        print "touch down"
        if touch.button == 'scrolldown' or touch.button == 'scrollup':
            #Ignore scroll button
            pass
        else:
            t = partial(self.display_menu, touch)
            touch.ud['menu_timeout'] = t
            Clock.schedule_once(t, self.timeout)
            return super(MenuSpawner, self).on_touch_down(touch, *args)

    def on_touch_move(self, touch, *args):
        if (
            touch.ud['menu_timeout'] and
            dist(touch.pos, touch.opos) > self.cancel_distance
        ):
            Clock.unschedule(touch.ud['menu_timeout'])
        return super(MenuSpawner, self).on_touch_move(touch, *args)

    def on_touch_up(self, touch, *args):
        print "on touch up"
        if touch.ud.get('menu_timeout'):
            Clock.unschedule(touch.ud['menu_timeout'])
        return super(MenuSpawner, self).on_touch_up(touch, *args)

    def display_menu(self, touch, dt):
        
        shiftedPos = ((touch.pos[0] - self.parent.pos[0])/self.parent.scale, (touch.pos[1] - self.parent.pos[1])/self.parent.scale)
        
        menu = self.menu_cls(center=shiftedPos, **self.menu_args)
        self.add_widget(menu)
        menu.start_display(touch)