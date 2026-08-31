$code = @"
using System;
using System.Runtime.InteropServices;
public static class Wf {
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
}
"@
Add-Type -TypeDefinition $code
Add-Type -AssemblyName System.Drawing

$targetPid = 7504
$script:hwnd = [IntPtr]::Zero
$cb = [Wf+EnumWindowsProc]{
    param($hWnd, $lParam)
    $pid2 = 0
    [Wf]::GetWindowThreadProcessId($hWnd, [ref]$pid2) | Out-Null
    if ($pid2 -eq $targetPid -and [Wf]::IsWindowVisible($hWnd)) { $script:hwnd = $hWnd; return $false }
    return $true
}
[Wf]::EnumWindows($cb, [IntPtr]::Zero) | Out-Null

$wr = New-Object Wf+RECT
[Wf]::GetWindowRect($script:hwnd, [ref]$wr) | Out-Null
$width = $wr.Right - $wr.Left
$height = $wr.Bottom - $wr.Top
Write-Output ("Window {0}x{1}" -f $width, $height)

$bmp = New-Object System.Drawing.Bitmap($width, $height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$hdc = $g.GetHdc()
$ok = [Wf]::PrintWindow($script:hwnd, $hdc, 0)
if (-not $ok) { $ok = [Wf]::PrintWindow($script:hwnd, $hdc, 2) }
$g.ReleaseHdc($hdc)
$g.Dispose()

$winPath = 'C:\rocket-autopilot-game\docs\win_latest.png'
$bmp.Save($winPath, [System.Drawing.Imaging.ImageFormat]::Png)
Write-Output ("PrintWindow ok={0}, saved {1} bytes" -f $ok, (Get-Item $winPath).Length)

# crop client area: offset (8,31), size 1280x720
$crop = New-Object System.Drawing.Rectangle(8, 31, 1280, 720)
$out = New-Object System.Drawing.Bitmap(1280, 720)
$og = [System.Drawing.Graphics]::FromImage($out)
$og.DrawImage($bmp, 0, 0, $crop, [System.Drawing.GraphicsUnit]::Pixel)
$og.Dispose()
$outPath = 'C:\rocket-autopilot-game\docs\screenshot.png'
$out.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
$out.Dispose()
$bmp.Dispose()
Write-Output ("Cropped client screenshot saved: {0} bytes" -f (Get-Item $outPath).Length)
