# start the server
& 'c:\tools\rats\Bozok 1.5.1\server.exe'
Start-Sleep -Seconds 5

# get pid
# $process_id = (Get-Process -Name server).id # does not work
$process_id = (Get-Process server | sort CPU | select -last 1).id # this one works
# cmd /c pause | out-null # debug

# update
$configuration = Get-Content -path "c:\tools\apps\apt_collector_release-master\user_configuration.txt"
$configuration[12] = "output_whitelist_processid $process_id"
$configuration | Set-Content -path "c:\tools\apps\apt_collector_release-master\user_configuration.txt"
