$ErrorActionPreference = "Stop"

$html = Get-Content -Path "index.html" -Raw

function Extract-Block {
    param (
        [string]$startMarker,
        [string]$endMarker
    )
    $startIndex = $html.IndexOf($startMarker)
    if ($startIndex -eq -1) { throw "Start not found: $startMarker" }
    
    if ([string]::IsNullOrEmpty($endMarker)) {
        $endIndex = $html.Length
    } else {
        $endIndex = $html.IndexOf($endMarker, $startIndex)
        if ($endIndex -eq -1) { throw "End not found: $endMarker" }
    }
    
    return $html.Substring($startIndex, $endIndex - $startIndex)
}

$preHero = $html.Substring(0, $html.IndexOf("    <!-- Hero Section -->"))
$hero = Extract-Block -startMarker "    <!-- Hero Section -->" -endMarker "    <!-- Quem Somos -->"
$quemSomos = Extract-Block -startMarker "    <!-- Quem Somos -->" -endMarker "    <!-- Soluções -->"
$solucoes = Extract-Block -startMarker "    <!-- Soluções -->" -endMarker "    <!-- Cases de Sucesso -->"
$cases = Extract-Block -startMarker "    <!-- Cases de Sucesso -->" -endMarker "    <!-- Ecossistema Tecnológico -->"
$ecossistema = Extract-Block -startMarker "    <!-- Ecossistema Tecnológico -->" -endMarker "    <!-- Timeline do Processo de Engenharia -->"
$timeline = Extract-Block -startMarker "    <!-- Timeline do Processo de Engenharia -->" -endMarker "    <!-- Modelo Comercial & Segurança -->"
$comercial = Extract-Block -startMarker "    <!-- Modelo Comercial & Segurança -->" -endMarker "    <!-- ROI Calculator -->"
$roi = Extract-Block -startMarker "    <!-- ROI Calculator -->" -endMarker "    <!-- Footer -->"
$footer = $html.Substring($html.IndexOf("    <!-- Footer -->"))

$newNav = @"
            <div class="nav-links">
                <a href="#roi-calculator">ROI</a>
                <a href="#solucoes">Soluções</a>
                <a href="#cases">Cases</a>
                <a href="#sobre">Quem Somos</a>
                <a href="#ecossistema">Stack</a>
                <a href="#processo">Processo</a>
                <a href="#comercial">Modelo</a>
            </div>
"@

$newPreHero = $preHero -replace '(?s)<div class="nav-links">.*?</div>', $newNav

$newHtml = $newPreHero + $hero + $roi + $solucoes + $cases + $quemSomos + $ecossistema + $timeline + $comercial + $footer

[System.IO.File]::WriteAllText("index.html", $newHtml, [System.Text.Encoding]::UTF8)
Write-Output "SUCCESS"
