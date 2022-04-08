#!/usr/bin/env python3

import asyncio
from concurrent import futures
import datetime
import logging
import os
import shlex
import subprocess
import sys

from asciimatics.widgets import (
    Button,
    Divider,
    Frame,
    CheckBox,
    Layout,
    PopUpDialog,
    DatePicker,
    TimePicker,
    TextBox,
    Widget,
)
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import (
    ResizeScreenError,
    NextScene,
    StopApplication,
)

import footrecon
from footrecon.core.logs import logger
from footrecon.modules import (
    audio,
    bluetooth,
    satnav,
    camera,
    wireless,
)


class App:

    def __init__(self):
        self.running = False
        self.quit_pending = False
        self.screen = None
        self.tasks = None
        self.session = None
        self.executor = None
        self.tasks = list()
        self.data = dict()
        self.modules = dict()
        self.modules['audio'] = audio.Audio(self, self.executor)
        self.modules['bluetooth'] = bluetooth.Bluetooth(self, self.executor)
        self.modules['satnav'] = satnav.Satnav(self, self.executor)
        self.modules['camera'] = camera.Camera(self, self.executor)
        self.modules['wireless'] = wireless.Wireless(self, self.executor)
        for mod in self.modules.keys():
            self.data[mod] = self.modules[mod].device_name

    def screen_update(self):
        self.screen.draw_next_frame()
        asyncio.get_event_loop().call_later(0.1, self.screen_update)

    def data_update(self, data):
        self.data.update(data)

    def stop(self):
        self.running = False
        for task in self.tasks:
            task.cancel()
        if self.executor:
            self.executor.shutdown(wait=False, cancel_futures=True)
        logger.info('Application stopped')
        if self.quit_pending:
            raise StopApplication('Quit')

    def start(self):
        logger.info('Application started')
        self.running = True
        self.executor = futures.ThreadPoolExecutor()
        self.session = footrecon.Session()
        loop = asyncio.get_event_loop()
        if not loop.is_running():
            loop.run_until_complete(self.main())

    async def main(self):
        self.tasks = list()
        for name, module in self.modules.items():
            if self.data[name]:
                self.tasks.append(asyncio.create_task(module.execute(self.session)))
        try:
            for task in self.tasks:
                await task
        except asyncio.CancelledError:
            return
        except Exception as exc:
            logger.error(f'Error: {exc}')


class TabButtons(Layout):

    def __init__(self, frame, active_tab):
        cols = [1, 1, 1, 1]
        super().__init__(cols)
        self._frame = frame
        btns = [
            Button('Controls', self.action_controls, add_box=False),
            Button('Settings', self.action_settings, add_box=False),
            Button('Quit', self.action_quit, add_box=False),
        ]
        for i, btn in enumerate(btns):
            self.add_widget(btn, i)
        btns[active_tab].disabled = True

    def action_controls(self):
        raise NextScene('Controls')

    def action_settings(self):
        raise NextScene('Settings')

    def action_quit(self):
        self._frame.scene.add_effect(
            PopUpDialog(self._frame.screen, 'Are you sure?', ['Quit', 'Cancel'], has_shadow=True, on_close=self.action_final_quit)
        )

    def action_final_quit(self, selected):
        if selected == 0:
            app.quit_pending = True
            app.stop()


class SaveDataFrame(Frame):

    def data_changed(self):
        self.save()
        app.data_update(self.data)

    def reset(self):
        super().reset()
        self.data = app.data


class ControlsView(SaveDataFrame):

    def __init__(self, screen):
        super().__init__(screen, screen.height, screen.width, can_scroll=False, title=footrecon.name + ' [Controls]')
        self.widget_start = Button('Start', name='start', on_click=self.action_start)
        self.widget_stop = Button('Stop', name='stop', on_click=self.action_stop, disabled=True)
        layout_onoff = Layout([50, 50])
        layout_divider_top = Layout([1])
        layout_main = Layout([50, 50], fill_frame=True)
        layout_divider_bottom = Layout([1])
        self.add_layout(layout_onoff)
        self.add_layout(layout_divider_top)
        self.add_layout(layout_main)
        self.add_layout(layout_divider_bottom)
        layout_onoff.add_widget(self.widget_start, 0)
        layout_onoff.add_widget(self.widget_stop, 1)
        layout_divider_top.add_widget(Divider())
        for idx, (name, module) in enumerate(app.modules.items()):
            disabled = not bool(module.device_name)
            layout_main.add_widget(
                CheckBox(self.device_label(name), name.capitalize(), name, disabled=disabled, on_change=self.data_changed),
                idx % 2
            )
        layout_divider_bottom.add_widget(Divider())
        layout_tabs = TabButtons(self, 0)
        self.add_layout(layout_tabs)
        self.fix()

    def devices_disabled(self, disabled):
        logger.debug('Changing devices state')
        if disabled:
            for name in app.modules.keys():
                self.find_widget(name).disabled = disabled
        else:
            for name in app.modules.keys():
                self.find_widget(name).disabled = not bool(app.modules[name].device_name)

    def data_changed(self):
        logger.debug('Changing application data')
        super().data_changed()
        any_device = any([bool(app.data[name]) for name in app.modules.keys()])
        if any_device:
            self.widget_start.disabled = False
            self.widget_stop.disabled = True
        else:
            self.widget_start.disabled = True
            self.widget_stop.disabled = True

    def device_label(self, value):
        return 'Device: ' + str(app.data[value])

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

    def __init__(self, screen):
        super().__init__(screen, screen.height, screen.width, can_scroll=False, title=footrecon.name + ' [Settings]')
        layout_utility = Layout([1, 1, 1])
        layout_divider_top = Layout([1])
        layout_main = Layout([1], fill_frame=True)
        layout_divider_bottom = Layout([1])
        self.add_layout(layout_utility)
        self.add_layout(layout_divider_top)
        self.add_layout(layout_main)
        self.add_layout(layout_divider_bottom)
        layout_utility.add_widget(Button('About', on_click=self.action_about), 0)
        layout_utility.add_widget(Button('Reboot', on_click=self.action_reboot), 1)
        layout_utility.add_widget(Button('Shutdown', on_click=self.action_shutdown), 2)
        layout_divider_top.add_widget(Divider())
        layout_main.add_widget(DatePicker('Date', name='date', year_range=range(2021, 2100), on_change=self.datetime_changed))
        layout_main.add_widget(TimePicker('Time', name='time', seconds=True, on_change=self.datetime_changed))
        layout_divider_bottom.add_widget(Divider())
        layout_tabs = TabButtons(self, 2)
        self.add_layout(layout_tabs)
        self.fix()

    def datetime_changed(self):
        logger.info('Changed date and time')
        self.data_changed()
        new_datetime = datetime.datetime.combine(self.data['date'], self.data['time'])
        datetime_str = new_datetime.strftime('%a %d %b %Y %H:%M:%S')
        if not hasattr(self, '_set_ntp_false'):
            subprocess.run(shlex.split('sudo timedatectl set-ntp false'), stdout=subprocess.DEVNULL)
            setattr(self, '_set_ntp_false', True)
        subprocess.run(shlex.split('sudo date -s "{}"'.format(datetime_str)), stdout=subprocess.DEVNULL)
        subprocess.run(shlex.split('sudo hwclock -w'), stdout=subprocess.DEVNULL)

    def action_reboot(self):
        self._scene.add_effect(
            PopUpDialog(self._screen, 'Are you sure?', ['Reboot', 'Cancel'], has_shadow=True, on_close=self.action_final_reboot)
        )

    def action_final_reboot(self, selected):
        logger.info('Rebooting')
        if selected == 0:
            subprocess.run(shlex.split('sudo reboot'), stdout=subprocess.DEVNULL)

    def action_shutdown(self):
        self.scene.add_effect(
            PopUpDialog(self.screen, 'Are you sure?', ['Shutdown', 'Cancel'], has_shadow=True, on_close=self.action_final_shutdown)
        )

    def action_final_shutdown(self, selected):
        logger.info('Shutting down')
        if selected == 0:
            subprocess.run(shlex.split('sudo poweroff'), stdout=subprocess.DEVNULL)

    def action_about(self):
        about_text = ' ░▒▓ Footrecon ▓▒░ \n\n https://github.com/tasooshi/footrecon \n\n Version {}'.format(footrecon.__version__)
        popup = PopUpDialog(self.screen, about_text, ['Ok'], has_shadow=True, on_close=self.action_final_about)
        self.scene.add_effect(popup)

    def action_final_about(self, selected):
        raise NextScene('Settings')


def play(screen, scene):
    scenes = [
        Scene([ControlsView(screen)], -1, name='Controls'),
        Scene([SettingsView(screen)], -1, name='Settings'),
    ]
    app.screen = screen
    asyncio.get_event_loop().call_soon(app.screen_update)
    screen.play(scenes, stop_on_resize=True, start_scene=scene, allow_int=True)


app = App()


def entry_point():
    if '--debug' in sys.argv:  # FIXME: Replace with argparse etc
        logger.setLevel(logging.DEBUG)
    if '--start' in sys.argv:
        app.start()
    else:
        last_scene = None
        while True:
            try:
                Screen.wrapper(play, catch_interrupt=True, arguments=[last_scene])
                sys.exit(0)
            except ResizeScreenError as e:
                last_scene = e.scene


if __name__ == '__main__':
    entry_point()
