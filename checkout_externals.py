import os.path
import subprocess


def find_top_dir():
    current_path = os.getcwd()
    git_path = os.path.join(current_path, '.git')
    while not os.path.isdir(git_path):
        current_path = '/'.join(current_path.split('/')[:-1])
        if current_path == "":
            raise Exception('Could not find .git directory.' +\
                ' Call this script from a git repository.')
        git_path = os.path.join(current_path, '.git')
    return current_path


def get_externals_list(top_path, repo_root):
    result = subprocess.check_output(['git svn show-externals'], shell=True)
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
            name = os.path.join(top_path, folder, name)
            if target.startswith('/'):
                target = os.path.join(repo_root, target[1:])
            target = norm_url(target)
            externals.append((target, name))
    return externals


def get_repo_root():
    result = subprocess.check_output(['git svn info'], shell=True)
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
    subprocess.call(['git svn clone %s %s' % (target, name)], shell=True)


def add_to_ignore_file(top_path, name):
    exclude_file = open(os.path.join(top_path, '.git/info/exclude'), 'r')
    lines = exclude_file.readlines()
    name = name[len(top_path):]
    for l in lines:
        if l.startswith(name):
            print "Path %s is already in exclude list." % name
            return
    print "Adding path %s to exclude list." % name
    exclude_file = open(os.path.join(top_path, '.git/info/exclude'), 'a')
    exclude_file.write("%s\n" % name)
    exclude_file.close()


def norm_url(url):
    protocol, path = url.split('://')
    path = os.path.normpath(path)
    return '://'.join((protocol, path))


if __name__ == "__main__":
    top_path = find_top_dir()
    repo_root = get_repo_root()
    externals_list = get_externals_list(top_path, repo_root)
    print "Found %i externals." % len(externals_list)
    for target, name in externals_list:
        checkout_repo(target, name)
        add_to_ignore_file(top_path, name)
        print ""
