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
    #TODO add usage + parameter check
    regurl = sys.argv[1:][0]
    command = sys.argv[1:][1]

    if command == "list":
        repo_to_list = sys.argv[1:][2]
        if repo_to_list == "all":
            try:
                all_repos = get_all_repos(regurl)
                for repo_in_registry in all_repos:
                    print repo_in_registry
            except:
                print "no repos found"
                exit(1)
        else:
            try:
                all_tags = get_all_tags_for_repo(regurl, repo_to_list)
            except:
                print "no tags for this repo"
                exit(1)
            for tag_in_repo in all_tags:
                print tag_in_repo

    elif command == "delete":
        image_to_delete = sys.argv[1:][2]
        tag_to_delete = sys.argv[1:][3]
        try:
            digest = get_digest(regurl, image_to_delete, tag_to_delete)
        except:
            print "no digest found for tag"
            exit(1)
        try:
            response = requests.delete(regurl + "/v2/" + image_to_delete + "/manifests/" + digest)
        except:
            print "Error deleting image"