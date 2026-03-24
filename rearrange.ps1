$filePath = "c:\Users\lipec\Desktop\GenesisKore Clinicas\index.html"
$content = Get-Content -Path $filePath -Raw -Encoding UTF8

# Helper to extract a block using Regex
function Get-Block ($startMarker, $endMarker) {
    # .NET Regex for cross-line match
    $pattern = "(?s)($startMarker.*?)($endMarker)"
    if ($content -match $pattern) {
        return $matches[1]
    }
    return ""
}

$roi = Get-Block "    <!-- ROI Calculator -->" "    <!-- Soluções -->"
$solucoes = Get-Block "    <!-- Soluções -->" "    <!-- Cases de Sucesso -->"
$cases = Get-Block "    <!-- Cases de Sucesso -->" "    <!-- Quem Somos -->"
$sobre = Get-Block "    <!-- Quem Somos -->" "    <!-- Ecossistema Tecnológico -->"
$ecossistema = Get-Block "    <!-- Ecossistema Tecnológico -->" "    <!-- Timeline do Processo de Engenharia -->"
$processo = Get-Block "    <!-- Timeline do Processo de Engenharia -->" "    <!-- Modelo Comercial & Segurança -->"
$comercial = Get-Block "    <!-- Modelo Comercial & Segurança -->" "    <!-- Footer -->"

$prefixPattern = "(?s)(.*?)    <!-- ROI Calculator -->"
if ($content -match $prefixPattern) { $prefix = $matches[1] } else { $prefix = "" }

$suffixPattern = "(?s)(    <!-- Footer -->.*)"
if ($content -match $suffixPattern) { $suffix = $matches[1] } else { $suffix = "" }

# Check that we parsed successfully
if ([string]::IsNullOrEmpty($roi) -or [string]::IsNullOrEmpty($comercial)) {
    Write-Host "Failed to parse blocks."
    exit 1
}

$newContent = $prefix + $roi + $sobre + $solucoes + $cases + $processo + $ecossistema + $comercial + $suffix

[System.IO.File]::WriteAllText($filePath, $newContent, [System.Text.Encoding]::UTF8)
Write-Host "Success"
