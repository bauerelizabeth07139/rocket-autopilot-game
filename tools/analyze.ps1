param([string]$Path = 'C:\rocket-autopilot-game\docs\win_1.png')
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Runtime.InteropServices

$bmp = [System.Drawing.Bitmap]::FromFile($Path)
$W = $bmp.Width; $H = $bmp.Height
$rect = New-Object System.Drawing.Rectangle(0, 0, $W, $H)
$data = $bmp.LockBits($rect, [System.Drawing.Imaging.ImageLockMode]::ReadOnly, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$stride = $data.Stride
$bytes = New-Object byte[] ($stride * $H)
[System.Runtime.InteropServices.Marshal]::Copy($data.Scan0, $bytes, 0, $bytes.Length)
$bmp.UnlockBits($data)
$bmp.Dispose()

# BGRA layout: index = y*stride + x*4 ; bytes[x] = B, bytes[x+1]=G, bytes[x+2]=R, bytes[x+3]=A

function Test-Color([byte]$R, [byte]$G, [byte]$B, [int]$tR, [int]$tG, [int]$tB) {
    [Math]::Abs([int]$R - $tR) -le 30 -and [Math]::Abs([int]$G - $tG) -le 30 -and [Math]::Abs([int]$B - $tB) -le 30
}

function Get-BBox([scriptblock]$matcher, [int]$minCount = 4) {
    $minX = 99999; $minY = 99999; $maxX = -1; $maxY = -1; $count = 0
    for ($y = 0; $y -lt $H; $y++) {
        $base = $y * $stride
        for ($x = 0; $x -lt $W; $x++) {
            $i = $base + $x * 4
            $b = $bytes[$i]; $g = $bytes[$i+1]; $r = $bytes[$i+2]
            if (& $matcher $r $g $b) {
                $count++
                if ($x -lt $minX) { $minX = $x }
                if ($x -gt $maxX) { $maxX = $x }
                if ($y -lt $minY) { $minY = $y }
                if ($y -gt $maxY) { $maxY = $y }
            }
        }
    }
    if ($count -ge $minCount) {
        return [pscustomobject]@{ Count = $count; X0 = $minX; Y0 = $minY; X1 = $maxX; Y1 = $maxY; W = $maxX-$minX+1; H = $maxY-$minY+1 }
    }
    return $null
}

function Show([string]$name, $bb, [string]$expect = "") {
    if ($bb) { Write-Output ("{0,-22} FOUND   count={1,-7} bbox=({2},{3})-({4},{5}) size={6}x{7}  {8}" -f $name, $bb.Count, $bb.X0, $bb.Y0, $bb.X1, $bb.Y1, $bb.W, $bb.H, $expect) }
    else      { Write-Output ("{0,-22} MISSING                                     {1}" -f $name, $expect) }
}

# --- background / stars ---
$stars = Get-BBox { param($r,$g,$b) ([int]$r -eq [int]$g) -and ([int]$b - [int]$r) -ge 10 -and ([int]$r -ge 40) -and ([int]$r -le 210) }
Show "Stars (gray-blue)" $stars "expect: many tiny clusters in upper 2/3"

# --- home planet / ground ---
$ground = Get-BBox { param($r,$g,$b) (Test-Color $r $g $b 44 62 100) }
Show "Ground rect (44,62,100)" $ground "expect: full width strip y~660-720"
$gline = Get-BBox { param($r,$g,$b) (Test-Color $r $g $b 120 150 200) }
Show "Ground line (120,150,200)" $gline "expect: horizontal line y~660"
$planet = Get-BBox { param($r,$g,$b) (Test-Color $r $g $b 52 74 120) }
Show "Planet circle (52,74,120)" $planet "expect: wide blue arc below ground"

# --- landing pad ---
$pady = Get-BBox { param($r,$g,$b) (Test-Color $r $g $b 250 220 60) }
Show "Pad yellow (250,220,60)" $pady "expect: stripes near x 505-775, y 648-656"
$padd = Get-BBox { param($r,$g,$b) (Test-Color $r $g $b 40 40 46) }
Show "Pad dark (40,40,46)" $padd "expect: alternate stripes"
$padb = Get-BBox { param($r,$g,$b) (Test-Color $r $g $b 70 74 84) }
Show "Pad base (70,74,84)" $padb "expect: strip y~646-662"

# --- moon ---
$moon = Get-BBox { param($r,$g,$b) (Test-Color $r $g $b 150 156 170) }
Show "Moon body (150,156,170)" $moon "expect: circle ~ (176,116)-(324,264)"
$moonc = Get-BBox { param($r,$g,$b) (Test-Color $r $g $b 122 128 142) }
Show "Moon craters (122,128,142)" $moonc "expect: small circles inside moon"

# --- space station ---
$stb = Get-BBox { param($r,$g,$b) (Test-Color $r $g $b 170 180 220) }
Show "Station body (170,180,220)" $stb "expect: (994,136)-(1046,166)"
$stp = Get-BBox { param($r,$g,$b) (Test-Color $r $g $b 90 110 190) }
Show "Station pods (90,110,190)" $stp "expect: two side rects"
$stred = Get-BBox { param($r,$g,$b) (Test-Color $r $g $b 255 90 90) }
Show "Station red dot (255,90,90)" $stred "expect: ~ (1016,140) 4px"
$stgrn = Get-BBox { param($r,$g,$b) (Test-Color $r $g $b 60 255 120) }
Show "Station port green (60,255,120)" $stgrn "expect: ~ (1016,190)"
$stblink = Get-BBox { param($r,$g,$b) ([int]$r -eq [int]$g) -and ([int]$b -eq 60) -and ([int]$r -ge 100) -and ([int]$r -le 255) }
Show "Station port bar (blink,blink,60)" $stblink "expect: (1008,181)-(1032,187)"

# --- rocket ---
$rock = Get-BBox { param($r,$g,$b) (Test-Color $r $g $b 255 92 92) }
Show "Rocket red (255,92,92)" $rock "expect: nose+fins cluster somewhere in mid area"
$rhull = Get-BBox { param($r,$g,$b) (Test-Color $r $g $b 226 228 235) }
Show "Rocket hull (226,228,235)" $rhull "expect: vertical hull"
$rwin = Get-BBox { param($r,$g,$b) (Test-Color $r $g $b 40 60 90) }
Show "Rocket window (40,60,90)" $rwin "expect: small circle in hull"
$flame1 = Get-BBox { param($r,$g,$b) (Test-Color $r $g $b 255 170 40) }
Show "Flame orange (255,170,40)" $flame1 "expect: below rocket if thrusting"
$flame2 = Get-BBox { param($r,$g,$b) (Test-Color $r $g $b 255 240 150) }
Show "Flame light (255,240,150)" $flame2 "expect: inner flame"

# --- HUD left panel ---
$fuel = Get-BBox { param($r,$g,$b) (Test-Color $r $g $b 255 200 60) }
Show "Fuel bar fill (255,200,60)" $fuel "expect: (16,38)-(~196,52) top-left"
$fuelr = Get-BBox { param($r,$g,$b) (Test-Color $r $g $b 255 90 90) }
Show "Fuel bar red (low fuel)" $fuelr "expect: only if fuel<20"
$hudval = Get-BBox { param($r,$g,$b) (Test-Color $r $g $b 240 240 240) }
Show "HUD values (240,240,240)" $hudval "expect: top-left column"
$hudlab = Get-BBox { param($r,$g,$b) (Test-Color $r $g $b 170 190 210) }
Show "HUD labels (170,190,210)" $hudlab "expect: left column names"

# --- mode banner + phase + help bar ---
$bannerW = Get-BBox { param($r,$g,$b) (Test-Color $r $g $b 255 255 255) -and ($r -gt 240) }
Show "Banner white (MANUAL)" $bannerW "expect: text near top-center"
$bannerG = Get-BBox { param($r,$g,$b) (Test-Color $r $g $b 120 255 200) }
Show "Banner green / target" $bannerG "expect: if autopilot mode"
$phase = Get-BBox { param($r,$g,$b) (Test-Color $r $g $b 170 200 220) }
Show "Phase text (170,200,220)" $phase "expect: below banner / HUD labels"
$help = Get-BBox { param($r,$g,$b) (Test-Color $r $g $b 150 160 175) }
Show "Help bar (150,160,175)" $help "expect: bottom center y~694-710"

# --- overall stats ---
$blk = 0; $tot = $W*$H
for ($y = 0; $y -lt $H; $y++) {
    $base = $y * $stride
    for ($x = 0; $x -lt $W; $x++) {
        $i = $base + $x * 4
        if ([int]$bytes[$i] -eq 0 -and [int]$bytes[$i+1] -eq 0 -and [int]$bytes[$i+2] -eq 0) { $blk++ }
    }
}
Write-Output ("Overall: {0}x{1}, pure-black pixels {2} ({3:P1})" -f $W, $H, $blk, ($blk / $tot))
