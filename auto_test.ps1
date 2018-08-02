#update pid

# start the server
& 'c:\tools\rats\SpyGate RAT v3.3\server.exe'

# get pid
# $process_id = (Get-Process -Name server).id # does not work
$process_id = (Get-Process server | sort CPU | select -last 1).id # this one works
# cmd /c pause | out-null # debug

# update
$configuration = Get-Content -path "c:\tools\apps\apt_collector_release-master\user_configuration.txt"
$configuration[12] = "output_whitelist_processid $process_id"
$configuration | Set-Content -path "c:\tools\apps\apt_collector_release-master\user_configuration.txt"

#start client and auto test
#cd "C:\tools\apps\apt_collector_release-master"
#c:\tools\apps\apt_collector_release-master\ETWDataCollectorRedesigned.exe -f
#sleep 20
cd "C:\tools\rats\SpyGate RAT v3.3"
& "C:\tools\rats\SpyGate RAT v3.3\SpyGate.exe"
cd "C:\tools\uipath_projects\SpyGate RAT v3.3"
C:\Users\Debugger\AppData\Local\UiPath\app-18.2.3\UiRobot.exe -f "C:\tools\uipath_projects\SpyGate RAT v3.3\Main.xaml"

#end
taskkill /im server.exe /f
taskkill /im "SpyGate.exe" /f
#$date = Get-Date -Format 'yyyyMMddHHmmss'
#copy C:\tools\apps\apt_collector_release-master\output.out -destination c:\tools\output\SpyGate-RAT-v3.3-$date.out