Add-Type -AssemblyName System.Drawing
$bmp = [System.Drawing.Bitmap]::FromFile('C:\rocket-autopilot-game\docs\win_1.png')
$rows = @(30, 60, 100, 150, 200, 260, 300, 350, 380, 420, 440, 470, 520, 580, 640, 660, 670, 680, 700, 720, 740)
foreach ($y in $rows) {
    $sb = New-Object System.Text.StringBuilder
    [void]$sb.Append(("y={0,3}: " -f $y))
    for ($x = 0; $x -lt $bmp.Width; $x += 30) {
        $c = $bmp.GetPixel($x, $y)
        # classify
        $ch = ''
        $m = [Math]::Max($c.R, [Math]::Max($c.G, $c.B))
        if ($m -lt 12) { $ch = '.' }
        elseif ($m -lt 45) { $ch = ':' }
        elseif ($m -lt 90) { $ch = 'o' }
        elseif ($m -lt 150) { $ch = 'O' }
        else { $ch = '#' }
        if ($c.B -gt 60 -and $c.B -gt $c.R + 25 -and $c.B -gt $c.G + 20) { $ch = 'B' }
        elseif ($c.R -gt 60 -and $c.R -gt $c.G + 30 -and $c.R -gt $c.B + 30) { $ch = 'R' }
        elseif ($c.G -gt 60 -and $c.G -gt $c.R + 20 -and $c.G -gt $c.B + 20) { $ch = 'G' }
        elseif ([Math]::Abs($c.R-$c.G) -lt 15 -and [Math]::Abs($c.G-$c.B) -lt 15 -and $m -ge 45) { $ch = 'S' }
        [void]$sb.Append($ch)
    }
    Write-Output $sb.ToString()
}
$bmp.Dispose()
