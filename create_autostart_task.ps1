#Requires -RunAsAdministrator
# 创建开机启动任务 - 最简单可靠的方式

$TaskName = "YashanMcpServer"
$ProjectPath = "C:\Users\coden\mcp2\yashan\mcp-yashan"
$PythonExe = (Get-Command python).Source

Write-Host "创建崖山 MCP Server 开机启动任务..." -ForegroundColor Green

# 删除旧任务
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

# 创建任务动作
$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument "server.py --host 0.0.0.0 --port 20302" -WorkingDirectory $ProjectPath

# 创建触发器（用户登录时启动）
$Trigger = New-ScheduledTaskTrigger -AtLogon

# 创建任务设置
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# 注册任务
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "崖山数据库 MCP Server" | Out-Null

# 启动任务
Start-ScheduledTask -TaskName $TaskName

Write-Host "✅ 任务创建成功！" -ForegroundColor Green
Write-Host "任务名称: $TaskName" 
Write-Host "启动方式: 用户登录时自动启动"
Write-Host ""
Write-Host "管理命令:" 
Write-Host "  启动: Start-ScheduledTask $TaskName"
Write-Host "  停止: Stop-ScheduledTask $TaskName"
Write-Host "  查看: Get-ScheduledTask $TaskName"
Write-Host "  删除: Unregister-ScheduledTask $TaskName -Confirm:`$false"
