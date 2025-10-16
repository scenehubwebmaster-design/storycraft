# PowerShell script to convert TanStack Router files to React Router

$files = @(
    "Stories.jsx",
    "StoryDetail.jsx",
    "Worlds.jsx",
    "WorldDetail.jsx",
    "Settings.jsx",
    "CreateCharacter.jsx",
    "CreateStory.jsx",
    "CreateWorld.jsx",
    "CreateScene.jsx",
    "CreateLocation.jsx"
)

foreach ($file in $files) {
    $path = "E:\storycraft\frontend\src\pages\$file"
    
    Write-Host "Converting $file..."
    
    # Read the file
    $content = Get-Content $path -Raw
    
    # Replace imports
    $content = $content -replace 'import \{ createFileRoute, Link, useNavigate, useParams, useSearch, Outlet, useMatches \} from "@tanstack/react-router";', 'import { Link, useNavigate, useParams, useSearchParams, useLocation } from "react-router-dom";'
    $content = $content -replace 'import \{ createFileRoute, Link, useNavigate, useParams, useSearch \} from "@tanstack/react-router";', 'import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";'
    $content = $content -replace 'import \{ createFileRoute, Link, useNavigate, useParams \} from "@tanstack/react-router";', 'import { Link, useNavigate, useParams } from "react-router-dom";'
    $content = $content -replace 'import \{ createFileRoute, Link, useNavigate, useSearch \} from "@tanstack/react-router";', 'import { Link, useNavigate, useSearchParams } from "react-router-dom";'
    $content = $content -replace 'import \{ createFileRoute, Link, useNavigate \} from "@tanstack/react-router";', 'import { Link, useNavigate } from "react-router-dom";'
    $content = $content -replace 'import \{ createFileRoute, Link, Outlet, useMatches \} from "@tanstack/react-router";', 'import { Link, useLocation } from "react-router-dom";'
    $content = $content -replace 'import \{ createFileRoute, Link \} from "@tanstack/react-router";', 'import { Link } from "react-router-dom";'
    $content = $content -replace 'import \{ createFileRoute \} from "@tanstack/react-router";', 'import { } from "react-router-dom";'
    
    # Fix relative imports (from ../../ to ../)
    $content = $content -replace 'from "\.\.\/\.\.\/config\/api"', 'from "../config/api"'
    $content = $content -replace 'from "\.\.\/\.\.\/components\/', 'from "../components/'
    $content = $content -replace 'from "\.\.\/\.\.\/hooks\/', 'from "../hooks/'
    
    # Remove Route export and component wrapper
    $content = $content -replace 'export const Route = createFileRoute\([^)]+\)\(\{[^}]+\}\);', ''
    
    # Replace function component names with export default
    $content = $content -replace 'function (\w+Component)\(\) \{', 'export default function $1() {'
    $content = $content -replace 'function (\w+Page)\(\) \{', 'export default function $1() {'
    
    # Replace Route.useParams() with useParams()
    $content = $content -replace 'const \{ (\w+) \} = Route\.useParams\(\);', 'const { $1 } = useParams();'
    
    # Replace useSearch with useSearchParams
    $content = $content -replace 'const searchParams = useSearch\(\{ from: "[^"]+" \}\);', 'const [searchParams] = useSearchParams();'
    $content = $content -replace 'searchParams\?\.(\w+)', 'searchParams.get("$1")'
    
    # Replace useMatches with useLocation
    $content = $content -replace 'const matches = useMatches\(\);', 'const location = useLocation();'
    $content = $content -replace 'const isChildRouteActive = matches\.length > 2;', '// No longer needed with React Router'
    $content = $content -replace 'if \(isChildRouteActive\) \{\s+return <Outlet />;\s+\}', ''
    
    # Remove Outlet usage
    $content = $content -replace '<Outlet />', ''
    
    # Write back
    Set-Content $path -Value $content
    
    Write-Host "✓ Converted $file"
}

Write-Host ""
Write-Host "All files converted!"
