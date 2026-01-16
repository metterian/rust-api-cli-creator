#!/bin/bash
#
# rust-api-cli-creator Skill Installer
# Installs the skill to local project or global ~/.claude/skills/
#

set -e

SKILL_NAME="rust-api-cli-creator"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║           rust-api-cli-creator Skill Installer            ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}! $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if skill is already installed at a location
check_existing() {
    local path="$1"
    if [ -d "$path/$SKILL_NAME" ]; then
        return 0
    fi
    return 1
}

# Install skill to target directory
install_skill() {
    local target_dir="$1"
    local skill_path="$target_dir/$SKILL_NAME"

    # Create target directory if needed
    mkdir -p "$target_dir"

    # Check if already exists
    if [ -d "$skill_path" ]; then
        echo ""
        print_warning "Skill already exists at: $skill_path"
        read -p "Overwrite? (y/N): " overwrite
        if [[ ! "$overwrite" =~ ^[Yy]$ ]]; then
            echo "Installation cancelled."
            exit 0
        fi
        rm -rf "$skill_path"
    fi

    # Copy skill files
    echo ""
    echo "Installing to: $skill_path"
    mkdir -p "$skill_path"

    # Copy core files
    cp "$SCRIPT_DIR/SKILL.md" "$skill_path/"
    print_success "Copied SKILL.md"

    # Copy references
    if [ -d "$SCRIPT_DIR/references" ]; then
        mkdir -p "$skill_path/references"
        cp -r "$SCRIPT_DIR/references/"* "$skill_path/references/"
        print_success "Copied references/"
    fi

    # Copy scripts
    if [ -d "$SCRIPT_DIR/scripts" ]; then
        mkdir -p "$skill_path/scripts"
        cp -r "$SCRIPT_DIR/scripts/"* "$skill_path/scripts/"
        chmod +x "$skill_path/scripts/"*.py 2>/dev/null || true
        chmod +x "$skill_path/scripts/"*.sh 2>/dev/null || true
        print_success "Copied scripts/"
    fi

    echo ""
    print_success "Installation complete!"
    echo ""
    echo "Skill installed to: $skill_path"
}

# Main
print_header

echo "Where would you like to install the skill?"
echo ""
echo "  1) Global  (~/.claude/skills/) - Available in all projects"
echo "  2) Local   (./.claude/skills/) - Only this project"
echo "  3) Custom  (specify path)"
echo ""
read -p "Select option [1-3]: " choice

case "$choice" in
    1)
        TARGET_DIR="$HOME/.claude/skills"
        echo ""
        print_success "Selected: Global installation"
        ;;
    2)
        TARGET_DIR="./.claude/skills"
        echo ""
        print_success "Selected: Local installation"
        ;;
    3)
        read -p "Enter custom path: " custom_path
        TARGET_DIR="${custom_path/#\~/$HOME}"
        echo ""
        print_success "Selected: Custom path"
        ;;
    *)
        print_error "Invalid option. Exiting."
        exit 1
        ;;
esac

install_skill "$TARGET_DIR"

echo ""
echo "Usage:"
echo "  - The skill will auto-trigger on relevant requests"
echo "  - Or use: /rust-api-cli-creator"
echo ""
echo "Quick start:"
echo "  $TARGET_DIR/$SKILL_NAME/scripts/init_rust_cli.py my-cli --api-name MyAPI --path ."
echo ""
