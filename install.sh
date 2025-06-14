#!/bin/bash
# Cells Tool Registry Installer
# Installs tools from the registry to your local system

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default installation directory
INSTALL_DIR="${HOME}/.local/bin"
TOOLS_DIR="$(dirname "$0")/tools"

# Print usage
usage() {
    echo "Usage: $0 [OPTIONS] <tool_name>"
    echo ""
    echo "Options:"
    echo "  --all              Install all available tools"
    echo "  --dir <path>       Set installation directory (default: ~/.local/bin)"
    echo "  --list             List available tools"
    echo "  --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 weather_cli     Install the weather CLI tool"
    echo "  $0 --all           Install all tools"
    echo "  $0 --list          List all available tools"
}

# List available tools
list_tools() {
    echo -e "${BLUE}Available tools:${NC}"
    if [ -d "$TOOLS_DIR" ]; then
        for tool in "$TOOLS_DIR"/*; do
            if [ -d "$tool" ]; then
                tool_name=$(basename "$tool")
                if [ -f "$tool/README.md" ]; then
                    description=$(grep -m 1 "^#" "$tool/README.md" | sed 's/^# *//')
                    echo -e "  ${GREEN}$tool_name${NC} - $description"
                else
                    echo -e "  ${GREEN}$tool_name${NC}"
                fi
            fi
        done
    else
        echo "No tools directory found!"
        exit 1
    fi
}

# Install a single tool
install_tool() {
    local tool_name=$1
    local tool_path="$TOOLS_DIR/$tool_name"
    
    if [ ! -d "$tool_path" ]; then
        echo -e "${RED}Error: Tool '$tool_name' not found!${NC}"
        echo "Use --list to see available tools"
        exit 1
    fi
    
    echo -e "${BLUE}Installing $tool_name...${NC}"
    
    # Create installation directory if it doesn't exist
    mkdir -p "$INSTALL_DIR"
    
    # Check if tool has setup.sh
    if [ -f "$tool_path/setup.sh" ]; then
        echo "Running setup script..."
        (cd "$tool_path" && bash setup.sh)
    fi
    
    # Create virtual environment if needed
    if [ -f "$tool_path/pyproject.toml" ] || [ -f "$tool_path/requirements.txt" ]; then
        echo "Setting up Python virtual environment..."
        python3 -m venv "$tool_path/venv"
        source "$tool_path/venv/bin/activate"
        
        # Install dependencies
        if [ -f "$tool_path/pyproject.toml" ]; then
            pip install -e "$tool_path"
        elif [ -f "$tool_path/requirements.txt" ]; then
            pip install -r "$tool_path/requirements.txt"
        fi
        
        deactivate
    fi
    
    # Create wrapper script
    local wrapper_path="$INSTALL_DIR/$tool_name"
    cat > "$wrapper_path" << EOF
#!/bin/bash
# Auto-generated wrapper for $tool_name
TOOL_DIR="$tool_path"

# Activate virtual environment if it exists
if [ -d "\$TOOL_DIR/venv" ]; then
    source "\$TOOL_DIR/venv/bin/activate"
fi

# Run the tool
python "\$TOOL_DIR/${tool_name}.py" "\$@"
EOF
    
    chmod +x "$wrapper_path"
    echo -e "${GREEN}✓ Installed $tool_name to $wrapper_path${NC}"
    
    # Check if install directory is in PATH
    if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
        echo -e "${BLUE}Note: Add $INSTALL_DIR to your PATH:${NC}"
        echo "  export PATH=\"\$PATH:$INSTALL_DIR\""
    fi
}

# Parse arguments
if [ $# -eq 0 ]; then
    usage
    exit 1
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            echo -e "${BLUE}Installing all tools...${NC}"
            for tool in "$TOOLS_DIR"/*; do
                if [ -d "$tool" ]; then
                    install_tool "$(basename "$tool")"
                fi
            done
            exit 0
            ;;
        --dir)
            INSTALL_DIR="$2"
            shift 2
            ;;
        --list)
            list_tools
            exit 0
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            install_tool "$1"
            exit 0
            ;;
    esac
done