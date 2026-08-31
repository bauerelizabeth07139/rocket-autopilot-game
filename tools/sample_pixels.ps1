Add-Type -AssemblyName System.Drawing

$paths = @('C:\rocket-autopilot-game\docs\shot1.png', 'C:\rocket-autopilot-game\docs\shot2.png')

# Check if files are identical
$f1 = Get-Item $paths[0]
$f2 = Get-Item $paths[1]
Write-Output ("shot1: $($f1.Length) bytes, shot2: $($f2.Length) bytes")
if ($f1.Length -eq $f2.Length) {
    $bytes1 = [System.IO.File]::ReadAllBytes($paths[0])
    $bytes2 = [System.IO.File]::ReadAllBytes($paths[1])
    $diff = 0
    for ($i = 0; $i -lt $bytes1.Length; $i++) {
        if ($bytes1[$i] -ne $bytes2[$i]) { $diff++ }
    }
    Write-Output ("Byte differences between shot1 and shot2: $diff")
}

foreach ($path in $paths) {
    $bmp = New-Object System.Drawing.Bitmap($path)
    $w = $bmp.Width
    $h = $bmp.Height
    Write-Output ("=== $path ($w x $h) ===")

    # Sample key areas
    # Top center - should have "AUTO DOCK" text (green)
    Write-Output ("  Top-center area (AUTO DOCK text, ~y=50-80):")
    for ($x = 400; $x -lt 900; $x += 50) {
        for ($y = 40; $y -lt 90; $y += 10) {
            $c = $bmp.GetPixel($x, $y)
            if ($c.G -gt 100) {
                Write-Output ("    ($x,$y) R=$($c.R) G=$($c.G) B=$($c.B)")
            }
        }
    }

    # Left side - fuel bar (orange)
    Write-Output ("  Left area (fuel bar, ~y=60-80):")
    for ($x = 20; $x -lt 200; $x += 20) {
        for ($y = 55; $y -lt 85; $y += 5) {
            $c = $bmp.GetPixel($x, $y)
            if ($c.R -gt 150 -and $c.G -gt 100) {
                Write-Output ("    ($x,$y) R=$($c.R) G=$($c.G) B=$($c.B)")
            }
        }
    }

    # Center - CRASH text (red)
    Write-Output ("  Center area (CRASH text, ~y=350-400):")
    for ($x = 300; $x -lt 1000; $x += 50) {
        for ($y = 340; $y -lt 400; $y += 10) {
            $c = $bmp.GetPixel($x, $y)
            if ($c.R -gt 150 -and $c.G -lt 120 -and $c.B -lt 120) {
                Write-Output ("    ($x,$y) R=$($c.R) G=$($c.G) B=$($c.B)")
            }
        }
    }

    # Bottom - landing pad (yellow stripes)
    Write-Output ("  Bottom area (landing pad, ~y=690-710):")
    for ($x = 400; $x -lt 900; $x += 30) {
        for ($y = 685; $y -lt 715; $y += 5) {
            $c = $bmp.GetPixel($x, $y)
            if ($c.R -gt 150 -and $c.G -gt 130) {
                Write-Output ("    ($x,$y) R=$($c.R) G=$($c.G) B=$($c.B)")
            }
        }
    }

    # Right side - space station (blue with red dot)
    Write-Output ("  Right area (space station, ~x=1050-1200, y=140-200):")
    for ($x = 1040; $x -lt 1210; $x += 20) {
        for ($y = 130; $y -lt 210; $y += 10) {
            $c = $bmp.GetPixel($x, $y)
            if ($c.R -gt 100 -or $c.G -gt 100) {
                Write-Output ("    ($x,$y) R=$($c.R) G=$($c.G) B=$($c.B)")
            }
        }
    }

    # Green circle target marker
    Write-Output ("  Target marker area (~x=1050, y=230):")
    for ($x = 1020; $x -lt 1100; $x += 10) {
        for ($y = 220; $y -lt 260; $y += 5) {
            $c = $bmp.GetPixel($x, $y)
            if ($c.G -gt 150) {
                Write-Output ("    ($x,$y) R=$($c.R) G=$($c.G) B=$($c.B)")
            }
        }
    }

    $bmp.Dispose()
}
