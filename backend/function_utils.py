import git 
import shutil
import os
import stat

def is_same_repo(repo_path: str, repo_url: str) -> bool:
    """Check if the existing repo at repo_path matches the requested repo_url"""
    try:
        if not os.path.exists(repo_path):
            return False
            
        if not os.path.exists(os.path.join(repo_path, '.git')):
            return False
            
        repo = git.Repo(repo_path)
        
        # Check if remote origin matches the expected URL
        if 'origin' in repo.remotes:
            origin_url = repo.remotes.origin.url
            # Normalize URLs for comparison (handle .git suffix and trailing slashes)
            normalized_origin = origin_url.rstrip('/').rstrip('.git')
            normalized_expected = repo_url.rstrip('/').rstrip('.git')
            
            return normalized_origin == normalized_expected
        
        return False
        
    except (git.InvalidGitRepositoryError, Exception):
        return False

def clone_repo(repo_url: str, repo_path: str):
    """Clone a repository from a URL to a local path
    
    Args:
        repo_url: URL of the repository to clone
        repo_path: Path to the local repository
        
    Returns:
        git.Repo: The cloned repository
    """
    # Check if we already have the same repo
    if is_same_repo(repo_path, repo_url):
        print(f"✅ Same repo already exists at {repo_path}, skipping clone")
        return git.Repo(repo_path)
    
    # Different repo or no repo exists - delete existing and clone fresh
    if os.path.exists(repo_path) and os.listdir(repo_path):
        print(f"🗑️ Different repo detected, deleting existing repo at {repo_path}")
        delete_cloned_repo(repo_path)

    # Check if repo path exists
    if not os.path.exists(repo_path):
        print(f"📁 Creating repo folder: {repo_path}")
        os.makedirs(repo_path)

    print(f"📥 Cloning {repo_url} to {repo_path}")
    
    try:
        # Try cloning main branch first
        repo = git.Repo.clone_from(repo_url, repo_path, branch="main")
        print(f"✅ Repo cloned successfully (main branch): {repo_path}")
        return repo
    except git.GitCommandError:
        try:
            # Fallback to master branch
            repo = git.Repo.clone_from(repo_url, repo_path, branch="master")
            print(f"✅ Repo cloned successfully (master branch): {repo_path}")
            return repo
        except git.GitCommandError:
            try:
                # Clone without specifying branch (get default)
                repo = git.Repo.clone_from(repo_url, repo_path)
                print(f"✅ Repo cloned successfully (default branch): {repo_path}")
                return repo
            except Exception as e:
                print(f"❌ Repo cloning failed: {e}")
                raise e

def delete_cloned_repo(repo_path: str) -> bool:
    """
    Delete a cloned repository from a local path
    
    Args:
        repo_path: Path to the repository to delete
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        # Check if path exists
        if not os.path.exists(repo_path):
            print(f"Path does not exist: {repo_path}")
            return False
            
        # Verify it's actually a git repository
        if not os.path.exists(os.path.join(repo_path, '.git')):
            print(f"Warning: Path does not appear to be a git repository: {repo_path}")
            
        # Handle Windows read-only files in git repos
        def handle_remove_readonly(func, path, exc):
            """Error handler for Windows readonly files"""
            if os.path.exists(path):
                os.chmod(path, stat.S_IWRITE)
                func(path)
                
        # Delete the repository
        shutil.rmtree(repo_path)
        print(f"Successfully deleted repository: {repo_path}")
        return True
        
    except PermissionError as e:
        print(f"Permission error deleting {repo_path}: {e}")
        return False
    except Exception as e:
        print(f"Error deleting repository {repo_path}: {e}")
        return False
    
def get_most_recent_commit(repo: git.Repo) -> git.Commit:
    """
    Get the most recent commit in a repository
    """
    return repo.head.commit