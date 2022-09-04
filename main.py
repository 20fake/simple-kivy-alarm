from abc import ABC

from kivymd.tools.hotreload.app import MDApp
from kivy.lang import Builder
from kivy.clock import Clock
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.pickers import MDTimePicker, MDDatePicker
# from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.screenmanager import MDScreenManager
from kivy.core.window import Window
import pygame
import datetime
import sqlite3
from kivymd.uix.screen import MDScreen

Window.size = (350, 600)

"""
My Suggestions:

1. Add more columns to your database table to keep track of  the new data. example ->> 'alarm_title', 'alarm_date', 'alarm_time'

2. For more functionality, give the possibility to your user to activate or deactivate the alarms he want. A switch could be of help.
    If you do this, then you should add a new column to your database's table named 'state' to keep track.
    Link: https://kivymd.readthedocs.io/en/0.104.0/components/selection-controls/index.html#mdswitch

3. For more functionality, give the possibility to your user to change the alarm sound when creating the alarm. A radio/check box could help.
    If you do this, then you should add a new column to your database's table named 'alarm_sound' to keep track.
    Link: https://kivymd.readthedocs.io/en/0.104.0/components/selection-controls/index.html#mdcheckbox-with-group

4. Did you even know Kivy has tools to treat audio files? You could use it instead of using Pygame to play the alarm sound.. or just for exercise purposes
    Link: https://kivy.org/doc/stable/api-kivy.core.audio.html

5. Instead of using the normal Screen class, use MDScreen. Instead of using the normal ScreenManager class, use MDScreenManager. 
    Stuffs with MD are always better and have more functionalities.

6. When using "%H:%M:%S", I think you could get rid of the %S, check your phone's alarm app and you would see that the seconds are never shown.

Let me know if there is any problem or question..
Thanks!
"""


# use MDScreen instead. It is always better and has more functionalities than the normal kv one
class Homesc(MDScreen):
    """
    This class will be the main screen and show the saved alarm
    """
    name = "home"  # screen's name

    def stopbutton(self):
        selfalarm = Alarmsc()
        selfalarm.sound.stop()
        Clock.unschedule(selfalarm.set_volume)


# use MDScreen instead. It is always better and has more functionalities than the normal kv one
class Alarmsc(MDScreen):
    name = "alarm"  # screen's name

    pygame.init()
    # Loading the sound to be used by the app
    sound = pygame.mixer.Sound("alarm.mp3")
    volume = 0

    title = "Alarm App"  # The window's title

    time_dialog = None

    def __init__(self, *args, **kwargs):
        """
        The function creates a database if it doesn't exist, and then initialises the time and date picker dialogs.
        It also schedules the alarm function to run every second
        """
        super().__init__(*args, **kwargs)  # when using the __init__ function in kivy, the super class must be called

        conn = sqlite3.connect('alarm.db')  # Connect database
        c = conn.cursor()
        c.execute("""CREATE TABLE if not exists alarm(name NUMERIC)""")
        c.execute("""CREATE TABLE if not exists title(name TEXT)""")
        conn.commit()
        conn.close()

        self.time_dialog = MDTimePicker()  # initialise
        self.date_dialog = MDDatePicker()  # initialise
        Clock.schedule_interval(self.alarm, 1)  # schedule the alarm function for every one second

    def time_picker(self):
        """
        The time_picker function creates a dialog box that allows the user to select a time.
        The function then binds the on_save event to the schedule function, which adds the selected time to the database
        and schedules an alarm for this time.
        """
        self.time_dialog.bind(on_save=self.schedule)
        self.time_dialog.open()

    def schedule(self, *args):
        """
        The schedule function is used to add the alarm time to the database.
        It also sets the text of a label on the screen.
        """
        self.ids.alarm_timed.text = str(self.time_dialog.time)
        # conn = sqlite3.connect('alarm.db')
        # c = conn.cursor()
        # c.execute("INSERT INTO alarm VALUES (:first)",
        #           {
        #               'first': self.ids.alarm_timed.text,
        #           })

        # conn.commit()
        # conn.close()

    def alarm(self, *args):
        """
        The alarm function is used to check the current time and compare it to the
        alarm times in the database. If there is a match, then it will start the alarm
        and play alarm sound.
        """
        current_time = datetime.datetime.now().strftime("%H:%M:%S")

        conn = sqlite3.connect('alarm.db')
        c = conn.cursor()
        c.execute("SELECT * FROM alarm")
        records = c.fetchall()
        conn.commit()
        conn.close()

        # we save all the alarms found in our database using a list comprehension
        alarms = [record[0] for record in records]
        if str(current_time) in alarms:
            # if the current time is in the database, then..
            self.start()

    def start(self, *args):
        """
        The start function plays the alarm.mp3 file.
        It is called when the current time is found in the records/database.
        """
        self.sound.play(-1)
        self.set_volume()

    def set_volume(self, *args):
        """
        The set_volume function is a method of the SoundLoader class. It is called
        when the user presses the volume button on their device, and it increases
        the volume by 0.05 every 10 milliseconds until it reaches 1 (100%). The set_volume
        method is called with an interval of 10 milliseconds.
        """
        self.volume += 0.05
        if self.volume < 1.0:
            # changed schedule_interval to schedule_once, inorder to avoid scheduling-Recursion/multi-scheduling
            Clock.schedule_once(self.set_volume, 10)
            self.sound.set_volume(self.volume)
            print(self.volume)
        else:
            self.sound.set_volume(1)

    def show_records(self):
        """
        The show_records function is used to display the records from the database.
        It connects to the database and grabs all the records. It then loops through
        the records and displays them in a list on the screen.
        """
        conn = sqlite3.connect('alarm.db')
        c = conn.cursor()

        # Grab records from database
        c.execute("SELECT * FROM alarm")
        records = c.fetchall()

        word = ''
        # Loop thru records
        for record in records:
            word = f'{word}\n{record[0]}'
            self.ids.listalarm.text = f'{word}'

        conn.commit()
        conn.close()

    # Add Date
    def save_date(self, instance, value, date_range):
        """
        The save_date function is to show the date we pick from date_picker function
        """
        # Used to show the date we pick from date_picker function
        self.ids.date_time.text = str(value)

    def date_picker(self):
        """
        The date_picker function is create the dialog box that showing calendar.
        When the date picked, it will be shown on save_date function
        """

        # Binding the on_save event to the save_date function.
        self.date_dialog.bind(on_save=self.save_date)
        # Opening the date dialog box for date picking
        self.date_dialog.open()

    # Save time and date
    def save_reminder(self):
        """
        This function is to save the title, time and date into database.
        After the save button clicked the home screen will show the saved time and date.
        """
        self.ids.title_add.text = str(self.ids.title_add.text)
        self.ids.alarm_timed.text = str(self.time_dialog.time)

        conn = sqlite3.connect('alarm.db')
        c = conn.cursor()
        c.execute("INSERT INTO title VALUES (:first)",
                  {
                      'first': self.ids.title_add.text,
                  })
        
        c.execute("INSERT INTO alarm VALUES (:first)",
                  {
                      'first': self.ids.alarm_timed.text,
                  })

        conn.commit()
        conn.close()


        self.ids.title_add.text = "" # Reempty the add title text field
        self.ids.alarm_timed.text = "" # Reempty the add time text field

        self.manager.transition.direction = "right"  # set the direction of the transition before moving to next
        self.manager.current = "home"  # move to the home screen

        # reference_to_next_screen.ids.listalarm.text = I don't know what I've supposed to do on this line code
        print(self.manager.get_screen("home").ids.listalarm.text)  # What you asked for is in the bracket ! !


"""
# I created a class to take care of this efficiently instead. Always use classes!!
# use MDScreenManager instead of the normal ScreenManager 

sm = ScreenManager()
sm.add_widget(Homesc(name="home")) 
sm.add_widget(Alarmsc(name="alarm"))
"""


class CustomScreenManager(MDScreenManager):
    """
    This is screen manager, that used to manage screen, like switching screen
    """


# choose descriptive names for your classes..
class AlarmApp(MDApp):

    # I used build and not build_app
    def build(self):
        """
        The function loads the file containing the app's UI and returns it
        """
        return Builder.load_file("ui.kv")

    def pop_up_reminder(self):
        """
        The function showing pop-up dialog box while the alarm is running.
        The function will shown the title of the alarm and stop button to stop the alarm.
        

        THE FUNCTION IS NOT WORKING YET
        """
        if not self.dialog:
            self.dialog = MDDialog(
                text="Discard draft?",
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                    ),
                    MDFlatButton(
                        text="DISCARD",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                    ),
                ],
            )
        self.dialog.open()


if __name__ == '__main__':
    # Running the app.
    AlarmApp().run()
