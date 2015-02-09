; save current window ID to return here later
WinGet stID, ID, A

WinGet, RprocID, ID, ahk_class Rgui
if (RprocID == "")
{
    WinGet, RprocID, ID, ahk_class Rgui Workspace
}

if (RprocID == "")
{
    Rguiexe = %1%
    if (Rguiexe = 1) {
        RegRead, Rhome, HKEY_LOCAL_MACHINE,SOFTWARE\R-core\R, InstallPath
        Rguiexe := Rhome . "\bin\x64\Rgui.exe"
    }
    else if (Rguiexe = 0){
        RegRead, Rhome, HKEY_LOCAL_MACHINE,SOFTWARE\R-core\R, InstallPath
        Rguiexe := Rhome . "\bin\i386\Rgui.exe"
    }
    else if 0=0
    {
        ; debug
        RegRead, Rhome, HKEY_LOCAL_MACHINE,SOFTWARE\R-core\R, InstallPath
        Rguiexe := Rhome . "\bin\i386\Rgui.exe"
    }
    OutputDebug Rhome from registry is %Rhome%
    Outputdebug % dstring . "R not found"

    run %Rguiexe% --sdi
    WinWait ,ahk_class Rgui,, 2
    WinGet RprocID, ID, ahk_class Rgui
}

Outputdebug % dstring . "RprocID=" . RprocID

oldclipboard = %clipboard%

if 0=2
{
    cmd = %2%
    cmd := RegExReplace(cmd, "^\n", "")
    newline = `n
    clipboard := cmd . newline
}
else {
    ; for debug
    clipboard = proc.time()`n
}
WinMenuSelectItem ahk_id %RprocID%,,2&,2& ;edit->paste
WinActivate ahk_id %stID%
clipboard := oldclipboard
