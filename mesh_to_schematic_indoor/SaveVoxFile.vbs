Set ObjShell = WScript.CreateObject("WScript.Shell")
strPath = Wscript.ScriptFullName
Set objFSO = CreateObject("Scripting.FileSystemObject")
Set objFile = objFSO.GetFile(strPath)
ObjShell.AppActivate "mesh_to_schematic"
objShell.Run objFile +"\..\vendor\MagicaVoxel-0.99.6.4-win64\MagicaVoxel.exe " & objFile+"\..\TMP_outputfiles\vox_output.vox"
WScript.Sleep 1000
Set Processes = GetObject("winmgmts:").InstancesOf("Win32_Process")

For Each Process In Processes
    If StrComp(Process.Name, "MagicaVoxel.exe", vbTextCompare) = 0 Then

        ObjShell.AppActivate Process.ProcessId

        ' We found our process. No more iteration required...
        Exit For

    End If
Next
WScript.Sleep 1500
objShell.Sendkeys "{F2}"
WScript.Sleep 1500
objShell.Run "taskkill /F /IM MagicaVoxel.exe"