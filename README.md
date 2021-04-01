# Reproduction instructions

1. Run `pulumi up` once.
2. Run `pulumi up` again, and observe the spurious diff in the preview:

   ```
   benesch@langur$ pulumi up
   Previewing update (dev)

   View Live: https://app.pulumi.com/benesch/pulumi-bug/dev/previews/1f073b5f-ecb8-4ef6-ba52-b645387ea2a7

        Type                                                                             Name                                                              Plan
        pulumi:pulumi:Stack                                                              pulumi-bug-dev
        └─ kubernetes:helm.sh/v3:Chart                                                   aws-load-balancer-controller
    -      ├─ kubernetes:core/v1:ServiceAccount                                          default/aws-load-balancer-controller                              delete
    -      ├─ kubernetes:rbac.authorization.k8s.io/v1:Role                               default/aws-load-balancer-controller-leader-election-role         delete
    -      ├─ kubernetes:core/v1:Secret                                                  default/aws-load-balancer-tls                                     delete
    -      ├─ kubernetes:rbac.authorization.k8s.io/v1:ClusterRole                        aws-load-balancer-controller-role                                 delete
    -      ├─ kubernetes:rbac.authorization.k8s.io/v1:RoleBinding                        default/aws-load-balancer-controller-leader-election-rolebinding  delete
    -      ├─ kubernetes:core/v1:Service                                                 default/aws-load-balancer-webhook-service                         delete
    -      ├─ kubernetes:rbac.authorization.k8s.io/v1:ClusterRoleBinding                 aws-load-balancer-controller-rolebinding                          delete
    -      ├─ kubernetes:admissionregistration.k8s.io/v1:ValidatingWebhookConfiguration  aws-load-balancer-webhook                                         delete
    -      ├─ kubernetes:admissionregistration.k8s.io/v1:MutatingWebhookConfiguration    aws-load-balancer-webhook                                         delete
    -      ├─ kubernetes:apps/v1:Deployment                                              default/aws-load-balancer-controller                              delete
    -      └─ kubernetes:apiextensions.k8s.io/v1beta1:CustomResourceDefinition           targetgroupbindings.elbv2.k8s.aws                                 delete

   Resources:
       - 11 to delete
       33 unchanged
   ```

3. Accept the diff, and notice that none of the resources Pulumi was threatening
   to delete were deleted:

   ```
   View Live: https://app.pulumi.com/benesch/pulumi-bug/dev/updates/10

        Type                                                                                Name                               Status       Info
        pulumi:pulumi:Stack                                                                 pulumi-bug-dev
        ├─ eks:index:Cluster                                                                pulumi-bug
        │  └─ aws:eks:Cluster                                                               pulumi-bug-eksCluster
        └─ kubernetes:helm.sh/v3:Chart                                                      aws-load-balancer-controller
    ~      ├─ kubernetes:admissionregistration.k8s.io/v1:MutatingWebhookConfiguration       aws-load-balancer-webhook          updated      [diff: ~webhooks]
    ~      ├─ kubernetes:admissionregistration.k8s.io/v1:ValidatingWebhookConfiguration     aws-load-balancer-webhook          updated      [diff: ~webhooks]
           ├─ kubernetes:apiextensions.k8s.io/v1beta1:CustomResourceDefinition              targetgroupbindings.elbv2.k8s.aws               1 warning
    +-     └─ kubernetes:core/v1:Secret                                                     default/aws-load-balancer-tls      replaced     [diff: ~data]

   Diagnostics:
     kubernetes:apiextensions.k8s.io/v1beta1:CustomResourceDefinition    (targetgroupbindings.elbv2.k8s.aws):
       warning: apiextensions.k8s.io/v1beta1/CustomResourceDefinition is deprecated by    apiextensions.k8s.io/v1/CustomResourceDefinition and not supported by Kubernetes    v1.22+ clusters.

   Resources:
       ~ 2 updated
       +-1 replaced
       3 changes. 41 unchanged

   Duration: 14s
   ```