#!/usr/bin/env python3

import argparse
import concurrent.futures
import configparser
import datetime
import importlib
import logging
import pathlib
import shlex
import subprocess
import sys
import threading

from asciimatics import (
    widgets,
    scene,
    screen,
    exceptions,
)

import footrecon
from footrecon.core.logs import logger


class App:

    def __init__(self):
        self.screen = None
        self.executor = None
        self.headless = False
        self.stop_event = threading.Event()
        self.tasks = list()
        self.data = dict()
        self.data['modules'] = dict()

    def class_import(self, path):
        module_path, _, cls_name = path.rpartition('.')
        path_module = importlib.import_module(module_path)
        cls_obj = getattr(path_module, cls_name)
        return cls_obj

    def load_config(self, path):
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read(path)
        for module_path, enabled in config.items('modules'):
            mod_cls = self.class_import(module_path)
            enabled = bool(int(enabled))
            module_init = {
                'enabled': enabled,
                'module_path': module_path,
            }
            if module_path in config.sections():
                module_init.update(config.items(module_path))
            self.data['modules'][module_path] = mod_cls(self.stop_event, **module_init)
            if enabled:
                self.data[module_path] = True  # Used for the UI checkboxes state

    def data_update(self, data):
        self.data.update(data)

    def stop(self, final=False):
        self.stop_event.set()
        for module in self.data['modules'].values():
            module.loop.sleep_event.set()
        for task in self.tasks:
            task.result()
        if final:
            raise exceptions.StopApplication('Quit')
        self.executor.shutdown(wait=False, cancel_futures=True)
        logger.info(f'Quit')

    def output_dir_name(self):
        name_date = datetime.datetime.now().strftime('%Y%m%d_%H%M')
        name = f'{footrecon.name_lower}-{name_date}'
        suffix = 0
        while pathlib.Path(name).exists():
            suffix += 1
            name = f'{footrecon.name_lower}-{name_date}-{suffix}'
        return name

    def module_enabled(self, module_path):
        if app.headless:
            return self.data['modules'][module_path].enabled
        else:
            return self.data[module_path]

    def start(self):
        logger.info('Application started')
        self.tasks = list()
        self.stop_event.clear()
        output_dir_name = self.output_dir_name()
        logger.info(f'Saving output to {output_dir_name}')
        self.executor = concurrent.futures.ThreadPoolExecutor()
        for module_path, module in self.data['modules'].items():
            module.output_dir_name = output_dir_name
            logger.debug(f'Checking if {module_path} is enabled')
            if self.module_enabled(module_path):
                logger.debug(f'Starting task for {module_path}')
                self.tasks.append(self.executor.submit(module.execute))
            else:
                logger.debug(f'Module {module_path} is disabled, skipped')


class TabButtons(widgets.Layout):

    def __init__(self, frame, active_tab):
        cols = [1, 1, 1, 1]
        super().__init__(cols)
        self._frame = frame
        btns = [
            widgets.Button('Controls', self.action_controls, add_box=False),
            widgets.Button('Settings', self.action_settings, add_box=False),
            widgets.Button('Quit', self.action_quit, add_box=False),
        ]
        for i, btn in enumerate(btns):
            self.add_widget(btn, i)
        btns[active_tab].disabled = True

    def action_controls(self):
        raise exceptions.NextScene('Controls')

    def action_settings(self):
        raise exceptions.NextScene('Settings')

    def action_quit(self):
        self._frame.scene.add_effect(
            widgets.PopUpDialog(self._frame.screen, 'Are you sure?', ['Quit', 'Cancel'], has_shadow=True, on_close=self.action_final_quit)
        )

    def action_final_quit(self, selected):
        if selected == 0:
            app.stop(final=True)


class SaveDataFrame(widgets.Frame):

    def data_changed(self):
        self.save()
        app.data_update(self.data)

    def reset(self):
        super().reset()
        self.data = app.data


class ControlsView(SaveDataFrame):

    def __init__(self, scr):
        super().__init__(scr, scr.height, scr.width, can_scroll=False, title=footrecon.name + ' [Controls]')
        self.widget_start = widgets.Button('Start', name='start', on_click=self.action_start)
        self.widget_stop = widgets.Button('Stop', name='stop', on_click=self.action_stop, disabled=True)
        layout_onoff = widgets.Layout([50, 50])
        layout_divider_top = widgets.Layout([1])
        layout_main = widgets.Layout([50, 50], fill_frame=True)
        layout_divider_bottom = widgets.Layout([1])
        self.add_layout(layout_onoff)
        self.add_layout(layout_divider_top)
        self.add_layout(layout_main)
        self.add_layout(layout_divider_bottom)
        layout_onoff.add_widget(self.widget_start, 0)
        layout_onoff.add_widget(self.widget_stop, 1)
        layout_divider_top.add_widget(widgets.Divider())
        for idx, module in enumerate(app.data['modules'].values()):
            widget = widgets.CheckBox(self.device_label(module.module_path), module.name, module.module_path, self.data_changed)
            widget.value = module.enabled
            layout_main.add_widget(
                widget,
                idx % 2
            )
        layout_divider_bottom.add_widget(widgets.Divider())
        layout_tabs = TabButtons(self, 0)
        self.add_layout(layout_tabs)
        self.fix()
        self.data_changed()

    def devices_disabled(self, disabled):
        logger.debug('Changing devices state')
        for module_path in app.data['modules'].keys():
            self.find_widget(module_path).disabled = disabled

    def data_changed(self):
        logger.debug('Changing application data')
        super().data_changed()
        try:
            any_device = any([app.data[module_path] for module_path in app.data['modules'].keys()])
        except KeyError:
            # The app is not initialized yet, wait until next one
            pass
        else:
            if any_device:
                self.widget_start.disabled = False
                self.widget_stop.disabled = True
            else:
                self.widget_start.disabled = True
                self.widget_stop.disabled = True

    def device_label(self, module_path):
        device_name = app.data['modules'][module_path].device_name
        return f'Device: {device_name}'

    def action_start(self):
        logger.debug('Clicked "Start"')
        self.widget_start.disabled = True
        self.widget_stop.disabled = False
        self.widget_stop.focus()
        self.screen.force_update()
        self.devices_disabled(True)
        self.reset()
        app.start()

    def action_stop(self):
        logger.debug('Clicked "Stop"')
        self.widget_stop.disabled = True
        self.widget_start.disabled = False
        self.widget_start.focus()
        self.screen.force_update()
        self.devices_disabled(False)
        self.reset()
        app.stop()


class SettingsView(SaveDataFrame):

    def __init__(self, scr):
        super().__init__(scr, scr.height, scr.width, can_scroll=False, title=f'{footrecon.name} [Settings]')
        layout_utility = widgets.Layout([1, 1, 1])
        layout_divider_top = widgets.Layout([1])
        layout_main = widgets.Layout([1], fill_frame=True)
        layout_divider_bottom = widgets.Layout([1])
        self.add_layout(layout_utility)
        self.add_layout(layout_divider_top)
        self.add_layout(layout_main)
        self.add_layout(layout_divider_bottom)
        layout_utility.add_widget(widgets.Button('About', on_click=self.action_about), 0)
        layout_utility.add_widget(widgets.Button('Reboot', on_click=self.action_reboot), 1)
        layout_utility.add_widget(widgets.Button('Shutdown', on_click=self.action_shutdown), 2)
        layout_divider_top.add_widget(widgets.Divider())
        layout_main.add_widget(widgets.DatePicker('Date', name='date', year_range=range(2021, 2100), on_change=self.datetime_changed))
        layout_main.add_widget(widgets.TimePicker('Time', name='time', seconds=True, on_change=self.datetime_changed))
        layout_divider_bottom.add_widget(widgets.Divider())
        layout_tabs = TabButtons(self, 2)
        self.add_layout(layout_tabs)
        self.fix()

    def datetime_changed(self):
        logger.info('Changed date and time')
        self.data_changed()
        new_datetime = datetime.datetime.combine(self.data['date'], self.data['time'])
        datetime_str = new_datetime.strftime('%a %d %b %Y %H:%M:%S')
        if not hasattr(self, '_set_ntp_false'):
            subprocess.run(shlex.split('timedatectl set-ntp false'), stdout=subprocess.DEVNULL)
            setattr(self, '_set_ntp_false', True)
        subprocess.run(shlex.split(f'date -s "{datetime_str}"'), stdout=subprocess.DEVNULL)
        subprocess.run(shlex.split('hwclock -w'), stdout=subprocess.DEVNULL)

    def action_reboot(self):
        self._scene.add_effect(
            widgets.PopUpDialog(self._screen, 'Are you sure?', ['Reboot', 'Cancel'], has_shadow=True, on_close=self.action_final_reboot)
        )

    def action_final_reboot(self, selected):
        logger.info('Rebooting')
        if selected == 0:
            subprocess.run(shlex.split('reboot'), stdout=subprocess.DEVNULL)

    def action_shutdown(self):
        self.scene.add_effect(
            widgets.PopUpDialog(self.screen, 'Are you sure?', ['Shutdown', 'Cancel'], has_shadow=True, on_close=self.action_final_shutdown)
        )

    def action_final_shutdown(self, selected):
        logger.info('Shutting down')
        if selected == 0:
            subprocess.run(shlex.split('poweroff'), stdout=subprocess.DEVNULL)

    def action_about(self):
        about_text = f' ░▒▓ Footrecon ▓▒░ \n\n https://github.com/tasooshi/footrecon \n\n Version {footrecon.__version__}'
        popup = widgets.PopUpDialog(self.screen, about_text, ['Ok'], has_shadow=True, on_close=self.action_final_about)
        self.scene.add_effect(popup)

    def action_final_about(self, selected):
        raise exceptions.NextScene('Settings')


app = App()


def play(scr, scn):
    scenes = [
        scene.Scene([ControlsView(scr)], -1, name='Controls'),
        scene.Scene([SettingsView(scr)], -1, name='Settings'),
    ]
    app.screen = scr
    scr.play(scenes, stop_on_resize=True, start_scene=scn, allow_int=True)


def entry_point():
    parser = argparse.ArgumentParser(
        description='A mobile all-in-one solution for physical recon.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('-c', '--config', help='Configuration file', default='footrecon.ini')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--debug', action='store_const', dest='loglevel', const=logging.DEBUG, default=logging.INFO, help='Enable debugging mode (verbose output)')
    parsed_args = parser.parse_args()
    logger.setLevel(parsed_args.loglevel)
    if pathlib.Path(parsed_args.config).exists():
        app.load_config(parsed_args.config)
    else:
        logger.error(f'Configuration file missing ({parsed_args.config})')
        sys.exit(1)
    if parsed_args.headless:
        app.headless = True
        logger.info('Running in headless mode')
        app.start()
    else:
        last_scene = None
        while True:
            try:
                screen.Screen.wrapper(play, catch_interrupt=True, arguments=[last_scene])
                sys.exit(0)
            except exceptions.ResizeScreenError as e:
                last_scene = e.scene


if __name__ == '__main__':
    entry_point()
