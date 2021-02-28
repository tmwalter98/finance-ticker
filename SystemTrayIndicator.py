#!/usr/bin/python3
import gi
import time
import signal
from threading import Thread
import threading

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gtk, GLib, GObject
try:
    from gi.repository import AppIndicator3 as AppIndicator
except:
    from gi.repository import AppIndicator

TICKER_INTERVAL_SECONDS = 5

class SystemTrayIndicator(threading.Thread):
    def __init__(self, app_id, tickers):
        threading.Thread.__init__(self)
        self.app_id = app_id
        self.indicator = AppIndicator.Indicator.new(app_id, "emblem-synchronizing-symbolic", AppIndicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.menu())
        self.indicator.set_label(' Contacting APIs...','Syncing data with finance APIs')
        self.tickers = tickers 

    def start(self):
        GObject.threads_init()
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.thread = threading.Thread(target=self.updater)
        self.thread.daemon = True
        self.thread.start()
        self.gtk = threading.Thread(target=Gtk.main)
        self.gtk.daemon = True
        self.gtk.start()

    def stop(self):
        Gtk.main_quit()  

    def updater(self):
        while True:
            for t in self.tickers.copy().keys():
                time.sleep(TICKER_INTERVAL_SECONDS)

                # Get ticker data and calculate daysGainPct, then format string for tray label
                sym = self.tickers[t]
                daysGainPct = 0 if(not(sym['daysGainPct'])) else sym['daysGainPct'] / 100
                ticker_string = '  {:<18} ${:<10.2f}   {:>+.2%}'.format(sym['symbolDescription'], sym['costPerShare'], daysGainPct)
            
                # Determine icon based on day's gain/loss
                dv = sym['daysGainPct']
                dv_icon = 'go-up-symbolic' if(dv > 0) else 'go-down-symbolic' if(dv < 0) else 'list-remove-symbolic'
                
                # Update system tray with current ticker
                GObject.idle_add(
                    self.indicator.set_icon,
                    dv_icon,
                    priority=GObject.PRIORITY_DEFAULT
                )
                GObject.idle_add(
                    self.indicator.set_label,
                    ticker_string, self.app_id,
                    priority=GObject.PRIORITY_DEFAULT
                )
        

    def menu(self):
        menu = Gtk.Menu()
        command_sync = Gtk.MenuItem('Sync Now')
        command_sync.connect('activate', self.force_sync)
        menu.append(command_sync)
        
        command_preferences = Gtk.MenuItem(label='Preferences')
        #command_preferences.connect('activate', self.on_preferences_activated)
        command_preferences.connect('activate', self.force_sync)
        menu.add(command_preferences)

        exittray = Gtk.MenuItem('Exit Tray')
        exittray.connect('activate', quit)
        menu.append(exittray)
        
        menu.show_all()
        return menu

    def force_sync(self, _):
        #etrade()
        print('yah')

    def open_window(self):
        #etrade(_)
        window = Gtk.Window(title="Hello World")
        window.show()
        window.connect("destroy", Gtk.main_quit)
        Gtk.main()

    def quit(self,_):
        Gtk.main_quit()