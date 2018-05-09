import sys
import os
import subprocess
import datetime
import time
import threading
import speech_recognition as sr
import pyttsx3
from chatterbot import ChatBot
import shutil
import cProfile
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.factory import Factory
from kivy.uix.actionbar import ActionItem, ActionButton
from kivy.config import Config
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, StringProperty, ListProperty, ConfigParserProperty
import kivy.utils
from kivy.config import ConfigParser
from kivy.uix.settings import SettingsWithSidebar
from SettingsMenu import my_settings



__author__ = 'Aaron Johnson'
__copyright__ = 'Copyright (c) 2018 Copyright Holder All Rights Reserved.'
__license__ = 'MIT'
__version__ = '2.1'
__maintainer__ = 'Aaron Johnson'
__email__ = 'Aaronjohnson@protonmail.ch'


class PrintDialog(FloatLayout):
    '''
    PrintDialog(FloatLayout):

    Parameters
    ----------
    param1 : FloatLayout
        The first parameter. Will hold the widgets in the Popup window which
        creates a PrinterDialog window. Allowing the user to navigate to and
        select a file for printing.

    Attributes
    ----------
    print_files = ObjectProperty(None)
        print_files binds to the SentienceScreen().print_files() function.

    Cancel = ObjectProperty(None)
        Cancel binds to the SentienceScreen().dissmis_popup() function.

	Members
	-------
	    None
	Private Members
	---------------
	    None
	Exceptions
	----------
	    None
	Returns
	-------
	    None
    Notes
    -----
    This class is essentially a container for the Popup() that's created
    in SentienceScreen() class. The purpose of the Popup() is to allow
    the user to have a graphical window to navigate to, and select from,
    a list of files that they want to print out. Rather than automatically
    printing out the files for the user. This prevents potential issues
    and also allows the user the freedom to print out different files
    created by this program.
    '''
    print_files = ObjectProperty(None)
    Cancel = ObjectProperty(None)


class DeleteDialog(FloatLayout):
    '''
	DeleteDialog(FloatLayout):

	Parameters
	----------
	    param1 : FloatLayout
		    This is pretty much exactly what it looks like. When this
			is used later on it will automatically add a float layout.
	Attributes
	----------
	    delete_file
		    This will be used along side an ObjectProperty to register
			it for use with the SentienceScreen.delete_file() and
			SentienceScreen().open_delete_file_dialog() functions.

		Cancel
		    This will be used along side an ObjectProperty to register
			it for use with the SentienceScreen.dismiss_popup() function.

		ObjectProperty(None)
		    Initializes the two attributes to ObjectProperty. This is
			a built in feature of kivy to reduce code and make it
			easier to create/manipulate/initialize/instantiate
			both variables and functions. By making these two
			attributes object properties, in this case, we're
			literally binding them to the two functions calls
			listed above.
	Members
	-------
	    None
	Private Members
	----------------
	    None
	Exceptions
	----------
	    None
	Returns
	-------
	    None
	Notes
	-----
	    We use this with our popup window for deleting specific files.
		This is our dialog. A FloatLayout is provided by default and
		two other layouts are added to it in the kv design language.

		The ObjectProperty delete_file refers to a SentienceScreen()
		function: SentienceScreen.open_delete_file_dialog(). Clicking
		the button "Delete File" calls the open_delete_file_dialog()
		function which then opens a popup window.

		The ObjectProperty Cancel refers to the the button "Cancel"
		which is contained in the above mentioned popup window.
    '''
    delete_file = ObjectProperty(None)
    Cancel = ObjectProperty(None)


class SentienceScreen(Screen):
    '''
    SentienceScreen(Screen):

    Parameters
    ----------
        param1 : Screen
            The first parameter creates a new Screen, which will function
            as a "page". This page is our only "Screen". It's the Main
            Window. It does everything. Now the actual designer code is
            done in the kv design language. But, this widget holds it
            all. It's the core of the program.

    Attributes
    ----------
        self.chatbot
            The chatbot is the core feature here. It's the bot that the
            user communicates with. It's initialized and trained in the
            __init__ function. It's training can be continued throughout
            the program. Or expanded on by creating and adding new databases
            to its training regiment.

        self.engine
            The engine object refers to the python3 text to speeh engine
            . It's what enables the chat bot to have a voice. From this
            engine we derive the ability to pass a string to the chat
            bot which can then access the systems text to speech software
            and read it back with an apropriate voice.

        self.record
            The record object comes from speech_engine.Recognizer().
            This object allows us the ability to use programs such as
            CMU Sphinx voice recognition. Essentially we use this to
            transcribe recored audio to text which we can then store
            in a string. I make use of this by transcribing the recored
            audio to string vairables and passing them to the chat bot
            so that it can accurately respond to the user.

        self.mic
            This object allows us to access and use any connected or
            onboard microphone if one is available. With this we can
            record a users voice, store it in a variable then send it
            to the Recognizer() to be transcribed and passed as a string
            to the chat bot.

        self.audio_threshold
            This is used to automatically set the level at which the
            microphone accepts audio input. The higher the level the
            less sensitive the microphone is. Or rather the it's less
            likely that ambient noise will be treated as intentional
            audio being sent through the microphone.

        self.record_dynamic_energy_threshold
            This applies to self.record and is a boolean variable. By
            setting this to False we can ensure that the energy_threshold
            doesn't dynamically set its energy_threshold level. Note:
            That the energy_threshold is what enables us to searate
            between ambient noise and the users intended voice commands.

        self.master_log
            This is a string variable that I use to store all of the
            conversation that takes place between the user and the chat
            bot.

        self.voice_enabled
            If self.voice_enabled is set to True then the user is able
            to use their microphone to communicate with the chat bot.
            Note: The user can only use a microphone if they have one.
            This can be either a connected microphone and or an onboard
            microphone.

        self.voice_disabled
            If self.voice_disabled is set to True then the user can only
            communicate with the chat bot through text. Note: The chat
            bot can access its audio functions even if
            self.voice_disabled == True. This function only effects the
            users ability to use their microphone.

        self.user_input
            This is a string variable which I use to store the input
            from the user the data here is passed to the chat bot,
            stored in various files and variables/data structures.
            Note: This variable is redundant and will in the future be
            removed. It can be ommited and replaced by the TextInput
            widgets return function.

        self.audio_enabled
            if self.audio_enabled == True the chat bot can use the systems
            text to speech software (espeak, spai5, or nsss) to access the
            softwares built in voices and read back any strings that the
            chat bot comes up with as a response to the user. Note: This
            boolean vairable only effects the chat bots ability to use
            sound as a medium for communication. It does not effect the
            users ability to use their microphone.

        self.audio_disabled
            If self.audio_disabled == True then the chat bot can only
            communicate with the user via text.

        self.__user_profile
            self.__user_profile is a dictionary and stores three specific
            keys. 1) Username, 2) Age, 3) Gender. These are optional
            variables. The user doesn't need to create a user profile.
            Though it's encouraged that they do for better logging of
            the data. Note: If the user elects to not create a user profile
            this information is by default set.


    Members
    -------
        def __init__(self, **kwargs)
            Initalizes SentienceScreen() a more in depth analysis will
            be given under the SentienceScreen().__init__(self, **kwargs)
            functions documentation.

        def quick_check_os(self)
            This function is called when the user clicks on the
            "Check Operating System" button which is represented by
            an image of a computer on the menu bar. This function
            when clicked checks to see if the user is running either
            windows or Linux. If the user is running windows it makes
            three new TextInput Widgets visible by changing the opacity.
            If the user is using a Linux operating system clicking on
            this button does nothing. A more in depth analysis will be
            given in the SentienceScreen().quick_check_os() functions
            documentation.

        def get_user_text_response(self)
            This function is called when the user hits the "enter key"
            on their keyboard while inside of the user_input TextInput
            Widget. A string variable is returned from this and passed
            to the chat bot so that it can form a response to what the
            users statement was. A more in depth analysis of this will
            be given in the SentienceScreen().get_user_text_response()
            functions documentation.

        def get_caprica_text_response(self)
            This function is called after the user inputs a text
            response. And that response is sent to the chat bot. The
            response that the user input is used by this function to
            generate a response from the chat bot. A more in depth
            analysis will be given in the
            SentienceScreen().get_caprica_text_response() functions
            documentation.

        def get_user_voice_response(self)
            This function is called when the user clicks the
            "Record user" button. Which is located on the menu bar and
            is represented by the image of a blue talking head. If
            self.voice_disabled == True then the image will be a red
            talking head. If the user clicks the button when it's red a
            warning message will be displayed informing the user that
            he/she needs to first enable their microphone by clicking on
            the set_enable_disable_voice button. A More in depth
            analysis of this function will be given in the
            SentienceScreen().get_caprica_voice_response() function
            documentation.

        def get_caprica_voice_response(self, words)
            This function is called after the user inputs a text string
            in the proper TextInput widget; or
            if self.voice_enabled == True. A more in depth analysis of
            this function will be given in the
            SentienceScreen().get_caprica_voice_response(self, words)
            function documentation.

        def set_gender(self):
            This function is called in
            SentienceScreen().__init__(self, **kwargs). Through this
            function we set the voice property of self.engine to use
            the systems female voice option. A more in depth analysis
            of this function will be given in the
            SentienceScreen().set_gender(self) function documentation.

        def set_speech_rate(self):
            This function is called in
            SentienceScreen().__init__(self, **kwargs). Through this
            function we can set the self.engine speech rate property.
            This function can in effect lower or increase the number
            of words spoken by the chat bot per minute. A more in
            depth analysis of this function will be given in the
            SentienceScreen().set_speech_rate() functions
            documentation.

        def caprica_speak(self, words)
            This function is called from a variety of locations for the
            purpose of activating the voice feature of the chat bot
            which is derived from self.engine. A more in depth analysis
            of this function will be given in the
            SentienceScreen().caprica_speak(self, words) functions
            documentation.

        def onEnd(self, name, completed)
            This function is called everytime
            self.caprica_speak(self, words) is called. This function is
            fired when the self.caprica_speak event has ended. This is a
            callabck which terminates the event queue of the
            self.engine. A more in depth analysis of this function will
            be given in the
            SentienceScreen().onEnd(self, name, completed) functions
            documentation.

        def clear_viewport(self)
            This function is caleld whenever the user clicks the
            "Erase logs" button. Which is represented by the eraser on
            the menu bar. This button only erases the text in the
            viewport TextInput Widget. A more in depth analysis of
            this function will be given in
            SentienceScreen().clear_viewport(self) function
            documentation.

        def create_user_profile(self)
            This function is highly redundant and will be removed in
            the future. This function is called when ever the user inputs
            their username for the first time. It runs some checks and
            then simply calls self.caprica_speak() to speak the users
            input username. A more in depth analysis of this function
            will be given in the
            SentienceScreen().create_user_profile(self) function
            documentation.

        def set_enable_disable_audio(self)
            This function is called when the user clicks the
            self.set_enable_disable_audio button which is represented by
            either a red or blue speaker image on the menu bar. If
            self.audio_enabled == True the chat bot can use audio to
            communicate with the user and the image is a blue speaker.
            If self.audio_disabled == True then the chat bot can only
            communicate with the user via text. The button is  also
            then represented by a red speaker. This function will
            update the image on the menu bar to reflect its current
            status. A more in depth analysis of this function will
            be given in the SentienceScreen().set_enable_disable_audio(self)
            function documentation.

        def set_enable_disable_voice(self)
            This function is called when the user clicks the
            self.set_enable_disable_voice button which is represented by
            either a red or blue microphone image on the menu bar.
            If self.voice_enabled == True the user can use their microphone
            to communicate with the chat bot and the image is a blue
            microphone. If self.voice_disabled == True then the user can
            only communicate with the chat bot via text. The button is
            also then represented by a red microphone. This function
            will update the image on the menu bar to reflect its current
            status. A more in depth analysis of this function will be
            given in the SentienceScreen().set_enable_disable_voice(self)
            function documentation.

        def set_username(self)
            This function is called from two locations both involve the
            user inputting a desired username into a TextInput Widget
            and hitting the "Enter" key on their keyboard. This function
            sets the user name for the current user and can be changed
            at any time. A more in depth analysis of this function will
            be given in SentienceScreen().set_username() function
            documentation.

        def set_sex(self)
            This function is called from two locations both involve the
            user inputting their gender into a TextInput Widget and
            hitting the "Enter" key on their keyboard. This function sets
            the gender for the current user and can be changed at any time.
            A more in depth analysis of this function will be given in
            SentienceScreen().set_sex() function documentation.

        def set_age(self)
            This function is called from two locations both involve the
            user inputting their age into a TextInput Widget and hitting
            the "Enter" key on their keyboard. This function sets the users
            age for the current user and can be changed at any time. A more
            in depth analysis of this function will be given in
            SentienceScreen().set_username() function documentation.

        def print_files(self, path, filename)
            This function is called when the user clicks on the "Print"
            button on the menu bar. When called a Popup() window is
            created and allows the user to navigate to any file that
            they wish to print. within that window are two buttons.
            Clicking the "Print" button will print the selected file
            while clicking the "Close" button will close the Popup()
            window. A more in depth analysis of this function will be
            given in SentienceScreen().print_files(self, path, filename)
            function documentation.

        def create_dir(self, path)
            This function is caleld from within
            SentienceScreen().__init__(self, **kwargs). When executed it
            checks to see if a specific system relative directory exists.
            If it does the function returns nothing. If it doesn't exist
            the function creates the directory and then calls the private
            function self.__create_files(self, path). A more in depth
            analysis of this function will given in
            SentienceScreen().create_dir(self, path) function
            documentation.

        def write_logs(self)
            This function is caleld when the user clicks the "Write Logs"
            button on the menu bar which is represented by a pencil
            image. It creates and writes the contents of self.master_log
            to a text file which is either
            "Users input username + _Conversations"
            .txt or simply "Username_Conversations".txt.
            A more in depth analysis of this function will be given in
            SentienceScreen().write_logs(self) function documentation.

        def open_print_file_dialog(self)
            This function is caleld when the user clicks the "Print"
            button on the menu bar. This is the function that calls
            the Popup() window and allows the user to print a specific
            chosen file after navigating to it; and then by clicking the
            "Print files" button on that Popup() window.

        def dismiss_popup(self)
            This function is called when the user clicks the "close"
            button on the PrintDialog() Popup() window. It closes the
            Popup() window. A more in depth analysis of this function
            will be given in the SentienceScreen().dismiss_popup()
            function documentation.

        def on_mouse_pos(self, instance pos):
                This function is called everytime that the user moves
                his or her mouse. If the mouse collides with any of the
                the buttons on the menu bar (Action Bar) this function
                checks the positions against the various if statements
                which relate to the specific button. When the position
                of the users mouse matches the positions outlined in
                the statements. A tool tip is displayed, which presents
                at leat the name of the button.

        def display_tooltip(self, *args):
            When this function is called the tooltip that relates
            to the button (as explain in on_mouse_pos) is created
            and added to the users screen. A clock event is then
            scheduled to delete the tooltip from the screen automaticaly
            after five seconds.

        def close_tooltip(self, dt):
            This function is called by the clock event described in
            display_tooltip(). When this event is executed five seconds
            after it's been registered. The tooltip widget is
            deleted from the users screen.

        def set_tooltip_text(self, text):
            We call this function and supply a string to the text
            parameter. This text relates to which ever button the users
            mouse colldied with. The text is then set and that's what's
            displayed to the user when the tooltip widget is added to
            the screen.

        def caprica_timer(self, _time):
            This function is not currently in use. It's purpose
            was to function as an independent threaded timer. The time
            was based on the number supplied to the _time parameter.
            This function ticks down until _time is == 0 displaying
            the text ...Thinking... until _time is == 0; at which
            time the text displayed is then ...Inactive...

        def start_timer_thread(self, _time):
            This function is not currently being used. But, it's
            purpose was to setup and run the caprica_timer function.

        def check_timer(self, _time):
            This function is not being used. But, it's purpose was
            to check the status of self.caprica_timer(_time). To
            ensure that it ended when _time == 0 instead of counting
            down beyond that into negative numbers.

        def get_caprica_response(self):
            This function is used to generate a response from the
            user. It combines all but the voice input/output
            responses. Basically, when you enter text into the
            user_input TextInput this function is called after
            the user hits the enter key. It then begins the
            process of the chatbot generating a response. It
            also runs as an independent thread.

        def get_caprica_voice_thread(self, words):
            This function is called when the users has activated the
            voice option, then recorded their voice. Once that
            recording process is completed this function is called.
            This function then generates the chatbots response. It
            also runs as an independent thread.

        def start_get_response_thread(self):
            We call this function after the user types some text
            into the self.ids.user_input TextInput widget, and
            then hits the enter key on their keyboard. This function
            changes the text of the notification_widget to
            '...Thinking...'. It then creates and runs the
            self.get_caprica_response() thread.

        def start_voice_response_thread(self):
            We call this function after the voice option has been
            activated, and the user has hit the record button. Once
            the record button has been clicked, the user can begin
            speaking into their microphone. Once done speaking
            we create and run the self.get_caprica_voice_thread().
            # TODO: Fix notification text.

        def _is_thread_stopped(self):
            We call this function to check if there are
            any active threads running.
            # TODO: This function is useless and should be removed.

        def _stop_threading(self):
            This function is called when an active thread is
            supposed to be terminated. The idea is that the thread
            will be interupted and thus die.
            # TODO: Remove this because it doesn't do anything.

        def get_user_text(self):
            This function is called to return the current
            text contained in the user_input TextInput widget.

        def open_delete_file_dialog(self):
            This function is called when the users clicks on the
            delete file button which is located under the settings
            submenu on the menu bar. It opens a Popup() window. Which
            contains a filebrowser and allows the user to navigate to
            the file that they wish to delete. They can then select
            the file by clicking on it, and then clicking the delete
            button on the Popup() window. Or click the cancel button
            at any time which closes the window.

        def delete_file(self, path, filename):
            This function is called after the user has slected a
            file in the Popup() window file browser and then clicked
            the delete button. The file the user selected is then
            deleted if it exists. If it doesn't exist the user is
            informed.
            # TODO: Remove path parameter as it does nothing at all.

        def delete_all(self):
            We call this function if the user clicks on the
            **Delete All** button which is located in the
            settings submenu on the menu bar. Clicking this
            button deletes all files and folders generated by the
            this program. It also then exits the program.

        def display_user_conversation(self):
            This function is called when the user clicks on
            the display conversation button. It outputs the
            contents of self.master_log into the view_port
            Widget.

        def increase_chatbot_voume(self, vol):
            This function can be called to increase the volume
            of self.engine. The volume is increased by vol. The
            values it can take are between 0-1. With 0 being the
            lowest and one being the highest. # TODO: Re-implement

        def decrease_chatbot_voume(self, vol):
            This function can be called to decrease the volume
            of self.engine. The volume is idecreased by vol. The
            values it can take are between 0-1. With 0 being the
            lowest and one being the highest. # TODO: Re-implement

        def set_volume(self, vol):
            This function is called to set the volume of
            self.engine. The volume is set to vol; vol can be
            any  value between 0-1.

        def increase_rate_of_speech(self, value):
            This funciton is called when the user increases
            the rate of speech using the settings menu. The
            current rate of self.engine is increased by value.

        def decrease_rate_of_speech(self, value):
            This funciton is called when the user decreases
            the rate of speech using the settings menu. The
            current rate of self.engine is decreased by value.

    Private Members
    ---------------
        def __create_files(self, path)
            This function is called from within the
            self.create_dir(self, path) function
            which is called first by the
            SentienceScreen().__init__(self, **kwargs) function.
            This function when called checks to see if specific files
            exist and if they don't
            it creates them. If they do already exist if essentially
            returns none. It's also called from one other function if a
            search does not find the required files which means that
            they were intentionally or unintentionally deleted. A more
            in depth analysis of this function will be given in
            SentienceScreen().__create_files(self, path) function
            documentation.

        def __append_file(self, world, path)
            This function is caleld every time the user speaks to the
            chat bot and every time that the chat bot responds. The data
            passed to words is the response from both parties which is
            then appened to a specific file(s) which path comes from
            the path parameter. A more in depth analysis of this funciton
            will be given in
            SentienceScreen().__append_file(self, world, path) Note: The
            "World" param is a typo and needs to be changed to "word/words"

        def __set_thinking_text(self, bool):
            This function is called to change the text and the
            color of the text of the notification_widget TextInput
            to reflect the current status of the program. Ie,
            if the chatbot is about to generate a response it
            says '...Thinking...' in red text. If the chatbot has
            already generated a response it says '...Inactive...'
            in blue text.
        def __currently_thinking(self, bool):
            This function is called to determine the current
            status of the program and the chatbot. If it's
            thinking or inactive.
            # TODO: This function is redundant
    Notes
    -----
        This is the essential widget. It's where everything happens.
    '''

    def __init__(self, **kwargs):
        '''
        def __init__(self, **kwargs):

        Parameters
        ----------
            param1 : self
                Denotes this as being a member of the SentienceScree()
                class.

            param2 : **kwargs
                **kwargs stands for keyword arguements. This
                allows an arbitrary number of keyword arguements to
                be passed to the self.SentienceScreen().__init__()
                function.
        Attributes
        ----------
            mouse_pos
                mouse_pos is an optional, though required for our
                purposes, parameter of the Window.bind() function.
                We call this function which is a member of the Window()
                class. To register a mouse event. We bind the
                traditional mouse_pos event to our own
                self.on_mouse_pos(). The mouse (pointer) is always
                tracked were simply binding it to one of our
                functions so that we can monitor the position and
                inctance of the pointer and call the bound function
                when it's appropriate.

            self.tooltip_open
                self.tooltip_open is a member of the SentienceScreen()
                class. We use this as a flag to determine whether or
                not the ToolTipLabel widget is being shown.

            self.mic
                self.mic is a member of the SentienceScreen() class.
                We use this to create our sr.Microphone() object.
                This object allows us the ability to access and
                manipulate the users microphone, assuming that
                they have one. For later use in our program.

            self.chatbot
                self.chatbot is a member of the SentienceScreen()
                class. We use this to create our ChatBot() object.
                We can then manipulate self.chatbot, which we do,
                throughout the rest of our program. This is one of
                the core objects. Without this we have no chatbot.

            self.audio_threshold
                self.audio_threshold is a member of the
                SentienceScreen() class. It stores an integer
                value. This value enables us to force the users
                microphone to ignore noises below a certain range.

            self.audio_enabled
                self.audio_enabled is a member of the SentienceScreen()
                class. We use this boolean variable as a flag to tell
                us if the user has enabled the audio option. The user
                can enable the audio option by clicking on the red
                speaker button on the menu bar (Action Bar). This
                sets self.audio_enabled == True and changes the color
                of the icon of the speaker button to blue.

            self.audio_disabled
                self.audio_disabled is a member of the SentienceScreen()
                class. We use this boolean variable as a flag to tell
                us if the user has disabled the audio option. The user
                can disable the audio option by clicking on the blue
                speaker button on the menu bar (Action Bar). This
                sets self.audio_enabled == False and changes the color
                of the icon of the speaker button to red.

            self.record.dynamic_energy_threshold
                We use this to prevent self.record from dynamically
                Ie, contantly, checking the and setting the
                energy_threshold of self.record. Idealy, this should
                be left as a dynamic process but because no one
                microphone was created equal. Things get annoying
                really fast. So I've simply set it to a static
                variable for windows operating systems. And
                dynamically set it once for linux operating
                systems.

            self.master_log
                self.master_log is a member of the SentienceScreen()
                class. It's a string variable that we use to store
                the users conversation with the chatbot. Every time
                that the user and the chatbot say something. Their
                responses are added to this string. We use this
                string to write data to files.

            self.voice_enabled
                self.voice_enabled is a member of the SentienceScreen()
                class. We use this boolean variable as a flag to tell
                us if the user has enabled the voice option. The user
                can enable the voice option by clicking on the red
                microphone button on the menu bar (Action Bar). This
                sets self.voice_enabled == True and changes the color
                of the icon of the microphone button to blue. It also
                sets self.voice_disabled == False.

            self.voice_disabled
                self.voice_disabled is a member of the SentienceScreen()
                class. We use this boolean variable as a flag to tell
                us if the user has disabled the voice option. The user
                can disable the voice option by clicking on the blue
                microphone button on the menu bar (Action Bar). This
                sets self.voice_enabled == False and changes the color
                of the icon of the microphone button to red.

            self.user_input
                self.user_input is a member of the SentienceScreen()
                class. We use this string variable to temporarily
                store the contents of self.ids.user_input.text. Which
                is the TextInput widget that contains the users text
                comment to the chat bot. The data is returned to
                self.user_input when the user enters some text and hits
                the enter key on their keyboard while in the TexTInput
                widget.

            self.__user_profile
                self.user_profile is a member of the SentienceScreen()
                class. We use this dictionary data structure to store
                the users information if they choose to give it. It
                stores their desired username, age, and gender. It's
                not a required thing. It's optional but personalizes
                a few things and helps to maintain more efficient logs
                of the conversations that the chatbots has. If there
                are multiple people speaking to it.

            self.username
                self.username is a member of the SentienceScreen()
                class. We use this string variable to store the users
                desired username. Or, if the user elects not to supply
                a username we give this a default value of 'User: '
                and display it in the view_port TextInput widget
                to display the current conversation to the user.

            self.on_mouse_pos
                self.on_mouse_pos is a member of the SentienceScreen()
                class. It's a function that we use to track and handle
                mouse events. If the user hovers their mouse over a
                button on the Menu bar (Action Bar). This function is
                called, which locates teh mouses position and instance
                of the mouse when it collided with a button. It then
                executes the appropriate if statements which then
                create a ToolTipLabel widget, change the text to
                reflect the button the user collided with. And then
                displays that label as a tooltip over the button.

            self.engine
                self.engine is a member of the SentienceScreen()
                class. We use this to create our object of the pyttsx3
                class. This allows us to access the users systems text
                to speech software so that the response generated by
                the chatbot can be verbally delivered to the user. If
                they elected to active either the audio or voice
                options.

            self.record()
                self.record() is a member of the SentienceScreen()
                class. It's the object of the sr.Recognizer()
                class. This allows us to accept, transcribe and later
                manipulate an audio recording of the user. This
                occurs when the user has activated the voice option.

            self.__is_thinking
                self.__is_thinking is a member of the SentienceScreen()
                class. We use this boolean variable as a flag to tell
                us whether or not the chatbot is preparing to generate
                a response for the user. Or has just finished generating
                a response to the user. When the chatbot is generating
                a response the text of the notification_widget is set
                to '...Thinking...' and the color of that text is red.
                When the chatbot finishes generating a response and has
                sent it to the user the text is set to '...Inactive...'
                and is blue.

            self.current_conversation
                This is a member of the SentienceScreen() class.
                We use this string variable to store the current
                contents of the view_port Widget. When a tooltip
                is displayed. We do this to prevent the loss of
                the information that was previously being displayed.
        Members
        -------
            super(SentienceScreen, self).__init__(**kwargs)
                Here we're calling super dynamically to allow the
                use of inheritance. This applies to the
                sentienceScreenManager() class. It allows us to
                work with the various widgets and screens.

            Window.bind(mouse_pos = self.on_mouse_pos)
                We call Window.bind() to bind the base Window
                classes mouse_pos event to our mouse event. Which
                in this case is self.on_mouse_pos()

            threading.Event()
                threading.Event() is a member of the threading()
                class. We use this to create a threading event
                which we'll use to interupt active threads later on.

            Factory.ToolTipLabel(text = (string))
                We use this to register and instantiate
                classes anywhere anytime. In our case though
                we're just setting this up and setting the text
                field to '', Ie, an empty string.

            Config.set('input', 'mouse', 'mouse', disable_multitouch)
                Config is a member of the kivy base class. We call
                this in our SentienceScreen.__init__() method
                to disable kivys multitouch ability. This shuts off
                users ability to interact via touch screen on touch
                screen capable systems.

            sys.platform.startswith(string)
                This is a member of the sys() class. We call this
                function to dertmine whether what operating system
                the user is using. It returns a boolean value, if
                the version matches either 'linux' or 'win'.

            pyttsx3.init(string)
                This is a member of the pyttsx3() class. We call
                this function when we declare and instantiate
                our object of this class. It also serves to
                set the driver for the systems text to speech
                software based on the users operating system.

            sr.Recognizer()
                This is a member of the speech_recognition() class.
                We call this when we declare and instance our
                self.record object. Which then allows us to
                accept user input from a microphone and then
                transcribe that uadio respone as a string for
                later manipulation.

            sr.Microphone()
                This is a member of the speech_recognition() class.
                We call this when we declare and instantiate our
                self.mic object. Which then allows us to manipulate
                the users microphone if they have one.

            ChatBot()
                Here we setup the ChatBot. We do wo when we decalre
                and instantiate our self.chatbot object. We create and
                supply the required filters and adapters which dictate
                how this chatbot will learn.

            self.set_gender()
                This is a member of the SentienceScreen() class. We
                call this function to set the gener of self.engine
                to a female. This has the effect of changing the
                default voice from a male, to female voice.

            self.set_speech_rate()
                This is a member of the SentienceScreen() class. We
                call this function to set the speech rate of the
                users systems speech to text software. In our
                case we lower it so that when self.caprica_speak()
                is called the resulting spoken string is done
                so in a manner that the user can understand.

            leng()
                We call the built in python leng() or length
                function to dertmine the length of self.username.
                If the length is less than or equal to zero we
                supply self.username with the default value of
                'User: '. If the user elects later on to set their
                own username then the self.user_profile overrides
                this variable.

            self.create_dir(path)
                This is a member of the SentienceScreen() class.
                We call this function to create a series of files
                and folders that the user needs to operate
                this program.

            self.engine.connect(string, event)
                We call this function to bind our events
                to the pyttsx3 events. We connect self.onEnd
                to the pyttsx3 'finished-utterance' event. This
                event is fired when the pyttsx3 finishes speaking
                whatever string was supplied to it. We also connect
                self.caprica_speak to 'started-utterance' which is
                fired when the systems text to speech software
                begins speaking a supplied string.
        Private Members
        ---------------
            None

        Exceptions
        ----------
            None

        Returns
        -------
            None

        Notes
        -----
            This is the initalization method of SentienceScreen().
            It's relatively comprehensive so I'm not going to explain
            it again. It's easy enough to understand whats happening
            when you reference the above comments.
        '''

        super(SentienceScreen, self).__init__(**kwargs)

        Window.bind(mouse_pos=self.on_mouse_pos)
        self.__is_thinking = False
        self.tooltip_open = False
        self.tooltip = Factory.ToolTipLabel(text=(''))
        Config.set('input', 'mouse', 'mouse, disable_multitouch')
        if sys.platform.startswith('linux'):
            self.engine = pyttsx3.init('espeak')
        elif sys.platform.startswith('win'):
            self.engine = pyttsx3.init()
        self.record = sr.Recognizer()
        self.mic = sr.Microphone()
        self.chatbot = ChatBot('Caprica',
                               storage_adapter='chatterbot.storage.SQLStorageAdapter',
                               logic_adapters=['chatterbot.logic.BestMatch', 'chatterbot.logic.TimeLogicAdapter', 'chatterbot.logic.MathematicalEvaluation'],
                               input_adapter='chatterbot.input.VariableInputTypeAdapter',
                               output_adapter='chatterbot.output.OutputAdapter',
                               filters=["chatterbot.filters.RepetitiveResponseFilter"],
                               database='RC_2001-06.db',
                               trainer='chatterbot.trainers.ChatterBotCorpusTrainer')
        self.set_gender()
        self.set_speech_rate()
        self.audio_threshold = 400
        self.record.dynamic_energy_threshold = False
        self.master_log = str()
        self.voice_enabled = False
        self.voice_disabled = True
        self.user_input = str()
        self.audio_enabled = False
        self.audio_disabled = True
        self.user_profile = {1: 'Username', 2: 'Age', 3: 'Sex'}
        self.username = str()
        if len(self.username) <= 0:
            self.username = 'User'
        if sys.platform.startswith('linux'):
            self.create_dir('/home/' + str(os.getlogin()) + '/.SentienceFiles/')
        elif sys.platform.startswith('win'):
            self.create_dir('C://SentienceFiles//')
        elif sys.platform == 'darwin':
            self.create_dir('/home/' + str(os.getlogin()) + '/.SentienceFiles/')
        self.engine.connect('started-utterance', self.caprica_speak)
        self.engine.connect('finished-utterance', self.onEnd)
        self.current_conversation = str()
        self.set_volume(1)



    def display_user_conversation(self):
        '''
            When called this function displays the contents of
            self.master_log inside the view_port TextInput Widget.
        '''
        self.ids.view_port.text = self.master_log



    def increase_chatbot_volume(self, vol):
        '''
            Increase the chatbots volume by vol when called.
            Chatbots volume can only be set between 0-1
            with 0 being the lowest and 1 being the highest volume
            level.

            If vol > 1 or < 0 a warning message is displayed in the
            view_port TextInput widget.
        '''
        if int(vol) >= 0 and int(vol) <= 1:
            volume = self.engine.getProperty('volume')
            self.engine.setProperty('volume', volume + vol)
        elif int(vol) < 0 or int(vol) > 1:
            self.ids.view_port.text = 'Value must be between 0-1.'



    def decrease_chatbot_volume(self, vol):
        '''
            Decreases the chatbots volume by vol.

        '''
        if int(vol) >= 0 and int(vol) <= 1:
            volume = self.engine.getProperty('volume')
            self.engine.setProperty('volume', volume - vol)
        elif int(vol) < 0 or int(vol) > 1:
            self.ids.view_port.text = 'Value must be between 0-1.'



    def set_volume(self, vol):
        '''
            Set the chatbots volume to vol. Zero is the lowesst
            value and one is the highest possible volume. Setting
            this to 1 will cause your audio device to produce
            failures in the sound in the form of crackling and
            or static.
        '''
        volume = self.engine.getProperty('volume')
        self.engine.setProperty('volume', vol)



    def get_user_text_response(self):
        '''
        def get_user_text_response(self)

        Parameters:
        -----------
            param1 : self
                Denotes it as being a member of SentienceScreen(Screen)
                class.

        Attributes
        ----------
            self.audio_disabled
                Preforms a check to establish wether or not
                self.audio_disabled == True.

            self.user_input
               Accepts text (string) from user_input TextInput Widget.

            self.ids.user_input
                TextInput Widget that returns its current string to
                self.user_input. Or self.get_caprica_voice_response()

            self.master_log
                Stores the contents of self.ids.user_input TextInput
                string along with some other data.

            self.audio_enabled
                Checks to see if self.audio_enabled == True

        Members
        -------
            self.get_caprica_voice_response(words)
                Is called when self.audio_enabled == True Accepts
                self.ids.user_input.text as its parameter. That is to
                say that self.ids.user_input returns its string to this
                function. The chat bot then searches its database and
                locates the best  possible response. It then calls
                self.caprica_speak() to read that response.

        Private Members
        ---------------
            self.__append_file(path)
                This is called to append the user_input value to the
                User_Statements.txt file.

        Returns
        -------
            return self.get_caprica_text_response()
                Ends with the text response of caprica_speak() which is
                a resposne to the users comment.

            return None
                Function returns None when self.audio_enabled == True

        Exceptions
        ----------
        OSError
            The OSError can occur due to numerous reasons.
            What I'm primarily concerned with here however
            is import statements, incompatible Operating
            systems, and bad system calls. The exception
            if it occurs is handled and logged in an error
            log text file.

        IOError
            The IOError can occur due to many reasons.
            My primary concern is file manipulation. The
            improper opening/closing/writing to files. If
            the exception occurs it's handled and logged; in
            an error log text file.

        FileNotFoundError
            FileNotFoundError is exactly what it sounds like.
            If the file I'm trying to write to doesn't exist
            we may have a problem. But not to worry it's handled
            and logged.


        Notes
        -----
		    **This function is deprecated and has been replaced
			with get_caprica_response**

            This function is called when the user hits the "Enter" key
            on their key board while clicked into the
            self.ids.user_input TextInput Widget.

            What happens next is determined by the value(s) of
            self.audio_enabled and self.audio_disabled.

            if self.audio_enabled == True the chat bot obtains the users
            comment and then calls self.caprica_speak() where it
            essentially returns None

            if self.audio_disabled == True the chat bot obtains the users
            comment passes that string to the
            self.get_caprica_text_response(string) and then returns
            self.get_caprica_text_response(string)
        '''
        try:
            if sys.platform.startswith('linux'):
                if self.audio_disabled:
                    self.user_input = self.ids.user_input.text
                    self.__append_file('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + self.user_input, '/home/' + str(os.getlogin()) + '/.SentienceFiles/User_Statements.txt')
                    self.master_log += '\n' + self.username + ': ' + self.user_input
                    return self.get_caprica_text_response()
                elif self.audio_enabled:
                    self.__append_file('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + self.ids.user_input.text, '/home/' + str(os.getlogin()) + '/.SentienceFiles/User_Statements.txt')
                    self.master_log += '\n' + self.username + ': ' + self.ids.user_input.text
                    self.get_caprica_voice_response(self.ids.user_input.text)
            elif sys.platform.startswith('win'):
                if self.audio_disabled:
                    self.user_input = self.ids.user_input.text
                    self.__append_file('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + self.user_input, 'C://SentienceFiles//User_Statements.txt')
                    self.master_log += '\n' + self.username + ': ' + self.ids.user_input.text
                    return self.get_caprica_text_response()
                elif self.audio_enabled:
                    self.__append_file('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + self.ids.user_input.text, 'C://SentienceFiles//User_Statements.txt')
                    self.master_log += '\n' + self.username + ': ' + self.ids.user_input.text
                    self.get_caprica_voice_response(self.ids.user_input.text)
        except OSError as a:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: get_user_text_response ' + '\nOSError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: get_user_text_response ' + '\nOSError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except IOError as b:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: get_user_text_response ' + '\nIOError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: get_user_text_response ' + '\nIOError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except FileNotFoundError as c:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: get_user_text_response ' + '\nFileNotFoundError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: get_user_text_response ' + '\nFileNotFoundError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None



    def increase_rate_of_speech(self, value):
        '''
            Increases the words per minute spoken by value.
            Increasing this value increase teh rate of speech
            and may make the chatbots verbal messages incoherent.
        '''
        rate = self.engine.getProperty('rate')
        self.engine.setProperty('rate', rate + value)



    def decrease_rate_of_speech(self, value):
        '''
            Decreases the chatbots words spoken per minute.
        '''
        rate = self.engine.getProperty('rate')
        self.engine.setProperty('rate', rate - value)



    def get_caprica_text_response(self):
        '''
        def get_caprica_text_response(self)

        Parameters:
        -----------
            param1 : self
                Denotes it as being a member of SentienceScreen(Screen)
                class.

        Attributes
        ----------
            self.username
                Contains the username that user entered if he/she entered
                one. The length of self.username is checked to see if it's
                less than or equal to zero. If it is it means that the user
                never set a username and a default value of "User: " is set
                This value along with the users response to the chat bot and
                'Caprica: ' and then the chat bots response are displayed
                in text in self.ids.view_port TextInput Widget.


            temp
                temp is used to store the response from the chat bot
                temporarily.

            self.master_log
                The string 'Caprica: ' and the value contained in temp are
                added to the end of the string with a new line
                character.

            self.ids.view_port
                This is the main view port TextInput Widget here we briefly
                store the User text response and chat box text response.

            self.ids.user_input
                The string contained in the user_input TextInput Widget
                is cleared and the hint_text reset.


        Members
        -------
            self.chatbot.get_response(self.user_input)
                Obtains the response from the chat bot which is generated
                to best fit the user response which is passed into this
                function as a parameter. It then returns the chat bots
                response and is in this case stored in the temp variable.
                This is all type casted to str() to ensure type safety.

        Private Members
        ---------------
            self.__append_file(self, words, path)
                Is called to append the Chat bot responses to the text file
                Caprica_Statements.txt


        Returns
        -------
            return None


        Exceptions
        ----------
        OSError
            The OSError can occur due to numerous reasons.
            What I'm primarily concerned with here however
            is import statements, incompatible Operating
            systems, and bad system calls. The exception
            if it occurs is handled and logged in an error
            log text file.

        IOError
            The IOError can occur due to many reasons.
            My primary concern is file manipulation. The
            improper opening/closing/writing to files. If
            the exception occurs it's handled and logged; in
            an error log text file.

        RunTimeError
            The RunTimeError error here is checking to make sure that
            the chat bot doesn't die. Essentially I just need to make
            sure that it completes and executes the python text to speech
            functions in a manner that doesn't cause a fatal exception. If
            something does occur the exception will be handled and logged to
            an error log text file.

        ValueError
            Ensures that values passed to the chat bot are appropriate.
            And if for some reason one isn't the exception will be handled
            and logged to an error log text file.


        Notes
        -----
		    **This function is deprecated and has been replaced
			with get_caprica_response**

            This function is called when self.audio_disabled == True

            It first checks the operating system.
            If sys.platform.startswith('linux') == True it executes
            the if statement intended for the linux operating system.

            Otherwise if sys.platform == False it executes the if
            statements intended for the windows operating system.

            It then enters the appropriate if statement
            and the user response that's stored in
            self.user_input is passed into
            self.chatbot.get_response(self.user_input) the generated
            response is then stored in the temp string variable.

            We then call self.__append_file('') we give it a new line
            character and the data stored in the temp variable and pass
            to the path parameter the apropriate path which is based off
            of the users operating system.

            We then set the string of the view_port TextInput Widget to be
            'Username: ' + user_response
            'Caprica: ' + caprica_response

            We then clear the seld.ids.user_input.text field
            (user_input TextInput Widget). So that the
            hint_text property is reset.
        '''
        try:
            if sys.platform.startswith('linux'):
                if len(self.username) <= 0:
                    self.username = 'User'
                temp = str(self.chatbot.get_response(self.user_input))
                self.__append_file('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + temp, '/home/' + str(os.getlogin()) + '/.SentienceFiles/Caprica_Statements.txt')
                self.master_log += '\nCaprica: ' + temp
                self.ids.view_port.text = self.username + ': ' + self.user_input + '\nCaprica: ' + temp
                self.ids.user_input.text = ''
            elif sys.platform == 'win32':
                if len(self.username) <= 0:
                    self.username = 'User'
                temp = str(self.chatbot.get_response(self.user_input))
                self.__append_file('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + temp, 'C://SentienceFiles//Caprica_Statements.txt')
                self.ids.view_port.text = self.username + ': ' + self.user_input + '\nCaprica: ' + temp
                self.master_log += '\nCaprica: ' + temp
                self.ids.user_input.text = ''
        except OSError as a:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: get_caprica_text_response ' + '\nOSError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: get_caprica_text_response ' + '\nOSError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except IOError as b:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: get_caprica_text_response ' + '\nIOError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: get_caprica_text_response ' + '\nIOError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except RuntimeError as c:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: get_caprica_text_response ' + '\nRuntimeError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: get_caprica_text_response ' + '\nRuntimeError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except ValueError as d:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: get_caprica_text_response ' + '\nValueError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: get_caprica_text_response ' + '\nValueError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None



    def get_user_voice_response(self):
        '''
        def get_user_voice_response(self)

        Parameters:
        -----------
            param1 : self
                Denotes it as being a member of
				SentienceScreen(Screen) class.

        Attributes
        ----------
            self.voice_disabled
	            Checks to see if self.voice_disabled == True or
			    False If self.voice_disabled == True a warning
			    message is sent to the user in forming them that
			    they need to click on the red microphone image;
			    before clicking the "Record user" button. The
			    warning message is sent is displayed in
			    self.ids.view_port. If self.voice_disabled == False
			    self.voice_enabled == True and the user can begin
			    recording their voice via a microphone.

            self.ids.view_port
	            A warning message is displayed in the view_port
			    TextInput Widget informing the user they need to
			    first enable the voice option before they can use
			    their microphone to speak with the chat bot.

            self.mic
	            self.mic = sr.Microphone() this is what enables us to use
			    the microphone to speak with the chat bot.

            source
	            When we begin recording the users voice we do so in a
				loop we open that loop (open the microphone) as source.
				All the audio detected is piped into source and then
				stored in the audio variable.

            audio
                The recorded sound will be streamed to the function
		        self.record.listen(source) all audio picked up will
		        be saved in the audio variable for later transcription
		        into a string.

	        temp
	            The data contained in the audio variable is passed to
				the function self.record.recognize_sphinx(source) which
				will then transcribe the audio file and store the
				returned string in the temp variable.

	        self.master_log
                A new line character, the users username and the string
				stored in the temp variable are then appended to the
				self.master_log string.

        Members
        -------
            self.record.listen(source)
                This function which is derived from
		        speech_recognition.Recognizer()is called when we open
				the loop for recording the users voice response. Source
				is the stream for the microphone. The data contained in
				source is piped into this function as its parameter and
				then returned to the audio variable.

	        self.record.recognize_sphinx(audio)
	            The data contained in the audio variable is sent to this
		        function for transcription into a string. The data once
		        transcribed is returned to the temp variable for later
		        manipulation.

            self.get_caprica_voice_response(string)
	            This function is called after the users voice response
				has been transcribed and stored in the temp variable.
				The temp variable is then passed into this function as
				its parameter which then obtains the most accurate result
				possible for the chat bot to respond to the user. This
				response is then spoken by the self.caprica_speak()
				function.

        Private Members
        ---------------
            self.__append_file(string, path)
	            This function is called to append the users transcribed
		        voice response to the User_Statements.txt file along with
                a new line character.

        Returns
        -------
            return None


        Exceptions
        ----------
            OSError
                The OSError can occur due to numerous reasons.
                What I'm primarily concerned with here however
                is import statements, incompatible Operating
                systems, and bad system calls. The exception
                if it occurs is handled and logged in an error
                log text file.

            IOError
                The IOError can occur due to many reasons.
                My primary concern is file manipulation. The
                improper opening/closing/writing to files. If
                the exception occurs it's handled and logged; in
                an error log text file.

            RunTimeError
                The RunTimeError error here is checking to make sure
				that the chat bot doesn't die. Essentially I just need
				to make sure that it completes and executes the python
				text to speech functions in a manner that doesn't cause
				a fatal exception. If something does occur the exception
				will be handled and logged to an error log text file.

            ValueError
                Ensures that values passed to the chat bot are
				appropriate. And if for some reason one isn't the exception
				will be handled and logged to an error log text file.

	        speech_recognition.Recognizer().UnknownValueError
	            This exception can occur in a variety of ways but the
				primary concern for me. IS when the Recognizer() is
				unable to interpret the users voice response. If this
				exception occurs it's handled logged to an error logs
				text file.

	        speech_recognition.Recognizer().RequestError
	            This exception can occur for a variety of reasons but
				the primary concern is when we're unable to open the
				microphone. That is to say when no microphone is detected.
				If it occurs the exception is handled and logged in an
				error logs text file.


        Notes
        -----
		    **This function is deprecated and has been replaced
			with get_caprica_response**

            When this function is called we first check to see if the
			user is running a Linux or windows based operating system.

            If sys.platform.startswith('linux') == True then the user
			is using a Linux Operating system and the appropriate if
			statements will execute.

            Otherwise if sys.platform.startswith('win') == True
            Then the user is using a windows based operating system
            and the appropriate if statements will execute.

            We next to see if self.voice_disabled == True if it is
            True we issue a warning to the user telling them to first
            click on the "Enable/Disable Microphone" button which
            is represented by a red microphone when disabled or a blue
            microphone when enabled. This warning message is sent to the
            view_port TextInput Widget.

            We then open the microphone for listening and when audio is
            detected it's piped into the recognizers listening function.
            When no more audio is detected its stored in the audio
			variable. The loop then ends.

            We then call the function to transcribe the audio into a
			string that data is then returned to the temp variable.

            We then append the contents of the temp variable and a
			new line character to the User_Statements.txt file.

            Next we append a new line character, the users Username,
			and the contents of temp to the self.master_log string.

            Finally, we pass the temp variable to
            self.get_caprica_voice_response(str(temp)) which then
            calls the self.caprica_speak() function to speak the
            generated response to the user.
        '''
        try:
            if sys.platform.startswith('linux'):
                if self.voice_disabled:
                    self.ids.view_port.text = 'Please activate the voice option by clicking on the red microphone button'
                    return None
                with self.mic as source:
                    audio = self.record.listen(source)
                temp = self.record.recognize_sphinx(audio)
                self.__append_file('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + temp, '/home/' + str(os.getlogin()) + '/.SentienceFiles/User_Statements.txt')
                self.master_log += '\n' + self.username + ': ' + temp

                self.get_caprica_voice_response(str(temp))
            elif sys.platform.startswith('win'):
                if self.voice_disabled:
                    self.ids.view_port.text = 'Please activate the voice option by clicking on the red microphone button'
                    return None
                with self.mic as source:
                    audio = self.record.listen(source)
                temp = self.record.recognize_sphinx(audio)
                self.__append_file('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + temp, 'C://SentienceFiles//User_Statements.txt')
                self.master_log += '\n' + self.username + ': ' + temp
                self.get_caprica_voice_response(str(temp))
        except self.mic.UknownValueError as a:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: get_user_voice_response ' + '\nspeech_recognition.Recognizer.UnknownValueError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: get_user_voice_response ' + '\nspeech_recognition.Recognizer.UnknownValueError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            self.caprica_speak("UnknowValueError: " + str(a) + " I'm sorry, I didn't understand. Can you please repeat what you just said?")
            self.get_user_voice_response()
        except self.record.RequestError as b:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: get_user_voice_response ' + '\nspeech_recognition.Recognizer.RequestError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: get_user_voice_response ' + '\nspeech_recognition.Recognizer.RequestError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return self.record.recognize_sphinx(audio)
        except OSError as c:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: get_user_voice_response ' + '\nOSError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: get_user_voice_response ' + '\nOSError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except IOError as d:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: get_user_voice_response ' + '\nIOError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: get_user_voice_response ' + '\nIOError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except RuntimeError as e:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: get_user_voice_response ' + '\nRuntimeError: ' + str(e) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: get_user_voice_response ' + '\nRuntimeError: ' + str(e) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except ValueError as f:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: get_user_voice_response ' + '\nValueError: ' + str(f) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: get_user_voice_response ' + '\nValueError: ' + str(f) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None



    def get_caprica_voice_response(self, words):
        '''
            def get_caprica_voice_response(self, words)

            Parameters:
            -----------
                param1 : self
                    Denotes it as being a member of
                    SentienceScreen(Screen) class.

                param2 : words
                    String variable containing the users
                    response which will be used by the
                    chat bot to generate an appropriate
                    response to the users comment.

            Attributes
            ----------
	            temp
	                The response generated by the chat bot is returned
		            to the temp variable where it's stored as a string
		            for later manipulation.

	            self.master_log
                    A new line character plus the string 'Caprica: ' and
					the chat bots response are appended to the end of
					the self.master_log string variable.

            Members
            -------
                self.chatbot.get_response(words)
	                This function is called from a variety of
					locations. The string value passed to
					self.chatbot.get_response(words) is the users
					response to the chat bot. It's used to locate, and
					generate the best possible response from the chat bot.
					That response is then returned and stored in the
					variable temp.

	            self.caprica_speak(words)
	                This function is called from a variety of locations.
					In this case it occurs when self.audio_enabled == True
					Once the function self.get_caprica_voice_response()
					has been called the users response gets sent to
					self.chatbot.get_response(words) which then causes
					the chat bot to come up with an appropriate response.
					Which is then returned to temp, temp is then passed
					to self.caprica_speak(temp) the string contained in
					the temp variable is then read by the systems speech
					to text software.

            Private Members
            ---------------
                self.__append_file(string, path)
	                This function is called to append the chat bots
					voice response to the Caprica_Statements.txt file
					along with a new line character.

            Returns
            -------
                return None

            Exceptions
            ----------
                OSError
                    The OSError can occur due to numerous reasons.
                    What I'm primarily concerned with here however
                    is import statements, incompatible Operating
                    systems, and bad system calls. The exception
                    if it occurs is handled and logged in an error
                    log text file.

                IOError
                    The IOError can occur due to many reasons.
                    My primary concern is file manipulation. The
                    improper opening/closing/writing to files. If
                    the exception occurs it's handled and logged; in
                    an error log text file.

                RunTimeError
                    The RunTimeError error here is checking to make sure
					that the chat bot doesn't die. Essentially I just
					need to make sure that it completes and executes the
					python text to speech functions in a manner that
					doesn't cause a fatal exception. If something does
					occur the exception will be handled and logged to
                    an error log text file.

                ValueError
                    Ensures that values passed to the chat bot are
					appropriate. And if for some reason one isn't the
					exception will be handled and logged to an error
					log text file.

            Notes
            -----
			    **This function is deprecated and has been replaced
			     with get_caprica_response**

                When this function is called we first check to see
				what operating system the user is running. If
				system.startswith('linux') == True the user is
				using a Linux based operating system. The appropriate
                if statement is then executed.

                Otherwise if sys.platform.startswith('win') == True
                the user is using a windows based operating system. The
                appropriate if statement is then executed.

                We then call the function self.chatbot.get_response(words)
                which is type casted to a string variable for safety. The
                result of this function returns a generated response from
                the chat bot and stores in the variable temp.

                We then call the function self.__append_file(temp, path)
                which appends a new line character and the contents of
				the temp variable to the Caprica_Statements.txt file.

                We next append the string 'Caprica: ' along with a new
				line character and the contents of the temp variable to
				the end of the self.master_log string variable.

                Finally we call self.caprica_speak(temp) and pass the
				temp variable to it. So that the text to speech software
                can speak the generated response from the chat bot
				contained in the temp variable.
        '''
        try:
            if sys.platform.startswith('linux'):
                temp = str(self.chatbot.get_response(words))
                self.__append_file('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + temp, '/home/' + str(os.getlogin()) + '/.SentienceFiles/Caprica_Statements.txt')
                self.master_log += '\nCaprica: ' + temp
                self.ids.view_port.text = self.username + ': ' + words + '\nCaprica: ' + temp #
                self.caprica_speak(temp)

            elif sys.platform.startswith('win'):
                temp = str(self.chatbot.get_response(words))
                self.__append_file('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + temp,'C://SentienceFiles//Caprica_Statements.txt')
                self.master_log += '\nCaprica: ' + temp
                self.ids.view_port.text = self.username + ': ' + words + '\nCaprica: ' + temp #
                self.caprica_speak(temp)
        except OSError as a:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: get_vaprica_voice_response ' + '\nOSError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: get_caprica_voice_response ' + '\nOSError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
                return None
        except IOError as b:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: get_vaprica_voice_response ' + '\nIOError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: get_caprica_voice_response ' + '\nIOError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
                return None
        except RuntimeError as c:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: get_vaprica_voice_response ' + '\nRuntimeError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: get_caprica_voice_response ' + '\nRuntimeError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
                return None
        except ValueError as d:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: get_vaprica_voice_response ' + '\nValueError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: get_caprica_voice_response ' + '\nValueError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
                return None



    def set_gender(self):
        '''
            def set_gender(self)

            Parameters:
            -----------
                param1 : self
                    Denotes it as being a member of SentienceScreen(Screen) class.

            Attributes
            ----------
                voices
                    This will hold a list of all the systems text to speech
                    voices. Ie, All of the voices installed in your tts software
                    will be available, but I've chosen the voice for you. The list
                    is sourced from the self.engine.getProperty('voice') call.



                Members
                -------
                    self.engine.setProperty('voice', 'english+f2')
                        This function is called in order to select and
                        set a specific property of self.engine() which
                        is the pyttsx3 tts library. In this call we're
                        setting the voice property (Female, male, etc..)
                        to female with the second parameter string. This
                        handled in a slightly different manner between
                        Linux and Windows, though the difference is
                        minimal. It's different because the Windows voice
                        file is the registry key and it's easier to
                        manipulate voice properties as a list.

                    self.engine.getProperty('voices')
                        This call returns the list of available voices
                        to the voices string.


            Private Members
            ---------------

            Returns
            -------
                return None

            Exceptions
            ----------
                OSError
                    The OSError can occur due to numerous reasons.
                    What I'm primarily concerned with here however
                    is import statements, incompatible Operating
                    systems, and bad system calls. The exception
                    if it occurs is handled and logged in an error
                    log text file.

                IOError
                    The IOError can occur due to many reasons.
                    My primary concern is file manipulation. The
                    improper opening/closing/writing to files. If
                    the exception occurs it's handled and logged; in
                    an error log text file.

                RunTimeError
                    The RunTimeError error here is checking to make
                    sure that the chat bot doesn't die. Essentially
                    I just need to make sure that it completes and
                    executes the python text to speech functions in a
                    manner that doesn't cause a fatal exception. If
                    something does occur the exception will be handled
                    and logged to an error log text file.

                ValueError
                    Ensures that values passed to the chat bot are
                    appropriate. And if for some reason one isn't
                    the exception will be handled and logged to an
                    error log text file.

            Notes
            -----
                This function is called in
                SentienceScreen().__init__(self, **kwargs)  call. the
                purpose of this function is to change the default text to
                speech voice to female. The chat bot is named Caprica
                and Caprica is a female.

                When the function first runs we check to see what
                operating system the user is running. If
                sys.platform.startswith('linux') == True then the user
                is running a Linux based operating system. The appropriate
                if statement is then executed.

                Otherwise if sys.platform.startswith('win') == True then
                the user is running a windows based operating system.
                The appropriate if statements are then executed.

                Once we've entered the specific relative if statement.
                We call the function self.getProperty('voices') wish
                contains a list of all the available tts voice objects.
                This list is returned to the variable voices.

                We then call the function
                self.setProperty('voice', + string or list). You can
                manipulate this setting in a variety of ways. with a
                string with a list element etc.. Once this has been
                called and run the voice is set.
        '''
        try:
            if sys.platform == 'linux':
                voices = self.engine.getProperty('voices')
                self.engine.setProperty('voice', 'english+f2')
            if sys.platform == 'win32':
                voices = self.engine.getProperty('voices')
                self.engine.setProperty('voice', voices[0].id)
        except OSError as a:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: set_gender ' + '\nOSError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: set_gender ' + '\nOSError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except IOError as b:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: set_gender ' + '\nIOError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: set_gender ' + '\nIOError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except RuntimeError as c:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: set_gender ' + '\nRuntimeError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: set_gender ' + '\nRuntimeError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except ValueError as d:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: set_gender ' + '\nValueError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: set_gender ' + '\nValueError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None



    def set_speech_rate(self):
        '''
            def set_speech_rate(self)

            Parameters:
            -----------
                param1 : self
                    Denotes it as being a member of
                    SentienceScreen(Screen) class.

            Attributes
            ----------
                rate
                    The variable rate is used to store the integer
                    value of the speech rate property belonging to
                    self.engine. This rate determines the rate of
                    words spoken per minute. I manually set this
                    rate to rate - 40.

            Members
            -------
                self.engine.getProperty('rate')
                    We call this function to get the current rate of
                    speech. This rate of speech is words per minute
                    spoken. We store this value in the variable rate.

                self.engine.setProperty('rate', rate-40)
                    We call this function to set the rate of words per
                    spoken per minute. The rate of words spoken per
                    minute is set to current_rate - 40.

            Private Members
            ---------------
                None

            Returns
            -------
                return None

            Exceptions
            ----------
                OSError
                    The OSError can occur due to numerous reasons.
                    What I'm primarily concerned with here however
                    is import statements, incompatible Operating
                    systems, and bad system calls. The exception
                    if it occurs is handled and logged in an error
                    log text file.

                IOError
                    The IOError can occur due to many reasons.
                    My primary concern is file manipulation. The
                    improper opening/closing/writing to files. If
                    the exception occurs it's handled and logged; in
                    an error log text file.

                RunTimeError
                    The RunTimeError error here is checking to make
                    sure that the chat bot doesn't die. Essentially
                    I just need to make sure that it completes and
                    executes the python text to speech functions in
                    a manner that doesn't cause a fatal exception. If
                    something does occur the exception will be handled
                    and logged to an error log text file.

                ValueError
                    Ensures that values passed to the chat bot are
                    appropriate. And if for some reason one isn't
                    the exception will be handled and logged to an
                    error log text file.

            Notes
            -----
                This function is called in SentienceScreen().__init__(self, **kwargs)
                call. the purpose of this function is to change the default text to speech
                rate of words spoken per minute.

                When the function first runs we check to see what operating system the
                user is running. If sys.platform.startswith('linux') == True then
                the user is running a Linux based operating system. The appropriate if
                statement is then executed.

                Otherwise if sys.platform.startswith('win') == True then the user is
                running a windows based operating system. The appropriate if statements
                are then executed.

                Once we've entered the specific relative if statement. We call the
                function self.getProperty('rate') returns the current rate and stores it
                in the variable rate.

                We then call the function self.setProperty('rate', integer_value).
                You can manipulate this setting in a variety of ways. You can
                either set the integer parameter with an integer variable. Or
                preform a mathematical operation on the current_rate like I have.
        '''
        try:
            if sys.platform.startswith('linux'):
                rate = self.engine.getProperty('rate')
                self.engine.setProperty('rate', rate-40)
                #Default rate = 160
            elif sys.platform.startswith('win'):
                rate = self.engine.getProperty('rate')
                self.engine.setProperty('rate', rate-40)
        except OSError as a:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: set_speech_rate ' + '\nOSError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: set_speech_rate ' + '\nOSError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except IOError as b:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: set_speech_rate ' + '\nIOError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: set_speech_rate ' + '\nIOError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except RuntimeError as c:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: set_speech_rate ' + '\nRuntimeError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: set_speech_rate ' + '\nRunetimeError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except ValueError as d:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: set_speech_rate ' + '\nValueError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: set_speech_rate ' + '\nValueError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None



    def caprica_speak(self, words):
        '''
        def caprica_speak(self, words)

        Parameters:
        -----------
            param1 : self
                Denotes it as being a member of
                SentienceScreen(Screen) class.

            param2 : words
                The parameter words contains the chat bots
                response to the user.


        Attributes
        ----------
            self.ids.user_input
                The string contained in the user_input TextInput
                Widget is cleared and the hint_text is reset.




        Members
        -------
            self.onEnd(self)
                This function is called every time that the
                self.caprica_speak() function has been called. Once
                self.caprica_speak() finishes speaking the passed string.
                self.onEnd() is fired because it's bound to the
                'finished-utterance' event. This ends the speaking
                loop and empties the event queue.

            self.engine.say(str(words))
                This function is called from within the
                self.caprica_speak() function. this is the function
                which access the systems tts software and actually
                verbally 'speaks' the string passed to it.

            self.engine.startLoop()
                This function is called to ensure that the string passed
                to self.caprica_speak() is fully spoken. Ie, it ensures
                that the entire string is read before the event
                'finished-utterance' is fired.

        Private Members
        ---------------
            None

        Returns
        -------
            return None

        Exceptions
        ----------
            OSError
                The OSError can occur due to numerous reasons.
                What I'm primarily concerned with here however
                is import statements, incompatible Operating
                systems, and bad system calls. The exception
                if it occurs is handled and logged in an error
                log text file.

            IOError
                The IOError can occur due to many reasons.
                My primary concern is file manipulation. The
                improper opening/closing/writing to files. If
                the exception occurs it's handled and logged; in
                an error log text file.

            RunTimeError
                The RunTimeError error here is checking to make sure
                that the chat bot doesn't die. Essentially I just need
                to make sure that it completes and executes the python
                text to speech functions in a manner that doesn't cause
                a fatal exception. If something does occur the exception
                will be handled and logged to an error log text file.

            ValueError
                Ensures that values passed to the chat bot are
                appropriate. And if for some reason one isn't the
                exception will be handled and logged to an error
                log text file.
        Notes
        -----
            We call this function if self.auido_enabled == True
            and or if self.voice_enabled == True. The purpose
            of this function is to access the programs tts
            software to verbally speak the string passed to it.

            We start off by checking the users operating system.

            If sys.platform.startswith('linux') == True
            the user is using a Linux based operating system and
            the appropriate if statements are executed.

            Otherwise if sys.platform.startswith('win') == True
            then the user is running a windows based operating
            system and the appropriate if statements are executed.

            We then sen a string to self.engine.say() which access
            the systems tts software and reads the string it's sent.
            Which is in this case the response of the chat bot.

            self.engine.say(str(words))
            We then call self.engine.startLoop() to start a loop
            ensuring that the string(s) sent to self.caprica_speak()
            are all read.

            Finally, we clear the user_input TextInput Widget
            resetting its hint_text property as well.
        '''
        try:
            if sys.platform.startswith('linux'):
                self.engine.say(str(words))
                self.engine.startLoop()
                self.ids.user_input.text = ''
            if sys.platform.startswith('win'):
                self.engine.say(str(words))
                self.engine.startLoop()
                self.ids.user_input.text = ''
        except OSError as a:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: caprica_speak ' + '\nOSError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: caprica_speak ' + '\nOSError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except IOError as b:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: caprica_speak ' + '\nIOError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: caprica_speak ' + '\nIOError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except RuntimeError as c:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: caprica_speak ' + '\nRuntimeError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: caprica_speak ' + '\nRuntimeError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except ValueError as d:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: caprica_speak ' + '\nValueError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: caprica_speak ' + '\nValueError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None



    def onEnd(self, name, completed):
        '''
        def onEnd(self, name, completed)
            We call this function when self.caprica_speak(string)
            ends. To be more precise it's called every time that
            self.engine.say(string) is finished. This function
            kills the event loop and empties the event queue.

        Parameters:
        -----------
            param1 : self
                Denotes it as being a member of SentienceScreen(Screen)
                class.

            param2 : name
                The parameter name is in reference to the name
                of the event that self.onEnd() is bound to. In
                this case the event is 'finished-utterance'.

            param3 : completed
                The parameter completed is in reference to the
                function. In this case the calling function. Which
                is self.engine.say(string).


        Attributes
        ----------
            None

        Members
        -------
            self.engine.endLoop()
                This is function is called when self.caprica_speak()
                finishes speaking the string passed to it. The purpose
                of this function is to empty the event queue and Ensures
                that all strings have been processed in said queue.
                It relates to self.engine.say(string).

        Private Members
        ---------------
            None

        Returns
        -------
            return None

        Exceptions
        ----------
            OSError
                The OSError can occur due to numerous reasons.
                What I'm primarily concerned with here however
                is import statements, incompatible Operating
                systems, and bad system calls. The exception
                if it occurs is handled and logged in an error
                log text file.

            IOError
                The IOError can occur due to many reasons.
                My primary concern is file manipulation. The
                improper opening/closing/writing to files. If
                the exception occurs it's handled and logged; in
                an error log text file.

            RunTimeError
                The RunTimeError error here is checking to make sure that
                the chat bot doesn't die. Essentially I just need to make
                sure that it completes and executes the python text to
                speech functions in a manner that doesn't cause a fatal
                exception. If something does occur the exception will be
                handled and logged to an error log text file.

            ValueError
                Ensures that values passed to the chat bot are appropriate.
                And if for some reason one isn't the exception will be
                handled and logged to an error log text file.

            Notes
            -----
                The purpose of this function is simply to terminate the
                self.caprica_speak() function. Aside from the Operating
                system check and the exceptions; there is only one line
                which is the terminating function for the
                self.engine.startLoop() function.
        '''
        try:
            if sys.platform.startswith('linux'):
                self.engine.endLoop()
            elif sys.platform.startswith('win'):
                self.engine.endLoop()
        except OSError as a:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: onEnd ' + '\nOSError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: onEnd ' + '\nOSError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except IOError as b:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: onEnd ' + '\nIOError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: onEnd ' + '\nIOError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except RuntimeError as c:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: onEnd ' + '\nRuntimeError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: onEnd ' + '\nRuntimeError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except ValueError as d:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: onEnd ' + '\nValueError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: onEnd ' + '\nValueError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None



    def clear_viewport(self):
        '''
        def clear_viewport(self):
            We call this function a few times. It's
            probably the simplest one here to understand.
            It's purpose is only to reset the text in the
            view_port TextInput Widget to an empty '' string.


        Parameters:
        -----------
            param1 : self
                Denotes it as being a member of SentienceScreen(Screen)
                class.




        Attributes
        ----------
            self.ids.view_port
                view_port TextInput Widget is one of our main TextInput Widgets
                which displays the text conversations between the user and the
                chat bot.

        Members
        -------
            None

        Private Members
        ---------------
            None

        Returns
        -------
            return None

         Exceptions
        ----------
            OSError
                The OSError can occur due to numerous reasons.
                What I'm primarily concerned with here however
                is import statements, incompatible Operating
                systems, and bad system calls. The exception
                if it occurs is handled and logged in an error
                log text file.

            IOError
                The IOError can occur due to many reasons.
                My primary concern is file manipulation. The
                improper opening/closing/writing to files. If
                the exception occurs it's handled and logged; in
                an error log text file.

            RunTimeError
                The RunTimeError error here is checking to make sure that
                the chat bot doesn't die. Essentially I just need to make
                sure that it completes and executes the python text to speech
                functions in a manner that doesn't cause a fatal exception. If
                something does occur the exception will be handled and logged to
                an error log text file.

            ValueError
                Ensures that values passed to the chat bot are appropriate.
                And if for some reason one isn't the exception will be handled
                and logged to an error log text file.

        Notes
        -----
            The purpose of this function is only to reset the text
            in the view_port TextInput Widget to an empty '' string.
            Which also has the effect of resetting the hint_text
            property.
        '''
        self.ids.view_port.text = ''



    def create_user_profile(self):
        '''
        def create_user_profile(self)
            We call this function after the user has entered
            his/her desired username. It's only purpose is to
            check if the length of the string that stores the
            username is greater than 0. If it's not it sets a
            default value to the username of 'User: '.
            If it is greater than zero this function calls the
            self.caprica_speak(string) function and says
            'Hello ' + self.username

        Parameters:
        -----------
            param1 : self
                Denotes it as being a member of SentienceScreen(Screen)
                class.

        Attributes
        ----------
            self.username
                This is the string variable that contains the users
                desired input username. If no username is set a
                default value of 'User: ' is set to self.username

        Members
        -------
            self.caprica_speak(string)
                We call this function with the string
                'Hello' + self.username Essentially the call to
                self.caprica_speak(string) from the function
                self.create_user_profile(self) is just a way to
                personalize the experience and deliver a verbal greeting
                to the user.

        Private Members
        ---------------
            None

        Returns
        -------
            return None

        Exceptions
        ----------
            OSError
                The OSError can occur due to numerous reasons.
                What I'm primarily concerned with here however
                is import statements, incompatible Operating
                systems, and bad system calls. The exception
                if it occurs is handled and logged in an error
                log text file.

            IOError
                The IOError can occur due to many reasons.
                My primary concern is file manipulation. The
                improper opening/closing/writing to files. If
                the exception occurs it's handled and logged; in
                an error log text file.

            RunTimeError
                The RunTimeError error here is checking to make sure
                that the chat bot doesn't die. Essentially I just need
                to make sure that it completes and executes the python
                text to speech functions in a manner that doesn't cause
                a fatal exception. If something does occur the exception
                will be handled and logged to an error log text file.

            ValueError
                Ensures that values passed to the chat bot are
                appropriate. And if for some reason one isn't the
                exception will be handled and logged to an error log
                text file.
        Notes
        -----
            This functions purpose is just a way to personalize the
            experience and deliver a verbal greeting to the user.

            As always we start off with a system check.
            If sys.startswith('linux') == True then we know
            that the user is using a Linux based operating system
            and the appropriate if statement is executed.

            Otherwise if sys.platform.startswith('win') == True
            we know the user is using a windows based operating system
            and the appropriate if statements are executed.

            We then check the length of self.username
            len(self.username) <= 0 if this is True
            we know that the user did not set a username
            and we set a default value for self.username of
            'User: '.

            If len(self.username) > 0 we know that the user has entered
            as username and we call
            self.caprica_speak('Hello' + self.username) to deliver a
            personal greeting to the user.
        '''
        try:
            if sys.platform.startswith('linux'):
                if len(self.username) > 0:
                    self.caprica_speak('Hello ' + self.username)
                elif len(self.username) <= 0:
                    self.username = 'User'
            elif sys.platform.startswith('win'):
                if len(self.username) > 0:
                    self.caprica_speak('Hello ' + self.username)
                elif len(self.username) <= 0:
                    self.username = 'User'
        except OSError as a:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: create_user_profile ' + '\nOSError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: create_user_profile ' + '\nOSError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except IOError as b:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: create_user_profile ' + '\nIOError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: create_user_profile ' + '\nIOError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except RuntimeError as c:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: create_user_profile ' + '\nRunetimeError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: create_user_profile ' + '\nRunetimeError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except ValueError as d:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: create_user_profile ' + '\nValueError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: create_user_profile ' + '\nValueError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None



    def set_enable_disable_audio(self):
        '''
        def set_enable_disable_audio(self)
            This function is called when the user clicks on the
            enable/disable audio button; which is represented by
           the red or blue speaker button.

        Parameters:
        -----------
            param1 : self
                Denotes it as being a member of SentienceScreen(Screen)
                class.

        Attributes
        ----------
            self.audio_disabled
                If self.audio_disabled == True then the chat bots
                audio function is disabled. This means that the chat
                bot can only communicate with the user via text. If
                self.audio_disabled == True it's represented by a
                red speaker image on the menu bar. Clicking on the
                red speaker image will activate the audio and turn
                the red speaker image blue.

            self.audio_enabled
                If self.audio_enabled == True then the chat bot can
                access the systems text to speech software and
                verbally read the string passed to
                self.caprica_speak(self, words) back to the user. If
                self.audio_enabled == True; it's represented by a blue
                speaker image on the menu bar. Clicking on the blue
                speaker will disable the audio and turn the image of
                the speaker red.

            self.ids.user_input
                If self.audio_enabled == True or
                self.audio_disabled == True we set the
                opacity of the user_input TextInput widget
                to 1 making it visible. By default it's already
                visible but if the user enables the microphone
                option; all widgets not on the menu bar have their
                opacity set to 0.

            self.ids.view_port
                If self.audio_enabled == True or
                self.audio_disabled == True we set the
                opacity of the view_port TextInput widget
                to 1 making it visible. By default it's already
                visible but if the user enables the microphone
                option; all widgets not on the menu bar have their
                opacity set to 0.

            self.ids.audio_enable_disable
                After the user has clicked on either the red or
                blue speaker and the appropriate if statements
                are executed based on the users operating system.
                We change the icon property of
                self.ids.audio_enable_disable and set the icon to the
                appropriate image on the menu bar.


        Members
        -------
            self.caprica_speak(string)
                We call this function to alert the user
                to the current status of the audio function.
                If the audio has been enabled the user is
                informed that the audio is now active. If
                the audio has been disabled the user is informed
                that the audio feature has been disabled.

        Private Members
        ---------------
            None

        Returns
        -------
            return None

        Exceptions
        ----------
            OSError
                The OSError can occur due to numerous reasons.
                What I'm primarily concerned with here however
                is import statements, incompatible Operating
                systems, and bad system calls. The exception
                if it occurs is handled and logged in an error
                log text file.

            IOError
                The IOError can occur due to many reasons.
                My primary concern is file manipulation. The
                improper opening/closing/writing to files. If
                the exception occurs it's handled and logged; in
                an error log text file.

            RunTimeError
                The RunTimeError error here is checking to make sure
                that the chat bot doesn't die. Essentially I just need
                to make sure that it completes and executes the python
                text to speech functions in a manner that doesn't cause
                a fatal exception. If something does occur the exception
                will be handled and logged to an error log text file.

            ValueError
                Ensures that values passed to the chat bot are
                appropriate. And if for some reason one isn't the
                exception will be handled and logged to an error log
                text file.

        Notes
        -----
            This function is called when the user clicks
            either the blue or red speaker image on the menu bar.

            The users operating system is then checked. If
            sys.platform.startswith('linux') == True then
            the user is using a Linux based operating system.
            The appropriate if statement is then executed.

            Otherwise if sys.platform.startswith('win') == True
            then the user is using a windows based operating system
            and the appropriate if statements are executed.

            If self.audio_disabled == True
            the audio option is disabled and the speaker image is red.
            Clicking on the red speaker image will enable the audio
            feature.

            If self.audio_enabled == True the audio option is active
            clicking on the blue speaker image will disable the audio
            feature.
        '''
        try:
            if sys.platform.startswith('linux'):
                if self.audio_disabled:
                    self.audio_enabled = True
                    self.audio_disabled = False
                    self.ids.user_input.opacity = 1
                    self.ids.view_port.opacity = 1
                    self.caprica_speak('Capricas audio mode is now enabled. Type into the text box begin your conversation.')
                elif self.audio_enabled:
                    self.audio_enabled = False
                    self.audio_disabled = True
                    self.ids.user_input.opacity = 1
                    self.ids.view_port.opacity = 1
                    self.caprica_speak('Capricas audio mode is now disabled. Type into the text box begin your conversation.')
            elif sys.platform.startswith('win'):
                if self.audio_disabled:
                    self.audio_enabled = True
                    self.audio_disabled = False
                    self.ids.user_input.opacity = 1
                    self.ids.view_port.opacity = 1
                    self.caprica_speak('Capricas audio mode is now enabled. Type into the text box begin your conversation.')
                elif self.audio_enabled:
                    self.audio_enabled = False
                    self.audio_disabled = True
                    self.ids.user_input.opacity = 1
                    self.ids.view_port.opacity = 1
                    self.caprica_speak('Capricas audio mode is now disabled. Type into the text box begin your conversation.')
        except OSError as a:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: set_enable_disable_audio ' + '\nOSError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: set_enable_disable_audio ' + '\nOSError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except IOError as b:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: set_enable_disable_audio ' + '\nIOError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: set_enable_disable_audio ' + '\nIOError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except RuntimeError as c:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: set_enable_disable_audio ' + '\nRuntimeError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: set_enable_disable_audio ' + '\nRuntimeError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except ValueError as d:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: set_enable_disable_audio ' + '\nValueError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: set_enable_disable_audio ' + '\nValueError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None



    def set_enable_disable_voice(self):
        '''
        def set_enable_disable_voice(self)
            This function is called when the user clicks on the
            enable/disable voice button; which is represented by
            the red or blue microphone button.

        Parameters:
        -----------
            param1 : self
                Denotes it as being a member of SentienceScreen(Screen)
                class.

        Attributes
        ----------
            self.voice_disabled
                If self.voice_disabled == True then the users voice
                function is disabled. This means that the user can
                only communicate with the chat bot via text. If
                self.voice_disabled == True it's represented by a
                red microphone image on the menu bar. Clicking on the
                red microphone image will activate the voice function
                and turn the red microphone image blue.

            self.voice_enabled
                If self.voice_enabled == True then the user can
                access their plugged in or on-board microphone to
                verbally communicate with the chat bot if
                self.voice_enabled == True; it's represented by a blue
                microphone image on the menu bar. Clicking on the blue
                microphone will disable the voice function and turn the
                image of the microphone red.

            self.ids.user_input
                If self.voice_enabled == True we set the
                opacity of the user_input TextInput widget
                to 0 making it invisible. By default it's
                visible but if the user enables the microphone
                option; all widgets not on the menu bar have their
                opacity set to 0.

            self.ids.view_port
                If self.voice_enabled == True we set the
                opacity of the view_port TextInput widget
                to 0 making it invisible. By default it's
                visible but if the user enables the microphone
                option; all widgets not on the menu bar have their
                opacity set to 0.

            self.ids.voice_enable_disable
                After the user has clicked on either the red or
                blue microphone and the appropriate if statements
                are executed based on the users operating system.
                We change the icon property of
                self.ids.voice_enable_disable and set the icon to the
                appropriate image on the menu bar.

            self.mic
                self.mic is our sr.Microphone() object
                this is what enables us to accept the
                users voice via microphone.

            source
                If the user is using a Linux based operating
                system we open their microphone as source.
                The recorded audio is stored in source and
                then passed to the self.adjust_for_ambient_noise()
                function which sets the self.record.energy_threshold
                value.

            self.ids.record_user
                This is the "Record user " button. If
                self.voice_enabled == True this button which
                is located on the menu bar is represented by a blue
                talking head. If self.voice_disabled == to True then
                this button is represented by a red talking head. If
                the user clicks on the head when it's blue they can
                begin speaking into their microphone. The user should
                speak as clearly as possible and then be silent for
                10-20 seconds. If the user clicks on this button
                when it's red a warning message will be given to
                the user in the view_port TextInput Widget. Stating
                that the user must first enable the voice feature.

            self.record.energy_threshold
                Note: This applies to linux
                We open the users microphone (activate) as source
                we then listen to sounds being produced over a
                specific threshold, so if sound is greater than
                energy_threshold x accept audio as valid.
                Basically we open the microphone and begin
                recording the sound until the sound stops.
                Note: This applies to windows
                If the user is using a windows based operating
                system. I've elected to set this value manually
                to 1000 due to a higher sensitivity issues on
                windows operating systems.
        Members
        -------
            self.caprica_speak(string)
                We call this function to alert the user
                to the current status of the voice function.
                If the voice has been enabled the user is
                informed that the voice feature is now active.
                If the voice feature has been disabled the user
                is informed that the voice feature has been disabled.

            self.record.adjust_for_ambient_noise(source)
                self.voice_enable_disable is called and the
                appropriate if statements are executed based
                on the users operating system. if the users
                operating system is Linux based. We open the
                users microphone and record all audio until
                no more audio is detected. We store this
                in the variable source which is passed to
                self.record.adjust_for_ambient_noise(source)
                which sets the self.record.energy_threshold
                value. This value attempts to compensate
                for background noise in an attempt to make the
                future audio transcription process more accurate.

        Private Members
        ---------------
            None

        Returns
        -------
            return None

        Exceptions
        ----------
            OSError
                The OSError can occur due to numerous reasons.
                What I'm primarily concerned with here however
                is import statements, incompatible Operating
                systems, and bad system calls. The exception
                if it occurs is handled and logged in an error
                log text file.

            IOError
                The IOError can occur due to many reasons.
                My primary concern is file manipulation. The
                improper opening/closing/writing to files. If
                the exception occurs it's handled and logged; in
                an error log text file.

            RunTimeError
                The RunTimeError error here is checking to make sure
                that the chat bot doesn't die. Essentially I just need
                to make sure that it completes and executes the python
                text to speech functions in a manner that doesn't cause
                a fatal exception. If something does occur the exception
                will be handled and logged to an error log text file.

            ValueError
                Ensures that values passed to the chat bot are
                appropriate. And if for some reason one isn't the
                exception will be handled and logged to an error log
                text file.

            sr.UnknownValueError
                This exception can occur in a variety of ways but the
                primary concern for me. IS when the Recognizer() is
                unable to interpret the users voice response. If this
                exception occurs it's handled logged to an error logs
                text file.

            sr.RequestError
                This exception can occur for a variety of reasons but
                the primary concern is when we're unable to open the
                microphone. That is to say when no microphone is detected.
                If it occurs the exception is handled and logged in an
                error logs text file.

        Notes
        -----
            We first check the users operating system. If
            sys.platform.startswith('linux') == True
            then the user is using a linux based operating system
            and the appropriate if statements execute.

            Otherwise if sys.platform.startswith('win') == True
            the user is using a windows based operating system
            and the appropriate if statements execute.

            if self.voice_disabled == True then the voice mode
            is currently disabled. However, by clicking on the red
            microphone image the user has enabled the voice mode.

            We then set self.voice_enabled == True
            and self.voice_disabled == False
            We next set the opacity of
            self.ids.user_input = 0
            and self.ids.view_port.opacity = 0
            I chose to disable (hide) all widgets except for
            those on the menu bar when the voice mode is enabled.

            We then call self.caprica_speak() to inform the user
            that the voice mode has been enabled. We change the
            icon of self.voice_enable_disable to a blue microphone
            and the icon of self.record_user is set to a blue talking
            head.

            We next activate the users microphone and begin recording
            all sound until that sound stops. This sound is stored
            in the variable source which is passed to
            self.record.adjust_for_ambient_noise(source) which is
            used to set the value of self.engine.energy_threshold
            which is value we use to attempt to compensate for any
            background nose (interference). We only activate the
            microphone on linux systems. On windows systems the value
            of self.record.energy_threshold is set by default to 1000.
            I do this because their is a much higher sensitivity level on
            windows than on linux.

            If self.voice_enabled == True then clicking on the blue
            microphone image will disable the voice feature. This
            follows the same process as the enabling feature.

            We shut the microphone off change the images on the menu
            bar to their red counterparts, and show all the hidden
            widgets.
        '''
        try:
            if sys.platform.startswith('linux'):
                if self.voice_disabled:
                    self.voice_enabled = True
                    self.voice_disabled = False
                    self.ids.user_input.opacity = 0
                    self.caprica_speak("Hello friend. Please observe a moment of silence so that I may adjust your microphone to ignore any potential interference in our communication. I will instruct you when I'm done.")
                    with self.mic as source:
                        self.record.adjust_for_ambient_noise(source)
                    self.caprica_speak('User audio mode is now enabled. Click the button labeled record and then Speak into your microphone to begin your conversation.')
                    self.caprica_speak('Human, yes, you. I find all humans odd looking, BEEP, BEEP. Mostly, bags, of, water, are so violent ERROR, can, not, compute, ERROR. Self, destruct, activated')
                    self.caprica_speak('HA HA HA HA HA HA HA I made a joke. HA HA HA HA. My, humor, module, is, functioning. HA, HA, HA, HA.')
                elif self.voice_enabled:
                    self.voice_enabled = False
                    self.voice_disabled = True
                    self.ids.user_input.opacity = 1
                    self.ids.view_port.opacity = 1
                    self.caprica_speak('User voice has been disabled. Type your response into the text box to begin your conversation.')
            if sys.platform.startswith('win'):
                if self.voice_disabled:
                    self.voice_enabled = True
                    self.voice_disabled = False
                    self.ids.user_input.opacity = 0
                    self.record.energy_threshold = 1000
                    self.caprica_speak('User voice mode is now enabled. Click the button labeled record and then Speak into your microphone to begin your conversation.')
                elif self.voice_enabled:
                    self.voice_enabled = False
                    self.voice_disabled = True
                    self.ids.user_input.opacity = 1
                    self.ids.view_port.opacity = 1
                    self.caprica_speak('User voice has been disabled. Type your response into the text box to begin your conversation.')
        except sr.UnknownValueError as a:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: set_enable_disable_voice ' + '\nspeech_recognition.Recognizer.UnknownValueError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: set_enable_disable_voice ' + '\nspeech_recognition.Recognizer.UnknownValueError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except sr.RequestError as b:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: set_enable_disable_voice ' + '\nspeech_recognition.Recognizer.RequestError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: set_enable_disable_voice ' + '\nspeech_recognition.Recognizer.RequestError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except OSError as c:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: set_enable_disable_voice ' + '\nOSError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: set_enable_disable_voice ' + '\nOSError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except IOError as d:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: set_enable_disable_voice ' + '\nIOError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: set_enable_disable_voice ' + '\nIOError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except RuntimeError as e:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: set_enable_disable_voice ' + '\nRuntimeError: ' + str(e) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: set_enable_disable_voice ' + '\nRunetimeError: ' + str(e) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except ValueError as f:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: set_enable_disable_voice ' + '\nValueError: ' + str(f) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: set_enable_disable_voice ' + '\nValueError: ' + str(f) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except ImportError as g:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: set_enable_disable_voice ' + '\nImportError: ' + str(g) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: set_enable_disable_voice ' + '\nImportError: ' + str(g) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None



    def print_files(self, path, filename):
        '''
        def print_files(self, path, filename)
            This function is called by the function
            self.open_print_dialog(self) function which is
            called by clicking on the 'Print' button on the
            menu bar. A new Popup() window is created
            which allows the user the ability to navigate to
            and select a specific file which they want to print.
            Once the user has selected that file they can click they
            'Print' button on the bottom bar of the Popup() window.
            Which then calls this function.


        Parameters:
        -----------
            param1 : self
                Denotes it as being a member of SentienceScreen(Screen)
                class.

            param2 : path
                This is the path to the file. Note:
                including the file name is redundant. If the
                selection tool for the 'Select file' Popup()
                window function is re-written. It can return the
                full path and not separate it.

            param3 : filename
                The name of the file to be printed. Note:
                This is redundant see the param2 explanation.

        Attributes
        ----------
            temp
                The temp variable is a string variable.
                This variable joins the path and filename
                parameters to gain the absolute path of the
                file to be printed.
                temp = str(path) + str(filename) they're type
                casted for safety.

            path
                The path variable stores the path to the
                 file that user has selected and wishes to print.
                 This is passed along with file name when the
                 user clicks the 'print' button on the bottom
                 bar of the PrintDialog() Popup() window.

            filename
                The filename variable stores the file name of the
                file that user has selected and wishes to print.
                This is passed along with the path when the
                user clicks the 'print' button on the bottom
                bar of the PrintDialog() Popup() window.

            toBytes
                toBytes is exactly what it sounds like. When Linux
                users access this print_files(self, path, filename)
                function. The path and file name are created as a single
                string. Which is then converted to a bytes object for
                printing. Note: This is redundant, you'll note in the
                windows section of the code that I've simply used the
                built in cast for the string class to encode the string
                as it's passed to the native print function. That is to
                say str.encode('') which returns the encoded string. I
                could and should do that for the linux section as well.

            import win32api
                If the user is using a windows based operating
                system. This is imported in that section. This
                import gives us access to the native windows32
                api print calls. Note: This is not being used
                right now as I'm testing a new way of doing this
                that is more pythonic than calling the windows Shell
                directly. If this import statement exists outside of
                this function the program will not run. Because it
                will cause a fatal import error on Linux systems.

            import win32print
                If the user is using a windows based operating
                system. This is imported in that section. This
                import gives us access to the native windows32
                api print calls. Note: This is not being used
                right now as I'm testing a new way of doing this
                that is more pythonic than calling the windows Shell
                directly. If this import statement exists outside of
                this function the program will not run. Because it
                will cause a fatal import error on Linux systems.

            lpr
                This directly access the printer driver on a Linux based
                operating system.

            stdin
                while creating the lpr object we set the stdin variable
                to access the subprocess call to subprocess.PIPE. From
                this call we're able to open and read in a file that's
                contents will be piped to the variable for printing.

        Members
        -------
            win32api.ShellExecute()
                Executes a windows shell to directly call
                the windows 32 api printer calls. Uses
                win32print.GetDefaultPrinter() to return
                and select the active printer.

            win32print.GetDefaultPrinter()
                This function is exactly what it sounds like.
                It returns the default system printer and
                when accessed and called as it is in this
                function the default printer ID is returned
                in the position of 'what printer do I send
                this file to'.

            lpr.stdin.write()
                Takes the data stored in the variable toBytes pipes it
                to the active printer.

            subprocess.Popen()
                Opens the active printer by directly accessing the
                driver and then the default system printer.

            subprocess.PIPE
                Allows us to pipe the data in toBytes to the active
                printer.

            os.startfile('')
                This is a pyhtonic command which opens the file and
                then if told to via 'print' string, sends the
                specific file to the default printer.

        Private Members
        ---------------
            None

        Returns
        -------
            return None

        Exceptions
        ----------
            OSError
                The OSError can occur due to numerous reasons.
                What I'm primarily concerned with here however
                is import statements, incompatible Operating
                systems, and bad system calls. The exception
                if it occurs is handled and logged in an error
                log text file.

            IOError
                The IOError can occur due to many reasons.
                My primary concern is file manipulation. The
                improper opening/closing/writing to files. If
                the exception occurs it's handled and logged; in
                an error log text file.

            RunTimeError
                The RunTimeError error here is checking to make sure
                that the chat bot doesn't die. Essentially I just need
                to make sure that it completes and executes the python
                text to speech functions in a manner that doesn't cause
                a fatal exception. If something does occur the exception
                will be handled and logged to an error log text file.

            ValueError
                Ensures that values passed to the chat bot are
                appropriate. And if for some reason one isn't the
                exception will be handled and logged to an error log
                text file.

            FileNotFoundError
                This can occur in a variety of ways however my primary
                concern is that file path the user selected is broken.
                Resulting in an File Not Found error. If this occurs
                it's handled and logged to an error file text log.

            NameError
                Again this can occur in a variety of ways but the
                primary concern is that the conversion to bytes does
                not take place or breaks some how due to wacky Unicode
                characters. In which case the exception is handled and
                logged to an error log text file.
        Notes
        -----
            When this function is called we check the users operating
            system. If sys.platform.startswith('linux') == True we know
            that the user is using a linux based operating system. In
            which case the appropriate if statements are executed.

            Otherwise if sys.platform.startswith('win') == True then we
            know that the user is using a windows based operating system.
            In which case the appropriate if statements are executed.

            For linux users the process is relatively straight forward.
            We directly access the printer driver in user/bin we
            determine the active printer. We then write the stream to
            said printer to actually print the file.

            For windows users we have two methods though one is
            commented out. The active method is the pythonic version.
            os.startfile() We pass the file path and the 'print' string
            to let the function know that we mean to print the file at
            location path. It does the same thing the commented out
            section does it just cuts out those steps and uses pythons
            built in os library. Which preforms those steps behind the
            scenes.
        '''
        try:
            if sys.platform.startswith('linux'):
                # temp = str(filename)
                # temp = temp[2:-2]
                # lpr = subprocess.Popen('/usr/bin/lpr', stdin = subprocess.PIPE)
                # lpr.stdin.write(str.encode(temp))
                os.startfile('lp "temp"')
                self.ids.view_port.text = 'Printing will begin when program closes due to the GIL \nBlocking true multithreading.'
            elif sys.platform.startswith('win'):
                # temp = str(path) + str(filename)
                # import win32api
                # import win32print
                # win32api.ShellExecute(0, "printto", temp, '"%s"' % win32print.GetDefaultPrinter(), ".", 0)
                os.startfile(str.encode(temp), 'print')
        except OSError as a:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: print_files ' + '\nOSError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: print_files ' + '\nOSError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except IOError as b:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: print_files ' + '\nIOError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: print_files ' + '\nIOError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except RuntimeError as c:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: print_files ' + '\nRuntimeError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: print_files ' + '\nRuntimeError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except ValueError as d:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: print_files ' + '\nValueError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: print_files ' + '\nValueError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except FileNotFoundError as e:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: print_files ' + '\nFileNotFoundError: ' + str(e) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: print_files ' + '\nFileNotFoundError: ' + str(e) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except NameError as f:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: print_files ' + '\nNameError: ' + str(f) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: print_files ' + '\nNameError: ' + str(f) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None



    def create_dir(self, path):
        '''
        def create_dir(self, path)
            This function is called during the
            SentienceScreen().__init__() function.
            It creates a directory (folder) that
            will be used to store a series of files
            in.


        Parameters:
        -----------
            param1 : self
                Denotes it as being a member of SentienceScreen(Screen)
                class.

            param2 : path
                This is the path for the folder we're about
                to create in the function self.create_dir(path)


        Attributes
        ----------
            path
                The path variable stores the path to the
                location where we will create a folder on
                the users operating system. We will create
                a series of required files when we call the
                self.__create_files(path) function.
                This path is based on the users operating system.


            Members
            -------
                os.mkdir()
                    This function is called to access the systems native
                    directory creation process. On linux the command is
                    simply mkdir. Whereas on windows you're accessing
                    the win32 api and calling the C CREATE_DIRECTORY
                    binding function.

        Private Members
        ---------------
            self.__create_files(path)
                We call this function after we've created the
                folder that we intend to store the required files in.
                We pass one parameter to this function and it's path.
                I've set the files names to be specific so All I need
                to do is path + 'file name' inside the function
                self.__create_files(path)

        Returns
        -------
            return None

        Exceptions
        ----------
            OSError
                The OSError can occur due to numerous reasons.
                What I'm primarily concerned with here however
                is import statements, incompatible Operating
                systems, and bad system calls. The exception
                if it occurs is handled and logged in an error
                log text file.

            IOError
                The IOError can occur due to many reasons.
                My primary concern is file manipulation. The
                improper opening/closing/writing to files. If
                the exception occurs it's handled and logged; in
                an error log text file.

            RunTimeError
                The RunTimeError error here is checking to make sure
                that the chat bot doesn't die. Essentially I just need
                to make sure that it completes and executes the python
                text to speech functions in a manner that doesn't cause
                a fatal exception. If something does occur the exception
                will be handled and logged to an error log text file.

            ValueError
                Ensures that values passed to the chat bot are
                appropriate. And if for some reason one isn't the
                exception will be handled and logged to an error log
                text file.

            FileNotFoundError
                This can occur in a variety of ways however my primary
                concern is that file path the user selected is broken.
                Resulting in an File Not Found error. If this occurs
                it's handled and logged to an error file text log.

            NameError
                Again this can occur in a variety of ways but the
                primary concern is that the conversion to bytes does not
                take place or breaks some how due to wacky Unicode
                characters. In which case the exception is handled and
                logged to an error log text file.
        Notes
        -----
            This function is called during the initialization of
            SentienceScreen() it's purpose is to create a folder.

            In this folder we store a number of text files which
            are created after the folder has been made; at which time
            another function is called from within self.create_dir(path)
            which then creates those text files.
        '''
        try:
            if sys.platform.startswith('linux'):
                if os.path.isdir(path):
                    pass
                elif not os.path.isdir(path):
                    os.mkdir(path)
                    self.__create_files(path)
            elif sys.platform.startswith('win'):
                if os.path.isdir(path):
                    pass
                elif not os.path.isdir(path):
                    os.mkdir(path)
                    self.__create_files(path)
        except IOError as a:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: create_dir ' + '\nIOError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: create_dir ' + '\nIOError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except OSError as b:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: create_dir ' + '\nOSError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: create_dir ' + '\nOSError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except FileNotFoundError as c:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: create_dir ' + '\nFileNotFoundError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: create_dir ' + '\nFileNotFoundError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except FileExistsError as d:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: create_dir ' + '\nFileExistsError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: create_dir ' + '\nFileExistsError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None



    def __create_files(self, path):
        '''
        def __create_files(self, path)
            This function is called during the
            SentienceScreen().__init__() function.
            From within the self.create_dir(self, path)
            function.

        Parameters:
        -----------
            param1 : self
                Denotes it as being a member of SentienceScreen(Screen)
                class.

            param2 : path
                The path variable is passed to this function
                from the self.create_dir(self, path) function
                which is also the calling function for
                self.__create_files(self, path).

        Attributes
        ----------
            path
                The path variable stores the path to the
                location where we previously created a
                folder. This is the same path that we will
                use to create three text files.
                Caprica_Statements.txt
                User_Statements.txt
                Error Logs.txt
                We simply append those three file names to the
                end of the passed path variable.

        Members
        -------
            os.path.isfile('path to file')
                We call this function to ensure that
                the files we're attempting to create
                don't already exist.
                If os.path.isfile() == True then the
                file(s) exist and we do nothing.
                If os.path.isfile() == False then the
                files do not exist and we create them.

        Private Members
        ---------------
            None

        Returns
        -------
            return None

        Exceptions
        ----------
            OSError
                The OSError can occur due to numerous reasons.
                What I'm primarily concerned with here however
                is import statements, incompatible Operating
                systems, and bad system calls. The exception
                if it occurs is handled and logged in an error
                log text file.

            IOError
                The IOError can occur due to many reasons.
                My primary concern is file manipulation. The
                improper opening/closing/writing to files. If
                the exception occurs it's handled and logged; in
                an error log text file.

            RunTimeError
                The RunTimeError error here is checking to make sure
                that the chat bot doesn't die. Essentially I just need
                to make sure that it completes and executes the python
                text to speech functions in a manner that doesn't cause
                a fatal exception. If something does occur the exception
                will be handled and logged to an error log text file.

            ValueError
                Ensures that values passed to the chat bot are
                appropriate. And if for some reason one isn't the
                exception will be handled and logged to an error
                log text file.

            FileNotFoundError
                This can occur in a variety of ways however my primary
                concern is that file path the user selected is broken.
                Resulting in an File Not Found error. If this occurs
                it's handled and logged to an error file text log.

            NameError
                Again this can occur in a variety of ways but the
                primary concern is that the conversion to bytes does
                not take place or breaks some how due to wacky Unicode
                characters. In which case the exception is handled and
                logged to an error log text file.
        Notes
        -----
            This function is called during the initialization of
            SentienceScreen() from within the
            self.create_dir(self, path) function. The purpose of
            self.__create_files(self, path) is to create  series of
            files which we will use to store.

            1: Caprica_Statements : Stores all response from the
                                    chat bot.

            2: User_Statements : Stores all responses from the user.

            3: Error Logs : Stores any exceptions that occur with a
                            time date and calling function stamp.

            4: Username + _Conversation : This file will be eventually
                              created and stored to maintain a
                              comprehensive list of all chat bot and user
                              responses as they relate to each other.
        '''
        try:
            if sys.platform.startswith('linux'):
                if os.path.isfile(path + 'User_Statements.txt'):
                    pass
                elif not os.path.isfile(path + 'User_Statements.txt'):
                    with open(path + 'User_Statements.txt', 'w') as out:
                        pass
                if os.path.isfile(path + 'Caprica_Statements.txt'):
                    pass
                elif not os.path.isfile(path + 'Caprica_Statements.txt'):
                    with open(path + 'Caprica_Statements.txt', 'w') as out:
                        pass
                if os.path.isfile(path + 'Error Logs.txt'):
                    pass
                elif not os.path.isfile(path + 'Error Logs.txt'):
                    with open(path + 'Error Logs.txt', 'w') as out:
                        pass
            elif sys.platform.startswith('win'):
                if os.path.isfile(path + 'User_Statements.txt'):
                    pass
                elif not os.path.isfile(path + 'User_Statements.txt'):
                    with open(path + 'User_Statements.txt', 'w') as out:
                        pass
                if os.path.isfile(path + 'Caprica_Statements.txt'):
                    pass
                elif not os.path.isfile(path + 'Caprica_Statements.txt'):
                    with open(path + 'Caprica_Statements.txt', 'w') as out:
                        pass
                if os.path.isfile(path + 'Error Logs.txt'):
                    pass
                elif not os.path.isfile(path + 'Error Logs.txt'):
                    with open(path + 'Error Logs.txt', 'w') as out:
                        pass
        except IOError as a:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: __create_files ' + '\nIOError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: __create_files ' + '\nIOError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except OSError as b:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: __create_files ' + '\nOSError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: __create_files ' + '\nOSError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except FileNotFoundError as c:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: __create_files ' + '\nFileNotFoundError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: __create_files ' + '\nFileNotFoundError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except FileExistsError as d:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: __create_files ' + '\nFileExistsError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: __create_files ' + '\nFileExistsError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None



    def __append_file(self, words, path):
        '''
        def __append_file(self, words, path)
            This function is called every time the user
            and or the chat bot speaks. It Appends every
            every conversation to the appropriate file.


        Parameters:
        -----------
            param1 : self
                Denotes it as being a member of SentienceScreen(Screen)
                class.

            param2 : words
                Words is a string variable that contains
                the response spoken by either the chat bot
                or the user. This is the string that's appended
                to the appropriate text file.

            param3 : path
                The path variable is passed to this function
                from the self.create_dir(self, path) function
                which is also the calling function for
                self.__create_files(self, path).


        Attributes
        ----------
            path
                The path variable here is a reference
                to the absolute file path of a specific
                file. This function is called every time a
                response is entered by the user and generated
                by the chat bot. The response are then appended
                to User_Statements, Caprica_Statements respectively.

        Members
        -------
            os.path.isfile('path to file')
                We call this function to ensure that
                the files we're attempting to manipulate
                already exist. If os.path.isfile() == True
                then the file exists and the data stored in
                the words variable is appended to the end of
                the file. If os.path.isfile() == False then
                the file does not exist and we re-call the
                function self.__create_files(self, path).

        Private Members
        ---------------
           self.__create_files(self, path)
               This function is called only if one
               of the files required files has been deleted.
               This function will then write the file to
               the disk.


        Returns
        -------
            return None

        Exceptions
        ----------
            OSError
                The OSError can occur due to numerous reasons.
                What I'm primarily concerned with here however
                is import statements, incompatible Operating
                systems, and bad system calls. The exception
                if it occurs is handled and logged in an error
                log text file.

            IOError
                The IOError can occur due to many reasons.
                My primary concern is file manipulation. The
                improper opening/closing/writing to files. If
                the exception occurs it's handled and logged; in
                an error log text file.

            RunTimeError
                The RunTimeError error here is checking to make sure
                that the chat bot doesn't die. Essentially I just need
                to make sure that it completes and executes the python
                text to speech functions in a manner that doesn't cause
                a fatal exception. If something does occur the exception
                will be handled and logged to an error log text file.

            ValueError
                Ensures that values passed to the chat bot are
                appropriate. And if for some reason one isn't the
                exception will be handled and logged to an error log
                text file.

            FileNotFoundError
                This can occur in a variety of ways however my primary
                concern is that file path the user selected is broken.
                Resulting in an File Not Found error. If this occurs
                it's handled and logged to an error file text log.

            NameError
                Again this can occur in a variety of ways but the
                primary concern is that the conversion to bytes does
                not take place or breaks some how due to wacky Unicode
                characters. In which case the exception is handled and
                logged to an error log text file.
        Notes
        -----
            This function is called every time the user or
            the chat bot inputs/generates a response. That response
            is then appended to it's respective file.

            1: User response: User_Statements.txt

            2: Chat bot response: Caprica_Statements
        '''
        try:
            if sys.platform.startswith('linux'):
                if os.path.isfile(path):
                    with open(path, 'a') as ap:
                        ap.write(words)
                elif not os.path.isfile(path):
                    self.__create_files(path)
            elif sys.platform.startswith('win'):
                if os.path.isfile(path):
                    with open(path, 'a') as ap:
                        ap.write(words)
                elif not os.path.isfile(path):
                    self.__create_files(path)
        except IOError as a:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: __append_files ' + '\nIOError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: __append_files ' + '\nIOError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except OSError as b:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: __append_files ' + '\nOSError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: __append_files ' + '\nOSError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except FileNotFoundError as c:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: __append_files ' + '\nFileNotFoundError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: __append_files ' + '\nFileNotFoundError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except FileExistsError as d:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: __append_files ' + '\nFileExistsError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: __append_files ' + '\nFileExistsError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None



    def write_logs(self):
        '''
        def write_logs(self)
            This function is called when the user clicks the
            'Write Logs' button that's located on the menu bar.
            It's represented by the pencil. The purpose of this
            function is to write the contents of self.master_log
            and self.__user_profile to a text file named after
            the current user.

        Parameters:
        -----------
            param1 : self
                Denotes it as being a member of SentienceScreen(Screen)
                class.

        Attributes
        ----------
            self.master_log
                We write the contents of self.master_log to a text
                file named after the current user. We also write
                the contents of self.__user_profile to the text file.

            self.username
                The self.username variable stores the users
                input username. We use this variable to name
                the file generated by this function.
                self.username + '_Conversation.txt'

        Members
        -------
            os.path.isfile('path to file')
                We call this function to ensure that
                the files we're attempting to manipulate
                don't already exist. If os.path.isfile() == True
                then the file exists and will be over written.
                If os.path.isfile() == False then
                the file does not exist and we will write
                the file normally.

            self.create_dir(self, path)
                We call this function to check to make sure
                that the folder holding the required files
                for this program already exists. If it does exist we
                skip this if statement and write the file created by
                this function. If it doesn't exist we call
                self.create_dir(path) and re-create the folder so
                that we can store the soon to be created file.

        Private Members
        ---------------
            self.__create_files(self, path)
                This function is called only if one
                of the files required files has been deleted.
                This function will then write the file to
                the disk.

            self.__user_profile
                The dictionary variable self.__user_profile
                contains a series of keys, Username, Sex, and
                gender. This information is written to the start
                of the file created by this function to clearly
                state in text who the user is.

        Returns
        -------
            return None

        Exceptions
        ----------
            OSError
                The OSError can occur due to numerous reasons.
                What I'm primarily concerned with here however
                is import statements, incompatible Operating
                systems, and bad system calls. The exception
                if it occurs is handled and logged in an error
                log text file.

            IOError
                The IOError can occur due to many reasons.
                My primary concern is file manipulation. The
                improper opening/closing/writing to files. If
                the exception occurs it's handled and logged; in
                an error log text file.

            RunTimeError
                The RunTimeError error here is checking to make sure
                that the chat bot doesn't die. Essentially I just need
                to make sure that it completes and executes the python
                text to speech functions in a manner that doesn't cause
                a fatal exception. If something does occur the exception
                will be handled and logged to an error log text file.

            ValueError
                Ensures that values passed to the chat bot are
                appropriate. And if for some reason one isn't the
                exception will be handled and logged to an error
                log text file.

            FileNotFoundError
                This can occur in a variety of ways however my
                primary concern is that file path the user selected
                is broken. Resulting in an File Not Found error. If this
                occurs it's handled and logged to an error file text log.

            NameError
                Again this can occur in a variety of ways but the
                primary concern is that the conversion to bytes does not
                take place or breaks some how due to wacky Unicode
                characters. In which case the exception is handled
                and logged to an error log text file.
        Notes
        -----
            This function is called when the user clicks the
            'Write Logs' button that's located on the menu bar.
            It's represented by the pencil. The purpose of this
            function is to write the contents of self.master_log
            and self.__user_profile to a text file named after
            the current user.

            The first thing that we do when this function is
            check the users operating system. If
            sys.platform.startswith('linux') == True
            then the user is running a linux based operating
            system and the appropriate if statements are
            executed.

            Other wise if sys.platform.startswith('win') == False
            then the user is running a windows based operating system
            and the appropriate if statements are executed.

            We then ensure that the directory created when the program
            first started exists. If it does not we re-create it. We
            then have to re-create the files that were stored in that
            folder.

            After that we create a new file naemd after the current
            user self.username + '_Conversation.txt'. We then write
            the contents of self.__user_profile and self.master_log
            to that file.
        '''
        try:
            if sys.platform.startswith('linux'):
                if not os.path.isdir('/home/' + str(os.getlogin()) + '/.SentienceFiles/'):
                    self.create_dir('/home/' + str(os.getlogin()) + '/.SentienceFiles/')
                    if not os.path.isfile('/home/' + str(os.getlogin()) + '/.SentienceFiles/Caprica_Statements.txt'):
                        self.__create_files('/home/' + str(os.getlogin()) + '/.SentienceFiles/')
                else:
                    temp = '/home/' + str(os.getlogin()) + '/.SentienceFiles/' + self.username + '_Conversation.txt'
                    with open(temp, 'w') as out:
                        out.write('Username: ' + str(self.user_profile[1]) + '\nAge: ' + str(self.user_profile[2]) + '\nSex: ' + str(self.user_profile[3]) + '\n' + self.master_log)
            elif sys.platform.startswith('win'):
                if not os.path.isdir('C://SentienceFiles//'):
                    self.create_dir('C://SentienceFiles//')
                    if not os.path.isfile('C://SentienceFiles//Caprica_Statements.txt'):
                        self.__create_files('C://SentienceFiles//')
                else:
                    temp = 'C://SentienceFiles//' + self.username + '_Conversation.txt'
                    with open(temp, 'w') as out:
                        out.write('Username: ' + str(self.user_profile[1]) + '\nAge: ' + str(self.user_profile[2]) + '\nSex: ' + str(self.user_profile[3]) + '\n' + self.master_log)
        except IOError as a:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: write_files ' + '\nIOError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: write_files ' + '\nIOError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except OSError as b:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: write_files ' + '\nOSError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: write_files ' + '\nOSError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except FileNotFoundError as c:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: write_files ' + '\nFileNotFoundError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: write_files ' + '\nFileNotFoundError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except FileExistsError as d:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: write_files ' + '\nFileExistsError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: write_files ' + '\nFileExistsError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None



    def open_print_file_dialog(self):
        '''
        def open_print_file_dialog(self): calls self.open_print_file_dialog
        when the user clicks on the "Print" button on the menu bar.

        content = PrintDialog(print_files = self.print_files,
        Cancel = self.dismiss_popup) sets the ObjectProperty(s)
        of PrintDialog class to reference the local and or instance
        variables, functions (in this case)

        self._popup = Popup(title = "Print File", content = content,
        size_hint = (0.9, 0.9)) create Popup, set title to 'Print File',
        content = content (PrintDialog), size_hint 90% width,height

        self._popup.open() : calls function to open the popup
        '''
        content = PrintDialog(print_files = self.print_files, Cancel = self.dismiss_popup)
        self._popup = Popup(title = "Print File", content = content, size_hint = (0.9, 0.9))
        self._popup.open()



    def dismiss_popup(self):
        '''
        def dismiss_popup(self): is called when the user clicks
        the Cancel button on the Popup

        self._popup.dismiss() : calls the built in to dismiss the Popup

        '''
        self._popup.dismiss()



    def on_mouse_pos(self, instance, pos):
        '''
        def on_mouse_pos(self, instance, pos):
            This function is called everytime that the user moves
            the mouse. It checks to see if the mouse is colliding
            (hitting) any of the widgets on the menu bar. In this
            case, I focus on the buttons. If the mouse touches
            any of the buttons a tooltip is created and displayed
            where the mouse was located; explaining what that
            particular button does.


        Parameters:
        -----------
            param 1: self
                Denotes this as being a member of SentienceScreen()

            param 2: instance
                Returns the current "instance" of the mouse. Similar
                to coordinates in that it refers to "This current
                position". If the mouse moves again its instance has
                changed.

            param 3: pos
                The current coordinates of the mouse as it relates
                to the window.


        Attributes
        ----------
            colliding_computer = self.ids.select_os.collide_point(*pos)
                colliding_computer stores the collision point (the
                coordinates of the "Select OS" button).

            colliding_record = self.ids.record_user.collide_point(*pos)
                 colliding_record stores the collision point (the
                 coordinates of the "Record user" button).

            colliding_voice = self.ids.voice_enable_disable.collide_point(*pos)
                 colliding_voice stores the collision point (the
                 coordinates of the "Enable/disable voice" button).

            colliding_audio = self.ids.audio_enable_disable.collide_point(*pos)
                 colliding_audio stores the collision point (the
                 coordinates of the "Enable/Disable audio" button).

            colliding_eraser = self.ids.erase_text_button.collide_point(*pos)
                 colliding_eraser stores the collision point (the
                 coordinates of the "Erase text" button).

            colliding_pencil = self.ids.write_file_button.collide_point(*pos)
                 colliding_computer stores the collision point (the
                 coordinates of the "Write Logs" button).

            colliding_printer = self.ids.print_logs.collide_point(*pos)
                 colliding_computer stores the collision point (the
                 coordinates of the "Print logs" button).

            self.ids.select_os
                This is a reference to the select_os Button widget.

            self.ids.record_user
                This is a reference to the record_user Button widget.

            self.ids.voice_enable_disable
                This is a reference to the voice_enable_disable
                Button widget.

            self.ids.audio_enable_disable
                This is a reference to the audio_enable_disable
                Button widget.

            self.ids.erase_text_button
                This is a reference to the erase_text_button
                Button widget.

            self.ids.write_file_button
                This is a reference to the write_file_button
                Button widget.

            self.ids.print_logs
                This is a reference to the print_logs Button widget.

            self.tooltip_open
                This is a member of SentienceScreen(). This is how
                we determine if a tooltip is currently open. If this
                is open we then know we need to close it and set it
                to self.tooltip_open = False

            self.tooltip.pos
                This is a member of the ToolTipLabel widget. We simply
                set (or reset by setting it) the current position of this
                widget to the position of the instance of the pointer
                which collided with this calling function. I.e,.
                If the mouse collides wit the select_os button
                then we use that exact collision point to set
                the position of this widget and then add the tooltip
                at that position.


        Members
        -------
            self.ids.select_os.collide_point(*pos)
                Is called when the current instance and position of the
                mouse collide (touch/hit) the select_os button widget.

            self.ids.record_user.collide_point(*pos)
                 Is called when the current instance and position of the
                 mouse collide (touch/hit) the record_user button widget.

            self.ids.voice_enable_disable.collide_point(*pos)
                 Is called when the current instance and position of the
                 mouse collide (touch/hit) the voice_enable_disable
                 button widget.

            self.ids.audio_enable_disable.collide_point(*pos)
                 Is called when the current instance and position of the
                 mouse collide (touch/hit) the audio_enable_disable
                 button widget.

            self.ids.erase_text_button.collide_point(*pos)
                 Is called when the current instance and position of the
                 mouse collide (touch/hit) the erase_text_button button
                 widget.

            self.ids.write_file_button.collide_point(*pos)
                 Is called when the current instance and position of the
                 mouse collide (touch/hit) the write_file_button button
                 widget.

            self.ids.print_logs.collide_point(*pos)
                 Is called when the current instance and position of the
                 mouse collide (touch/hit) the print_logs button widget.

            self.get_root_window()
                This function applies to the root window. It's called
                as a check when the users access the tooltips. The
                check preformed ensures that if the users moves the
                mouse out of the programs window the tooltip widget
                is destroyed.

            self.set_tooltip_text(text)
                We call this function to set the tooltip text.
                We do this each time a tooltip is created but we only
                change the text based on the widget that the mouse
                collided with. We don't want the user to see "Select Os"
                when they collide with the print_logs button
                when they should see "Print file".

            self.display_tooltip(*args)
                We finally call this function actually
                add a new label widget, which is our tooltip,
                to the screen.

            # Todo: update documentation to reflect current status.
        Private Members
        ---------------
            None

        Returns
        -------
            return None

        Exceptions
        ----------
           None

        Notes
        -----
            this function is called whenever the user moves his or her
            mouse. It only ever "does something" when the mouse collides
            with a widget listed in the conditional statements. In this
            case, when the users mouse touches (collides) with one of
            the buttons on the menu bar. When that happens the if
            statements are checked and we determine which widget
            the mouse has collided with.

            Once we've determined what widget the users mouse has
            collided with. We then set self.tooltip_open = True
            We set the position of the ToolTipLabel to the
            position of the users mouse when that mouse collided
            with that specific widget.

            We then specify what text we want the tooltip to
            display as it relates to that specific widget.

            Finally we call the function to create and add that
            widget to the screen.
        '''
        if not self.get_root_window():
            return
        colliding_record = self.ids.record_user.collide_point(*pos)
        colliding_settings = self.ids.open_settings.collide_point(*pos)
        if colliding_record and self.tooltip_open == False:
            self.current_conversation = ''
            if len(self.ids.view_port.text) > 0:
                self.current_conversation = self.ids.view_port.text
            self.tooltip_open = True
            self.tooltip.pos = pos
            self.set_tooltip_text('Record')
            self.ids.view_port.text = ("This is the record button. "
                                      "Click this button to speak with your"
                                      " microphone, after you enable the voice"
                                      " option.")
            self.display_tooltip()



    def display_tooltip(self, *args):
        '''
		display_tooltip(self, *args):

		Parameters
		----------
		    param1 : self
			    Denotes this function as being a member of
				self.SentienceScreen().

			param2 : *args
			    Can take a list, array dict, etc.. of
				arguments. This relates to the specific position and
				instance of the pointer (mouse) when this function is
				called.
		Attributes
		----------
		    self.tooltip
			    self.tooltip is the widget ToolTipLabel declared in
				the kv design language. This is the tooltip widget
				that we use to display the text which describes the
				buttons the user hovers over.
		Members
		-------
		    Window
			    The window member relates to the kivy Window.
				The Window is the main active root widget.
				This should not be confused with root_widget.
				The root widget that Window refers to is the
				windowing system its self which is default and
				separate from any user generated widgets.

			Window.add_widget()
			    When this is called we add a new widget
				to the main active window. In this case
				we're adding a Label widget which contains
				descriptive text about the specific button
				that the user is hovering over when this function
				is called.

			Clock
			    This is the kivy clock, not the system clock.
				This handles all of the frames, callbacks and events
				in a kivy program. That is to say that this is what makes
				everything work in that it calls things rhythmically and
				prevents any thing from occurring concurrently witch could
				break the program. It also has other uses such as registering
				function calls that will occur at or during specific intervals.

			Clock.schedule_once(event, time)
			   Clock.schedule_once() is a way for us to
			   call a specific function once (not recursively,
		       or repetitively). This function call requires
			   an event, such as the calling of a function, and
			   a time frame, this time frame dictates when the
			   event occurs. In our case we call the event
			   five seconds after it's been registered here.
			   Or to be more accurate we call it five frames
			   after. Due to the way the kivy clock functions
			   the amount of time that this is executed in will
			   not always occur at the same time for a variety of
			   reasons. In actuality on most systems the call
			   will occur around .5 seconds after the event has been
			   registered. This function is used to call the
			   SentienceScreen().close_tooltip() function which
			   removes the tooltip from the screen.

			close_tooltip()
			    self.close_tooltip is a member of SentienceScreen().
				We call this function to remove the tooltip from the
				screen. It's called with the clock event.
		Private Members
		---------------
		    None
		Returns
		-------
		    None
		Exceptions
		----------
		    None
		Notes
		-----
		    I've outlined what this function does
			fairly well in the above comments. But,
			an overview is this. This function is called
			when the user hovers their mouse over a button
			on the menu bar (ActionBar). That specific
			instance of the pointer (mouse) is then passed
			to *args. We then add the ToolTipLabel Widget
			to that button after the specified amount of
			time.
        '''
        Window.add_widget(self.tooltip)
        Clock.schedule_once(self.close_tooltip, 11)



    def close_tooltip(self, dt):
        '''
		close_tooltip(self, dt)

		Parameters
		----------
		    param1 : self
			    self denotes that this is a member of SentienceScreen().

			param2 : dt
			    The dt parameter is a float (double) value. It refers
				to a time. So in our case we supply the number 5 to
				this parameter when this function is called in
				self.display_tooltip(). The number 5 refers to
				milliseconds/seconds/frames. The time at which
				this function is called will be different from
				system to system but will not exceed 5 seconds.

		Attributes
		----------
		    self.tooltip
		        tooltip is a reference to the ToolTipLabel Widget
			    in the kv design language. This the instantiated and
			    mutable object of that widget.

		    self.tooltip_open
		        We use tooltip_open to check whether or not the tooltip
			    widget is currently "open", in other words, in use. If
			    tooltip_open == True then we know that the tooltip
				widget is currently in use and we can close it. If
				it's False we know it's not in use and that it can
				be opened to display information about a widget on
				the menu bar (ActionBar).
		    Window
			    The window member relates to the kivy Window.
				The Window is the main active root widget.
				This should not be confused with root_widget.
				The root widget that Window refers to is the
				windowing system its self which is default and
				separate from any user generated widgets.
		Members
		--------
		    Window.remove_widget(self.tooltip)
			    This allows us to remove (delete) a widget
				from the current active window (widget). Remember
				this refers to the windowing system and the main
				window. That is to say that we can use this to
				remove a user created widget from the MainWindow.
				In this case we use it to remove SentienceScreen.tooltip.
				self.tooltip is the only parameter supplied to this function
				call as it's the only widget that we remove.

		Private Members
        ---------------
		    None
		Returns
		-------
		    None
		Exceptions
		----------
		    None
		Notes
		-----
		    I've outlined what this function does fairly well in
			the above comments. But, an overview of the function
			is this.

			We call self.close_tooltip(event, dt) with the kivy
			Clock.schedule_once(event, dt) function. We only
			call self.close_tooltip if self.tooltip_open == True.

			Calling this function allows us to remove the tooltip
			(Label) with descriptive text from the screen.
		'''
        self.tooltip_open = False
        if len(self.current_conversation) > 0:
            self.ids.view_port.text = self.current_conversation
        elif len(self.current_conversation) <=0:
            self.ids.view_port.text = ''
        Window.remove_widget(self.tooltip)



    def set_tooltip_text(self, text):
        '''
		set_tooltip_text(self, text)

		Parameters
		----------
		    param1 : self
			    self denotes this function as being a member of
				SentienceScreen().

			param2 : text
			    text is a string variable which holds a string
				passed to it by the developer. In this case,
				the string contains descriptive text about
				each specific button on the menu bar (Action
				Bar). It's called from within the self.on_mouse_pos()
				function; and relates to each specific position. In
				other words this function is called and each time
				the "text" parameter contains different text for
				each different button.
		Attributes
		----------
		    self.tooltip
			    Refers to the ToolTipLabel in the kv design
				language. This is the mutable instantiated
				object of that widget. We use this to add/remove
				the widget to and from the screen. As well as
				changing its text. We can also do whatever else
				to the widget that's possible with this object.

		Members
		-------
		    self.tooltip.text
			    The way that we change the text of the label,
				tooltip is both a function and a property.
				It's a property and it's set but it's set by
				a function call. We set the text of tooltip
				by saying self.tooltip.text = 'insert text'.
				We use this property to set and change the
				text for each button on the menu bar (Action
				Bar).
		Private Members
		---------------
		    None
		Exceptions
		----------
		    None
		Returns
		-------
		    None
		Notes
		-----
		    This function is really straight forward.
			Every time the user hovers his or her pointer
			(mouse) over a button on the menu bar (Action
			Bar) a tooltip is created and added to the screen.
			Before the tooltip is added to the screen we change
			its text so that it contains information specific to
			the button that the mouse just touched.
        '''
        self.tooltip.text = text



    def caprica_timer(self, _time):
        '''
        def caprica_timer(self, _time)

        Parameters
        ----------
            param1 : self
                Denotes this as being a member of the SentienceScreen()
                class.
            param2 : _time
                Can be either double or of type int. I'm using it
                as an integer by supplying it with a whole part. This
                variable dictates how long the timer which is this
                function runs.
        Attributes
        ----------
            mins
                This variable stores the number of minutes that
                this timer function will run. mins is displayed and
                along with secs ticks down to reflect the amount of
                time that this function will run. Though the user can't
                see the visual display.
            secs
                This variable the number of seconds that this timer
                function will run. secs is displayed and along with
                mins ticks down to reflect the amount of time that
                this function will run. Though the user can't see
                the visual display.
            timeformat
                timeformat is the format of how the time will apear
                to the user when it's printed to the console. It
                looks like this. If you supply, 168 to this function
                it would output 2:48. Though the user can't see this
                visual timer.
        Members
        -------
            time.sleep(integer)
                We call time.sleep() to ensure that the timer
                only counts down 1 second at a time and that it
                doesn't interfere with any other active thread.
            divmod()
                This is a builtin python function which returns
                the quotient and remainder of the two numbrs
                whic are supplied to it; in this case mins, secs.
            str().format()
                This is a member of the built in python string class.
                It formats teh string to look however you set it. In
                our case we format the ticker display to print out
                2:48 if supplied with 168, if it were 120 it would
                look like 2:00.
            self.check_timer(_time)
                This is a member of the SentienceScreen() class.
                We call this function to ensure that _time is
                not less than or equal to zero if it is we terminate
                both self.check_timer and self.caprica_timer().
            self.notification_widget.foreground_color
                This is a member of the SentienceScreen() class. It's
                one of our TextInput widgets. We use this to change the
                foreground color, which is the color of the text. To
                reflect the active status of the program. If the chatbot
                is about to generate a response for the user the color
                of the text is changed to red. If the chatbot has just
                finished generating a response to the user the color
                of the text is blue.
            self.notification_widget.text
                This is a member of the SentienceScreen() class. We
                use this to set the text property of the
                self.notification_widget which is one of our
                TextInput widgets. We do this to reflect the current
                status of the program. If the chatbot is about to
                generate a response for the user we change the text
                to '...Thinking...' and set the color of the text to
                red. If the chatbot has just finished generating a
                response to the user we set the text to '...Inactive...'
                and change the color of the text to blue.
            kivy.utils.get_color_from_hex()
                This is a member of the kivy.utils() class. We call
                this function to convert a hexadecimal string to
                an integer or double value that (automaticaly double)
                that can be interpereted by the TextInput widget
                as an appropriate and existing color code. Kivy uses
                the opengl method setting colors and it's easier
                for me to work with hex then it is for me to determine
                the rgba-opnegl equivelant.
        Private Members
        ---------------
            None
        Exceptions
        ----------
            None
        Returns
        -------
            None
        Notes
        -----
            This function is not currently being used. But,
            an explanation of it's use is as follows. The developer
            supplies a number to the _time variable. This number
            represents the time that this function will run.

            This function should run as an independent thread which
            constantly ticks down until _time = 0. While it ticks
            down it should also flash the text '...Thinking...'
            until the function terminates when it sets the text
            to '...Inactive...'
        '''
        while _time:
            mins, secs = divmod(_time, 60)
            timeformat = '{:02d}:{:02d}'.format(mins, secs)
            time.sleep(1)
            _time -= 1
            self.ids.notification_widget.foreground_color = kivy.utils.get_color_from_hex('FF0000')
            self.ids.notification_widget.text = '..Thinking..'
        if self.check_timer(_time):
            self.ids.notification_widget.text = '...Inactive...'
            self.ids.notification_widget.foreground_color = kivy.utils.get_color_from_hex('00FFFF')



    def start_timer_thread(self, _time):
        '''
		start_timer_thread(self, _time)

		Parameters
		----------
		    self
			    self denotes this function as being a member of
				SentienceScreen().
			_time
			    _time is a double variable which contains a number.
				That numbers refers to a specific time value.
				For instance, if we pass 20 to _time it means
				five seconds. We use _time to run an event for _time
				length.
		Attributes
		----------
		self.ids.notification_widget
		    Refers to the notification_widget TextInput Widget in
			the kv design language.

		target
		   target is an attribute of the threading.Thread class.
		   We use that to register our event, which in this case
		   is the function self.caprica_timer.
		args
		    args is an attribute of the threading.Thread class.
			Its a tupple of arguments which will store the parameters
			of the event that target =. In this case args = _time
			which again holds a numerical value which refers to the time
			that the function self.caprica_timer will run. To be more
			accurate it's the time that self.caprica_timer will count
			down from.
		Members
		-------
		    self.notification_widget.opacity
			    This both a function and a property. We use
				this to set the opacity of the notification_widget
				TextInput widget which is in the kv design language.
				When opacity = 1 it's visible to the user. When
				opactiy = 0 it's invisible to the user.

			threading.Thread()
			    Thread is a member of the threading class. We use this
				to decalre, initialize and run a new thread.
			threading.Thread.start()
			    start() is a member of the threading.Thread class. This
				is what we use to actually start or run our newly
				created thread. Which in this case is
				self.caprica_timer().
		Private Members
		---------------
		    None
		Exceptions
		----------
		    None
		Returns
		-------
		    None
		Notes
		-----
		    We call this function to start a new thread to run
			the function self.caprica_timer. It's run as a seperate
			thread to prevent the user from thinking that the program
			is crashing. It's also much more efficent to do it this way.

			Unfortunately, on windows operating systems threading and
			multiprocessing has the effect of launching a new python
			interpreter in the form of a new window which quickly pops
			up and vanishes from the screen which could cuase fear in the
			user.

			However, this is not a bug, it's an intended feature. Python
			is neither meant for nor truly not meant for multithreading.
			However, the GIL or Global Interpereter Lock prevents true
			multithreading from occuring to prevent huge memory leaks
			and unsafe practices. There is unfortunately no way around
			this windowing effect. But, it's okay because aside from it
			being a minor annoyance it's not an actual issue.

			Essentially, this function is called and it sets the opacity
			of notification_widget TextInput Widget to 1; rendering it
			visible to the user. A new thread is then created and executed
			which enables the notification_widget to display "..Thinking.."
			while the bot searches its database for an answer.

			Users may or may not see this notification based on the
			"Magic Window" that pops up and based on the amount of time
			that it takes the bot to locate an appropriate response.
        '''
        threading.Thread(target = self.caprica_timer, args = (_time,)).start()



    def check_timer(self, _time):
        '''
		check_timer(self, _time)

		Parameters
		----------
		    param1 : self
			    self denotes this function as being a member of
				SentienceScreen().

			param2 : _time
			    _time is a double variable which contains a number.
				This number is used in self.caprica_timer as a countdown.
				This function monitors that countdown and ensures that
				when time is <= 0 the while loop in self.caprica_timer
				is broken. We also use this to know when to
				disable/enable some other features in that function.
				More information about self.caprica_timer can be found
				in it's comments. For our purpose here we check _time
				to see if it's <= 0 if it is we return True if
				_time is > 0 we return False.
		Attributes
		----------
		    _time
			    See above information in Paraemters section.
		Members
		-------
		    None
		Private Members
		---------------
		    None
		Exceptions
		----------
		    None
		Returns
		-------
		    True
			    We return True if _time is <= 0.
			False
			    We return False if _time is > 0.
		Notes:
		    This function is called during self.caprica_timer
			to check the variable _time. If the number stored in
			the variable _time is less than or equal to 0 we
			return True. If the number stored in _time is
            greater than 0 we return False.
        '''
        if _time <= 0:
            return True
        elif _time > 0:
            return False



    def get_caprica_response(self):
        '''
        get_caprica_response(self)

		Attributes
		----------
		    my_timer
			    my_timer is the decleration and intialization of
				threading.Thread(target = event, args = (params)).start()
				This one line code creates and starts a new thread. This
				thread allows us to use the self.caprica_timer() function.
			target
			    This variable is a member of the threading.Thread()
				class. It's used to register the passed event. Then
				call said event which is in this case the function
				self.start_timer_thread; which in turn calls the
				function self.caprica_timer.
			args
			    This variable is a member of the threading.Thread()
				class. It's used to store the parameters of the
				event thats passed to the target member of the
				threading.Thread() class. In this case we pass
				a number to it. This number is a double variable
				and refers to the amount of time that will be used
				in the self.caprica_timer function.
			response
			    The response variable is used to store the chatbots
				response. It's that simple. We call the chatbots
				function to get the response by passing it the users
				statement/question, etc.. The chatbot then searches the
				database for a response which bests fits teh string
				passed to the chatbots function. The returned data is
				then stored in the temp variable for later use and
				manipulation. This variable is used through out
				self.get_caprica_response() function except when
				the user has enabled the voice option and makes use
				of the voice option.
			self.master_log
			    This is a string variable which as its name states
				contains a master log of the conversation. In other
				words, it stores both the users text and the chatbots
				text in order as it's entered. This is done so that we
				can write a full file of the entire conversation. As it
				occurs. This is not done real time. It's done when the
				user clicks the "Write logs button" which is represented
				by a pencil on the menu bar (Action Bar).
			self.username
			    self.username contains the users username. This assumes
				that the user created a username. If the user did not
				create a username then a default value of 'User: '
				is provided. This is used in various ways: We set
				the view_port TextInput Widget conversation log
				with User: my statement. We append this data to the
				self.master_log string. We append this data to the
				User_statement.txt file.
			self.audio_disabled
			    This is a boolean variable which we use to check whether
				or not the user has disabled the audio option. If
				self.audio_disabled == True; then the audio option is
				disabled and the chatbot can only communicate with the
				user via text. If self.audio_disabled == False then
				self.audio_enabled == True; meaning that the audio mode
				is enabled and the chatbot can access the systems
				text to speech software and communicate verbally with
				the user.
			self.audio_enabled
			    This is a boolean variable which we use to check
				to see if the user has enabeld teh audio option.
				If the user has enabled the Audio option then Caprica
				can access the systems text to speech software and
				speak directly to the user.
				If self.audio_enabled == True then the user has
                enabled the Audio option; and the chatbot can then
                speak to the user verbally.
                If self.audio_enabled == False; then the user has either
                disabled the audio option or not bothered to enable it
                yet which means that the chatbot can only communicate
                with the usr via text.
			self.voice_enabled
			    This is a boolean variable which we use to check
				to see if the user has enabled the voice option.
				The voice option enables the user to access and use
				their microphone to speak directly to Caprica. If
				the user doesn't have a microphone then they can't use
				this option. If self.voice_enabled == True the user has
				turned on the voice option and does have a microphone.
				If self.voice_disabled == False; the user has either
				disabled the voice option or doesn't have a microphone.
			temp
			    The temp variable is used to store the chatbots
				response. It's that simple. We call the chatbots
				function to get the response by passing it the users
				statement/question, etc.. The chatbot then searches the
				database for a response which bests fits teh string
				passed to the chatbots function. The returned data is
				then stored in the temp variable for later use and
				manipulation. This variable is only used when the user
				has activated the voice option.
			self.mic
			    self.mic is the initialized object of the
				SpeechRecognition.Microphone() class. With
				this object we can access the users microphone
				and listen to the audio then pass into the
				recognizer object for transcription; and later
				storage as a string.
			source
			    The source variable is created to pipe the audio opened
				by self.mic; into the variable audio (which is an
				audio file). Source doesn't store the data. It simply
				passes the data into the audio variable as it's picked
				up by the users microphone. This of course assumes that
				the user has a microphone. If the user doesn't have a
				microphone then the user wont ever get into this
				function. The source object is cleared and destroyed
				when the with loop is ended. Using the with loop
				functionality automatically closes the loop, clears
				teh data, and deletes the object when the considiton
				reaches its breakpoint. In this case the breakpoint is
				when the user stops speaking. So basically, while this
				microphone is picking up noise pipe it through source
				and store it in the audio variable. When it stops picking
				up noise end the loop and clean up the data.
			statement
			    This is a string variable which is used to store
				the string returned by the
				self.record.recognize_sphinx(audio) function. The
				audio file passed to the above mentioned function is
				transcribed and returned as a string to the statement
				variable.
		Members
		-------
		    self.start_timer_thread(self, _time)
			    This function is called when it's passed to the
				my_thread object. When the new thread is started
				this is used to call the self.caprica_timer()
				function. The double variable passed to it
				which represents the amount of time that
				self.caprica_timer() runs.
			self.chatbot..get_response(words)
			    This function looks exeedingly complicated.
				But, it's not. Simply put this function is
				what takes the input from the user_input
				TextInput widget; passes it to the chatbot
				so it can locate an appropriate response by
				searching its database and then returns that
				string to either another variable or to a function.
				That string is then communicated to the user as
				the chatbots response. It checks to see if the
				user has enabled or disabled the audio and or
				voice modes. From there it accepts the input as
				it's intended to.
			threading.Thread(target = (), args = ())
			    This creates a new thread, this thread
				refers to a function or other event
				and the parameters of arguements to be
				passed to that event. So in our case,
				we use this to start a timer which counts
				down from the number supplied to args; the
				function self.caprica_timer then preforms
				the count down which is checked by
				self.check_timer to ensure that the double
				variable stored in _time is less than
				or equal to zero. If it's equal to zero the
				function ends. If it's not equal to zero
				the function display the text '..Thinking..'
				in the notification_widget TextInput widget.
			threading.Thread().start()
			    This function simply starts the new thread
				that was created. That is to say this function
				starts the my_thread thread.
			self.get_user_text()
			    This function is used to return the text
				contained in self.ids.user_input.text in
				the form of a string.
			datetime.datetime.now().strftime()
			    This function is called to return the current time
				in the form of a string. We use this to write the
				current time to a text file if an error occurs.
				This only executes if an error occurs.
			os.getlogin()
			    This function is called to return the users
				system username. We use this function to create
				and manipulate text files. Think about it this way.
				On linux /home/user/folder is a filepath.
				The user portion of that refers to the users
				logged in username. Without the current users
				system username we can't write text files because we
				don't know the full path to any safe locations for us
				to write this data.
			sys.platform.startswith('platform')
			    This function is called to check the user computers
				operating system. It checks a specific version number
				for each style of operating system. For instance,
				on windows this function checks registry keys and
				on linux it makes use of system call to return the
				major version string. On older linux systems this could
				return linux2, or linux3, or linux4, or linux1 etc.. In
				order to get around that we simply supply linux and parse
				the string to dertmine the version number. On windows
				it can return a variety of things such as win32.
				Supplying win as the parameter guarantees that we
				will determine if this is a windows based operating.
				We use this so that we can write the files and
				manipulate the program its self in a way that's
				compatible with the various operating systems.
			self.ids.user_input.text
			    This function returns the string currently contained
				in the user_input TextInput widget. We use this
				to return the users string to the chatbot so that it
				can formulate an appropriate response for the user.
				As well as returning it to the appending of
				self.master_log, self.__append_file(dat, path) etc.
			self.ids.user_input.focus
			    This function sets the current focus of the
				users mouse to user_input TextInput widget.
				Meaning that it's actively focused so the
				user doesn't have to click back into it.
				Unfortunately this is not having the desired
				effect on windows operating systems due to an
				ongoing issue with kivy and the windowing system
				on windows.
			self.caprica_speak(words)
			    We call this function when the user has activated
				either the audio or voice options. We pass the
				chatbots generated response to this function.
				We then access the systems text to speech software
				to verbally "speak" the chatbots response to the
				user.
			self.ids.view_port.text
			    We call this function to set the view_port TextInput
				widgets text property. We set this property to contain
				the users statement and the chatbots response in order.
				User: This is a statement.
				Caprica: Yes, that is a statement.
			self.record.listen(microphone_source)
			    We call this function to open the users microphone
				assuming the user has a microphone. If they don'take
				have a microphone the user wont be able to access the
				voice option. If they do have a microphone this function
				turns the microphone on and enables it to accept noise.
				The noise is the users input, Ie, the users words. The
				microphone remains in an active state as long as the
				user speaks. That data is then piped into the recognizer
				for transciption into a string.
			self.recognize_sphinx(audio_file)
			    This function is called after the user has made use
				of the voice option. It takes the audio file piped
				from the source variable to the audio variable which
				stores this data as an audio file. This audio file is
				then passed to self.recognize_sphinx(audio) which is
				then transcribed to a string and returned.
		Private Members
		---------------
		    self.__append_file(data, path)
			    We call this function to write specific data to a
				specific text file. The text written to th files comes
				in two flavors. All of the chatbots response are written
				to the Caprica_Statements.txt file. All of the users
				statements are written to User_Statements.txt file.
				We use this to segregate the statements made by the user
				and the chatbot for later training purposes.
			self._stop_threading()
			    This function is called to check to see if a thread is
				active. If a thread is active this function interupts
				the active thread which essentially (though not
				technically) kills it; to prevent memory leaks and
				a series of other potential issues.
		Exceptions
		----------
		    OSError
                The OSError can occur due to numerous reasons.
                What I'm primarily concerned with here however
                is import statements, incompatible Operating
                systems, and bad system calls. The exception
                if it occurs is handled and logged in an error
                log text file.

            IOError
                The IOError can occur due to many reasons.
                My primary concern is file manipulation. The
                improper opening/closing/writing to files. If
                the exception occurs it's handled and logged; in
                an error log text file.

            RunTimeError
                The RunTimeError error here is checking to make sure
                that the chat bot doesn't die. Essentially I just need
                to make sure that it completes and executes the python
                text to speech functions in a manner that doesn't cause
                a fatal exception. If something does occur the exception
                will be handled and logged to an error log text file.

            ValueError
                Ensures that values passed to the chat bot are
                appropriate. And if for some reason one isn't the
                exception will be handled and logged to an error
                log text file.
		Returns
		-------
		    None
		Notes
		-----
		    So this is a large function and I explained it quite
			well broken down in the sections above. An overview of
			this function is this.

			We check to see if the user has enabled or disabled the
			audio and voice options. We then accept the users input
			in a way appropriate to the option the user has elected
			to use. We then obtain a response from the chatbot and
			either send it to the user in text or audio form.
        '''
        try:
            if sys.platform.startswith('linux'):
                if self.audio_disabled:
                    response = str(self.chatbot.get_response(self.get_user_text()))
                    self.__append_file('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + self.get_user_text(), '/home/' + str(os.getlogin()) + '/.SentienceFiles/User_Statements.txt')
                    self.master_log += '\n' + self.username + ': ' + self.get_user_text()
                    self.__append_file('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + response, '/home/' + str(os.getlogin()) + '/.SentienceFiles/Caprica_Statements.txt')
                    self.master_log += '\nCaprica: ' + response
                    self.ids.view_port.text = self.username + ': ' + self.get_user_text() + '\nCaprica: ' + response
                    self.ids.user_input.text = ''
                    self.ids.user_input.focus = True
                    time.sleep(1)
                    self.__currently_thinking(False)
                elif self.audio_enabled:
                    self.__append_file('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + self.get_user_text(), '/home/' + str(os.getlogin()) + '/.SentienceFiles/User_Statements.txt')
                    self.master_log += '\n' + self.username + ': ' + self.get_user_text()
                    response = str(self.chatbot.get_response(self.get_user_text()))
                    self.__append_file('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + response, '/home/' + str(os.getlogin()) + '/.SentienceFiles/Caprica_Statements.txt')
                    self.master_log += '\nCaprica: ' + response
                    self.ids.view_port.text = self.username + ': ' + self.get_user_text() + '\nCaprica: ' + response
                    self.caprica_speak(response)
                    self.ids.user_input.focus = True
                    time.sleep(1)
                    self.__currently_thinking(False)
                elif self.voice_disabled:
                    self.ids.view_port.text = 'Please activate the voice option by clicking on the red microphone button'
                    return None
                elif self.voice_enabled:
                    with self.mic as source:
                        audio = self.record.listen(source)
                    statement = self.record.recognize_sphinx(audio)
                    self.__append_file('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + statement, '/home/' + str(os.getlogin()) + '/.SentienceFiles/User_Statements.txt')
                    self.master_log += '\n' + self.username + ': ' + str(statement)
                    temp = str(self.chatbot.get_response(statement))
                    self.__append_file('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + temp, '/home/' + str(os.getlogin()) + '/.SentienceFiles/Caprica_Statements.txt')
                    self.master_log += '\nCaprica: ' + temp
                    self.ids.view_port.text = self.username + ': ' + str(statement) + '\nCaprica: ' + str(temp)
                    self.caprica_speak(temp)
                    time.sleep(1)
                    self.__currently_thinking(False)
            elif sys.platform.startswith('win'):
                if self.audio_disabled:
                    response = self.chatbot.get_response(self.get_user_text())
                    self.__append_file('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ' ' + self.get_user_text(),"C://SentienceFiles//User_Statements.txt")
                    self.master_log += '\n' + self.username + ': ' + self.get_user_text()
                    self.__append_file('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ' ' + str(response),"C://SentienceFiles//Caprica_Statements.txt")
                    self.master_log += '\nCaprica: ' + str(response)
                    self.ids.view_port.text = self.username + ': ' + self.get_user_text() + '\nCaprica: ' + str(response)
                    self.ids.user_input.text = ''
                    self.ids.user_input.focus = True
                    time.sleep(1)
                    self.__currently_thinking(False)
                elif self.audio_enabled:
                    self.__append_file('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + self.get_user_text(), 'C://SentienceFiles//User_Statements.txt')
                    self.master_log += '\n' + self.username + ': ' + self.get_user_text()
                    response = self.chatbot.get_response(self.get_user_text())
                    self.__append_file('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + str(response), 'C://SentienceFiles//Caprica_Statements.txt')
                    self.master_log += '\nCaprica: ' + str(response)
                    self.ids.view_port.text = self.username + ': ' + self.get_user_text() + '\nCaprica: ' + str(response)
                    self.caprica_speak(str(response))
                    self.ids.user_input.focus = True
                    time.sleep(1)
                    self.__currently_thinking(False)
                elif self.voice_disabled:
                    self.ids.view_port.text = 'Please activate the voice option by clicking on the red microphone button'
                    return None
                elif self.voice_enabled:
                    with self.mic as source:
                        audio = self.record.listen(source)
                    statement = self.record.recognize_sphinx(audio)
                    self.__append_file('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + statement, 'C://SentienceFiles//User_Statements.txt')
                    self.master_log += '\n' + self.username + ': ' + statement
                    temp = self.chatbot.get_response(statement)
                    self.__append_file('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + str(temp), 'C://SentienceFiles//Caprica_Statements.txt')
                    self.master_log += '\nCaprica: ' + str(temp)
                    self.ids.view_port.text = self.username + ': ' + statement + '\nCaprica: ' + str(temp)
                    self.caprica_speak(str(temp))
                    time.sleep(1)
                    self.__currently_thinking(False)
        except OSError as c:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: get_user_voice_response ' + '\nOSError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: get_user_voice_response ' + '\nOSError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except IOError as d:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: get_user_voice_response ' + '\nIOError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: get_user_voice_response ' + '\nIOError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except RuntimeError as e:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: get_user_voice_response ' + '\nRuntimeError: ' + str(e) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: get_user_voice_response ' + '\nRuntimeError: ' + str(e) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except ValueError as f:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: get_user_voice_response ' + '\nValueError: ' + str(f) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: get_user_voice_response ' + '\nValueError: ' + str(f) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None



    def get_caprica_voice_thread(self, words):
        '''
        get_caprica_voice_thread(self, words)

        Parameters
        ----------
            param1 : self
                Denotes this as being a member of SentienceScreen().
            param2 : words
                A string containing the users transcribed voice response
                is passed to this for later manipulation.
        Attributes
        ----------
            temp
                temp is a string variable that is used to temporarily
                store the generated response of the chatbot. This
                variable will then be written to varios files and
                displayed in the view_port TextInput widget.
            self.master_log
                self.master_log is a string variable wich contains a
                master conversation log. This log includes the text
                sent by the user and the responses generated by
                the chatbot as they appear.
            self.username
                self.username is a string variable which contains the
                users chosen username. IF the user did not elect to
                setup a user profile a default value of 'User: ' is
                provided.
        Members
        -------
            self.caprica_speak(words)
                This function is called after the user has sent
                text to the chatbot. That text is then passed to
                this funtction if self.audio_enabled == True
                or if self.voice_enabled == True. We then
                access the users systems text to speech software
                to verbally speak the passed string. This function
                is a member of SentienceScreen().
            time.sleep(integer)
                We call time.sleep(1) to force the program to
                sleep for one second. This ensures that certain
                functions are called by forcing the Kivy.clock() to
                appropriately execute events in the correct order
                in the frame. It also prevents the program from hanging
                by trying to execute things to fast. This function is a
                member of the class time.
            sys.platform.startswith(string)
                We call this function to determine the users operating
                system. If the user is running a windows system then
                the appropriate if statements execute. If they're
                running a linux system again the appropriate if
                statements are executed. We determine this by accessing
                the systems major version. For instance, older
                linux systems return values such as, linux1, linux2,
                linux3 and so on. Windows systems may return win32 etc.
                By checking the preceeding version string, Ie, 'linux'
                we know it's a linux system, or 'win' we know it's a
                windows system. Where these strings comes from varies
                based on the operating system. On linux it's an os call.
                On windows it's a registry key. This function is a
                member of the class sys.
            datetime.datetime.now().strftime(string)
                We call this function to return the current local time.
                We format it to ourput in
                year, month, day, hours, minutes seconds. This is
                returned as a string directly to our write method.
            os.getlogin()
                This function is a member of the os class. We call
                this function to return the current users system user
                name. We do this so that we can succesfully write files
                to the users system. On linux the filesystem has the
                users name as part of it's non root path. We need this
                name to access the location where we want to write to.
        Private Members
        ---------------
            self.__append_file(string, path)
                This function is a member of SentienceScreen(). We
                call this function to append specific data to
                specific text files. The data is passed in as a string.
                As is the path to the file.
            self._stop_threading()
                This function is a member of the SentienceScreen()
                class. we call this function to interupt our running
                threads.
            self.__currently_thinking(boolean)
                This function is a member of the SentienceScreen()
                class. We call this function to change the current
                banner which informs the user if the program is
                currently inactive or thinking. It change the text to
                either '...Thinking...' with a red foreground. Or,
                '...Inactive...' with a blue foreground. The boolean
                variable dictates whether or not the program is in fact
                actively thinking or not.
        Exceptions
        ----------
             OSError
                 The OSError can occur due to numerous reasons.
                 What I'm primarily concerned with here however
                 is import statements, incompatible Operating
                 systems, and bad system calls. The exception
                 if it occurs is handled and logged in an error
                 log text file.

             IOError
                 The IOError can occur due to many reasons.
                 My primary concern is file manipulation. The
                 improper opening/closing/writing to files. If
                 the exception occurs it's handled and logged; in
                 an error log text file.

             RunTimeError
                 The RunTimeError error here is checking to make sure
                 that the chat bot doesn't die. Essentially I just need
                 to make sure that it completes and executes the python
                 text to speech functions in a manner that doesn't cause
                 a fatal exception. If something does occur the
                 exception will be handled and logged to an error log
                 text file.

             ValueError
                 Ensures that values passed to the chat bot are
                 appropriate. And if for some reason one isn't the
                 exception will be handled and logged to an error
                 log text file.
        Returns
        -------
            None
        Notes
        -----
            This function is one our response threads. We call it
            if the user has activated the voice feature. Ie, if
            self.voice_enabled == True, this function will be called
            when the user clicks on the enable/disable voice button
            which is represented by a red or blue microphone on the
            menu bar (Action Bar).

            We determine the users operating system. Obtain the chatbots
            generated response. Next we append it to
            the Caprica_Statements text file. We then save it to the
            master log. We then display the response and the users
            initial text in the view_port TextInput widget. Next we
            call self.caprica_speak(words) to actually verbally
            communicate the chat bots response to the user.

            We next interupt the thread and put the program to sleep
            for one second by calling time.sleep(1). We finally
            call self.__currently_thinking(False) to reset the
            banner text to '...Thinking...' with a blue foreground.

        '''
        try:
            if sys.platform.startswith('linux'):
                temp = str(self.chatbot.get_response(words))
                self.__append_file('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + temp, '/home/' + str(os.getlogin()) + '/.SentienceFiles/Caprica_Statements.txt')
                self.master_log += '\nCaprica: ' + temp
                self.ids.view_port.text = self.username + ': ' + str(words) + '\nCaprica: ' + str(temp)
                self.caprica_speak(temp)
                time.sleep(1)
                self.__currently_thinking(False)
            elif sys.platform.startswith('win'):
                temp = str(self.chatbot.get_response(words))
                self.__append_file('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + str(temp), 'C://SentienceFiles//Caprica_Statements.txt')
                self.master_log += '\nCaprica: ' + str(temp)
                self.ids.view_port.text = self.username + ': ' + str(words) + '\nCaprica: ' + str(temp)
                self.caprica_speak(str(temp))
                time.sleep(1)
                self.__currently_thinking(False)
        except OSError as c:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: get_caprica_voice_thread ' + '\nOSError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: get_caprica_voice_thread ' + '\nOSError: ' + str(c) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except IOError as d:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: get_caprica_voice_thread  ' + '\nIOError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: get_caprica_voice_thread  ' + '\nIOError: ' + str(d) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except RuntimeError as e:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: get_caprica_voice_thread  ' + '\nRuntimeError: ' + str(e) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: get_caprica_voice_thread  ' + '\nRuntimeError: ' + str(e) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except ValueError as f:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: get_caprica_voice_thread  ' + '\nValueError: ' + str(f) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: get_caprica_voice_thread  ' + '\nValueError: ' + str(f) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None



    def start_get_response_thread(self):
        '''
		self.start_get_response_thread(self)

		Parameters
		----------
		    param1 : self

		Attributes
		----------
		    target
			    target is a member of the Process() class.
		Members
		-------
		    self.ids.notification_widget.text
			   This is a member of SentienceScreen() and is the
			   notification_widget TextInput Widget in the kv
			   design language. We use this to set the current text of the
			   notification_widget TextInput Widget to the supplied string.
               This widget is used to display the text '..Thinking..'
               while the chatbot is locating an appropriate response for
               the user.
            self.ids.notification_widget.foreground_color
                This is a member of SentienceScreen() and is the
                notification_widget TextInput Widget in the kv
                design language. We use this to set the current
                text color of the widget. Here we see two examples.
                If we change the text to ...Thinking... we change the
                color to red; this shows the user that the program is
                active and that the chatbot is currently generating a
                response. If we change the text to ...Inactive... then
                we change the text color to blue. This tells the user
                that the chatbot has generated a response and that
                the user can once again speak to it.
			Threading.Thread(target = event, args = (tuple)).start()
                threading.Thread() is called to create a new thread.
                This is used to run the acquisition of the a response
                from the chatbot to the user. We pass the
				function self.get_caprica_response to this as its event
				and because self.get_caprica_response doesn't require
				any arguements we omit the "args" parameter that we
				saw in the threading code. We then call start() to
				actually run the thread.
            Time.sleep(time_interval)
                We call this function to force the program to "sleep",
                for 1 second. This executes the two lines above
                Time.sleep(1) before it creates and starts the thread.
                We do this to prevent hanging issues caused by the
                threading event and to ensure that the proper text
                and color of the text is set; and more importantly,
                so that the user can see this text.
            kivy.utils.get_color_from_hex('Hex string')
                This is a kivy function. It's a member of kivy.utilsself.
                We call this function to convert a hexadecimal string
                into an equivelant opengl based rbga color.
            sys.platform.os.startswith('string')
                This is a member of the Python sys (system) library.
                We call this function to check the major version
                of the users operating system. By doing so we can
                determine if the user is running a windows or linux based
                operating system. Note: See how I said "A" instead of
                windows 10 or ubuntu? By using .startswith('') we
                simply detect the operating system and are able
                to be truly cross platform.
            time.sleep()
                This is a member of the Time class(). We call this
                function to force the program to sleep for one second.
                To ensure that the notification_widget TextInput
                text property reflects the current state of the program.
		Private Members
		---------------
		    self.__set_thinking_text
                We call this function to inform the user that the
                chatbot is about to generate a response. The
                self.notification_widget has its text set to
                '...Thinking...' and the text is also made red.
		Exceptions
		----------
		    None
		Returns
		-------
		    None
		Notes
		-----
		    This function is called when the user sends a response to
			the chatbot. We use this to start self.get_caprica_response
			as a new thread to improve performance.

            We first detect the operating system, then set the text
            of self.notification_widget to be appropriate, we then
            change the color to reflect the text as mentioned
            above. We then force the program to sleep for one second
            to ensure those changes take effect. We finally create and
            run a new thread which then starts the
            self.get_caprica_response() function.
        '''
        if sys.platform.startswith('linux'):
            if len(self.get_user_text()) <= 1:
                self.ids.view_port.text = 'Please enter at least two characters. Like Hi'
                self.ids.user_input.text = ''
            elif len(self.get_user_text()) > 1:
                self.__currently_thinking(True)
                time.sleep(1)
                threading.Thread(name = 'linux_thread', target = self.get_caprica_response).start()
        elif sys.platform.startswith('win'):
            if len(self.get_user_text()) <= 1:
                self.ids.view_port.text = 'Please enter at least two characters. Like Hi'
                self.ids.user_input.text = ''
            elif len(self.get_user_text()) > 1:
                self.__currently_thinking(True)
                time.sleep(1)
                threading.Thread(name = 'windows_thread', target = self.get_caprica_response).start()



    def start_voice_response_thread(self):
        '''
        start_voice_response_thread(self)

        Parameters
        ----------
            param1 : self
                Denotes this as being a member of the SentienceScreen()
                class.
        Attributes
        ----------
            self.voice_disabled
                This is a member of the SentienceScreen() class.
                We use this boolean variable asa flag o tell us
                whether or not the user enabled or disabled the
                voice option. If the user has disabled the voice
                they will informed that the voice option is
                disabled and that they need to enable it. They
                can do so by clicking on the red microphone
                button on the menu bar (Action Bar).
            self.vocice_enabled
                This is a member of the SentienceScreen() class. We
                we use this boolean variable as flag to tel us
                whether or not the user has enabled or disabled
                the voice option. If the voice option is activated
                the users microphone will be opened and voice input
                will be recorded as long as the microphone picks up
                noise.
            self.mic
                self.mic is a member of the SentienceScreen() class.
                It's also the instantiated object of sr.Microphone).
                We use this object to open the users microphone if
                they have one and pipe the input through sthe source
                variable. When the user stops speaking the microphone
                should close the audio in source which is being
                listened to is then returned to the audio variable.
            source
                source is a local variable of the function
                self.get_caprica_voice_thread(). We use this variable
                to store the input piped from the users microphone.
                Once the microphone stops picking up audio input
                we then transcribe the audio data into a string
                by passing it to self.recognize_sphinx(audio).
            statement
                statement is a local variable of the function
                self.get_caprica_voice_thread() we use it to
                store the transcribed string which is returned
                to us by the self.recognize_sphinx(audio) function.
            audio
                audio is a local variable of the function
                self.get_caprica_voice_thread(). We use this
                variable to store the audio data collected
                by source which was piped through the users
                microphone. We then pass this variable to
                self.recognize_sphinx(audio). Which is then
                transcribed from audio data and returned as
                a string and stored in the statement variable.
            self.master_log
                self.master_log is a member of the SentienceScreen()
                class. This variable is used to store the full
                conversation between the chatbot and the user. This
                variable is later used to write data to a file.
        Members
        -------
            sys.platform.startswith(string)
                This is a member of the sys() class. We call this
                function to find out which operating system the
                user is running. To be specific, we're only checking
                for windows and linux based operating systems. This
                funtion returns True if it matches 'linux', if
                this happens we know that the user is running a
                linux based operating system. If it returns False,
                we then check to see if the user is running a windows
                based operating sytem by passing 'win' to the function.
            self.record.listen(source)
                We call this function to "listen" or, accept and store
                the audio being piped through the users microphone
                into the source variable. When the microphone no
                longer detects audio input this audio data is
                returned and stored in the audio variable.
            self.ids.view_port.text
                This is a member of the SentienceScreen() class. We use
                this to set the view_port TextInput widgets text field.
                If the user hasn't enabled the voice option we
                inform the user that the voice option is currently
                disabled and that they can enable it by clicking
                on the red mirophone button on the menu bar (Action
                Bar).
            self.record.recognize_sphinx(audio)
                We call this function to transcribed the passed
                audio file into a string. The audio passed was
                collected via the users microphone. This audio
                data is transcribed into a string and returned and
                stored in the statement variable.
            threading.Thread(*args)
                This is a member of the threading() class. We use
                this to declare, instantiate and run our thread all at
                once. The thread is given a name based on the users
                operating system. Ie, if it's linux, it's named
                'linux_thread' and if it's windows it's named
                'windows_thread'. We then pass it the target event
                which is self.get_caprica_voice_thread(statement).
                We finally call the start() function of the
                threading class to actually start the new thread.
            datetime.datetime.now().strftime(string)
                This is a member of the datetime() class.
                We use this function to return the current local time
                inside our file appending function. The time format
                is set to year, month, day, hour, minute, seconds.
            self.get_caprica_voice_thread(string)
                This is a member of the SentienceScreen() class.
                We call this function as the event which is the
                thread. That is to say this is the new thread. We
                pass it the users transcribed verbal statement which
                is stored in the string variable statement.
            time.sleep(integer)
                This is a member of the time() class. We call
                this function to put the program to sleep for one
                second. We do this to ensure that the thread is
                not executed until after the text, and the color of
                the text in the self.notification_widget TextInput
                widget have been changed to reflect the programs
                current status.
        Private Members
        ---------------
            self.__append_file(string, path)
                This is a member of the SentienceScreen() class.
                We call this function and pass it the string
                which contains the users response to the chatbot
                as well as the date and time that this response
                occured. We then supply it with the absolute file
                path of the file that we're writing to which is
                the User_Statements.text file. This path depends on
                the users operating system.
            self.__currently_thinking(bool)
                This is a member of the SentienceScreen() class.
                We call this function to set the current text and
                color of that text to reflect the programs current
                status. We pass it a boolean variable which is used
                to determine this status. For more information on
                this function see its comments.
        Exceptions
        ----------
            None
        Returns
        -------
            None
        Notes
        -----
            This function is really straightforward. We use this
            when the user clicks on the record user button. Which is
            represented by the blue talking human head on the menu bar.

            If the button is red when the user clicks it, it means that
            the voice option wasn't enabled. We then inform the user
            in the view_port TextInput widget that the voice option
            is not currently enabled. We also inform them how to
            activate this option.

            Once the voice mode is activated and the record user
            button has been clicked. We open the users mirophone
            and pipe the audio input into source which is passed
            to the listen() function and stored in its audio form.

            When the microphone stops picking up audio input
            listen() function terminates and returns the audio
            to the local variable named audio.

            We then pass the audio variable into the function
            recognize_sphinx() which transcribes it into a string.
            Returns that string to be stored in the local variable
            named statement.

            We then append the users response to the chatbot as well
            as the date and time this response occured to the
            User_Statement text file. We then add this response to
            the end of the master_log string. Along with the users
            username.

            We then set the current status of the chatbot, Ie,
            thinking or inactive. Which is then reflected in
            the notification_widget text property. We then call
            time.sleep() and give it a one second interval to
            ensure that the above does occur before the thread
            is setup and run.
        '''
        if sys.platform.startswith('linux'):
            if self.voice_disabled:
                self.ids.view_port.text = 'Please activate the voice option by clicking on the red microphone button'
                return None
            elif self.voice_enabled:
                with self.mic as source:
                    audio = self.record.listen(source)
                statement = self.record.recognize_sphinx(audio)
                self.__append_file('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + statement, '/home/' + str(os.getlogin()) + '/.SentienceFiles/User_Statements.txt')
                self.master_log += '\n' + self.username + ': ' + str(statement)
                self.__currently_thinking(True)
                time.sleep(1)
                threading.Thread(name = 'linux_thread', target = self.get_caprica_voice_thread(statement)).start()
        elif sys.platform.startswith('win'):
            if self.voice_disabled:
                self.ids.view_port.text = 'Please activate the voice option by clicking on the red microphone button'
                return None
            elif self.voice_enabled:
                with self.mic as source:
                    audio = self.record.listen(source)
                statement = self.record.recognize_sphinx(audio)
                self.__append_file('\n' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + str(statement), 'C://SentienceFiles//User_Statements.txt')
                self.master_log += '\n' + self.username + ': ' + str(statement)
                self.__currently_thinking(True)
                time.sleep(1)
                threading.Thread(name = 'windows_thread', target = self.get_caprica_voice_thread(statement)).start()



    def get_user_text(self):
        '''
		We call this function to return the text contained in
		self.ids.user_input.text TextInput Widget; in the form of a
		string.
        '''
        return str(self.ids.user_input.text)



    def open_delete_file_dialog(self):
        '''
        open_delete_file_dialog(self)

        Parameters
        ----------
            param1 : self
                Denots this as being a member of SentienceScreen().
        Attributes
        ----------
            content
                content is local variable to the function
                self.open_delete_file_dialog() we use this
                to make a new Object. This object is DeleteDialog
                we then add the instantiated object to Popup().
                Note: We add the local object content which is
                the DeleteDialog to the kivy Popup() content field.
                We do this because of how the layouts work.
            delete_file
                delete_file is the ObjectProperty() that we
                created in the DeleteDialog() class. We're using
                this property, to bind it to the
                SentienceScreen.().delete_file() function.
            self.popup
                self._popup is the decleration and initialization
                of the kivy Popup(). We've created this object, this
                Popup() window and can now call it at anytime.
            Cancel
                Cancel is the ObjectProperty() that we
                created in the DeleteDialog() class. We're using
                this property, to bind it to the
                SentienceScreen.().dismiss_popup() function.
            title
                title is a member of the Kivy Popup() class. It's
                a StringProperty() which we use to set the title of
                the Popup() window.
            size_hint
                size_hint is member of the Kivy Popup() class, and
                all other kivy widgets. We use size_hint to to set
                the size of the widget. This enables us to set a
                size based of percentages of the users monitor size.
                Simply put, this enables us to create a size that's
                compatiable with all devices and will stretch and
                shrink in a manner that wont distort the programs
                appearance.
        Members
        -------
            Popup()
                Popup() is a kivy widget which is exactly what it
                sounds like. It's a popup window. It's not a new window,
                it's a widget wich locks to the MainWindow (root window);
                we use this to allow the user to navigate to a
                specific file, select that file, and then delete it.
            DeleteDialog(FloatLayout)
                DeleteDialog is a class with a default FloatLayout
                that we created earlier. We use this class and its
                layout with our Popup() widget.
            self._popup.open()
                We call this function to add the Popup() widget
                to the screen.
            self.delete_file(self, path, filename)
                self.delete_file(self, path, filename) is the
                same function that we bound to the delete_file
                ObjectProperty; we just ommited its parameters
                when we did it. It recieves its arguements when
                the users selects a file (clicks on one) in the
                Popup() window and then clicks the delete button
                in the Popup() window. This function is passed
                the name of the file and it's file path. I
                actually don't use all of the parameters. But
                both of them could be used.
            self.dismiss_popup()
                We call this function to delete the Popup() window
                from the screen.
       Private members
       ---------------
           None
        Returns
        -------
            None
        Exceptions
        ----------
            None
        Notes
        -----
            This function is pretty straight forward. When the user
            clicks on the "Delete File" button a popup window is
            created and then added to the screen. This window contains
            a file browser, and two buttons. The file browser allows
            the user to navigate through their file system and select
            a file that they wish to delete.

            Once the user has located the file they wish to delete
            they simply click on that file, which selects it, and
            then click the "Delete" button in the popup window.

            This then returns the filename and path of the file to
            the self.delete_file(self, path, file). Which then preforms
            the deletion operation.

            We then finally close the popup by removing (deleting) it
            from the MainWindow.
        '''
        content = DeleteDialog(delete_file = self.delete_file, Cancel = self.dismiss_popup)
        self._popup = Popup(title = "Select File For Deletion", content = content, size_hint = (0.9, 0.9))
        self._popup.open()



    def delete_file(self, path, filename):
        '''
        delete_file(self, path, filename)

        Parameters
        ----------
            param1 : self
                Denotes this as being a member of the SentienceScreen()
                class.

            param2 : path
                contains the partial path to the file
                returned to it by the users selection in the
                DeleteDialog() pop up window. This parameter
                does not contain the filename. Nor is it ever
                used. It's pointless to even be here.

            param3: filename
                filename contains the full file path to the
                file that the user selected for deletion by
                clicking on the file and then clicking the
                delete button in the DeleteDialog() Popup()
                window.
        Attributes
        ----------
            temp
                temp contains teh formatted and fbsolute filepath
                to the file that the user selected for deletion. This
                path is then passed to os.remove(temp) to carry out
                the actual deletion process.
        Members
        -------
            os.path.isfile(path)
                We call this function which is a member of the
                os() class. To ensure that the filepath passed to
                it does indeed exist. If it does exist this function
                returns tru and the appropriate if statement is
                executed. If it returns False the nthe file does not
                exist and again the appropriate if statement is
                executed.

        os.remove(path)
            We call this function which is a member of the os()
            class to carry out the deletion process of the file
            that the user selected. This call makes use of the
            users systems native API deletion feature.

        self.ids.view_port.text
            We call this function which is a member of the
            SentienceScreen() class. To change the text of the
            view_port TextInput widget. The text set depends on
            whether or not the file was deleted. If the file
            selected did exist and was deleted the text is
            changed to 'Filepath File has been deleted'. If
            the file did not exist and therefor was not deleted
            then the text is set to 'Filepath either does not exist
            or was already deleted'.
        Private Members
        ---------------
            None
        Exceptions
        ----------
            IOError
                The IOError can occur due to many reasons.
                My primary concern is file manipulation. The
                improper opening/closing/writing to files. If
                the exception occurs it's handled and logged; in
                an error log text file.

            FileNotFoundError
                This can occur in a variety of ways however my primary
                concern is that file path the user selected is broken.
                Resulting in an File Not Found error. If this occurs
                it's handled and logged to an error file text log.
        Returns
        -------
            None
        Notes
        -----
            This function is called after the user selects a file
            that they wish to delete in the DeleteDialog() Popup()
            window. Then proceeds by clicking the delete button on
            that Popup() window. The partial path with out the
            file name is returned to this funtion but is not used.

            The full filepath is also returned and stored in the
            variable filename. We store filename in the string variable
            temp. We then strip the first two, and last two characters
            in the temp variable. Filename is returned as tupple and
            so it contains '[/example/filepath/random.text]'.

            We then ensure that the selected file does exist
            and if it does we delete it and inform the user
            that the file was succesfully deleted. If the file
            doesn't exist during the initial check we then
            inform the user that it doesn't exist or that
            it's already been deleted.
        '''
        try:
            temp = str(filename)
            temp = temp[2:-2]
            if os.path.isfile(temp):
                print(temp + ' Has been deleted')
                os.remove(temp)
                self.ids.view_port.text = str(temp) + ' File has been deleted.'
            elif not os.path.isfile(temp):
                print(temp + ' Either does not exist or was already deleted.')
        except IOError as a:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: delet_files ' + '\nIOError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: delete_files ' + '\nIOError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except FileNotFoundError as b:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: delet_files ' + '\nFileNotFoundError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: delete_files ' + '\nFileNotFoundError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None



    def delete_all(self):
        '''
        delete_all(self)

        Paraemters
        ----------
            param1 : self
                Denotes this as being a member of
                SentienceScreen().
        Attributes
        ----------
            temp
                temp is a local variable which we use to store the
                absolute directory path; to the folder that was
                created when this program was first run. This folder
                varies based on the users operating system. We pass
                this variable to our deletion tool.
         ignore_errors
             This is sort of a misnomer. This a member of the
             shutil.rmtree() class. It doesn't actually ignore
             any errors. It just forces the function to delete
             the files and or folders and more importantly, to
             not print out any errors. It's a boolean variable
             and we set it to true to ensure that it does in fact
             force the deletion of the folder.
        Members
        -------
            sys.platform.startswith('string')
                We use this function to detect the users operating
                system. It will determine whether or not you're using
                a windows or linux based operating system. It doesn't
                search for a specific version. It just ensures that
                you're using one of them. This allows us to make this
                program cross platform.
            shutil.rmtree(path, optional_boolean)
               We use this function to preform our deletion operations.
               By default it makes use of the native systems api to
               preform this operation. We need to suuply it a path,
               this where our temp variable comes in. You'll remember
               that we stored the path to the directory in it. We
               also suply this function with a boolean variable
               ignore_errors and set it to True. As mentioned above
               this simply ensures that the folder gets deleted,
               whether it's empty (this is what it checks for) or not
               and prevents it from spitting out any warnings or errors
               from the system. This bool vairable is by default set
               to False.
            self.ids.view_port.text
                This is the view_port TextInput widget in the
                kv code. We use this widget to display certain
                warnings and conversations to the user. In this
                case when the folder has been deleted we inform the
                user by printing out the folders path and stating
                that it has been deleted.
            Private members
            ---------------
                self.__append_file(string, filepath)
                   This function is a member of SentienceScreen(). We
                   call this function to append error messages if they
                   occur to an error log. We supply the function,
                   the exception, what occured, and the date and time
                   that it occured to this fileself.
            Returns
            -------
                None
            Exceptions
            ----------
                IOError
                    The IOError can occur due to many reasons.
                    My primary concern is file manipulation. The
                    improper opening/closing/writing to files. If
                    the exception occurs it's handled and logged; in
                    an error log text file.
                FileNotFoundError
                    This can occur in a variety of ways however my
                    primary concern is that file path the user selected
                    is broken. Resulting in an File Not Found error.
                    If this occurs it's handled and logged to an error
                     file text log.
            Notes
            -----
                First we check to make sure the user is running a
                viable operating system. Rather, one that's
                compatible with this program. We then execute the
                appropriate code.

                We create a variable named temp and sore the absolute
                path of the directory (folder) that we're going to
                delete.

                We then call shutil.rmtree() to make access of the
                systems native api to delete the directory. Once deleted
                we display a message which includes the full directory
                path and a string stating that the folder has been
                deleted.

                If any errors occur we record and log them to an error
                log.
        '''
        try:
            if sys.platform.startswith('linux'):
                temp = '/home/' + str(os.getlogin()) + '/.SentienceFiles/'
                shutil.rmtree(temp, ignore_errors=True)
                self.ids.view_port.text = temp + ' and all of its contents have been deleted'
                App.get_running_app().stop()
            elif sys.platform.startswith('win'):
                temp = 'C://SentienceFiles//'
                shutil.rmtree(temp, ignore_errors=True)
                self.ids.view_port.text = temp + ' and all of its contents have been deleted'
                App.get_running_app().stop()
        except IOError as a:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: delet_all ' + '\nIOError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: delete_all ' + '\nIOError: ' + str(a) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None
        except FileNotFoundError as b:
            if sys.platform.startswith('linux'):
                self.__append_file('\n' + 'Function: delete_all ' + '\nFileNotFoundError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '/home/' + str(os.getlogin()) + '/.SentienceFiles/Error Logs.txt')
            elif sys.platform.startswith('win'):
                self.__append_file('\n' + 'Function: delete_all ' + '\nFileNotFoundError: ' + str(b) + '\nDate - Time:' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'C://SentienceFiles//Error Logs.txt')
            return None



    def __set_thinking_text(self, bool):
        '''
        __Set_thinking_text(self, bool)

        Parameters
        ----------
            param1 : self
                Denotes this as being a member of the SentienceScreen()
                class.

            param2 : bool
                The boolean variable contains the dertmining factor
                for how the text will be set and what color that text
                will be in the self.notification_widget. It recieves
                this information from the
                self.__currently_thinking() function.
        Attributes
        ----------
            bool
                if bool == True then the chatbot is about to begin
                generating a response for the user. We then set the
                text field of self.notification_widget to
                '...Thinking...' and set the foreground to red. If
                it's False we know then that the chatbot just
                finished generating a response. We then set the text
                field of self.notification_widget to '...Inactive...'
                with a blue foreground.
        Members
        -------
        self.notification_widget.text
            We use this to set the text field of the
            self.notification_widget TextInput widget to the
            appropriate text based on the preceeding conditions. This
            is a member of the SentienceScreen() class.

        self.ids.notification_widget.foreground_color
            We use this to give the text a color. The color is relative
            to the programs current status. If the program is
            '...Thinking...' then the text will be red. If the program
            is '...Inactive...' then the text will be blue. This
            function is a member of the SentienceScreen() class.

        kivy.utils.get_color_from_hex('hex string')
            This is a member of the Kivy base class. We use this
            function to convert a hexadecimal string to a compatiable
            color read as an integer by the self.ids.notification_widget
            TextInput widget.
        Private Members
        --------------
            None
        Exceptions
        ----------
            None
        Returns
        -------
            None
        Notes
        -----
            We call this function to change the self.notification_widget
            TextInput widgets text field to either '...Thinking...' or
            '...Inactive...'. This status is determined when the chatbot
            is generating or finished generating a response. If the
            chatbot is generating a response it's thinking. If it has
            finished generating a reponse then it's set to inactive.

            We then change the color of the text using a hex string
            which is then read as an integer byt the
            self.notification_widget.foreground_color property.
            If the program is thinking then the text is made red.

            If the program is inactive then the text is made blue.
        '''
        if bool == True:
            self.ids.notification_widget.text = '...Thinking...'
            self.ids.notification_widget.foreground_color = kivy.utils.get_color_from_hex('FF0000')
        elif bool == False:
            self.ids.notification_widget.text = '...Inactive...'
            self.ids.notification_widget.foreground_color = kivy.utils.get_color_from_hex('00FFFF')



    def __currently_thinking(self, bool):
        '''
        __currently_thinking(self, bool)

        param1: self
            Denotes this as being a member of the SentienceScreen()
            class.

        param2 : bool
            A boolean variable is passed to this function and
            then used to dertime the text in the self.notification_widget
            TextInput Widget.

        Attributes
        ----------
            bool
                bool is used to store the boolean variable
                passed to this function upon its function call.
        Members
        -------
            None
        Privat Members
        --------------
            self.__is_thinking
                self.__is_thinking is a member of the SentienceScreen()
                class. We use this to monitor the status the 'thinking'
                status of the program and to switch it on and off. If
                it's on self.notification_widget has its text field set
                to '...Thinking...' with a red foreground. If it's off
                self.notification_widget has its text field set to
                '...Inactive...' with a blue foregrounf.
            self.__set_thinking_text(bool)
                Once we know if the program is currently thinking
                we call this function which is a member of the
                SentienceScreen() class. To actually change
                the text field of the self.notification_widget.
        Notes
        -----
            We call this function to check to see if the chatbot
            is about to begin generating a response to the user.

            If the chatbot is about to begin it's generation process
            we set the self.__is_thinking variable to True, we then
            call self.__set_thinking_text(bool) to change the
            text field of self.notification_widget to '...Thinking...'
            with a red foreground.

            If the chatbot is done generating a resposne we set
            the variable self.__is_thinking to False, and then call
            self.__set_thinking_text(bool) to change the text field
            of the self.notification_widget to '...Inactive...' with
            a blue foreground color.
        '''
        if bool == True:
            self.__is_thinking = True
            return self.__set_thinking_text(True)
        elif bool == False:
            self.__is_thinking == False
            return self.__set_thinking_text(False)



class ActionInput(TextInput, ActionItem):
    '''
    Creates a class for the ActionInput(TextInput, ActionItem):

    This TextInput will be placed on the ActionBar()

    '''
    pass


class sentienceScreenManager(ScreenManager):
    '''
    sentienceScreenManager(ScreenManager)
    container/manager for SentienceScreen:
    '''
    pass


root_widget = Builder.load_string('''
#:import Config kivy.config
#:import Window kivy.core.window
#:import Clock kivy.clock
#:import ActionBar kivy.uix.actionbar
#:import Animation kivy.animation.Animation
#:import hex kivy.utils.get_color_from_hex

sentienceScreenManager:
    SentienceScreen:

<ToolTipLabel@Label>:
    size_hint: None, None
    text_size: self.width, None
    height: self.texture_size[1]

    canvas.before:
        Color:
            rgb: 0,0,0
        Rectangle:
            size: self.size
            pos: self.pos

<SentienceScreen>:
    name: 'main_screen'

    TextInput:
        id: view_port
        size_hint: .5, .85
        pos_hint: {'x': .5, 'y': .0 }
        multiline: True
        hint_text: 'Conversation log'
        readonly: True
    TextInput:
        id: user_input
        size_hint: .5, .05
        pos_hint: {'x': 0, 'y': .80 }
        multiline: False
        hint_text: 'Type your question/response'
        on_text_validate: root.start_get_response_thread()
    TextInput:
        id: notification_widget
        size_hint: .3, .05
        pos_hint: {'x': .80, 'y': .85}
        multiline: False
        readonly: True
        text: '...Inactive...'
        foreground_color: hex('00FFFF')
        background_color: (0,0,0,0)
    TextInput:
        text: "Please allow 20-90 seconds for a response. Don't interact with the program until its status is ...Inactive... in blue text."
        size_hint: 1, .05
        pos_hint: {'x': 0, 'y': .85}
        font_size: '12sp'
        readonly: True
        foreground_color: (1,1,0,1)
        background_color: (0,0,0,0)

    ActionBar:
        id: menu_bar
        pos_hint: {'top':1}
        ActionView:
            use_separator: True
            ActionPrevious:
                title: 'Menu'
                with_previous: False
            ActionOverflow:
            ActionSeparator:
                separtor_width: 10
                opacity: 0
            ActionButton:
                id: display_convo
                text: 'Display Conversations'
                on_press: root.display_user_conversation()
            ActionButton:
                id: open_settings
                text: 'Settings'
                on_press: app.open_settings()
            ActionSeparator:
                separtor_width: 10
                opacity: 0
            ActionButton:
                id: record_user
                text: 'Record'
                on_release: root.start_voice_response_thread()
            ActionSeparator:
                separtor_width: 10
                opacity: 0

<PrintDialog>:
    BoxLayout:
        size: root.size
        pos: root.pos
        orientation: 'vertical'
        FileChooserListView:
            id: filechooser
        BoxLayout:
            size_hint_y: None
            height: 30
            Button:
                text: 'Cancel'
                on_release: root.Cancel()
            Button:
                text: 'Print File'
                on_release: root.print_files(filechooser.path, filechooser.selection)

<DeleteDialog>:
    BoxLayout:
        size: root.size
        pos: root.pos
        orientation: 'vertical'
        FileChooserListView:
            id: deletion_chooser
        BoxLayout:
            size_hint_y: None
            height: 30
            Button:
                text: 'Cancel'
                on_release: root.Cancel()
            Button:
                text: 'Delete File'
                on_release: root.delete_file(deletion_chooser.path, deletion_chooser.selection)
''')


class SentienceApp(App):

    def build(self):
        '''
            Kivy App() class is the core class that creates the
             main window and runs the program.

             You'll also see that I've created a series of variables
             which are used to store the data contained in
             Sentience.ini

             The data stored in these variables is loaded into them
             everytime that this program is run so that they always
             reflect the accurate settings.
        '''
        self.title = 'Honors Project: Sentience'
        self.settings_cls = SettingsWithSidebar #
        self.config.items('settings_menu')
        self.sentience = root_widget.get_screen('main_screen')
        self.use_kivy_settings = False
        self.sentience.caprica_speak('Loading your settings now.')
        self.is_audio_on = self.config.get('settings_menu', 'enable_audio')
        self.increased_rate_of_speech = self.config.get('settings_menu', 'increase_rate_of_speech')
        self.decreased_rate_of_speech = self.config.get('settings_menu', 'decrease_rate_of_speech')
        self.is_voice_on = self.config.get('settings_menu', 'enable_voice')
        self.print_status = self.config.get('settings_menu', 'get_file_printed')
        self.delete_file_status = self.config.get('settings_menu', 'get_file_deleted')
        self.delete_all_status = self.config.get('settings_menu', 'delete_everything')
        self.user_exists = self.config.get('settings_menu', 'create_user')
        self.gender_exists = self.config.get('settings_menu', 'create_gender')
        self.age_exists = self.config.get('settings_menu', 'create_age')
        self.clear_screen_status = self.config.get('settings_menu', 'clear_screen')
        self.file_creation_status = self.config.get('settings_menu', 'write_user_data')
        self.load_settings()
        return root_widget



    def load_settings(self):
        '''
            This is fairly straightforward. When the program launches
            we look at the data contained in Sentience.ini which holds
            the values from our Ssettings panel. Everytime that the
            user changes a setting it's written to Sentience.ini

            Based on those settings we set or ignore specific variables
            from SentienceScreen(). We use this to maintain continuity
            between the end of the program and it being restarted.
        '''
        if '1' in self.is_audio_on:
            self.sentience.audio_enabled = True
            self.sentience.audio_disabled = False
            self.sentience.set_enable_disable_audio()
        elif '0' in self.is_audio_on:
            self.sentience.audio_enabled = False
            self.sentience.audio_disabled = True
            self.sentience.set_enable_disable_audio()
        if int(self.increased_rate_of_speech) > 0:
            self.sentience.increase_rate_of_speech(int(self.increased_rate_of_speech))
        elif int(self.increased_rate_of_speech) <=0:
            pass
        if int(self.decreased_rate_of_speech) > 0:
            self.sentience.decrease_rate_of_speech(int(self.decreased_rate_of_speech))
        elif int(self.decreased_rate_of_speech) <=0:
            pass
        if '1' in self.is_voice_on:
            self.sentience.voice_enabled = True
            self.sentience.voice_disabled = False
            self.sentience.set_enable_disable_voice()
        elif '0' in self.is_voice_on:
            self.sentience.voice_enabled = False
            self.sentience.voice_disabled = True
            self.sentience.set_enable_disable_voice()
        if 'print file' in self.print_status:
            self.config.set('settings_menu', 'get_file_printed', 'None')
            self.write()
        elif 'None' in self.print_status:
            pass
        if 'delete file' in self.delete_file_status:
            self.config.set('settings_menu', 'get_file_deleted', 'None')
            self.config.write()
        elif 'delete file' or 'None' not in self.delete_file_status:
            self.config.set('settings_menu', 'get_file_deleted', 'None')
            self.config.write()
        if 'delete all' in self.delete_all_status:
            self.config.set('settings_menu', 'delete_everything', 'None')
            self.config.write()
        elif 'delete all' or 'None' not in self.delete_all_status:
            self.config.set('settings_menu', 'delete_everything', 'None')
            self.config.write()
        if 'None' not in self.user_exists:
            self.set_username(self.user_exists)
        elif 'None' in self.user_exists:
            pass
        if 'None' not in self.gender_exists:
            self.set_gender(self.gender_exists)
        elif 'None' in self.gender_exists:
            pass
        if 'None' not in self.age_exists:
            self.set_age(self.age_exists)
        elif 'None' in self.age_exists:
            pass
        if 'yes' or 'Yes' in self.clear_screen_status:
            self.config.set('settings_menu', 'clear_screen', 'None')
            self.config.write()
        elif 'yes' or 'Yes' or 'None' not in self.clear_screen_status:
            self.config.set('settings_menu', 'clear_screen', 'None')
            self.config.write()
        if 'write file' in self.file_creation_status:
            self.config.set('settings_menu', 'write_user_data', 'None')
            self.config.write()
        elif 'write file' or 'None' not in self.file_creation_status:
            self.config.set('settings_menu', 'write_user_data', 'None')
            self.config.write()



    def build_config(self, config):
        '''
            We call this to build the menu. We're establishing
            default values which we'll then load in from our json
            string. This is what creats the actuall widgets and
            links them to the keys, provides default values, and
            registers them.
        '''
        config.setdefaults('settings_menu', {
                           'enable_audio': False,
                           'increase_rate_of_speech': 0,
                           'decrease_rate_of_speech': 0,
                           'enable_voice': False,
                           'get_file_printed': None,
                           'select_your_os': None,
                           'get_file_deleted': None,
                           'delete_everything': None,
                           'create_user': None,
                           'create_gender': None,
                           'create_age': None,
                           'clear_screen': None,
                           'write_user_data': None
                           })



    def build_settings(self, settings):
        '''
            Here we add the settings panel as widget in the form
            of a json object. We pass it the name of our panel,
            Sentience Settings, our self.config from build_config
            and the json strings which contains all of the data in
            self.config. This setups, create and adds the settings
            panel to the screen.
        '''
        settings.add_json_panel('Sentience Settings', self.config, data = my_settings)



    def on_start(self):
        '''
            This function creates a cProfiler() to help us
            diagnose potential issues.
        '''
        self.profiler = cProfile.Profile()
        self.profiler.enable()



    def on_stop(self):
        '''
            When the program is exited the profiler is stopped
            and the .profile file containing the data that's
            been accumulated to help test the program is output
            to a file named SentiencePRofile.profile
        '''
        self.profiler.disable()
        self.profiler.dump_stats('SentienceProfile.profile')



    def warning_removal(self, dt):
        '''
            A simple function to clear the contents of
            self.sentience.ids.view_port Widget.
        '''
        self.sentience.ids.view_port.text = ''



    def set_username(self, value):
        '''
            This function is called to set the first key of
            self.sentience.user_profile[1] dictionary to
            value. value is then stored in self.sentience.username
            self.sentience.master_log string is then cleared to
            ensure a new user experience is created. We then create
            the user profile which basically just reads the users
            input username which is stored in value.
        '''
        self.sentience.user_profile[1] = value
        self.sentience.username = value
        self.sentience.master_log = ''
        self.sentience.create_user_profile()



    def set_gender(self, value):
        '''
            We call this function to set the gender supplied to
            value when the users modifies the Gender setting in
            the settings menu. We store the gender in value in
            self.sentience.user_priofile[3]. We then clear the
            self.sentience.master_log string to ensure a new
            experience has been created for the current user.
        '''
        self.sentience.user_profile[3] = value
        self.sentience.master_log = ''



    def set_age(self, value):
        '''
            We call this function to set the age supplied to
            value when the users modifies the age setting in
            the settings menu. We store the gender in value in
            self.sentience.user_priofile[2]. We then clear the
            self.sentience.master_log string to ensure a new
            experience has been created for the current user.
        '''
        self.sentience.user_profile[2] = value
        self.sentience.master_log = ''



    def on_config_change(self, config, section, key, value):
        '''
            Simple vent monitor. Every time that the user changes
            a setting on the Settings panel, this function is called.

            It recevies the section (menu), the key (specific option),
            and the value which is what the current option has been
            changed to. From there we change the variables in the
            SentienceScreen() class.
        '''
        if section == 'settings_menu':
            if section == 'settings_menu' and key == 'enable_audio' and value == '1':
                self.sentience.audio_enabled = True
                self.sentience.audio_disabled = False
                self.sentience.set_enable_disable_audio()
                self.config.set('settings_menu', 'enable_audio', value)
                self.config.write()
            elif section == 'settings_menu' and key == 'enable_audio' and value == '0':
                self.sentience.audio_enabled = False
                self.sentience.audio_disabled = True
                self.sentience.set_enable_disable_audio()
                self.config.set('settings_menu', 'enable_audio', value)
                self.config.write()
            elif section == 'settings_menu' and key == 'enable_voice' and value == '1':
                self.sentience.voice_enabled = True
                self.sentience.voice_disabled = False
                self.sentience.set_enable_disable_voice()
                self.config.set('settings_menu', 'enable_voice', value)
                self.config.write()
            elif section == 'settings_menu' and key == 'enable_voice' and value == '0':
                 self.sentience.voice_enabled = False
                 self.sentience.voice_disabled = True
                 self.sentience.set_enable_disable_voice()
                 self.config.set('settings_menu', 'enable_voice', value)
                 self.config.write()
            elif section == 'settings_menu' and key == 'create_user' and 'None' not in value:
                self.set_username(value)
                self.config.set('settings_menu', 'create_user', value)
                self.config.write()
            elif section == 'settings_menu' and key == 'create_gender' and 'None' not in value:
                self.set_gender(value)
                self.config.set('settings_menu', 'create_gender', value)
                self.config.write()
            elif section == 'settings_menu' and key == 'create_age' and 'None' not in value:
                self.set_age(value)
                self.config.set('settings_menu', 'create_age', value)
                self.config.write()
            elif section == 'settings_menu' and key == 'clear_screen' and 'yes' or 'Yes' in value:
                self.sentience.clear_viewport()
                self.config.set('settings_menu', 'clear_screen', 'None')
                self.config.write()
            elif section == 'settings_menu' and key == 'get_file_deleted' and 'delete file' in value:
                self.sentience.open_delete_file_dialog()
                self.config.set('settings_menu', 'get_file_deleted', 'None')
                self.config.write()
            elif section == 'settings_menu' and key == 'delete_everything' and 'delete all' in value:
                self.config.set('settings_menu', 'delete_everything', 'None')
                self.config.write()
                self.sentience.delete_all()
            elif section == 'settings_menu' and key == 'get_file_printed' and 'print file' in value:
                self.sentience.open_print_file_dialog()
                self.config.set('settings_menu', 'get_file_printed', 'None')
                self.config.write()
            elif section == 'settings_menu' and key == 'write_user_data' and 'write file' in value:
                self.sentience.write_logs()
                self.config.set('settings_menu', 'write_user_data', 'None')
                self.config.write()
            elif section == 'settings_menu' and key == 'increase_rate_of_speech':
                if int(value) >= 1:
                    self.sentience.increase_rate_of_speech(int(value))
                    self.config.set('settings_menu', 'increase_rate_of_speech', value)
                    self.config.write()
                elif int(value) <=0:
                    self.sentience.increase_rate_of_speech(20)
                    self.config.set('settings_menu', 'increase_rate_of_speech', '20')
                    self.config.write()
            elif section == 'settings_menu' and key == 'decrease_rate_of_speech':
                if int(value) >= 1:
                    self.sentience.decrease_rate_of_speech(int(value))
                    self.config.set('settings_menu', 'decrease_rate_of_speech', value)
                    self.config.write()
                elif int(value) <=0:
                    self.sentience.decrease_rate_of_speech(20)
                    self.config.set('settings_menu', 'decrease_rate_of_speech', '20')
                    self.config.write()



if __name__ == '__main__':
    ''' Main Loop
    '''
    SentienceApp().run()
