#!/bin/bash

# Define the green color code
GREEN='\033[0;32m'
# Define the red color code
RED='\033[0;31m'
# Define the no color code to reset the color
NC='\033[0m'


pip3 show "black" > /dev/null 2>&1
# shellcheck disable=2181
if [ $? -ne 0 ]; then
    echo "'black' linter is not installed. Installing..."
    pip3 install black
fi
printf "\n${RED}Checking Python files...${NC}\n"
black . --check --no-color
printf "${GREEN}Please run 'black .' to fix found issues.${NC}\n"



brew list "shellcheck" > /dev/null 2>&1
# shellcheck disable=2181
if [ $? -ne 0 ]; then
    echo "'shellcheck' linter is not installed. Installing..."
    brew install shellcheck
fi
printf "\n${RED}Checking Bash files...${NC}\n"
shellcheck --color=never $(find . -type f -name "*.sh")


terraform --version > /dev/null 2>&1
# shellcheck disable=2181
if [ $? -ne 0 ]; then
    echo "'terraform' is not installed. Installing..."
    brew install terraform
fi
printf "\n${RED}Checking Terraform files...\nFiles that need formating:${NC}\n"
terraform fmt -check -recursive
printf "${GREEN}Please run 'terraform fmt -recursive' to fix found issues.${NC}\n"
