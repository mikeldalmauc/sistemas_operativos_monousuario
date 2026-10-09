# Despliegue del ranking desde Windows (PowerShell): hace commit+push de lo pendiente si lo pides
# y lanza desplegar.sh en el servidor por SSH. Requiere el Host "servidor-som" en ~/.ssh/config.
#     .\desplegar.ps1              → solo despliega lo que ya esté en GitHub
#     .\desplegar.ps1 "mensaje"    → git add -A, commit con ese mensaje, push, y despliega
param([string]$Mensaje = "", [string]$Servidor = "servidor-som")
$repo = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath)))
Set-Location $repo
if ($Mensaje -ne "") {
  git add -A
  git commit -m $Mensaje
  if ($LASTEXITCODE -ne 0) { Write-Host "Nada que commitear, sigo con el push/despliegue." }
}
git push
if ($LASTEXITCODE -ne 0) { Write-Error "git push ha fallado; no despliego."; exit 1 }
ssh $Servidor "bash ~/sistemas_operativos_monousuario/prueba_comandos/ranking/servidor/desplegar.sh"
