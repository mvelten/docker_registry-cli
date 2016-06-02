import argparse
import json
import requests


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
        blob_size_in_kilobyte = float(get_blob_size(url, repo, blob['blobSum'])) / 1000
        id = parsed_json['history'][blob_counter]["v1Compatibility"]
        v1_compat_json = json.loads(parsed_json['history'][blob_counter]["v1Compatibility"])
        id = v1_compat_json["id"]
        cmd = v1_compat_json["container_config"]["Cmd"]
        print(str(blob_size_in_kilobyte) + " KB: \t\t\t" + str(cmd) + " ")
        blob_counter += 1


def delete_digest(url, repo, digest):
    response = requests.delete(url + "/v2/" + repo + "/manifests/" + digest)
    return response.status_code

#
# base functions
#
def list(args):
    repo_to_list = format(args.repo)
    if repo_to_list == "all":
        try:
            all_repos = get_all_repos(format(args.regurl))
            for repo_in_registry in all_repos:
                print(repo_in_registry)
        except:
            print("no repos found")
            exit(1)
    else:
        response = get_all_tags_for_repo(format(args.regurl), format(args.repo))
        for tag in response:
            print(tag)

def show_blobsize(args):
    parsed_json = print_all_blob_sizes(format(args.regurl), format(args.repo), format(args.tag))

def delete(args):
    try:
        digest = get_digest(format(args.regurl), format(args.repo), format(args.tag))
    except:
        print("no digest found for tag")
        exit(1)
    try:
        delete_digest(format(args.regurl), format(args.repo), digest)
    except:
        print("Error deleting image")
        exit(1)
#
# argparse initialization
#
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

list_parser = subparsers.add_parser('list')
list_parser.add_argument('repo')
list_parser.add_argument('regurl')
list_parser.set_defaults(func=list)

delete_parser = subparsers.add_parser('delete')
delete_parser.add_argument('repo')
delete_parser.add_argument('tag')
delete_parser.add_argument('regurl')
delete_parser.set_defaults(func=delete)

show_blobsize_parser = subparsers.add_parser('show-blobsize')
show_blobsize_parser.add_argument('repo')
show_blobsize_parser.add_argument('tag')
show_blobsize_parser.add_argument('regurl')
show_blobsize_parser.set_defaults(func=show_blobsize)

#
# main function
#
if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)  # call the default function
