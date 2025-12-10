# Justfile for Intro252 Course Project
# Run `just` to see all available commands

# Default recipe: show all available commands
default:
    @just --list

# ============================================================================
# TEST RECIPES
# ============================================================================

# Run full test suite
test: test-structure test-extensions test-render test-css
    @echo "✅ All tests passed!"

# Verify project structure and essential files
test-structure:
    @echo "🔍 Checking project structure..."
    @test -f _quarto.yml || (echo "❌ Missing _quarto.yml" && exit 1)
    @test -f index.qmd || (echo "❌ Missing index.qmd" && exit 1)
    @test -f references.bib || (echo "❌ Missing references.bib" && exit 1)
    @test -f document.css || (echo "❌ Missing document.css" && exit 1)
    @test -f slides.css || (echo "❌ Missing slides.css" && exit 1)
    @test -f filters/strip-revealjs-html.lua || (echo "❌ Missing strip-revealjs-html.lua" && exit 1)
    @echo "✅ Essential files present"
    @echo "🔍 Checking session files..."
    @test -f sessions/01_intro/01_intro.qmd || (echo "❌ Missing Session 01" && exit 1)
    @test -f sessions/02_pragmatics/02_pragmatics.qmd || (echo "❌ Missing Session 02" && exit 1)
    @test -f sessions/03_phonetics/03_phonetics.qmd || (echo "❌ Missing Session 03" && exit 1)
    @test -f sessions/04_phonology/04_phonology.qmd || (echo "❌ Missing Session 04" && exit 1)
    @test -f sessions/05_syntax/05_syntax.qmd || (echo "❌ Missing Session 05" && exit 1)
    @test -f sessions/07_morphology/07_morphology.qmd || (echo "❌ Missing Session 07" && exit 1)
    @echo "✅ All session files present"

# Verify extension versions match (extension files only, not docs)
test-extensions:
    @echo "🔍 Checking extension versions..."
    @uv run --script scripts/check-version-consistency.py --skip-docs || exit 1

# Render project and verify outputs
test-render:
    @echo "📝 Rendering project..."
    @quarto render || (echo "❌ Rendering failed" && exit 1)
    @echo "🔍 Verifying output files..."
    @test -f _site/index.html || (echo "❌ index.html not created" && exit 1)
    @uv run --script scripts/check-rendered-outputs.py || exit 1

# Verify CSS inclusion in rendered files
test-css:
    @uv run --script scripts/check-css-inclusion.py

# Check speaker notes are stripped in production (curl check)
test-notes:
    @echo "🔍 Checking speaker notes in production..."
    @COUNT=$$(curl -s "https://wuqui.github.io/Intro252/sessions/01_intro/slides.html" | grep -c '<aside class="notes">' || echo "0"); \
    if [ "$$COUNT" -eq 0 ]; then \
        echo "✅ Speaker notes stripped in production (count: $$COUNT)"; \
    else \
        echo "⚠️  Speaker notes found in production (count: $$COUNT)"; \
    fi

# Check Quarto installation
test-quarto:
    @echo "🔍 Checking Quarto installation..."
    @quarto --version || (echo "❌ Quarto not installed or not in PATH" && exit 1)
    @echo "✅ Quarto installed"

# Full test including Quarto check
full: test-quarto test
    @echo "✅ Full test suite completed"

# ============================================================================
# DOCS RECIPES
# ============================================================================

# Verify extension versions match across documentation files
docs-version-check:
    @echo "🔍 Checking version consistency in documentation..."
    @uv run --script scripts/check-version-consistency.py

# Check date format consistency in documentation
docs-dates:
    @echo "🔍 Checking date formats in documentation..."
    @python3 -c "import re, sys; content = open('../inf/index.md').read(); dates = re.findall(r'^- \d{4}-\d{1,2}-\d{1,2}', content, re.M); invalid = [d for d in dates if not re.match(r'^\d{4}-\d{2}-\d{2}', d[2:])]; print('✅ Date formats are consistent (YYYY-MM-DD)' if not invalid else f'⚠️  Found dates not in YYYY-MM-DD format: {invalid}')" 2>/dev/null || echo "⚠️  Could not check date formats"

# Verify all documentation files exist
docs-files:
    @echo "🔍 Checking documentation files..."
    @test -f ../inf/index.md || (echo "❌ Missing inf/index.md" && exit 1)
    @test -f ../inf/workflows.md || (echo "❌ Missing inf/workflows.md" && exit 1)
    @test -f ../inf/best-practices.md || (echo "❌ Missing inf/best-practices.md" && exit 1)
    @test -f ../inf/status-summary.md || (echo "❌ Missing inf/status-summary.md" && exit 1)
    @test -f ../inf/sessions-overview.md || (echo "❌ Missing inf/sessions-overview.md" && exit 1)
    @test -f ../inf/agenda.md || (echo "❌ Missing inf/agenda.md" && exit 1)
    @test -f ../inf/README.md || (echo "❌ Missing inf/README.md" && exit 1)
    @echo "✅ All documentation files present"

# ============================================================================
# TIDY RECIPES
# ============================================================================

# Remove trailing whitespace from files
tidy-whitespace:
    @echo "🧹 Removing trailing whitespace..."
    @find . -type f \( -name "*.qmd" -o -name "*.lua" -o -name "*.css" -o -name "*.yml" -o -name "*.md" \) \
        -not -path "./_site/*" \
        -not -path "./.git/*" \
        -not -path "./_extensions/*" \
        -exec sed -i '' 's/[[:space:]]*$$//' {} \;
    @echo "✅ Trailing whitespace removed"

# Run basic tidy verification
tidy-verify:
    @echo "🔍 Running basic tidy checks..."
    @echo "Checking for merge conflict markers..."
    @if grep -r "<<<<<<< " . --include="*.qmd" --include="*.lua" --include="*.css" --include="*.yml" 2>/dev/null; then \
        echo "❌ Found merge conflict markers"; \
        exit 1; \
    else \
        echo "✅ No merge conflict markers found"; \
    fi

# ============================================================================
# PUSH RECIPES
# ============================================================================

# Render project (for push workflow)
push-render:
    @echo "📝 Rendering project..."
    @quarto render || (echo "❌ Rendering failed" && exit 1)
    @echo "✅ Rendering complete"

# Show git status summary
push-status:
    @echo "📋 Git status:"
    @git status -sb

# Basic pre-push verification
push-verify: test-structure push-status
    @echo "✅ Pre-push checks passed"

# ============================================================================
# UTILITY RECIPES
# ============================================================================

# Clean rendered output files
clean:
    @echo "🧹 Cleaning rendered files..."
    @rm -rf _site
    @echo "✅ Cleaned rendered files"

# Quick test: structure + extensions
quick: test-structure test-extensions
    @echo "✅ Quick test completed"
