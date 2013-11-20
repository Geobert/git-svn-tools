import os.path
import subprocess


def find_top_dir():
    current_path = os.getcwd()
    git_path = os.path.join(current_path, '.git')
    while not os.path.isdir(git_path):
        current_path = '/'.join(current_path.split('/')[:-1])
        if current_path == "":
            raise Exception('Could not find .git directory in ' +\
                '%s.' % os.getcwd() +\
                ' Call this script from a git repository.')
        git_path = os.path.join(current_path, '.git')
    return norm_path(current_path)


def get_externals_list(top_dir, repo_root):
    #Do we have chached values
    externals = read_externals_cache(top_dir, repo_root)
    if externals != None:
        return externals
    #No cached values, so fetch them
    result = subprocess.check_output([gitpath, 'svn', 'show-externals'], shell=True)
    folder = ""
    result = result.split('\n')
    externals = []
    for line in result:
        if line == "":
            continue
        elif line.startswith('# '):
            folder = line[3:]
        else:
            target, name = line.split(' ')
            name = os.path.join(top_dir, folder, name)
            if target.startswith('/'):
                target = os.path.join(repo_root, target[1:])
            target = norm_url(target)
            name = norm_path(name)
            externals.append((target, name))
    update_externals_cache(externals, top_dir, repo_root)
    return externals


def update_externals_cache(externals, top_dir, repo_root):
    print "update cache"
    cache_file = os.path.join(top_dir, '.git', 'externals_cache')
    cache = open(cache_file, 'w')
    for target, name in externals:
        print top_dir
        name = name.replace(top_dir, '')
        cache.write('%s, %s\n' % (target, name))
        print '%s, %s\n' % (target, name)


def read_externals_cache(top_dir, repo_root):
    cache_file = os.path.join(top_dir, '.git', 'externals_cache')
    try:
        cache = open(cache_file, 'r')
    except IOError:
        return None
    externals = []
    for line in cache:
        line = line.replace('\n', '')
        target, name = line.split(', ')
        name = top_dir + name
        externals.append((target, name))
    return externals


def get_repo_root():
    result = subprocess.check_output([gitpath, 'svn', 'info'], shell=True)
    result = result.split('\n')
    for line in result:
        if line.startswith('Repository Root:'):
            root = line.split(': ')[1]
            return root
    raise Exception('Could not find repository root .')


def checkout_repo(target, name):
    if os.path.isdir(name):
        print "Path %s already exists." % name
        return
    print "Cloning %s to %s" % (target, name)
    subprocess.call([gitpath, 'svn', 'clone', target, name], shell=True)


def add_to_ignore_file(top_path, name):
    try:
        exclude_file = open(os.path.join(top_path, '.git/info/exclude'), 'r')
        lines = exclude_file.readlines()
        name = name[len(top_path):]
        for l in lines:
            if l.startswith(name):
                print "Path %s is already in exclude list." % name
                return
    except IOError:
        #File does not exist. Create it.
        exclude_file = open(os.path.join(top_path, '.git/info/exclude'), 'w')
        exclude_file.close()
    print "Adding path %s to exclude list." % name
    exclude_file = open(os.path.join(top_path, '.git/info/exclude'), 'a')
    exclude_file.write("%s\n" % name)
    exclude_file.close()


def norm_url(url):
    protocol, path = url.split('://')
    path = os.path.normpath(path)
    path = path.replace('\\', '/')
    return '://'.join((protocol, path))


def norm_path(path):
    path = os.path.normpath(path)
    path = path.replace('\\', '/')
    return path
    

if __name__ == "__main__":
    gitpath = "C:\\Program Files (x86)\\Git\\bin\\git.exe"
    top_path = find_top_dir()
    repo_root = get_repo_root()
    externals_list = get_externals_list(top_path, repo_root)
    print "Found %i externals." % len(externals_list)
    for target, name in externals_list:
        checkout_repo(target, name)
        add_to_ignore_file(top_path, name)
        print ""
