NVIDIA Driver
=============

Install the [NVIDIA driver](https://www.nvidia.com/Download/index.aspx?lang=en-us) for Linux.

Requirements
------------

None

Role Variables
--------------
| Name              | Default Value       | Description          |
|-------------------|---------------------|----------------------|
| `nvidia_driver_download_dir` | `/var/tmp/nvidia` | Directory where the driver installer is downloaded |
| `nvidia_driver_version` | `515.76` | Version of the driver to download |
| `nvidia_driver_url` | [see `defaults/main.yml`] | URL where driver will be downloaded from |
| `nvidia_driver_extra_args` | <undefined> | Any extra command line parameters passed into the NVIDIA driver installer |



Example Playbook
----------------

    - hosts: dev
      roles:
         - samdoran.dev.nvidia_drivers


License
-------

Apache 2.0
