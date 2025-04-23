#!/bin/bash

# params: Profile, Region(s)


# Configure virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo "In virtual environment: $VIRTUAL_ENV"
    do_not_deactivate='true'
else
    echo "Not in virutal environment..."
    # shellcheck disable=1091
    source .venv/bin/activate
    # shellcheck disable=2181
    if [ $? -ne 0 ]; then
        echo "No Python virtual enviroment. Creating..."
        python3 -m venv ./.venv
        # shellcheck disable=1091
        source .venv/bin/activate
    fi
fi

# Install prowler if needed
prowler -v > /dev/null 2>&1
# shellcheck disable=2181
if [ $? -ne 0 ]; then
    echo "'prowler' is not installed. Installing..."
    pip3 install prowler
fi

prowler -v

# Clarity on parameters
if [ -z "$1" ]; then
    this_profile='default'
    echo "Using default profile: '$this_profile'"
else
    echo "Identitied Profile: '$1'"
    this_profile=$1
fi

if [ -z "$2" ]; then
    this_region=$(aws configure get region)
    echo "Using identified region in local configurations: '$this_region'"
else
    echo "Identitied Region: '$2'"
    this_region=$2
fi

# Run Prowler
prowler --profile "$this_profile" --region "$this_region" --quick-inventory #--output-modes csv json-asff html


if [ -z "$do_not_deactivate" ]; then
    echo "Finished. Exiting Python virtual environment..."
    deactivate
fi
