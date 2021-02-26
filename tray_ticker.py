#!/usr/bin/python3
import gi
import os
import time
from signal import pause
from threading import Thread
import threading


gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gtk as gtk
from gi.repository import GLib as glib
try:
    from gi.repository import AppIndicator3 as AppIndicator
except:
    from gi.repository import AppIndicator

class TrayTicker():
    def __init__(self, app_id, tickers):
        self.daemon = True
        self.indicator = AppIndicator.Indicator.new(app_id, "emblem-synchronizing-symbolic", AppIndicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.menu())
        self.indicator.set_label(' Contacting APIs...','Syncing data with finance APIs')
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.tickers = tickers

    def start(self):
        self.thread.start()
        gtk.main()

    def run(self):
        while True:
            for t in self.tickers.keys():
                sym = self.tickers[t]
                time.sleep(5)
                if(sym['daysGainPct']):
                    daysGainPct = sym['daysGainPct'] / 100
                else:
                    daysGainPct = 0
                ticker_string = ' {:<18} ${:<10.2f} {:>+.2%}'.format(sym['symbolDescription'], sym['costPerShare'], daysGainPct)
                self.indicator.set_label(ticker_string, sym['symbolDescription'])
                if(daysGainPct > 0):
                    self.indicator.set_icon('go-up-symbolic')
                elif(daysGainPct < 0):
                    self.indicator.set_icon('go-down-symbolic')
                else:
                    self.indicator.set_icon('list-remove-symbolic')
        

    def menu(self):
        menu = gtk.Menu()
        command_sync = gtk.MenuItem('Sync Now')
        command_sync.connect('activate', self.force_sync)
        menu.append(command_sync)
        
        command_preferences = gtk.MenuItem(label='Preferences')
        #command_preferences.connect('activate', self.on_preferences_activated)
        command_preferences.connect('activate', self.force_sync)
        menu.add(command_preferences)

        exittray = gtk.MenuItem('Exit Tray')
        exittray.connect('activate', quit)
        menu.append(exittray)
        
        menu.show_all()
        return menu

    def force_sync(self, _):
        #etrade()
        print('yah')

    def open_window(self):
        #etrade(_)
        window = gtk.Window(title="Hello World")
        window.show()
        window.connect("destroy", gtk.main_quit)
        gtk.main()

    def quit(self,_):
        gtk.main_quit()