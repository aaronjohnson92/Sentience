Add-Type -AssemblyName System.IO.Compression.FileSystem
if ((gwmi win32_operatingsystem | select osarchitecture).osarchitecture -eq "64-bit")
{
    Write "Downloading files for 64bit installation"
    $INSTALLME = "C:\Sentience-Install-Files"
	$SWIGDIR = "C:\swigwin-3.0.12"
	$swig_url = "https://sourceforge.net/projects/swig/files/swigwin/swigwin-3.0.12/swigwin-3.0.12.zip/download"
	$vs_url = "https://download.visualstudio.microsoft.com/download/pr/11835057/045b56eb413191d03850ecc425172a7d/vs_Community.exe"
	$sapi = "https://www.microsoft.com/en-us/download/confirmation.aspx?id=27226&6B49FDFB-8E5B-4B07-BC31-15695C5A2143=1"
	$env:Path = "C:\swigwin-3.0.12.zip"
    if(!(Test-Path -Path $INSTALLME))
	{
        New-Item -ItemType directory -Path $INSTALLME
		Write "Folder Created: "  $INSTALLME
		[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls11 -bor [System.Net.SecurityProtocolType]::Tls12;
	    Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.6.4/python-3.6.4-amd64.exe -OutFile C:\Sentience-Install-Files\python-3.6.4-amd64.exe
        Invoke-WebRequest -Uri http://www.ch-werner.de/sqliteodbc/sqliteodbc_w64.exe -OutFile C:\Sentience-Install-Files\sqliteodbc_w64.exe
        Invoke-WebRequest -Uri http://www.ch-werner.de/sqliteodbc/sqliteodbc.exe -OutFile C:\Sentience-Install-Files\sqliteodbc.exe
        Invoke-WebRequest -Uri http://www.ch-werner.de/sqliteodbc/sqliteodbc_w64_dl.exe -OutFile C:\Sentience-Install-Files\sqliteodbc_w64_dl.exe
        Invoke-WebRequest -Uri http://www.ch-werner.de/sqliteodbc/sqliteodbc_dl.exe -OutFile C:\Sentience-Install-Files\sqliteodbc_dl.exe
	    Invoke-WebRequest -Uri https://github.com/mhammond/pywin32/releases/download/b223/pywin32-223.win-amd64-py3.6.exe -OutFile C:\Sentience-Install-Files\pywin32-223.win-amd64-py3.6.exe
	    Invoke-WebRequest -Uri $sapi -OutFile C:\Sentience-Install-Files\MicrosoftSpeechPlatformSDK.msi
	    Invoke-WebRequest -Uri $swig_url -OutFile C:\Sentience-Install-Files\swigwin-3.0.12.zip -UserAgent [Microsoft.PowerShell.Commands.PSUserAgent]::FireFox
	    Invoke-WebRequest -Uri $vs_url -OutFile C:\Sentience-Install-Files\vs_community__779108239.1520996107.exe -UserAgent
	    [Microsoft.PowerShell.Commands.PSUserAgent]::FireFox
    
    }
	
	if(Test-Path -Path $INSTALLME)
	{
	    Write "Folder" $INSTALLME " Already exists"
	}
    
    if(!(Test-Path -Path $SWIGDIR))
	{
        New-Item -ItemType directory -Path $SWIGDIR
		Write "Folder Created: "  $SWIGDIR
		Expand-Archive C:\Sentience-Install-Files\swigwin-3.0.12.zip -DestinationPath C:\
    }
	
	if(Test-Path -Path $SWIGDIR)
	{
	    Write "Folder" $SWIGDIR " Already exists"
	}
	
	Write-host "
	Please note that the visual studio 2017 community url may be temporary 
	and if it doesn't download correctly you'll have to obtain it manually you can
	do so by going to https://www.visualstudio.com/downloads/ once there choose the 
	Visual Studio Community 2017 free download. 
	
	After you've installed everything in C:\Sentience-Install-Files\
	Including Visual Studio community 2017, we can continue with the installation if
        you attempt to continue with the installation without installing everything you 
        will not be able to progress and the remaining requirements will break.	
	Please type (y/n) and hit enter when ready to continue: " -ForegroundColor Red
    $Readhost = Read-Host " (y/n) " 
    Switch ($ReadHost) 
     { 
       Y {[Envrionment]::SetEnvrionmentVariable("Path", $env:Path, [System.EnvrionmentVariableTarget]::Machine); python -m pip install Cython; python -m pip install --upgrade pip wheel setuptools; python -m pip install docutils pygments kivy.deps.sdl2 kivy.deps.glew kivy.deps.gstreamer kivy.deps.angle kivy kivy_examples pandas xlwt chatterbot SpeechRecognition PocketSphinx pyttsx3 PyAudio; Remove-Item .\Sentience-Install-Files\ -Force -Recurse} 
       N {Write-Host "Aborting Installation, you can resume at any time be re-running ./Setup.ps1"} 
       Default {Write-Host "Aborting Installation, you can resume at any time be re-running ./Setup.ps1"} 
     } 

}   
else
{
    Write "Downloading Files for 32bit installation"
	$INSTALLME = "C:\Sentience-Install-Files"
	$SWIGDIR = "C:\swigwin-3.0.12"
	$swig_url = "https://sourceforge.net/projects/swig/files/swigwin/swigwin-3.0.12/swigwin-3.0.12.zip/download"
	$vs_url = "https://download.visualstudio.microsoft.com/download/pr/11835057/045b56eb413191d03850ecc425172a7d/vs_Community.exe"
	$sapi = "https://www.microsoft.com/en-us/download/confirmation.aspx?id=27226&6B49FDFB-8E5B-4B07-BC31-15695C5A2143=1"
	if(!(Test-Path -Path $INSTALLME))
	{
        New-Item -ItemType directory -Path $INSTALLME
		Write "Folder Created: "  $INSTALLME
		[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls11 -bor [System.Net.SecurityProtocolType]::Tls12;
		Invoke-WebRequest https://www.python.org/ftp/python/3.6.4/python-3.6.4.exe -OutFile C:\Sentience-Install-Files\python-3.6.4.exe
        Invoke-WebRequest http://www.ch-werner.de/sqliteodbc/sqliteodbc.exe -OutFile C:\Sentience-Install-Files\sqliteodbc.exe
        Invoke-WebRequest http://www.ch-werner.de/sqliteodbc/sqliteodbc_dl.exe -OutFile C:\Sentience-Install-Files\sqliteodbc_dl.exe
        Invoke-WebRequest https://github.com/mhammond/pywin32/releases/download/b223/pywin32-223.win32-py3.6.exe -OutFile C:\Sentience-Install-Files\pywin32-223.win32-py3.6.exe
        Invoke-WebRequest -Uri $sapi -OutFile C:\Sentience-Install-Files\MicrosoftSpeechPlatformSDK.msi
	    Invoke-WebRequest -Uri $swig_url -OutFile C:\Sentience-Install-Files\swigwin-3.0.12.zip -UserAgent [Microsoft.PowerShell.Commands.PSUserAgent]::FireFox
	    Invoke-WebRequest -Uri $vs_url -OutFile C:\Sentience-Install-Files\vs_community__779108239.1520996107.exe -UserAgent [Microsoft.PowerShell.Commands.PSUserAgent]::FireFox
    }
	
	if(Test-Path -Path $INSTALLME)
	{
	    Write "Folder" $INSTALLME " Already exists"
	}
		
	 if(!(Test-Path -Path $SWIGDIR))
	{
        New-Item -ItemType directory -Path $SWIGDIR
		Write "Folder Created: "  $SWIGDIR
		Expand-Archive C:\Sentience-Install-Files\swigwin-3.0.12.zip -DestinationPath C:\
    }
	
	if(Test-Path -Path $SWIGDIR)
	{
	    Write "Folder" $SWIGDIR " Already exists"
	}
	
	Write-host "
	Please note that the visual studio 2017 community url may be temporary 
	and if it doesn't download correctly you'll have to obtain it manually you can
	do so by going to https://www.visualstudio.com/downloads/ once there choose the 
	Visual Studio Community 2017 free download. 
	
	After you've installed everything in C:\Sentience-Install-Files\
	Including Visual Studio community 2017, we can continue with the installation if
        you attempt to continue with the installation without installing everything you 
        will not be able to progress and the remaining requirements will break.	
	Please type (y/n) and hit enter when ready to continue: " -ForegroundColor Red
    $Readhost = Read-Host " (y/n) " 
    Switch ($ReadHost) 
     { 
       Y {[Envrionment]::SetEnvrionmentVariable("Path", $env:Path, [System.EnvrionmentVariableTarget]::Machine); python -m pip install Cython; python -m pip install --upgrade pip wheel setuptools; python -m pip install docutils pygments kivy.deps.sdl2 kivy.deps.glew kivy.deps.gstreamer kivy.deps.angle kivy kivy_examples pandas xlwt chatterbot SpeechRecognition PocketSphinx pyttsx3 PyAudio; Remove-Item .\Sentience-Install-Files\ -Force -Recurse} 
       N {Write-Host "Aborting Installation, you can resume at any time be re-running ./Setup.ps1"} 
       Default {Write-Host "Aborting Installation, you can resume at any time be re-running ./Setup.ps1"} 
     } 
}
