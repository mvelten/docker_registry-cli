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


def get_digest(url, repo, tag):
    headers = {'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}
    request = requests.get(url + "/v2/" + repo + "/manifests/" + tag + "/", headers=headers)
    return request.headers['Docker-Content-Digest']


def get_blob_size(url, repo, blob):
    request = requests.head(url + "/v2/" + repo + "/blobs/" + blob)
    return request.headers['Content-Length']


def print_all_blob_sizes(url, repo, tag):
    request = requests.get(url + "/v2/" + repo + "/manifests/" + tag + "/")
    parsed_json = json.loads(request.text)
    blob_counter = 0

    for blob in parsed_json['fsLayers']:
        blob_size_in_kilobyte = float(get_blob_size(regurl, repo_to_list, blob['blobSum'])) / 1000
        id = parsed_json['history'][blob_counter]["v1Compatibility"]
        v1_compat_json = json.loads(parsed_json['history'][blob_counter]["v1Compatibility"])
        id = v1_compat_json["id"]
        cmd = v1_compat_json["container_config"]["Cmd"]
        print(str(blob_size_in_kilobyte) + " KB: \t\t\t" + str(cmd) + " ")
        blob_counter += 1


if __name__ == "__main__":
    # TODO add usage + parameter check
    regurl = sys.argv[1:][0]
    command = sys.argv[1:][1]

    if command == "list":
        repo_to_list = sys.argv[1:][2]
        if repo_to_list == "all":
            try:
                all_repos = get_all_repos(regurl)
                for repo_in_registry in all_repos:
                    print()
            except:
                print("no repos found")
                exit(1)

        else:
            try:
                all_tags = get_all_tags_for_repo(regurl, repo_to_list)
            except:
                print("no tags for this repo")
                exit(1)
            for tag_in_repo in all_tags:
                print(tag_in_repo)

    elif command == "delete":
        image_to_delete = sys.argv[1:][2]
        tag_to_delete = sys.argv[1:][3]
        try:
            digest = get_digest(regurl, image_to_delete, tag_to_delete)
        except:
            print("no digest found for tag")
            exit(1)
        try:
            response = requests.delete(regurl + "/v2/" + image_to_delete + "/manifests/" + digest)
        except:
            print("Error deleting image")

    elif command == "show-blobsize":
        repo_to_list = sys.argv[1:][2]
        tag_in_repo = sys.argv[1:][3]
        parsed_json = print_all_blob_sizes(regurl, repo_to_list, tag_in_repo)

    else:
        print("foo")
