import os
import requests
import json
import sys
#from subprocess import call

def call_api(owner, repo, subpath, data=None, username=None, password=None):
    """ Takes a subpath under the repository (ex: /releases) and returns the json data from the api """
    api_url = 'https://api.github.com/repos/%s/%s%s' % (owner, repo, subpath)
    # Use Github Authentication if available for the repo
    kwargs = {}
    if username and password:
        kwargs['auth'] = (username, password)

    if data:
        resp = requests.post(api_url, data=json.dumps(data), **kwargs)
    else:
        resp = requests.get(api_url, **kwargs)

    try:
        data = json.loads(resp.content)
        return data
    except:
        return resp.status_code

def create_release():
    ORG_NAME=os.environ.get('GITHUB_ORG_NAME')
    REPO_NAME=os.environ.get('GITHUB_REPO_NAME')
    USERNAME=os.environ.get('GITHUB_USERNAME')
    PASSWORD=os.environ.get('GITHUB_PASSWORD')
    BUILD_COMMIT=os.environ.get('BUILD_COMMIT')
    PACKAGE_VERSION=os.environ.get('PACKAGE_VERSION')
    
    existing = None
    
    releases = call_api(ORG_NAME, REPO_NAME, '/releases', username=USERNAME, password=PASSWORD)
    for rel in releases:
        if rel['name'] == PACKAGE_VERSION:
            existing = rel
            break
    
    if existing:
        print 'Release for %s already exists' % PACKAGE_VERSION
        exit()
    
    tag_name = PACKAGE_VERSION.replace(' (','-').replace(')','').replace(' ','_')
    
    data = {
        'tag_name': 'uat/%s' % tag_name,
        'target_commitish': BUILD_COMMIT,
        'name': PACKAGE_VERSION,
        'body': '',
        'draft': False,
        'prerelease': True,
    }
    
    rel = call_api(ORG_NAME, REPO_NAME, '/releases', data=data, username=USERNAME, password=PASSWORD)
    
    print 'Release created:'
    print rel

    # TODO: Zip and upload the unpackaged/pre and unpackage/post bundles

if __name__ == '__main__':
    try:
        create_release()
    except:
        e = sys.exc_info()[0]
        print e
        sys.exit(1)
