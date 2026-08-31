Add-Type -AssemblyName System.Drawing

$path = 'C:\rocket-autopilot-game\docs\shot1.png'
$bmp = New-Object System.Drawing.Bitmap($path)
$w = $bmp.Width
$h = $bmp.Height

# Sample specific known locations
Write-Output ("=== Sampling specific locations ===")

# Landing pad area - bottom center (visible in screenshot around y=695-710)
Write-Output ("Landing pad area (y=690-715, x=450-850):")
$found = $false
for ($x = 450; $x -lt 850; $x += 10) {
    for ($y = 690; $y -lt 715; $y += 2) {
        $c = $bmp.GetPixel($x, $y)
        if ($c.R -gt 100 -and $c.G -gt 80) {
            Write-Output ("  ($x,$y) R=$($c.R) G=$($c.G) B=$($c.B)")
            $found = $true
            break
        }
    }
    if ($found) { break }
}

# Fuel bar area - top left (visible around y=55-75, x=20-180)
Write-Output ("Fuel bar area (y=55-75, x=20-180):")
$found = $false
for ($x = 20; $x -lt 180; $x += 5) {
    for ($y = 55; $y -lt 75; $y += 2) {
        $c = $bmp.GetPixel($x, $y)
        if ($c.R -gt 100 -and $c.G -gt 80 -and $c.B -lt 100) {
            Write-Output ("  ($x,$y) R=$($c.R) G=$($c.G) B=$($c.B)")
            $found = $true
            break
        }
    }
    if ($found) { break }
}

# Green circle target - right side (visible around x=1050, y=230)
Write-Output ("Target marker area (x=1030-1080, y=220-250):")
$found = $false
for ($x = 1030; $x -lt 1080; $x += 5) {
    for ($y = 220; $y -lt 250; $y += 3) {
        $c = $bmp.GetPixel($x, $y)
        if ($c.G -gt 100) {
            Write-Output ("  ($x,$y) R=$($c.R) G=$($c.G) B=$($c.B)")
            $found = $true
            break
        }
    }
    if ($found) { break }
}

# Rocket position - search for red pixels cluster
Write-Output ("Rocket red pixel locations (scanning full image):")
$redLocations = @()
for ($x = 0; $x -lt $w; $x += 3) {
    for ($y = 0; $y -lt $h; $y += 3) {
        $c = $bmp.GetPixel($x, $y)
        if ($c.R -gt 200 -and $c.G -lt 130 -and $c.B -lt 130 -and $c.R -gt $c.G + 60) {
            $redLocations += "$($x),$($y) R=$($c.R) G=$($c.G) B=$($c.B)"
        }
    }
}
Write-Output ("  Total red pixels found: $($redLocations.Count)")
if ($redLocations.Count -gt 0) {
    Write-Output ("  First 20 locations:")
    for ($i = 0; $i -lt [Math]::Min(20, $redLocations.Count); $i++) {
        Write-Output ("  $($redLocations[$i])")
    }
    Write-Output ("  Last 5 locations:")
    for ($i = [Math]::Max(0, $redLocations.Count-5); $i -lt $redLocations.Count; $i++) {
        Write-Output ("  $($redLocations[$i])")
    }
}

$bmp.Dispose()

# Final file size report
Write-Output ("")
$sf = Get-Item 'C:\rocket-autopilot-game\docs\screenshot.png'
Write-Output ("screenshot.png: $($sf.Length) bytes")
$sf2 = Get-Item 'C:\rocket-autopilot-game\docs\shot1.png'
Write-Output ("shot1.png: $($sf2.Length) bytes")
$sf3 = Get-Item 'C:\rocket-autopilot-game\docs\shot2.png'
Write-Output ("shot2.png: $($sf3.Length) bytes")
