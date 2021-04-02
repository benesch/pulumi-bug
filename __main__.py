"""An AWS Python Pulumi program"""

import json
from urllib.request import urlopen

import pulumi
import pulumi_aws as aws
import pulumi_eks as eks
import pulumi_kubernetes as k8s
from pulumi import Output

def eks_role_policy(oidc_provider, namespace, service_account):
    return Output.from_input(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Federated": oidc_provider.arn,
                    },
                    "Action": "sts:AssumeRoleWithWebIdentity",
                    "Condition": {
                        "StringEquals": {
                            Output.concat(oidc_provider.url, ":sub"): Output.concat(
                                "system:serviceaccount:",
                                namespace,
                                ":",
                                service_account,
                            )
                        }
                    },
                }
            ],
        }
    ).apply(json.dumps)

cluster_name = "pulumi-bug"
cluster = eks.Cluster("pulumi-bug", name=cluster_name, create_oidc_provider=True,)

base_name = f"pulumi-bug-aws-load-balancer-controller"

policy_url = "https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.1.3/docs/install/iam_policy.json"

policy = aws.iam.Policy(base_name, policy=urlopen(policy_url).read().decode("utf8"))

role = aws.iam.Role(
    base_name,
    assume_role_policy=eks_role_policy(
        cluster.core.oidc_provider, "default", "aws-load-balancer-controller"
    ),
)

aws.iam.RolePolicyAttachment(base_name, policy_arn=policy.arn, role=role)

def fix_chart(args, opts):
    if args["kind"] == "CustomResourceDefinition":
        # The chart has an errant `status` field in its CRD.
        # https://github.com/pulumi/pulumi-kubernetes/issues/800
        del args["status"]

k8s.helm.v3.Chart(
    "aws-load-balancer-controller",
    k8s.helm.v3.ChartOpts(
        chart="aws-load-balancer-controller",
        version="1.1.6",
        namespace="default",
        fetch_opts=k8s.helm.v3.FetchOpts(repo="https://aws.github.io/eks-charts"),
        values={
            "clusterName": cluster_name,
            "serviceAccount": {
                "annotations": {
                    "eks.amazonaws.com/role-arn": role.arn,
                }
            },
        },
        transformations=[fix_chart],
    ),
    opts=pulumi.ResourceOptions(provider=cluster.provider),
)
