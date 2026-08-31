param([string]$out, [int]$pidTarget=0)
Add-Type -AssemblyName System.Drawing
if($pidTarget -eq 0){ $p=Get-Process python | Where-Object {$_.MainWindowTitle -like "*Rocket*"} | Select-Object -First 1 }
else { $p=Get-Process -Id $pidTarget }
if(-not $p){ Write-Output "NO_WINDOW"; exit 1 }
Add-Type @"
using System;using System.Runtime.InteropServices;
public class FW2{ [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h,IntPtr dc,uint f);
[DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h,out R r); public struct R{public int L,T,RT,B;} }
"@
$r=New-Object FW2+R; [FW2]::GetWindowRect($p.MainWindowHandle,[ref]$r)|Out-Null
$bmp=New-Object System.Drawing.Bitmap($r.RT-$r.L,$r.B-$r.T)
$g=[System.Drawing.Graphics]::FromImage($bmp);$dc=$g.GetHdc()
[FW2]::PrintWindow($p.MainWindowHandle,$dc,2)|Out-Null
$g.ReleaseHdc($dc)
$bmp.Save($out,[System.Drawing.Imaging.ImageFormat]::Png)
Write-Output ("SAVED {0} {1}x{2}" -f $out,($r.RT-$r.L),($r.B-$r.T))
