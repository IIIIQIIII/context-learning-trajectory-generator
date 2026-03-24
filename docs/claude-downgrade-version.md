To downgrade the version of Claude Code, the specific commands depend on how you originally installed it (e.g., native installer or npm). For greater control and stability, it is also recommended to disable auto-updates after downgrading. 
LinkedIn
LinkedIn
 +4
Steps for Downgrading Claude Code
1. Disable Auto-Updates (Recommended) 
First, disable automatic updates to prevent Claude Code from automatically re-updating to the newest version after you downgrade. 
Reddit
Reddit
Open your terminal or command prompt.
Run the following command:
bash
claude config set -g autoUpdaterStatus disabled
Alternatively, add "autoUpdates": false to your .claude.json configuration file. 
Reddit
Reddit
 +1
2. Downgrade the Version
The method for downgrading differs based on your installation method:
If installed via npm (Node Package Manager): You can install a specific version using npm install.
Run the command:
bash
npm install -g @anthropic-ai/claude-code@[version_number]
For example, to downgrade to a widely used stable version mentioned by users in community forums, you might run:
bash
npm install -g @anthropic-ai/claude-code@1.0.88
After installation, you may need to update the system's symbolic link to point to the desired version's binary.
If installed via the native installer (recommended method): The claude CLI tool may offer a built-in command.
Run the command:
bash
claude install [version_number]
The system typically only keeps the three latest versions, so older versions might not be available via this command. Check the official Claude Code documentation or the GitHub releases page for available releases. 
Reddit
Reddit
 +4
3. Verify the Downgrade
After running the installation or configuration commands, restart your terminal session completely. 
Claude Help Center
Claude Help Center
Verify the current version by running:
bash
claude --version
Test basic functionality to confirm the desired version is active and stable for your workflow. 

claude install 2.1.1

2.1.1这个版本是我自身觉得最好用的版本

npm install -g @anthropic-ai/claude-code@2.1.1