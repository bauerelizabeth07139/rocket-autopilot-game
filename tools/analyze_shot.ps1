Add-Type -AssemblyName System.Drawing

$paths = @('C:\rocket-autopilot-game\docs\shot1.png', 'C:\rocket-autopilot-game\docs\shot2.png')

foreach ($path in $paths) {
    $bmp = New-Object System.Drawing.Bitmap($path)
    $w = $bmp.Width
    $h = $bmp.Height
    Write-Output ("=== $path ($w x $h) ===")

    $redCount = 0
    $greenTextCount = 0
    $yellowCount = 0
    $darkBlueCount = 0
    $whiteCount = 0
    $orangeFuelCount = 0
    $moonGrayCount = 0
    $greenCircleCount = 0
    $rocketFlameCount = 0

    for ($x = 0; $x -lt $w; $x += 2) {
        for ($y = 0; $y -lt $h; $y += 2) {
            $c = $bmp.GetPixel($x, $y)
            $r = $c.R; $g = $c.G; $b = $c.B

            # Rocket red body: ~(255, 92, 92)
            if ($r -gt 240 -and $g -gt 70 -and $g -lt 120 -and $b -gt 70 -and $b -lt 120) { $redCount++ }

            # Green text (CRASH, APPROACH, etc): green dominant
            if ($g -gt 180 -and $r -lt 180 -and $b -lt 180 -and $g -gt $r + 30) { $greenTextCount++ }

            # Yellow landing pad stripes: ~(210, 190, 60)
            if ($r -gt 180 -and $g -gt 150 -and $b -lt 100) { $yellowCount++ }

            # Dark blue planet (bottom): ~(45, 55, 100)
            if ($r -gt 20 -and $r -lt 80 -and $g -gt 30 -and $g -lt 90 -and $b -gt 70 -and $b -lt 130) { $darkBlueCount++ }

            # White text pixels
            if ($r -gt 200 -and $g -gt 200 -and $b -gt 200) { $whiteCount++ }

            # Orange fuel bar: ~(200, 150, 50)
            if ($r -gt 180 -and $g -gt 120 -and $g -lt 180 -and $b -lt 80) { $orangeFuelCount++ }

            # Moon gray: ~(130-170, 130-170, 130-170)
            if ($r -gt 120 -and $r -lt 180 -and $g -gt 120 -and $g -lt 180 -and $b -gt 120 -and $b -lt 180 -and ($r -eq $g) -and ($g -eq $b)) { $moonGrayCount++ }

            # Green circle (target marker): bright green ~(50, 200, 100)
            if ($g -gt 180 -and $r -lt 100 -and $b -lt 150 -and $g -gt $r + 80) { $greenCircleCount++ }

            # Rocket flame orange/yellow
            if ($r -gt 250 -and $g -gt 150 -and $g -lt 220 -and $b -lt 50) { $rocketFlameCount++ }
        }
    }

    Write-Output ("  Rocket red body pixels: $redCount")
    Write-Output ("  Green text pixels: $greenTextCount")
    Write-Output ("  Yellow landing pad pixels: $yellowCount")
    Write-Output ("  Dark blue planet pixels: $darkBlueCount")
    Write-Output ("  White text pixels: $whiteCount")
    Write-Output ("  Orange fuel bar pixels: $orangeFuelCount")
    Write-Output ("  Moon gray pixels: $moonGrayCount")
    Write-Output ("  Green circle pixels: $greenCircleCount")
    Write-Output ("  Rocket flame pixels: $rocketFlameCount")

    $bmp.Dispose()
}

# Also check file sizes
Write-Output ""
foreach ($path in $paths) {
    $f = Get-Item $path
    Write-Output ("File: $path -> $($f.Length) bytes")
}
