Add-Type -AssemblyName System.Drawing
$bmp = [System.Drawing.Bitmap]::FromFile('C:\rocket-autopilot-game\docs\win_1.png')

# Banner: darkened white (135,135,135) text at game y 12-44 -> capture y 43-78
$n = 0
for ($y = 43; $y -le 80; $y++) {
    for ($x = 400; $x -le 900; $x++) {
        $c = $bmp.GetPixel($x, $y)
        if ($c.R -ge 110 -and $c.R -le 160 -and [Math]::Abs($c.R-$c.G) -le 10 -and [Math]::Abs($c.G-$c.B) -le 10) { $n++ }
    }
}
Write-Output ("Banner text dark-gray in (400,43)-(900,80): count={0}" -f $n)
# sample rows of the banner area to find text rows
for ($y = 45; $y -le 78; $y += 3) {
    $sb = New-Object System.Text.StringBuilder
    [void]$sb.Append(("y={0,3}: " -f $y))
    for ($x = 450; $x -le 850; $x += 20) {
        $c = $bmp.GetPixel($x, $y)
        $ch = '.'
        if ($c.R -ge 110 -and $c.R -le 165 -and [Math]::Abs($c.R-$c.G) -le 12 -and [Math]::Abs($c.G-$c.B) -le 12) { $ch = '#' }
        elseif ($c.R -gt 165) { $ch = 'S' }
        [void]$sb.Append($ch)
    }
    Write-Output $sb.ToString()
}

# HUD values: darkened (127,127,127) text, region game (16,64)-(330,200) -> capture (24,95)-(338,231)
$n2 = 0
for ($y = 95; $y -le 235; $y++) {
    for ($x = 24; $x -le 338; $x++) {
        $c = $bmp.GetPixel($x, $y)
        if ($c.R -ge 100 -and $c.R -le 155 -and [Math]::Abs($c.R-$c.G) -le 10 -and [Math]::Abs($c.G-$c.B) -le 10) { $n2++ }
    }
}
Write-Output ("HUD value text dark-gray in (24,95)-(338,235): count={0}" -f $n2)

# Phase text under banner: (170,200,220)->(90,106,117) at game y 50-70 -> capture y 81-101
$n3 = 0
for ($y = 81; $y -le 101; $y++) {
    for ($x = 400; $x -le 900; $x++) {
        $c = $bmp.GetPixel($x, $y)
        if ([Math]::Abs($c.R-90) -le 14 -and [Math]::Abs($c.G-106) -le 14 -and [Math]::Abs($c.B-117) -le 14) { $n3++ }
    }
}
Write-Output ("Phase text in (400,81)-(900,101): count={0}" -f $n3)

# LOW FUEL warning: (255,110,110)->(135,58,58) at game y 90-115 -> capture y 121-146
$n4 = 0
for ($y = 121; $y -le 146; $y++) {
    for ($x = 400; $x -le 900; $x++) {
        $c = $bmp.GetPixel($x, $y)
        if ([Math]::Abs($c.R-135) -le 14 -and [Math]::Abs($c.G-58) -le 14 -and [Math]::Abs($c.B-58) -le 14) { $n4++ }
    }
}
Write-Output ("LOW FUEL warn in (400,121)-(900,146): count={0}" -f $n4)

$bmp.Dispose()
