#!/usr/bin/env python3
"""
Copyright 2022 Matthew Vander Hoff
Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Rdetector

Finds K8s Deployments that have multiple pods running on the same node.

This implementation sacrifices speed for feature flexibility and extensibility
the requirements specify that we only highligh deployments that have multiple
pods on the same node, however it would be useful to highlight what deployments
are only running on one node so remediation steps can be prioritized to those
deployments.

By: Matthew Vander Hoff
Last Updated: 2022 11 15
"""

import json
from argparse import ArgumentParser

from kubernetes import client, config


def get_commandline_flags():
    parser = ArgumentParser(
        prog="rdetector",
        description="identify deplopyments with multiple pods on the same node"
    )
    parser.add_argument('--file', help='file path to KUBECONF')
    parser.add_argument('-v', '--verbose',
                        help='enable verbose output', action="store_true")
    parser.add_argument('--spof',
                        help='highlight deployments on a single host',
                        action="store_true")
    parser.add_argument('-i', '--indent', help='print out indented json',
                        action="store_true")
    parser.add_argument('-q', '--quite', help='suppress default output',
                        action="store_true")
    args = parser.parse_args()
    if args.indent:
        args.tabs = 2
    else:
        args.tabs = None
    return args


def build_label_filter(match_labels):
    # for each match label key value pair make a string 'key = value' then
    # join all the string with commas. this lets us honor multiple filters
    # provided by the deployment spec
    ml = []
    for k, v in match_labels.items():
        ml.append("{} = {}".format(k, v))
    return ",".join(ml)


def get_all_deployments(kubeconf=None):
    # if no kubeconf provided use default behaivour
    if kubeconf:
        config.load_kube_config(kubeconf)
    else:
        config.load_kube_config()
    core = client.CoreV1Api()
    apps = client.AppsV1Api()
    all_deployments = apps.list_deployment_for_all_namespaces()
    # build a mapping of deployment name to label selector
    deployments = []
    for dep in all_deployments.items:
        # turn the dictionary of label selectors in to a string that we can
        # use to filter the list pods endpoint
        label_selector = build_label_filter(dep.spec.selector.match_labels)
        # list the pods for the deployment and store what node the pods are on
        # in a list later used to detect if multiple are on the same node
        deployment_pods = core.list_pod_for_all_namespaces(
            watch=False, label_selector=label_selector)
        pods = []
        for pod in deployment_pods.items:
            pods.append({
                "pod": pod.metadata.uid,
                "node": pod.spec.node_name
            })
        deployments.append({
            "name": dep.metadata.name,
            "pods": pods
        })
    return deployments


def find_deployments_with_multiple_pods_on_one_node(deployments):
    # for each deployment make a list of nodes and iterate all pods checking
    # if the node the pod is on is in the list, adding the node to the list
    # after checking. if the node is already on the list then add the
    # deploytment to the found list
    deployments_found = []
    for deployment in deployments:
        nodes = []
        for pod in deployment.get('pods'):
            if pod.get('node') in nodes:
                deployments_found.append(deployment.get('name'))
                break
            nodes.append(pod.get('node'))
    return deployments_found


def find_deployments_on_only_one_node(deployments):
    deployments_found = []
    for deployment in deployments:
        # if there is only one pod add it to the list
        if len(deployment.get('pods')) == 1:
            deployments_found.append(deployment.get('name'))
            next
        for pod in deployment.get('pods'):
            pod.get('node')
    return deployments_found


if __name__ == "__main__":
    args = get_commandline_flags()
    deployments = get_all_deployments(args.file)
    if args.verbose:
        print(json.dumps(deployments, indent=args.tabs))
    if args.spof:
        spof = find_deployments_on_only_one_node(deployments)
        if len(spof) > 0:
            print(json.dumps(spof, indent=args.tabs))
    if not args.quite:
        found = find_deployments_with_multiple_pods_on_one_node(deployments)
        print(json.dumps(found, indent=args.tabs))
