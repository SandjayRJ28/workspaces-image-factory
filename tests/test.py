import pytest
import testinfra


@pytest.mark.parametrize("name,version", [
    ("7zip", "18.5.0.20180730"),
])
def test_packages(host, name, version):
    pkg = host.package(name)
    assert pkg.is_installed
    assert pkg.version.startswith(version)


# def check_ansible_play(host):
#     """
#     Verify that a package is installed using Ansible
#     package module
#     """
#     assert not host.ansible("package", "name=7zip state=present")["changed"]
