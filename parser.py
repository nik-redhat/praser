import git
import yaml
import shutil
import pprint
import os
import sys

repo = git.Repo('.')

# Load default upstream sources locations
f = open('upstream_sources.yaml.tmpl')
d = yaml.safe_load(f)
f.close()

usrc_updated = []

for i in d['git']:
    try:
        shutil.rmtree('abbccc')
    except:
        pass

    # Get proper repo name (upper case, no '-' characters)
    if i.get('alias', ''):
        name = i['alias'].upper().replace('-', '_')
    else:
        name = i['url'].split('/')[-1].upper().replace('-', '_')

    # Drop .git suffix
    if name.endswith('.GIT'):
        name = name[:-4]

    # Get the branch info, respect the branch overrides
    if os.environ.get(name + '_BRANCH_OVERRIDE', ''):
        new_branch = os.environ[name + '_BRANCH_OVERRIDE']
    else:
        new_branch = i['branch']

    # Check for COMMIT OVERRIDE
    if os.environ.get(name + '_COMMIT_OVERRIDE', ''):
        new_commit = os.environ[name + '_COMMIT_OVERRIDE']
    else:
        r = git.Repo.clone_from(i['url'], 'abbccc', single_branch = True, depth = '1', branch = new_branch)
        new_commit = r.head.object.hexsha

    # pprint.pprint({'url': i['url'], 'c1': i['commit'], 'c2': new_commit})
    if(i['commit'] != new_commit):
        usrc_updated.append("%s@%s: %s -> %s" % (i['url'].split('/')[-1], new_branch, i['commit'], new_commit))
    i['commit'] = new_commit

    # Process URL overrides
    if os.environ.get(name + '_URL_OVERRIDE', ''):
        i['url'] = os.environ.get(name + '_URL_OVERRIDE', '')

f = open('upstream_sources.yaml', 'w')
yaml.dump(d, f, default_flow_style=False)
f.close()

if not repo.index.diff(None) and not repo.index.diff('HEAD'):
    print("Nothing to update")
    sys.exit(0)


for diff_added in repo.index.diff('HEAD~1'):
    print(diff_added)