Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Runtime.InteropServices

$bmp = [System.Drawing.Bitmap]::FromFile('C:\rocket-autopilot-game\docs\win_1.png')
$W = $bmp.Width; $H = $bmp.Height
$rect = New-Object System.Drawing.Rectangle(0, 0, $W, $H)
$data = $bmp.LockBits($rect, [System.Drawing.Imaging.ImageLockMode]::ReadOnly, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$stride = $data.Stride
$bytes = New-Object byte[] ($stride * $H)
[System.Runtime.InteropServices.Marshal]::Copy($data.Scan0, $bytes, 0, $bytes.Length)
$bmp.UnlockBits($data)
$bmp.Dispose()

function BBox([int]$tR, [int]$tG, [int]$tB, [int]$tol, [string]$extraRule = 'none') {
    $minX = 99999; $minY = 99999; $maxX = -1; $maxY = -1; $count = 0
    for ($y = 0; $y -lt $H; $y++) {
        $base = $y * $stride
        for ($x = 0; $x -lt $W; $x++) {
            $i = $base + $x * 4
            $b = [int]$bytes[$i]; $g = [int]$bytes[$i+1]; $r = [int]$bytes[$i+2]
            $ok = [Math]::Abs($r-$tR) -le $tol -and [Math]::Abs($g-$tG) -le $tol -and [Math]::Abs($b-$tB) -le $tol
            if ($ok -and $extraRule -eq 'gray') {
                $ok = [Math]::Abs($r-$g) -le 12 -and [Math]::Abs($g-$b) -le 12
            }
            if ($ok) {
                $count++
                if ($x -lt $minX) { $minX = $x }
                if ($x -gt $maxX) { $maxX = $x }
                if ($y -lt $minY) { $minY = $y }
                if ($y -gt $maxY) { $maxY = $y }
            }
        }
    }
    if ($count -ge 3) { return [pscustomobject]@{ Count=$count; X0=$minX; Y0=$minY; X1=$maxX; Y1=$maxY; W=$maxX-$minX+1; H=$maxY-$minY+1 } }
    return $null
}
function Out2([string]$name, $bb) {
    if ($bb) { Write-Output ("{0,-26} FOUND count={1,-7} bbox=({2},{3})-({4},{5}) {6}x{7}" -f $name,$bb.Count,$bb.X0,$bb.Y0,$bb.X1,$bb.Y1,$bb.W,$bb.H) }
    else { Write-Output ("{0,-26} MISSING" -f $name) }
}

# game -> capture offset (8,31). Expected positions stated in capture coords.

$st = BBox 23 33 53 15
Out2 "GROUND rect dark (23,33,53)" $st
$gl = BBox 64 79 106 12 'gray'
Out2 "GROUND line dark (64,79,106)" $gl
$pl = BBox 28 39 64 15
Out2 "PLANET circle dark (28,39,64)" $pl
$py = BBox 132 116 32 15
Out2 "PAD yellow dark (132,116,32)" $py
$pd = BBox 21 21 24 10
Out2 "PAD dark stripes dark" $pd
$pb = BBox 37 39 44 10
Out2 "PAD base dark (37,39,44)" $pb

$mo = BBox 79 83 90 14
Out2 "MOON body dark (79,83,90)" $mo
$mc = BBox 65 68 75 12
Out2 "MOON craters dark" $mc

$sb = BBox 90 95 117 14
Out2 "STATION body dark" $sb
$sp = BBox 48 58 101 14
Out2 "STATION pods dark" $sp
$srd = BBox 135 48 48 14
Out2 "STATION red dot dark" $srd
$sgn = BBox 32 135 64 14
Out2 "STATION port green dark" $sgn

$rk = BBox 135 49 49 14
Out2 "ROCKET red dark (135,49,49)" $rk
$rh = BBox 120 121 124 10 'gray'
Out2 "ROCKET hull dark" $rh
$rw = BBox 21 32 48 12
Out2 "ROCKET window dark" $rw
$fl1 = BBox 135 90 21 14
Out2 "FLAME orange dark" $fl1
$fl2 = BBox 135 127 79 14
Out2 "FLAME light dark" $fl2

$fu = BBox 135 106 32 14
Out2 "FUEL bar fill dark (135,106,32)" $fu
$hvl = BBox 127 127 127 10 'gray'
Out2 "HUD values dark gray" $hvl
$hlb = BBox 90 101 111 10
Out2 "HUD labels dark (90,101,111)" $hlb
$bn = BBox 135 135 135 12 'gray'
Out2 "BANNER white dark (135,135,135)" $bn
$ph = BBox 90 106 117 10
Out2 "PHASE text dark (90,106,117)" $ph
$hp = BBox 79 85 93 10
Out2 "HELP bar dark (79,85,93)" $hp

# full-brightness text drawn on top of overlay
$msg = BBox 120 255 200 15
Out2 "OUTCOME msg green (120,255,200)" $msg
$msgR = BBox 255 120 120 15
Out2 "OUTCOME msg red (255,120,120)" $msgR
$sub = BBox 220 220 220 12 'gray'
Out2 "OUTCOME sub gray (220,220,220)" $sub
$hint = BBox 180 190 200 12
Out2 "OUTCOME hint (180,190,200)" $hint

# stars (darkened): R==G, B-R ~10
$star = BBox 0 0 0 0
