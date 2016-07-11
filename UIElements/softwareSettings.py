from kivy.uix.settings                import SettingsWithSpinner


# This JSON defines entries we want to appear in our App configuration screen
json = '''
[
    {
        "type": "string",
        "title": "Label caption",
        "desc": "Choose the text that appears in the label",
        "section": "My Label",
        "key": "text"
    },
    {
        "type": "numeric",
        "title": "Label font size",
        "desc": "Choose the font size the label",
        "section": "My Label",
        "key": "font_size"
    }
]
'''


class SoftwareSettings(SettingsWithSpinner):
    
    def build_config(self, config):
        """
        Set the default values for the configs sections.
        """
        config.setdefaults('My Label', {'text': 'Hello', 'font_size': 20})

    def build_settings(self, settings):
        """
        Add our custom section to the default configuration object.
        """
        # We use the string defined above for our JSON, but it could also be
        # loaded from a file as follows:
        #     settings.add_json_panel('My Label', self.config, 'settings.json')
        settings.add_json_panel('My Label', self.config, data=json)

    def on_config_change(self, config, section, key, value):
        """
        Respond to changes in the configuration.
        """
        Logger.info("main.py: App.on_config_change: {0}, {1}, {2}, {3}".format(
            config, section, key, value))

        if section == "My Label":
            if key == "text":
                self.root.ids.label.text = value
            elif key == 'font_size':
                self.root.ids.label.font_size = float(value)

    def close_settings(self, settings):
        """
        The settings panel has been closed.
        """
        Logger.info("main.py: App.close_settings: {0}".format(settings))
        super(MyApp, self).close_settings(settings)
