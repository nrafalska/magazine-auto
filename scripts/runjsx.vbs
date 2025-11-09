' runjsx.vbs
' VBScript для запуску ExtendScript в InDesign
' Використання: cscript runjsx.vbs "path/to/plan.json"

Option Explicit

Dim objInDesign
Dim strScriptPath
Dim strPlanPath
Dim objFSO
Dim objFile

' Отримуємо аргументи
If WScript.Arguments.Count < 1 Then
    WScript.Echo "Використання: cscript runjsx.vbs <plan.json>"
    WScript.Quit 1
End If

strPlanPath = WScript.Arguments(0)

' Перевіряємо чи існує plan.json
Set objFSO = CreateObject("Scripting.FileSystemObject")
If Not objFSO.FileExists(strPlanPath) Then
    WScript.Echo "Помилка: Файл не знайдено: " & strPlanPath
    WScript.Quit 1
End If

' Шлях до ExtendScript
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName) & "\compose.jsx"

If Not objFSO.FileExists(strScriptPath) Then
    WScript.Echo "Помилка: ExtendScript не знайдено: " & strScriptPath
    WScript.Quit 1
End If

' Запускаємо InDesign
On Error Resume Next
Set objInDesign = CreateObject("InDesign.Application.2024")

' Якщо не вдалось створити (версія 2024 не встановлена)
If Err.Number <> 0 Then
    Err.Clear
    ' Пробуємо інші версії
    Set objInDesign = CreateObject("InDesign.Application.2023")
End If

If Err.Number <> 0 Then
    Err.Clear
    Set objInDesign = CreateObject("InDesign.Application")
End If

If Err.Number <> 0 Then
    WScript.Echo "Помилка: Не вдалося запустити InDesign"
    WScript.Echo "Переконайтесь що Adobe InDesign встановлено"
    WScript.Quit 1
End If
On Error GoTo 0

' Встановлюємо шлях до плану як змінну середовища
' (щоб compose.jsx міг його прочитати)
Dim objShell
Set objShell = CreateObject("WScript.Shell")
objShell.Environment("Process")("MAGAZINE_PLAN_PATH") = strPlanPath

WScript.Echo "Запускаю InDesign..."
WScript.Echo "План: " & strPlanPath
WScript.Echo "Скрипт: " & strScriptPath

' Виконуємо ExtendScript
objInDesign.DoScript objFSO.OpenTextFile(strScriptPath, 1).ReadAll(), 1246973031 ' idJavascript

WScript.Echo "Готово!"

' Очищуємо
Set objInDesign = Nothing
Set objFSO = Nothing
Set objShell = Nothing

WScript.Quit 0
