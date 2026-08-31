Add-Type -AssemblyName System.Drawing
$bmp = [System.Drawing.Bitmap]::FromFile('C:\rocket-autopilot-game\docs\win_1.png')
$pts = @(
  @(20,60,'HUD fuel label area'), @(20,90,'HUD fuel bar'), @(20,160,'HUD ALT row'),
  @(640,30,'banner center'), @(640,60,'phase area'), @(640,300,'msg top area'),
  @(640,370,'msg/sub center'), @(640,430,'restart hint'), @(400,430,'hint left'), @(880,430,'hint right'),
  @(640,600,'planet center'), @(640,680,'ground'), @(400,680,'ground-left'), @(900,680,'ground-right'),
  @(960,180,'station area'), @(300,360,'msg left'), @(700,360,'msg right'),
  @(1100,100,'far right'), @(100,500,'mid-left star'), @(1200,300,'mid-right star')
)
foreach ($p in $pts) {
  $c = $bmp.GetPixel($p[0], $p[1])
  Write-Output ("({0,4},{1,4}) R={2,3} G={3,3} B={4,3}  {5}" -f $p[0], $p[1], $c.R, $c.G, $c.B, $p[2])
}
$bmp.Dispose()
