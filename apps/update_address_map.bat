:: author:cyrus
:: date:7/2/2018

@echo off
:: unzip, -o+ means override all if exists
:: "c:\program files\winrar\winrar" x -o+ %userprofile%\appdata\local\temp\symchk-master.zip %userprofile%\appdata\local\temp
:: "c:\program files\winrar\winrar" x -o+ %userprofile%\appdata\local\temp\callstracktracegenerate-master.zip %userprofile%\appdata\local\temp
:: "c:\program files\winrar\winrar" x -o+ %userprofile%\appdata\local\temp\apt_collector_release-master.zip %userprofile%\appdata\local\temp
"c:\program files (x86)\winrar\winrar" x -o+ symchk-master.zip .
"c:\program files (x86)\winrar\winrar" x -o+ callstracktracegenerate-master.zip .
"c:\program files (x86)\winrar\winrar" x -o+ apt_collector_release-master.zip .

:: update symbols
rd /s /q  c:\symbols\ntkrnlmp.pdb
.\symchk-master\symchk.exe /r c:\windows\system32\ntoskrnl.exe /s srv*c:\symbols*http://msdl.microsoft.com/download/symbols

rd /s /q  c:\symbols\win32k.pdb
.\symchk-master\symchk.exe /r c:\windows\system32\win32k.sys /s srv*c:\symbols*http://msdl.microsoft.com/download/symbols

:: copy symbols
where /r c:\symbols win32k.pdb > win32k.path
set /p win32k= < win32k.path
xcopy /y %win32k% .\callstracktracegenerate-master\res
del win32k.path

where /r c:\symbols ntkrnlmp.pdb > ntkrnlmp.path
set /p ntkrnlmp= < ntkrnlmp.path
xcopy /y %ntkrnlmp% .\callstracktracegenerate-master\res
del ntkrnlmp.path

:: update address map
del /q .\callstracktracegenerate-master\addressmap
cd .\callstracktracegenerate-master
obtain_syscall_address.exe
cd ..

del /q .\apt_collector_release-master\addressmap
xcopy /y .\callstracktracegenerate-master\addressmap .\apt_collector_release-master

del /q .\apt_collector_release-master\output.out

echo done
echo. & pause