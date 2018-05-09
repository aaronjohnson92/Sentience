# Sentience
Sentience is a machine learning cheatbot. Run the progra mand converse with the bot via text, or, microphone (if you have one). The chatbot can respond in either text or voice, by default if the chatbot verbally speaks to you it also prints out text of what its said.

The layout and use of the program should be quite straightforward. You run the program "Sentience.Py", and type a phrase into the text box which prompts you for your text. You can change the settings of the program by clicking on the "Settings" button. This program saves your settings so that you don't have to constantly change them. A more indepth explination of how to use the program is described in the users manual. 

The users manual also contains installation instructions. There are requirements to run this program, those requirements are outlined in the users manual under the installation section. There are two automatic installer scripts, one for linux and one for windows. The linux installer should run without any issues on ubuntu/kubuntu. The windows installer is somewhat buggy and you're not advised to use it until it's fixed. When it's fixed this file will be updated, this file will be periodically updated anyway.

Unfortunately this program will not run on Ubuntu/kubuntu 18.04 due to a build issue with the GUI Framework used by this software. You can chose to install the unstable devloper branch of the GUI framework, but unless you know what you're doing and are prepared to deal with bugs you shouldn't. They are aware of the issue and are in the process of handling it as its been patched in the dev branch.


The GUI framework that this program uses is Kivy 1.9.1 the main website for kivy can be found at https://kivy.org/#home
The kivy github page can be found at https://github.com/kivy

The core learning module is the python chatterbot module which can be found at https://github.com/gunthercox/ChatterBot
You can view this page to learn how to generate new conversational databases. This process can be done automatically using functions provided by the chatterbot module. You can also create your own custom training data which is again explained in-depth in the chatterbot documentation.

Due to size restrictions I'm only able to upload a small starter database. This basically means that right now the bot is dumb, very dumb. This program is still in its early stages of devlopment, and everything, except printing on linux systems currently works. 

You can view the user manual by locating and opening the USer manual folder, and you can view the doxygen generated documentation (Latex pdf) by locating and opening the pdf file in the Docs folder.
