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
import os
import shutil
from docopt import docopt
from .console_logger import ColorPrint
from .string_utils import StringUtils
from subprocess import Popen, PIPE

__version__ = '0.0.1'

class Kubexport(object):

    args = None
    checked_directory = []

    def __init__(self, argv=sys.argv[1:]):
        self.args = docopt(__doc__, version=__version__,  argv=argv)
        Kubexport.check_kubernetes()

    def start(self):
        if self.has_args('show-api-resources'):
            Kubexport.print_api_resoures()

        self.validate_output_format()

        if self.has_args('--resources'):
            self.export_resources()

        print(self.args)
        cmd = list()
        cmd.append(['kubectl', 'get'])

        namespaces = self.get_namespaces()
        if len(namespaces) > 0:
            for namespace in namespaces:
                pass

    def get_namespaces(self):
        if self.has_args('--namespaces'):
            s = self.args['--namespaces']
            return (s[1:] if s.startswith('=') else s).split(',')
        elif self.has_args('--all-namespaces'):
            return Kubexport.run_script_with_check(cmd=['kubectl', 'get', "-o=name", "namespaces"])\
                .replace("namespaces/", "").split()
        return []

    def export_resources(self):
        res = self.args['--resources']
        resources = (res[1:] if res.startswith('=') else res).split(',')
        cluster_res = Kubexport.get_resources(False, False)
        namespace_res = Kubexport.get_resources(True, False)

        for resource in resources:
            if resource in cluster_res:
                self.export_cluster_resource(resource)
            elif resource in namespace_res:
                self.export_namespace_resource(resource)
            else:
                ColorPrint.print_warning("Not found resource: " + str(resource))

    def export_cluster_resource(self, resource):
        ColorPrint.print_info("CLUSTER " + resource)

        cmd = ['kubectl', 'get']
        cmd.append("-o=name")
        cmd.append(resource)
        for row in Kubexport.run_script_with_check(cmd=cmd).split('\n'):
            self.check_directory(row)

            cmd = ['kubectl', 'get']
            cmd.append("-o")
            cmd.append(self.args["--output"])
            cmd.append(str(row))
            cmd.append("--export=true")
            with open(os.path.join(os.getcwd(), str(row) + '.' + self.args["--output"]), 'w') as file:
                file.write(Kubexport.run_script_with_check(cmd=cmd))

    def export_namespace_resource(self, resource):
        ColorPrint.print_info("NON CLUSTER " + resource)

    @staticmethod
    def print_api_resoures():
        ColorPrint.print_info("Cluster level resources: ")
        ColorPrint.print_info(Kubexport.get_resources(namespaced=False, wide=True))
        ColorPrint.print_info("Namespaced resources: ")
        ColorPrint.print_info(Kubexport.get_resources(namespaced=True, wide=True))
        sys.exit()

    @staticmethod
    def get_resources(namespaced, wide):
        cmd = ["kubectl", "api-resources"]
        cmd.append("-o")
        cmd.append("wide" if wide else "name")
        cmd.append("--namespaced=" + "true" if namespaced else "false")
        return Kubexport.run_script_with_check(cmd=cmd)

    def check_directory(self, row):
        chunks = row.split("/")

        dir = ""
        chunks.reverse()
        while len(chunks) > 1:
            dir += chunks.pop() if len(dir) == 0 else "/" + chunks.pop()

            if dir in self.checked_directory:
                continue
            directory = os.path.join(os.getcwd(), dir)
            exists = os.path.exists(directory)
            if exists and os.path.isfile(directory):
                ColorPrint.exit_after_print_messages("'" + directory + "' file exists in current directory.")

            if exists and not self.args['--keep-original']:
                shutil.rmtree(directory)

            if not os.path.exists(directory):
                os.makedirs(directory)

            self.checked_directory.append(dir)

    def validate_output_format(self):
        if self.args['--output'] not in ['yaml', 'json']:
            ColorPrint.print_error(message="Wrong output format, use default 'yaml' instead.")
            self.args['--output'] = 'yaml'

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
        command = "kubectl version --short --client"
        p = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        out, err = p.communicate()
        if not len(err) == 0 or len(out) == 0:
            ColorPrint.exit_after_print_messages(message=str(err).strip())
        ColorPrint.print_with_lvl(message="Kubernetes\n " + str(out).strip(), lvl=1)
        client_version = StringUtils.get_value_after_colon(out)
        if client_version is None:
            ColorPrint.exit_after_print_messages(message="Cannot fetch client version from: " + str(out).strip())
        if client_version < "v1.11.0":
            ColorPrint.exit_after_print_messages(message="Minimum client version is 1.11.0")


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
