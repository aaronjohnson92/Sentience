This is only for windows users with Powershell version >= 5.0

Open power shell as administrator type "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned" without quotes and then hit the enter key.

Then hit the "y" key on your keyboard and hit the enter key.

Next open the windows menu and type "Settings" open that and scroll down till you see "Update & Security" Click on that. 

Scroll down the list untill you see "For developers" click on that.  Make sure you check the box titled "Developer Mode".

Next go back to your powershell and type cd C:\ then hit the enter key.

Next, Type ./Setup.ps1 and hit the enter key and follow the prompts.

If you get an error stating that you don't have permission to do this. Make sure you've run the powershell in administrator mode

If you continue to get that error do the following:

Set-ExecutionPolicy Unrestricted (then hit enter)

then Type Get-ExecutionPolicy and hit enter, if it says "Unrestricted"

Type ./Setup.ps1 hit the enter key and then hit "r" for run once.
-----------------------------------------------------------------
If you experience any errors during this installation, (which is 
possible as this was only tested on 5.0) please refer back to the 
users manual to preform a manual instalation.
