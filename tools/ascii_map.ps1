param([string]$Path = 'C:\rocket-autopilot-game\docs\win_1.png')
Add-Type -AssemblyName System.Drawing

$bmp = [System.Drawing.Bitmap]::FromFile($Path)
$W = $bmp.Width; $H = $bmp.Height
$cols = 64; $rows = 32
$cw = [Math]::Ceiling($W / $cols); $ch = [Math]::Ceiling($H / $rows)

$grid = @()
for ($gy = 0; $gy -lt $rows; $gy++) {
    $line = ""
    for ($gx = 0; $gx -lt $cols; $gx++) {
        $sumR = 0.0; $sumG = 0.0; $sumB = 0.0; $n = 0
        for ($yy = $gy * $ch; $yy -lt [Math]::Min(($gy+1) * $ch, $H); $yy++) {
            for ($xx = $gx * $cw; $xx -lt [Math]::Min(($gx+1) * $cw, $W); $xx++) {
                $c = $bmp.GetPixel($xx, $yy)
                $sumR += $c.R; $sumG += $c.G; $sumB += $c.B; $n++
            }
        }
        $r = $sumR/$n; $g = $sumG/$n; $b = $sumB/$n
        $m = [Math]::Max($r, [Math]::Max($g, $b))
        $ch2 = ""
        if ($m -lt 12) { $ch2 = '.' }
        elseif ($m -lt 40) { $ch2 = ':' }
        elseif ($m -lt 80) { $ch2 = 'o' }
        elseif ($m -lt 140) { $ch2 = 'O' }
        else { $ch2 = '#' }
        # color hint char appended
        if ($b -gt 60 -and $b -gt $r + 25 -and $b -gt $g + 20) { $ch2 = 'B' }   # blue dominant
        elseif ($r -gt 60 -and $r -gt $g + 30 -and $r -gt $b + 30) { $ch2 = 'R' } # red dominant
        elseif ($g -gt 60 -and $g -gt $r + 20 -and $g -gt $b + 20) { $ch2 = 'G' } # green dominant
        elseif ([Math]::Abs($r-$g) -lt 15 -and [Math]::Abs($g-$b) -lt 15 -and $m -ge 40) { $ch2 = 'S' } # gray
        $line += $ch2
    }
    $grid += $line
}
for ($gy = 0; $gy -lt $rows; $gy++) {
    Write-Output ("y={0,3} {1}" -f ($gy * $ch), $grid[$gy])
}
$bmp.Dispose()
