Rdetector
---------

Finds K8s Deployments that have multiple pods running on the same node.

This implementation sacrifices speed for feature flexibility and extensibility
the requirements specify that we only highlight deployments that have multiple
pods on the same node, however it would be useful to highlight what deployments
are only running on one node so remediation steps can be prioritized to those
deployments.

- requirements
    - read a KUBECONFIG file for k8s cluster access
    - can use kubernetes-client and needed standard libraries
    - using kubectl is not allowed
- initial thoughts
    - what is in a kubeconfig
    - specifies we can query all namespaces, make sure to be able to use all namespaces but also allow the option to specify a name space
    - need to use option parsing library to satisfy the --file requirement
        - should there be a default behavior when no --file is passed
    - example lists how many node failures the pod can withstand, this could be useful for output
    - show basic output and also see if we can get node specs and container specs to right size or recommend placement
    - future improvements could auto move containers to nodes with most free resources and no other pods
- implementation research
    - mvp
        - use kubernetes library
            - the v1 core api has a method to list all pods across all namespaces
            - also can read in config from file
        - do a list comprehension to show pods with the same node value
            - ```
                def pod_on_node(pod, node):
                    if node in podmap.get(pod):
                        return node
                    else:
                        podmap.get(pod).append(node)
              
              [ pod for pod, node in all_pods.items() if pod_on_node(pod, node) ]
              ```
- implementation challenges
    - the kuberentes config module shows that it should support a key word argument for the file path of a kubeconf, however when passing `kube_config_path` it throws an unexpected keyword error, checking the function definition shows a positional config_file option is expected instead.
    - the information returned by `v1.list_pod_for_all_namespaces` is densely nested, and I need to read more documentation on how to identify what pods are members of what deployments. it looks like i could keep a mapping of pod to replica set then use the replica set id to identify the deployment. There may be a simpler way by getting all deployments first.
        - found out that deployments manage pods by specifying in the `spec` a `matchLables` slector, I can get this for each deployment then filter the pods retrieved using these labels to easily get all the pods for a deployment
- research on solving this problem through kubernetes configurations
    - topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: kubernetes.io/hostname
          whenUnsatisfiable: DoNotSchedule
          matchLabelKeys:
            - app
            - pod-template-hash
    - https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/
    - https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector