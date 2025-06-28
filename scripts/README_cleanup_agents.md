# Agent Cleanup Script

This script provides functionality to clean up agents from the database. Use with caution as it will permanently delete agent data.

## Usage

Run the script from the project root directory:

```bash
python scripts/cleanup_agents.py <action> [options]
```

## Actions

### List Agents

List all agents in the database without deleting anything:

```bash
python scripts/cleanup_agents.py list
```

### Cleanup All Agents

Delete all agents from the database:

```bash
python scripts/cleanup_agents.py cleanup-all
```

### Cleanup Agents by Type

Delete agents of a specific type:

```bash
python scripts/cleanup_agents.py cleanup-type --type <agent_type>
```

## Options

### --dry-run

Show what would be deleted without actually deleting:

```bash
python scripts/cleanup_agents.py cleanup-all --dry-run
python scripts/cleanup_agents.py cleanup-type --type "chatbot" --dry-run
```

### --type

Specify the agent type to delete (required for cleanup-type action):

```bash
python scripts/cleanup_agents.py cleanup-type --type "assistant"
```

## Examples

1. **List all agents:**

   ```bash
   python scripts/cleanup_agents.py list
   ```

2. **See what would be deleted (dry run):**

   ```bash
   python scripts/cleanup_agents.py cleanup-all --dry-run
   ```

3. **Delete all agents:**

   ```bash
   python scripts/cleanup_agents.py cleanup-all
   ```

4. **Delete only chatbot agents:**
   ```bash
   python scripts/cleanup_agents.py cleanup-type --type "chatbot"
   ```

## Safety Features

- **Confirmation prompts**: The script will ask for confirmation before deleting
- **Dry run mode**: Use `--dry-run` to see what would be deleted without actually deleting
- **Detailed output**: Shows exactly which agents will be affected
- **Error handling**: Graceful error handling with informative messages

## Warning

**This script permanently deletes data from the database. Make sure you have backups before running cleanup operations.**
