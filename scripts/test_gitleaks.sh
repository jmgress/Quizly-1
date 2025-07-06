#!/bin/bash

# Local GitLeaks Testing Script
# Run this script to test GitLeaks configuration locally

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔍 GitLeaks Local Testing Script${NC}"
echo "=================================="

downloadGitLeaks() {
    local version="8.27.2"
    local os_arch="darwin_arm64"
    
    # Detect OS and architecture
    if [[ "$OSTYPE" == "linux"* ]]; then
        os_arch="linux_x64"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if [[ "$(uname -m)" == "arm64" ]]; then
            os_arch="darwin_arm64"
        else
            os_arch="darwin_x64"
        fi
    fi
    
    local download_url="https://github.com/gitleaks/gitleaks/releases/download/v${version}/gitleaks_${version}_${os_arch}.tar.gz"
    
    echo -e "${YELLOW}📥 Downloading GitLeaks v${version} for ${os_arch}...${NC}"
    
    if ! wget -q "$download_url" -O gitleaks.tar.gz; then
        echo -e "${RED}❌ Failed to download GitLeaks${NC}"
        exit 1
    fi
    
    # Extract only the gitleaks binary to avoid overwriting project files like LICENSE
    tar -xzf gitleaks.tar.gz gitleaks
    chmod +x gitleaks
    echo -e "${GREEN}✅ GitLeaks downloaded successfully${NC}"
}

runGitLeaksScan() {
    echo -e "${YELLOW}🔍 Running GitLeaks scan...${NC}"
    
    if ./gitleaks detect \
        --config .gitleaks.toml \
        --redact \
        --verbose \
        --no-git \
        --source . \
        --report-format json \
        --report-path gitleaks-results.json; then
        
        echo -e "${GREEN}✅ GitLeaks scan completed successfully${NC}"
        echo -e "${GREEN}🎉 No secrets detected!${NC}"
    else
        echo -e "${YELLOW}⚠️  GitLeaks found potential secrets${NC}"
        displayResults
    fi
}

displayResults() {
    if [[ -f "gitleaks-results.json" ]]; then
        local findings=$(jq '. | length' gitleaks-results.json 2>/dev/null || echo "0")
        
        echo -e "${YELLOW}📋 Scan Results:${NC}"
        echo "Found $findings potential secret(s)"
        
        if [[ "$findings" -gt 0 ]]; then
            echo -e "${YELLOW}📝 Details:${NC}"
            jq -r '.[] | "  - \(.Description) in \(.File):\(.StartLine)"' gitleaks-results.json 2>/dev/null || echo "  Unable to parse results"
        fi
    fi
}

cleanupTestFiles() {
    echo -e "${YELLOW}🧹 Cleaning up test files...${NC}"
    rm -f gitleaks gitleaks.tar.gz gitleaks-results.json
    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

# Main execution
main() {
    if [[ ! -f ".gitleaks.toml" ]]; then
        echo -e "${RED}❌ .gitleaks.toml configuration file not found${NC}"
        echo "Please run this script from the project root directory"
        exit 1
    fi
    
    downloadGitLeaks
    runGitLeaksScan
    cleanupTestFiles
    
    echo -e "${GREEN}🎉 GitLeaks testing completed!${NC}"
}

# Execute main function
main "$@"
