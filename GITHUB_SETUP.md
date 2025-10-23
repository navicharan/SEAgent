# GitHub Integration Setup Guide

## 🔑 GitHub Token Setup

The 404 error you're experiencing is caused by missing GitHub authentication. Here's how to fix it:

### Step 1: Create a GitHub Personal Access Token

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a descriptive name like "SEAgent Integration"
4. Select the following scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
   - ✅ `read:org` (Read org and team membership)

### Step 2: Set the Environment Variable

**For Windows PowerShell:**
```powershell
$env:GITHUB_TOKEN="your_token_here"
```

**For Windows Command Prompt:**
```cmd
set GITHUB_TOKEN=your_token_here
```

**For persistent setup (Windows):**
1. Search for "Environment Variables" in Windows
2. Click "Edit the system environment variables"
3. Click "Environment Variables..."
4. Under "User variables", click "New..."
5. Variable name: `GITHUB_TOKEN`
6. Variable value: your token
7. Click OK and restart your terminal

### Step 3: Verify Setup

Run this command to test authentication:
```bash
python test_github_auth.py
```

### Step 4: Repository Requirements

Make sure:
- The repository exists on GitHub
- Your token has access to the repository
- Repository format is correct: `owner/repository-name`

## 🚨 Common Issues

**404 Error**: Usually means missing authentication token
**403 Error**: Token doesn't have required permissions
**Repository not found**: Check owner/repo name spelling

## 🔒 Security Notes

- Keep your token secure and never commit it to code
- Use environment variables only
- Regenerate tokens if compromised
- Consider using fine-grained tokens for better security

## 🧪 Testing

After setup, test with:
1. Generate some code in the UI
2. Fill in the GitHub form with:
   - Owner: your GitHub username
   - Repository: an existing repository name
   - Commit message: "Test upload from SEAgent"
3. Click "Upload to GitHub"

The upload should now work! 🎉