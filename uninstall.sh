#!/bin/bash
#
# rust-api-cli-creator Skill Uninstaller
# Removes the skill from local or global installation
#

set -e

SKILL_NAME="rust-api-cli-creator"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║          rust-api-cli-creator Skill Uninstaller           ║"
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

# Find all installations
find_installations() {
    local found=()

    # Check global
    if [ -d "$HOME/.claude/skills/$SKILL_NAME" ]; then
        found+=("$HOME/.claude/skills/$SKILL_NAME")
    fi

    # Check local
    if [ -d "./.claude/skills/$SKILL_NAME" ]; then
        found+=("./.claude/skills/$SKILL_NAME")
    fi

    echo "${found[@]}"
}

# Uninstall from specific path
uninstall_skill() {
    local path="$1"

    if [ ! -d "$path" ]; then
        print_error "Path does not exist: $path"
        return 1
    fi

    echo ""
    print_warning "This will remove: $path"
    read -p "Are you sure? (y/N): " confirm

    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        return 0
    fi

    rm -rf "$path"
    print_success "Removed: $path"

    # Clean up empty parent directories
    local parent_dir=$(dirname "$path")
    if [ -d "$parent_dir" ] && [ -z "$(ls -A "$parent_dir")" ]; then
        rmdir "$parent_dir" 2>/dev/null || true
    fi

    return 0
}

# Main
print_header

# Find installations
installations=($(find_installations))

if [ ${#installations[@]} -eq 0 ]; then
    echo "No installations found."
    echo ""
    echo "Checked locations:"
    echo "  - $HOME/.claude/skills/$SKILL_NAME"
    echo "  - ./.claude/skills/$SKILL_NAME"
    echo ""
    read -p "Enter custom path to uninstall (or press Enter to exit): " custom_path

    if [ -z "$custom_path" ]; then
        exit 0
    fi

    custom_path="${custom_path/#\~/$HOME}"
    if [ -d "$custom_path" ]; then
        uninstall_skill "$custom_path"
    else
        print_error "Path does not exist: $custom_path"
        exit 1
    fi
    exit 0
fi

echo "Found ${#installations[@]} installation(s):"
echo ""

idx=1
for install in "${installations[@]}"; do
    echo "  $idx) $install"
    ((idx++))
done
echo "  $idx) All of the above"
echo "  0) Cancel"
echo ""

read -p "Select installation to remove [0-$idx]: " choice

if [ "$choice" == "0" ]; then
    echo "Cancelled."
    exit 0
fi

if [ "$choice" == "$idx" ]; then
    # Remove all
    for install in "${installations[@]}"; do
        uninstall_skill "$install"
    done
else
    # Remove specific
    selected_idx=$((choice - 1))
    if [ $selected_idx -ge 0 ] && [ $selected_idx -lt ${#installations[@]} ]; then
        uninstall_skill "${installations[$selected_idx]}"
    else
        print_error "Invalid selection."
        exit 1
    fi
fi

echo ""
print_success "Uninstallation complete!"
echo ""
