import os
import fnmatch

def check_file_ignored(file_path, ignore_patterns):
    # This is a VERY simple simulation and might not perfectly match Docker's Go-based logic
    # but it helps debug simple patterns.
    path_parts = file_path.split('/')
    
    ignored = False
    matched_rule = None
    
    for pattern in ignore_patterns:
        pattern = pattern.strip()
        if not pattern or pattern.startswith('#'):
            continue
            
        is_negative = pattern.startswith('!')
        clean_pattern = pattern[1:] if is_negative else pattern
        
        # Simple glob matching
        if fnmatch.fnmatch(file_path, clean_pattern) or \
           fnmatch.fnmatch(os.path.basename(file_path), clean_pattern):
            if is_negative:
                ignored = False
                matched_rule = pattern
            else:
                ignored = True
                matched_rule = pattern
                
    return ignored, matched_rule

def main():
    target_file = 'frontend/package.json'
    dockerignore_path = '.dockerignore'
    
    if not os.path.exists(dockerignore_path):
        print(".dockerignore not found")
        return

    with open(dockerignore_path, 'r') as f:
        patterns = f.readlines()
        
    print(f"Checking if '{target_file}' is ignored by .dockerignore...")
    ignored, rule = check_file_ignored(target_file, patterns)
    
    if ignored:
        print(f"❌ IGNORED by rule: {rule}")
    else:
        print("✅ INCLUDED (Not ignored)")

if __name__ == "__main__":
    main()

