# Script to automatically fix rebase and remove .env from commit
$rebaseFile = ".git/rebase-merge/git-rebase-todo"
if (Test-Path $rebaseFile) {
    $content = Get-Content $rebaseFile
    $content = $content -replace '^pick bbb969e', 'edit bbb969e'
    Set-Content -Path $rebaseFile -Value $content
}

