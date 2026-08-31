$code = @"
using System;
using System.Runtime.InteropServices;
public static class Win32 {
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder lpString, int nMaxCount);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
}
"@
Add-Type -TypeDefinition $code
Add-Type -AssemblyName System.Drawing

$targetPid = 2328
$found = New-Object System.Collections.ArrayList
$cb = {
    param($hWnd, $lParam)
    $procId = 0
    [Win32]::GetWindowThreadProcessId($hWnd, [ref]$procId) | Out-Null
    if ($procId -eq $targetPid -and [Win32]::IsWindowVisible($hWnd)) {
        $sb = New-Object System.Text.StringBuilder 256
        [Win32]::GetWindowText($hWnd, $sb, 256) | Out-Null
        $r = New-Object Win32+RECT
        [Win32]::GetWindowRect($hWnd, [ref]$r) | Out-Null
        $found.Add([pscustomobject]@{ Handle=$hWnd; Title=$sb.ToString(); Left=$r.Left; Top=$r.Top; Right=$r.Right; Bottom=$r.Bottom }) | Out-Null
    }
    return $true
}
$delegate = [Win32+EnumWindowsProc]$cb
[Win32]::EnumWindows($delegate, [IntPtr]::Zero) | Out-Null
Write-Output ("Found {0} top-level visible windows for PID {1}:" -f $found.Count, $targetPid)
foreach ($w in $found) {
    Write-Output ("  hwnd=0x{0:X} title='{1}' rect=({2},{3})-({4},{5})" -f $w.Handle.Value, $w.Title, $w.Left, $w.Top, $w.Right, $w.Bottom)
}

$i = 1
foreach ($w in $found) {
    if ($w.Left -eq 0 -and $w.Top -eq 0 -and $w.Right -eq 0 -and $w.Bottom -eq 0) { continue }
    $width = $w.Right - $w.Left
    $height = $w.Bottom - $w.Top
    if ($width -le 0 -or $height -le 0) { continue }
    Write-Output ("Trying to bring window to foreground and capture: {0} ({1}x{2})" -f $w.Title, $width, $height)
    [Win32]::ShowWindow($w.Handle, 9) | Out-Null
    [Win32]::SetForegroundWindow($w.Handle) | Out-Null
    Start-Sleep -Milliseconds 300
    $bmp = New-Object System.Drawing.Bitmap($width, $height)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $hdc = $g.GetHdc()
    $ok = [Win32]::PrintWindow($w.Handle, $hdc, 0)
    if (-not $ok) {
        $ok = [Win32]::PrintWindow($w.Handle, $hdc, 2)
    }
    $g.ReleaseHdc($hdc)
    $g.Dispose()
    $path = "C:\rocket-autopilot-game\docs\shot1.png"
    $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $bmp.Dispose()
    $f = Get-Item $path
    Write-Output ("  PrintWindow ok={0} saved {1} bytes" -f $ok, $f.Length)
}
