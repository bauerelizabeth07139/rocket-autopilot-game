Add-Type -AssemblyName System.Drawing

$path = 'C:\rocket-autopilot-game\docs\shot1.png'
$bmp = New-Object System.Drawing.Bitmap($path)
$w = $bmp.Width
$h = $bmp.Height
Write-Output ("Image: $path ($w x $h)")

$rocketRed = 0
$crashRed = 0
$greenText = 0
$yellowPad = 0
$darkBluePlanet = 0
$whiteText = 0
$orangeFuel = 0
$moonGray = 0
$greenCircle = 0
$spaceStationBlue = 0
$blackBg = 0
$totalPixels = 0

for ($x = 0; $x -lt $w; $x += 1) {
    for ($y = 0; $y -lt $h; $y += 1) {
        $c = $bmp.GetPixel($x, $y)
        $r = $c.R; $g = $c.G; $b = $c.B
        $totalPixels++

        # Rocket red body: ~(255, 92, 92) - bright red
        if ($r -gt 230 -and $g -gt 70 -and $g -lt 130 -and $b -gt 70 -and $b -lt 130) { $rocketRed++ }

        # CRASH text red: ~(210, 99, 99) - muted red
        if ($r -gt 180 -and $r -lt 240 -and $g -gt 80 -and $g -lt 120 -and $b -gt 80 -and $b -lt 120) { $crashRed++ }

        # Green text (AUTO DOCK, APPROACH): dark green/teal ~(58, 124, 97)
        if ($g -gt 100 -and $r -lt 100 -and $b -gt 70 -and $b -lt 130 -and $g -gt $r + 40) { $greenText++ }

        # Yellow landing pad: ~(180-220, 160-200, 40-80)
        if ($r -gt 150 -and $g -gt 130 -and $b -lt 100 -and $r -gt $b + 60) { $yellowPad++ }

        # Dark blue planet (bottom): ~(45, 55, 100)
        if ($r -gt 20 -and $r -lt 90 -and $g -gt 30 -and $g -lt 100 -and $b -gt 70 -and $b -lt 140 -and $b -gt $r + 20) { $darkBluePlanet++ }

        # White/light text
        if ($r -gt 180 -and $g -gt 180 -and $b -gt 180) { $whiteText++ }

        # Orange fuel bar: ~(180-210, 140-170, 40-70)
        if ($r -gt 160 -and $r -lt 230 -and $g -gt 110 -and $g -lt 180 -and $b -lt 90) { $orangeFuel++ }

        # Moon gray: ~(130-170, 130-170, 130-170) neutral gray
        if ($r -gt 110 -and $r -lt 185 -and $g -gt 110 -and $g -lt 185 -and $b -gt 110 -and $b -lt 185 -and ($r - $g) -lt 15 -and ($g - $b) -lt 15) { $moonGray++ }

        # Bright green circle
        if ($g -gt 150 -and $r -lt 120 -and $b -lt 130 -and $g -gt $r + 50) { $greenCircle++ }

        # Space station blue-gray: ~(80-130, 90-140, 120-170)
        if ($r -gt 70 -and $r -lt 140 -and $g -gt 80 -and $g -lt 150 -and $b -gt 100 -and $b -lt 180 -and $b -gt $r + 10) { $spaceStationBlue++ }

        # Black background
        if ($r -lt 20 -and $g -lt 20 -and $b -lt 20) { $blackBg++ }
    }
}

Write-Output ("Total pixels: $totalPixels")
Write-Output ("Rocket red body (255,92,92): $rocketRed")
Write-Output ("CRASH red text (210,99,99): $crashRed")
Write-Output ("Green text (AUTO DOCK etc): $greenText")
Write-Output ("Yellow landing pad: $yellowPad")
Write-Output ("Dark blue planet: $darkBluePlanet")
Write-Output ("White text: $whiteText")
Write-Output ("Orange fuel bar: $orangeFuel")
Write-Output ("Moon gray: $moonGray")
Write-Output ("Green circle: $greenCircle")
Write-Output ("Space station blue: $spaceStationBlue")
Write-Output ("Black background: $blackBg")

$bmp.Dispose()

# Copy shot1 as screenshot.png
Copy-Item $path 'C:\rocket-autopilot-game\docs\screenshot.png' -Force
$sf = Get-Item 'C:\rocket-autopilot-game\docs\screenshot.png'
Write-Output ("")
Write-Output ("screenshot.png created: $($sf.Length) bytes")
