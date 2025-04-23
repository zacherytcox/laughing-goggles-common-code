# Laughing Goggles Common Code

A collection of common code utilities and tools for the Laughing Goggles project.

## Project Structure

```
laughing-goggles-common-code/
├── aws2tf/            # AWS to Terraform conversion tools
│   └── extract_all.sh # Script for importing AWS resources into Terraform
├── code_check/        # Code quality checking tools
│   └── check.sh      # Script for checking Python, Bash, and Terraform files
├── pre-hooks/         # Git pre-commit hooks setup
│   └── setup.sh      # Script for setting up pre-commit hooks
├── prowler/           # AWS security assessment tools
│   └── get_inventory.sh # Script for running AWS security inventory
└── terraformer/       # Terraform-related utilities
    └── extract_all.sh # Script for importing AWS resources into Terraform
```

## Pre-commit Hooks Setup

The `pre-hooks/setup.sh` script sets up Git pre-commit hooks to ensure code quality and consistency across the project. It automatically installs and configures pre-commit with a comprehensive set of hooks.

### Features

- **Code Formatting**: Uses `black` for Python code formatting
- **Code Quality**: Includes various checks for:
  - Trailing whitespace
  - End of file formatting
  - YAML validation
  - Large file detection
  - JSON formatting
  - Merge conflict detection
  - AWS credentials detection
  - Private key detection
  - Shell script validation (via shellcheck)
  - And many more

### Requirements

- Python 3.x with pip3
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd laughing-goggles-common-code
   ```

2. Make the setup script executable:
   ```bash
   chmod +x pre-hooks/setup.sh
   ```

3. Run the setup script:
   ```bash
   ./pre-hooks/setup.sh
   ```

The script will:
1. Check if pre-commit is installed and install it if missing
2. Create a `.pre-commit-config.yaml` file with recommended hooks
3. Prompt you to install the Git hooks
4. Run all hooks on all files after installation

### Dependencies

The script automatically installs these tools if missing:
- `pre-commit`: Git hook management
- `black`: Python code formatter
- `shellcheck`: Shell script analyzer
- Various pre-commit hooks from the pre-commit-hooks repository

## Code Quality Checker

The `code_check/check.sh` script provides automated code quality checks for Python, Bash, and Terraform files. It ensures consistent code formatting and identifies potential issues.

### Features

- **Python**: Uses `black` for code formatting
- **Bash**: Uses `shellcheck` for shell script validation
- **Terraform**: Uses `terraform fmt` for configuration formatting

### Requirements

- Python 3.x with pip3
- Homebrew (for installing dependencies)
- macOS (for Homebrew support)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd laughing-goggles-common-code
   ```

2. Make the check script executable:
   ```bash
   chmod +x code_check/check.sh
   ```

### Usage

Run the code quality checker:
```bash
./code_check/check.sh
```

The script will:
1. Check and install required dependencies if missing
2. Validate Python files using `black`
3. Check Bash scripts using `shellcheck`
4. Verify Terraform formatting using `terraform fmt`

### Dependencies

The script automatically installs these tools if missing:
- `black`: Python code formatter
- `shellcheck`: Shell script analyzer
- `terraform`: Infrastructure as Code tool

## Terraformer Utility

The `terraformer/extract_all.sh` script helps you import existing AWS infrastructure into Terraform configuration files. It uses the `terraformer` tool to automatically generate Terraform configurations for your AWS resources.

### Features

- Imports multiple AWS resources across all major regions
- Supports a wide range of AWS services including EC2, S3, RDS, and more
- Automatically installs required dependencies (terraform and terraformer)
- Interactive AWS profile selection
- Generates proper provider configuration

### Requirements

- macOS with Homebrew
- AWS credentials configured
- AWS CLI installed

### Usage

1. Make the script executable:
   ```bash
   chmod +x terraformer/extract_all.sh
   ```

2. Run the script:
   ```bash
   ./terraformer/extract_all.sh
   ```

3. Follow the prompts to:
   - Enter your AWS profile name
   - Confirm when you want to run the terraformer import

The script will:
1. Check and install required dependencies
2. Initialize Terraform with the AWS provider
3. Import your AWS resources into Terraform configuration files

### Supported AWS Resources

The script supports importing a comprehensive list of AWS resources including:
- Compute (EC2, ECS, Lambda)
- Storage (S3, EBS)
- Database (RDS, DynamoDB)
- Networking (VPC, Route53)
- Security (IAM, KMS)
- And many more AWS services

## AWS2TF Utility

The `aws2tf/extract_all.sh` script helps you convert existing AWS infrastructure into Terraform configuration files. It uses the `aws2tf` tool to automatically generate Terraform configurations for your AWS resources.

### Features

- Imports multiple AWS resources across all major services
- Supports a comprehensive list of AWS services including:
  - Networking (VPC, IGW, NATGW)
  - Compute (EC2, ECS, Lambda)
  - Storage (S3, EBS, EFS)
  - Database (RDS, DynamoDB, Aurora)
  - Security (IAM, KMS, Security Groups)
  - And many more AWS services
- Automatically organizes output by service
- Uses AWS SSO profile configuration

### Requirements

- AWS CLI configured with SSO
- Python 3.x
- AWS credentials configured with 'default' profile

### Usage

1. Configure AWS SSO:
   ```bash
   aws configure sso --profile default
   ```

2. Run the script:
   ```bash
   ./aws2tf/extract_all.sh
   ```

The script will:
1. Create a directory with timestamp and account information
2. Process each AWS service section
3. Generate Terraform configuration files for each service
4. Organize output in the created directory

## Prowler Security Assessment

The `prowler/get_inventory.sh` script provides automated AWS security assessment using the Prowler tool. It helps identify security risks and compliance issues in your AWS environment.

### Features

- Automated AWS security assessment
- Quick inventory of AWS resources
- Virtual environment management
- Support for multiple AWS profiles and regions
- CSV, JSON, and HTML output options

### Requirements

- Python 3.x
- AWS CLI configured
- Virtual environment support

### Usage

1. Make the script executable:
   ```bash
   chmod +x prowler/get_inventory.sh
   ```

2. Run the script:
   ```bash
   ./prowler/get_inventory.sh [profile] [region]
   ```

   Where:
   - `profile` (optional): AWS profile to use (defaults to 'default')
   - `region` (optional): AWS region to scan (defaults to configured region)

The script will:
1. Set up a Python virtual environment if needed
2. Install Prowler if not present
3. Run the security assessment
4. Generate inventory reports

## Disclaimer

This README was generated by an AI because, honestly, I was too lazy to write it myself. If it doesn't make sense or contains strange phrases, blame the machine — ~~it tried its best, I promise!~~ it tried.

Also, I do not accept any responsibility for the content of this repository or the scripts within it. It is what it is.
