import unittest
import rdetector


class TestRdetectorMethods(unittest.TestCase):
    deployments = [
        {'name': 'hello-minikube', 'pods': [
            {'pod': '825c0dec-e185-4c2e-8f29-716fc8650c4b', 'node': 'minikube'},
            {'pod': '414ac0f3-747f-49e8-ab89-c664cf2ac8a5', 'node': 'minikube'},
            {'pod': 'cf4a5605-6b9c-4208-b5c1-e7917fa78e52', 'node': 'minikube'}
        ]
        },
        {'name': 'coredns', 'pods': [
            {'pod': '8b62092d-df88-4160-8b81-0110f8b4c3ee', 'node': 'minikube'}
        ]
        },
        {'name': 'dashboard-metrics-scraper', 'pods': [
            {'pod': '465074a3-1a99-4cf8-bf0d-1422202ccaa8', 'node': 'minikube'}
        ]
        },
        {'name': 'kubernetes-dashboard', 'pods': [
            {'pod': '365c60b1-6124-4a4f-8993-e16576ceed99', 'node': 'minikube'}
        ]
        }
        ]

    def test_build_label_filter(self):
        match_labels = {
            'app': 'test-kubernetes'
        }
        match_many_labels = {
            'app': 'test-kubernetes',
            'group': 'more-data'
        }

        self.assertEqual(rdetector.build_label_filter(match_labels),
                         'app = test-kubernetes')
        self.assertEqual(rdetector.build_label_filter(match_many_labels),
                         'app = test-kubernetes,group = more-data')

    def test_find_deployments_with_multiple_pods_on_one_node(self):
        self.assertAlmostEqual(
            rdetector.find_deployments_with_multiple_pods_on_one_node(self.deployments),
            ["hello-minikube"]
            )
    
    def test_find_deployments_on_only_one_node(self):
        self.assertEqual(rdetector.find_deployments_on_only_one_node(self.deployments),
                         ["coredns", "dashboard-metrics-scraper", "kubernetes-dashboard"])
