Add-Type -AssemblyName System.Drawing
$bmp = [System.Drawing.Bitmap]::FromFile('C:\rocket-autopilot-game\docs\win_1.png')

function Sample([string]$name, [int]$x, [int]$y) {
    $c = $bmp.GetPixel($x, $y)
    Write-Output ("{0,-34} ({1},{2}) = R{3} G{4} B{5}" -f $name, $x, $y, $c.R, $c.G, $c.B)
}
function CountIn([string]$name, [int]$x0, [int]$y0, [int]$x1, [int]$y1, [scriptblock]$match, [int]$step=2) {
    $n = 0
    for ($y = $y0; $y -le $y1; $y += $step) {
        for ($x = $x0; $x -le $x1; $x += $step) {
            $c = $bmp.GetPixel($x, $y)
            if (& $match $c) { $n++ }
        }
    }
    Write-Output ("{0,-34} region=({1},{2})-({3},{4}) count={5}" -f $name, $x0, $y0, $x1, $y1, $n)
}

# --- HUD top-left (capture offset +8,+31) ---
Sample "HUD fuel label (game 16,16)" 24 47
CountIn "HUD fuel bar yellow dark" 24 69 204 83 { param($c) [Math]::Abs($c.R-135) -le 14 -and [Math]::Abs($c.G-106) -le 14 -and [Math]::Abs($c.B-32) -le 14 }
CountIn "HUD value text dark" 40 90 400 300 { param($c) $c.R -gt 100 -and $c.R -gt 180 -and [Math]::Abs($c.R-$c.G) -le 15 -and [Math]::Abs($c.G-$c.B) -le 15 }
Sample "Banner center (game 640,12)" 648 43
Sample "Banner center (game 640,22)" 648 53
CountIn "Banner text white-dark" 520 43 780 75 { param($c) $c.R -gt 110 -and $c.R -gt 200 -and [Math]::Abs($c.R-$c.G) -le 10 -and [Math]::Abs($c.G-$c.B) -le 10 }

# --- moon (game 250,190 r74) -> capture (258,221) ---
Sample "Moon center (game 250,190)" 258 221
Sample "Moon edge+50 (game 250,240)" 258 271
CountIn "Moon body gray dark" 180 145 340 300 { param($c) [Math]::Abs($c.R-79) -le 14 -and [Math]::Abs($c.G-83) -le 14 -and [Math]::Abs($c.B-90) -le 14 }

# --- station (game 1020,150) -> capture (1028,181) ---
Sample "Station body (game 1020,150)" 1028 181
Sample "Station body (game 1020,160)" 1028 191
CountIn "Station body dark" 1000 165 1060 200 { param($c) [Math]::Abs($c.R-90) -le 14 -and [Math]::Abs($c.G-95) -le 14 -and [Math]::Abs($c.B-117) -le 14 }

# --- pad (game 505-775, 646-662) -> capture (513-783, 677-693) ---
Sample "Pad stripe (game 600,653)" 608 684
Sample "Pad stripe (game 700,653)" 708 684
CountIn "Pad yellow stripes" 513 677 783 693 { param($c) [Math]::Abs($c.R-132) -le 14 -and [Math]::Abs($c.G-116) -le 14 -and [Math]::Abs($c.B-32) -le 14 }

# --- ground line (game y 660) -> capture y 691 ---
Sample "Ground line (game 400,660)" 408 691
Sample "Ground line (game 900,660)" 908 691

# --- rocket candidates ---
Sample "Rocket cand pad (game 640,623)" 648 654
CountIn "Rocket red near pad" 610 640 690 680 { param($c) [Math]::Abs($c.R-135) -le 12 -and [Math]::Abs($c.G-49) -le 12 -and [Math]::Abs($c.B-49) -le 12 }
Sample "Rocket cand moon (game 250,116)" 258 147
CountIn "Rocket red near moon" 200 110 320 200 { param($c) [Math]::Abs($c.R-135) -le 12 -and [Math]::Abs($c.G-49) -le 12 -and [Math]::Abs($c.B-49) -le 12 }
Sample "Rocket cand dock (game 1020,184)" 1028 215
CountIn "Rocket red near dock port" 990 200 1070 235 { param($c) [Math]::Abs($c.R-135) -le 12 -and [Math]::Abs($c.G-49) -le 12 -and [Math]::Abs($c.B-49) -le 12 }
# whole-window rocket-red clusters
$clusters = @()
for ($y = 30; $y -lt 750; $y += 4) {
    for ($x = 8; $x -lt 1288; $x += 4) {
        $c = $bmp.GetPixel($x, $y)
        if ([Math]::Abs($c.R-135) -le 10 -and [Math]::Abs($c.G-49) -le 10 -and [Math]::Abs($c.B-49) -le 10) {
            $clusters += ("({0},{1})" -f $x, $y)
        }
    }
}
Write-Output ("Rocket-red (darkened) matching pixels across window: {0}" -f ($clusters -join ' '))

# --- stars (darkened): R=G, B=R+10 ---
$starCount = 0
$starMinX=99999; $starMinY=99999; $starMaxX=-1; $starMaxY=-1
for ($y = 31; $y -lt 720; $y++) {
    for ($x = 8; $x -lt 1288; $x++) {
        $c = $bmp.GetPixel($x, $y)
        if ([Math]::Abs($c.R - $c.G) -le 2 -and ($c.B - $c.R) -ge 5 -and ($c.B - $c.R) -le 16 -and $c.R -ge 10 -and $c.R -le 130) {
            $starCount++
            if ($x -lt $starMinX){$starMinX=$x}; if($x -gt $starMaxX){$starMaxX=$x}
            if ($y -lt $starMinY){$starMinY=$y}; if($y -gt $starMaxY){$starMaxY=$y}
        }
    }
}
Write-Output ("Stars (darkened sig): count={0} bbox=({1},{2})-({3},{4})" -f $starCount, $starMinX, $starMinY, $starMaxX, $starMaxY)

# --- outcome message text at center ---
CountIn "Outcome msg green text" 178 344 1117 395 { param($c) [Math]::Abs($c.R-120) -le 20 -and [Math]::Abs($c.G-255) -le 20 -and [Math]::Abs($c.B-200) -le 20 }

# --- help bar bottom (game y 694-710) -> capture 725-741 ---
CountIn "Help bar text dark" 300 725 1000 741 { param($c) [Math]::Abs($c.R-79) -le 12 -and [Math]::Abs($c.G-85) -le 12 -and [Math]::Abs($c.B-93) -le 12 }

# --- top area: what is the gray band y 0-47? sample it ---
Sample "Top area (30,20)" 30 20
Sample "Top area (640,20)" 640 20
Sample "Top area (1270,20)" 1270 20

$bmp.Dispose()
