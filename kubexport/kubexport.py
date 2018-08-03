#!/usr/bin/env python
"""Export Kubernetes resources in structured  yaml or json files.
   Exported resources are stripped of timebased information.

Usage:
    kube-export [options]
    kube-export show-api-resources
    kube-export -h | --help
    kube-export --version


Options:
    -n, --namespace, --namespaces <namespaces>
                 List of namespaces to be exported, separated by commas
                 Examples: kube-export -n=namespace1,namespace2
    --all-namespace, --all-namespaces
                 If present export the requested object(s) across all namespaces and exclude sensitive information.
                 The namespace in current context is ignored even if specified with --namespace.
                 To specify a resource list to export use -r=<resources list>
                 This option is recommended to create export for all namespaces.
                 Examples: kube-export --all-namespaces

    -r, --resource, --resources <resources list>
                 List of resources to be exported, separated by commas
                 Examples: kube-export --resources=deployment,secret
                           kube-export -r=storageclasses,pv
                           kube-export -r=pod
                           kube-export -r=po,deploy,ds
    --recommended-resource, --recommended-resources
                 Export only recommended resources. This is the default option.
                 By default kube-export exports recommended resources.
                 To specify a resource to export use -r=<resources list>
                 If you define resources by --resource
                 or -r the --recommended-resource option will not be taken into account
                 Recommended resources are:
                 deployment, ...
    -c, --cluster-recommended-resource, --cluster-recommended-resources
                 Export only recommended resources from namespaces and cluster level
                 To specify a resource to export use -r=<resources list>
                 If you define resources by --resource, -r
                 the --cluster-recommended-resource option will not be taken into account
                 Recommended cluster resources are:
                 roles,rolebindings,clusterrolebindings,clusterroles,namespaces,pv,nodes,Storageclass,serviceaccounts
    -a, --all-resource, --all-resources
                 Export all resources from namespace(s) including pod, ...
    --all-cluster-resources
                 Export all cluster level resources including pod, ...

    show-api-resources
                 Prints the supported API resources on the Kubernetes server.
                 This command prints namespaced and unnamespaced resources separately.
                 Example: kube-export show-api-resources

    -k, --keep-original
                 Keep (don't clean, delete) original files and directories
                 before export to detect if resource is deleted in Kubernetes.

    -s, --sensitive
                 Include sensitive information from namespaces or cluster
                 Sensitive information are secrets,

                 Examples:
                          kube-export -s

    -o, --output (json, yaml)
                 Output format.
                 [default: yaml]
                 Examples:
                          kube-export -o=json

    --version    Show version
    -h, --help   Show help message

Examples:

    kube-export
                 Export all recommended resource from actual
                 namespace excluding sensitive information.
                 This option is recommended to create export for
                 actual namespace.

    kube-export -r deployments,configmap,secret
    kube-export --resources deployments,configmap,secret
                 Export only deployments,configmap and secret resource
                 from actual namespace

    kube-export show-api-resources
                 Print the supported API resources on the Kubernetes server.
                 This command prints namespaced and unnamespaced resources separetly.

    kube-export --all-namespaces
                 Export all recommended resource from all
                 namespaces excluding sensitive information.
                 This option is recommended to create export for
                 all namespaces

    kube-export -r node
    kube-export --resources node
                 Export only all node resources from cluster
    kube-export -c
    kube-export --cluster-recommended-resources
                 Export all recommended resources from all
                 namespaces including cluster resources but excluding
                 sensitive resources

    kube-export -cs
    kube-export --cluster-recommended-resources --sensitive
                 Export all recommended resources from all
                 namespaces including cluster resources and including
                 sensitive resources. !!! This options is recommended to
                 create cluster level export !!!
"""

import sys
import shutil
from docopt import docopt
from .console_logger import ColorPrint
from subprocess import Popen, PIPE

__version__ = '0.0.1'

CLUSTER_LVL_RESOURCES=['roles', 'rolebindings', 'clusterrolebindings', 'clusterroles', 'namespaces', 'pv', 'nodes',
                       'Storageclass', 'serviceaccounts']
SENSITIVE_RESOURCES=['secret']
RESOURCES=['cronjob', 'daemonset', 'deployment', 'job', 'pvc', 'configmap', 'serviceaccount', 'ingress',
           'service', 'statefulset', 'hpa']
BASE_COMMAND = ['kubectl', 'get']


class Kubexport(object):

    args = None

    def __init__(self, argv=sys.argv[1:]):
        self.args = docopt(__doc__, version=__version__,  argv=argv)
        Kubexport.check_kubernetes()

    def start(self):

        if self.has_args('--cluster-recommended-resources'):
            export_cluster_resources(CLUSTER_LVL_RESOURCES)

        cmd = list()
        cmd.append(BASE_COMMAND)

        namespaces = self.get_namespaces()
        if len(namespaces) > 0:
            for namespace in namespaces:
                pass

    def get_namespaces(self):
        if self.has_args('--namespaces'):
            s = self.args['--namespaces']
            return (s[1:] if s.startswith('=') else s).split(',')
        elif self.has_args('--all-namespaces'):
            return Kubexport.run_script_with_check(cmd=[BASE_COMMAND, "get", "-o=name", "namespaces"])\
                .replace("namespaces/", "").split()
        return []

    def export_cluster_resources(self):
        pass

    def has_args(self, *args):
        for arg in args:
            if not self.args.get(arg):
                return False
        return True

    @staticmethod
    def run_script_with_check(cmd):
        p = Popen(" ".join(cmd), stdout=PIPE, stderr=PIPE, shell=True)
        out, err = p.communicate()
        if not len(err) == 0:
            ColorPrint.exit_after_print_messages(message=str(err).strip())
        return out.strip()

    @staticmethod
    def check_kubernetes():
        command="kubectl version --short"
        p = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        out, err = p.communicate()
        if not len(err) == 0 or len(out) == 0:
            ColorPrint.exit_after_print_messages(message=str(err).strip())
        ColorPrint.print_with_lvl(message="Kubernetes\n " + str(out).strip(), lvl=1)


def main():
    kubexport = Kubexport()
    try:
        kubexport.start()
    except Exception as ex:
        if ColorPrint.log_lvl > 0:
            ColorPrint.exit_after_print_messages(message="Unexpected error: " + type(ex).__name__ + "\n" + str(ex))
        else:
            ColorPrint.exit_after_print_messages(message="Unexpected error: " + type(ex).__name__ + "\n" + str(ex.args)
                                                         + "\nRun with '-v' for more information.")

if __name__ == '__main__':
    sys.exit(main())
