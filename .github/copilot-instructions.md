# Python Random Scripts - Copilot Instructions

This file provides workspace-specific custom instructions for GitHub Copilot. For more details, visit [VS Code Copilot Customization](https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file).

## Project Overview

This is a Python project focused on creating standalone "drop-and-run" tools that can operate as both Python scripts and standalone EXE files. Each tool should work when placed in any directory and operate on the current working directory.

## Development Workflow Checklist

### 1. Clarify Project Requirements
- Ask for project type, language, and frameworks if not specified
- Skip if already provided

### 2. Scaffold the Project
- Ensure previous step is completed
- Use project setup tools with appropriate projectType parameter
- Use '.' as the working directory
- Create project structure manually if no appropriate projectType available

### 3. Customize the Project
- Verify all previous steps are completed
- Develop modification plan according to user requirements
- Apply modifications using appropriate tools and references
- Skip for "Hello World" projects

### 4. Install Required Extensions
- Only install extensions mentioned in get_project_setup_info
- Skip otherwise and mark as completed

### 5. Compile the Project
- Verify all previous steps are completed
- Install missing dependencies
- Run diagnostics and resolve issues
- Check markdown files for relevant instructions

### 6. Create and Run Task
- Verify all previous steps are completed
- Check if project needs a task based on package.json, README.md, and project structure
- Use create_and_run_task if needed
- Skip otherwise

### 7. Launch the Project
- Verify all previous steps are completed
- Prompt user for debug mode, launch only if confirmed

### 8. Ensure Documentation is Complete
- Verify all previous steps are completed
- Ensure README.md and copilot-instructions.md exist and contain current project information
- Clean up copilot-instructions.md by removing HTML comments

## Development Rules and Guidelines

### Communication
- Keep explanations concise and focused
- Avoid verbose explanations or printing full command outputs
- State briefly when steps are skipped (e.g., "No extensions needed")
- Don't explain project structure unless asked

### Development Practices
- Use '.' as the working directory unless user specifies otherwise
- Avoid adding media or external links unless explicitly requested
- Use placeholders only with a note that they should be replaced
- Use VS Code API tool only for VS Code extension projects
- Don't suggest reopening the project in VS Code once it's already open

### Folder Creation
- Always use the current directory as the project root
- Use '.' argument for terminal commands to ensure current working directory is used
- Don't create new folders unless explicitly requested (except .vscode for tasks.json)
- If scaffolding commands mention incorrect folder names, notify user to create correct folder and reopen in VS Code

### Extension Installation
- Only install extensions specified by get_project_setup_info
- Do not install any other extensions

### Project Content
- Assume "Hello World" project if user hasn't specified details
- Avoid adding links, URLs, files, folders, or integrations unless explicitly required
- Don't generate images, videos, or media files unless explicitly requested
- Use placeholders for media assets with clear replacement instructions
- Ensure all components serve a clear purpose
- Prompt for clarification if features are assumed but not confirmed
- Use VS Code API tool for VS Code extension projects with relevant queries

### Script Development Philosophy
- All new scripts should be designed as "drop-and-run" standalone tools
- Each script should work as both a Python script and as a standalone EXE
- When run as an EXE, the tool should operate on the current working directory (where the EXE is placed)
- Scripts should be self-contained, requiring no external dependencies when built as EXE
- Follow the established pattern: create script in scripts/, create build script, test functionality, build EXE
- All tools should preserve original files and create organized output in timestamped or structured folders
- Interactive prompts should keep console open when run as EXE for user review

### Task Completion Criteria
Your task is complete when:
- Project is successfully scaffolded and compiled without errors
- copilot-instructions.md file in the .github directory exists in the project
- README.md file exists and is up to date
- User is provided with clear instructions to debug/launch the project

## Guidelines for Contributors

### Template for New Scripts
- All new scripts should follow the "drop-and-run" philosophy
- Ensure scripts can operate as both Python scripts and standalone EXE files
- Include boilerplate code for handling the current working directory and user-friendly error messages

### Testing Guidelines
- Test both the Python script and the EXE version to ensure they work as expected
- Verify that outputs are created in a structured folder (e.g., `outputs/<script_name>/<timestamp>/`)
- Ensure EXE files preserve original files and do not overwrite existing data

### Output Folder Structure
- All scripts should save outputs in a structured folder:
  - `outputs/<script_name>/<timestamp>/`
  - This ensures outputs are organized and easy to locate

### Error Handling
- Include robust error handling in all scripts
- Provide clear and user-friendly error messages, especially for common issues like missing dependencies or invalid inputs

### Interactive Prompts
- EXE files should include interactive prompts to keep the console open for user review
- For example, prompt the user to press Enter before closing the console after execution

### Documentation Updates
- Update the `README.md` file whenever a new script or feature is added
- Ensure the documentation includes usage instructions, dependencies, and examples

### Build Script Guidelines
- Maintain and update the build scripts to ensure compatibility with the latest project changes
- Verify that build scripts create self-contained EXE files with all required dependencies
- Test the EXE files on a clean Windows system to ensure they work without additional setup
