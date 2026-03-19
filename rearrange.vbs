Const ForReading = 1
Const ForWriting = 2
Set objFSO = CreateObject("Scripting.FileSystemObject")
strFilePath = "c:\Users\lipec\Desktop\GenesisKore Clinicas\index.html"
Set objFile = objFSO.OpenTextFile(strFilePath, ForReading, False, -1) ' -1 for Unicode/UTF-16, try 0 for ASCII/UTF-8
strContent = objFile.ReadAll
objFile.Close

' As VBScript Regex is limited with capturing large multiline groups easily,
' we can just use the Split function based on the exact markers since they are unique.
arrROI = Split(strContent, "    <!-- ROI Calculator -->")
prefix = arrROI(0)
strAfterROI = "    <!-- ROI Calculator -->" & arrROI(1)

arrSolucoes = Split(strAfterROI, "    <!-- Soluções -->")
roiBlock = arrSolucoes(0)
strAfterSol = "    <!-- Soluções -->" & arrSolucoes(1)

arrCases = Split(strAfterSol, "    <!-- Cases de Sucesso -->")
solucoesBlock = arrCases(0)
strAfterCases = "    <!-- Cases de Sucesso -->" & arrCases(1)

arrSobre = Split(strAfterCases, "    <!-- Quem Somos -->")
casesBlock = arrSobre(0)
strAfterSobre = "    <!-- Quem Somos -->" & arrSobre(1)

arrEcos = Split(strAfterSobre, "    <!-- Ecossistema Tecnológico -->")
sobreBlock = arrEcos(0)
strAfterEcos = "    <!-- Ecossistema Tecnológico -->" & arrEcos(1)

arrProc = Split(strAfterEcos, "    <!-- Timeline do Processo de Engenharia -->")
ecosBlock = arrProc(0)
strAfterProc = "    <!-- Timeline do Processo de Engenharia -->" & arrProc(1)

arrCom = Split(strAfterProc, "    <!-- Modelo Comercial & Segurança -->")
procBlock = arrCom(0)
strAfterCom = "    <!-- Modelo Comercial & Segurança -->" & arrCom(1)

arrFoot = Split(strAfterCom, "    <!-- Footer -->")
comBlock = arrFoot(0)
suffix = "    <!-- Footer -->" & arrFoot(1)

' Desired order: ROI -> Quem Somos(sobre) -> Solucoes -> Cases -> Processo -> Stack(ecossistema) -> Modelo(comercial)
newContent = prefix & roiBlock & sobreBlock & solucoesBlock & casesBlock & procBlock & ecosBlock & comBlock & suffix

' Save as UTF-8 without BOM
Set objStream = CreateObject("ADODB.Stream")
objStream.Type = 2
objStream.Charset = "utf-8"
objStream.Open
objStream.WriteText newContent
objStream.SaveToFile strFilePath, 2
objStream.Close
