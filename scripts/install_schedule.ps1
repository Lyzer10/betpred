# Installs the daily update as a Windows scheduled task (runs scripts/daily.sh).
# Runs at 07:00, 13:00 and 18:00; if the PC was off, it runs as soon as it is back on.
# Remove it any time with:  Unregister-ScheduledTask -TaskName "PL Predictor daily update"
$repo = Split-Path -Parent $PSScriptRoot
$bash = "C:\Program Files\Git\bin\bash.exe"
# C:\Users\...\FOOTBALL  ->  /c/Users/.../FOOTBALL  (Git Bash path)
$forward = $repo -replace '\\', '/'
$script = "/" + $forward.Substring(0, 1).ToLower() + $forward.Substring(2)
$log = "$script/engine/data/live/daily.log"
$action = New-ScheduledTaskAction -Execute $bash -Argument "-lc `"$script/scripts/daily.sh >> $log 2>&1`""
$triggers = @(
  (New-ScheduledTaskTrigger -Daily -At 07:00),
  (New-ScheduledTaskTrigger -Daily -At 13:00),
  (New-ScheduledTaskTrigger -Daily -At 18:00)
)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
  -ExecutionTimeLimit (New-TimeSpan -Minutes 30) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "PL Predictor daily update" -Action $action -Trigger $triggers -Settings $settings `
  -Description "Refresh data, predict with Betpawa odds, publish to GitHub (Vercel redeploys)." -Force | Out-Null
Write-Host "Installed. Next runs:" (Get-ScheduledTaskInfo -TaskName "PL Predictor daily update").NextRunTime
