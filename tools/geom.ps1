$code = @"
using System;
using System.Runtime.InteropServices;
public static class W {
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr hWnd, out RECT lpRect);
    [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr hWnd, ref POINT lpPoint);
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
    [StructLayout(LayoutKind.Sequential)]
    public struct POINT { public int X; public int Y; }
}
"@
Add-Type -TypeDefinition $code

# --- find hwnd of PID 7504 ---
$script:hwnd = [IntPtr]::Zero
$cb = [W+EnumWindowsProc]{
    param($hWnd, $lParam)
    $pid2 = 0
    [W]::GetWindowThreadProcessId($hWnd, [ref]$pid2) | Out-Null
    if ($pid2 -eq 7504) { $script:hwnd = $hWnd; return $false }
    return $true
}
[W]::EnumWindows($cb, [IntPtr]::Zero) | Out-Null
Write-Output ("hwnd=0x{0:X}" -f $script:hwnd.Value)

$wr = New-Object W+RECT; [W]::GetWindowRect($script:hwnd, [ref]$wr) | Out-Null
$cr = New-Object W+RECT; [W]::GetClientRect($script:hwnd, [ref]$cr) | Out-Null
$pt = New-Object W+POINT; $pt.X = 0; $pt.Y = 0
[W]::ClientToScreen($script:hwnd, [ref]$pt) | Out-Null
$offX = $pt.X - $wr.Left
$offY = $pt.Y - $wr.Top
Write-Output ("Window rect=({0},{1})-({2},{3})" -f $wr.Left, $wr.Top, $wr.Right, $wr.Bottom)
Write-Output ("Client size={0}x{1}, offset in window={2},{3}" -f $cr.Right, $cr.Bottom, $offX, $offY)
