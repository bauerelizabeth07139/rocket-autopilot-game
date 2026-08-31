param($path)
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;

[StructLayout(LayoutKind.Sequential)]
public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }

public class WinCapture {
    [DllImport("user32.dll")]
    public static extern bool PrintWindow(IntPtr hwnd, IntPtr hdcBlt, uint nFlags);

    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hwnd, out RECT lpRect);

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);

    [DllImport("user32.dll")]
    public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);

    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);
}
"@

# Find window by exact title
$title = "Rocket Autopilot 火箭自动驾驶"
$hwnd = [WinCapture]::FindWindow($null, $title)

if($hwnd -eq [IntPtr]::Zero) {
    Write-Output "ERROR: Window '$title' not found"
    exit 1
}

$visible = [WinCapture]::IsWindowVisible($hwnd)
Write-Output "Window handle: $($hwnd.ToInt64()) Visible: $visible"

$rect = New-Object RECT
$result = [WinCapture]::GetWindowRect($hwnd, [ref]$rect) | Out-Null

if(-not $result) {
    Write-Output "ERROR: Could not get window rect"
    exit 1
}

$w = $rect.Right - $rect.Left
$h = $rect.Bottom - $rect.Top
Write-Output "Window size: ${w}x${h}"

$bmp = New-Object System.Drawing.Bitmap($w, $h)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$dc = $g.GetHdc()
$ret = [WinCapture]::PrintWindow($hwnd, $dc, 2)
$g.ReleaseHdc($dc)

if($ret) { Write-Output "PrintWindow succeeded" } else { Write-Output "PrintWindow FAILED (still saving)" }

$outPath = $path -replace "/", "\"
$bmp.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose()
$bmp.Dispose()
Write-Output "Saved: $outPath (${w}x${h})"
