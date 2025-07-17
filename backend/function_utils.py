import git 
import shutil
import os
import stat

def clone_repo(repo_url: str, repo_path: str):
    """Clone a repository from a URL to a local path
    
    Args:
        repo_url: URL of the repository to clone
        repo_path: Path to the local repository
        
    Returns:
        git.Repo: The cloned repository
    """
    # Check if repo exists and is non-empty
    if os.path.exists(repo_path) and os.listdir(repo_path):
        # Delete existing repo
        delete_cloned_repo(repo_path)

    # Check if repo path exists
    if not os.path.exists(repo_path):
        print(f"❗️ Creating repo folder: {repo_path}")
        os.makedirs(repo_path)

    # Check if repo is already cloned
    try:
        repo = git.Repo.clone_from(repo_url, repo_path, branch="main")
        if repo:
            print(f"✅ Repo cloned successfully: {repo_path}")
        else:
            print(f"❌ Repo cloning failed: {repo_path}")
        return repo
    except Exception as e:
        try:
            repo = git.Repo.clone_from(repo_url, repo_path, branch="master")
            if repo:
                print(f"✅ Repo cloned successfully: {repo_path}")
            else:
                print(f"❌ Repo cloning failed: {repo_path}")
            return repo
        except Exception as e:
            print(f"❌ Repo cloning failed: {repo_path}")
            return None

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