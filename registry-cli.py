import json
import requests
import sys


def get_all_repos(url):
    request = requests.get(url + "/v2/_catalog")
    parsed_json = json.loads(request.text)
    repo_array = parsed_json['repositories']

    return repo_array

def get_all_tags_for_repo(url, repo):
    request = requests.get(url + "/v2/" + repo + "/tags/list")
    parsed_json = json.loads(request.text)
    repo_array = parsed_json['tags']

    return repo_array

def get_digest(regurl, repo, tag):
    headers = {'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}
    request = requests.get(regurl + "/v2/" + repo + "/manifests/" + tag + "/", headers=headers)
    return  request.headers['Docker-Content-Digest']


if __name__ == "__main__":
    regurl = sys.argv[1:][0]
    keyword = sys.argv[1:][1]

    if keyword == "list":
        repo_to_list = sys.argv[1:][2]
        if repo_to_list == "all":
            for repo_in_registry in get_all_repos(regurl):
                    print repo_in_registry
        else:
            for tag_in_repo in get_all_tags_for_repo(regurl, repo_to_list):
                print tag_in_repo

    elif keyword == "delete":
        image_to_delete = sys.argv[1:][2]
        tag_to_delete = sys.argv[1:][3]
        digest = get_digest(regurl, image_to_delete, tag_to_delete)
        response = requests.delete(regurl + "/v2/" + image_to_delete + "/manifests/" + digest)