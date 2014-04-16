Attribute VB_Name = "NewMacros"
Sub AutoExec()
    ' Wait until a document opens.
    Application.OnTime Now, "AutoNew"
End Sub

Sub AutoOpen()
    If DocumentIsText() Then
        AutoNew
    End If
End Sub

Sub AutoNew()
    If Windows.Count = 0 Then
        Exit Sub
    End If
    ' Ensure that the draft font isn't used
    ' (e.g., if you say "draft view" by accident)
    With Dialogs(wdDialogToolsOptionsView)
        .DraftFont = DocumentIsText()
        .Execute
    End With
    ' Draft view is wdNormalView.
    If ActiveWindow.View.Type = wdPrintView Then
        ActiveWindow.View.Type = wdNormalView
    End If
    ' If window isn't maximized, ribbon doesn't collapse fully.
    Application.CommandBars("Ribbon").Visible = False
    ' Hide the horizontal scroll bar too.
    ActiveWindow.DisplayHorizontalScrollBar = False
End Sub

Public Sub SimulateSave()
    If ActiveDocument.Path = vbNullString Then
        Application.Dialogs(wdDialogFileSaveAs).Show
    Else
        ActiveDocument.Save
    End If
End Sub

Public Sub SaveWithoutPrompting()
    If ActiveDocument.Saved = True Then
        Exit Sub
    End If
    If DocumentIsText() Then
        Application.DisplayAlerts = wdAlertsNone
        SimulateSave
        Application.DisplayAlerts = wdAlertsAll
    Else
        SimulateSave
    End If
End Sub

Public Function DocumentIsText()
    Select Case ActiveDocument.SaveFormat
       Case WdSaveFormat.wdFormatText, _
            WdSaveFormat.wdFormatTextLineBreaks, _
            WdSaveFormat.wdFormatDOSText, _
            WdSaveFormat.wdFormatDOSTextLineBreaks, _
            WdSaveFormat.wdFormatEncodedText, _
            WdSaveFormat.wdFormatUnicodeText
        DocumentIsText = True
       Case Else
        DocumentIsText = False
    End Select
End Function
