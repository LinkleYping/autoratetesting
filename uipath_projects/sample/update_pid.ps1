# start the server
& 'c:\tools\rats\Greame RAT v1.9\server.exe'
# get pid
# $process_id = (Get-Process -Name server).id
$process_id = (Get-Process server | sort CPU | select -last 1).id
# debug begin
# cmd /c pause | out-null
# debug end
# update
$configuration = Get-Content -path "c:\tools\apps\apt_collector_release-master\user_configuration.txt"
$configuration[12] = "output_whitelist_processid $process_id"
# rewrite
$configuration | Set-Content -path "c:\tools\apps\apt_collector_release-master\user_configuration.txt"
