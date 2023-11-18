:: Author Stuart Beesley - StuWareSoftSystems - April 2022
:: Windows version of Moneydance launch script
:: Download the relevant Java JDK from here: https://adoptium.net/temurin/releases
:: Download the relevant javafx from glueonhq - e.g. https://download2.gluonhq.com/openjfx/18/openjfx-18_windows-x86_bin-sdk.zip
:: Run this bat file from the Moneydance' application's lib directory
:: Review launch-moneydance.sh (MacOS shell script) for a fuller implementaion... Copy bits into here as required.
:: NOTE: vmoptions file name must match the .exe name to take effect if running via .exe

@echo off
setlocal enabledelayedexpansion enableextensions
set LIST=
::for %%x in (%baseDir%\*) do set LIST=!LIST! %%x
for %%x in (*.jar) do set LIST=!LIST!;%%x
set LIST=%LIST:~1%

java -cp %LIST% --module-path D:\javafx-sdk-18\lib --add-modules javafx.swing,javafx.media,javafx.web,javafx.fxml Moneydance -d

 