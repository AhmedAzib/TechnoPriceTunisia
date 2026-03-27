# Fix syntax errors in MobilesPage.jsx
$content = Get-Content 'c:\Users\USER\Documents\programmation\frontend\src\MobilesPage.jsx'

# Fix line 296 - add missing semicolon after setFilters line
$content = $content -replace '    setFilters\(prev => \{', '    setFilters(prev => {;'

# Save the fixed content
Set-Content 'c:\Users\USER\Documents\programmation\frontend\src\MobilesPage.jsx' $content

Write-Host "Fixed syntax errors in MobilesPage.jsx" -ForegroundColor Green
