Google Cloud SDK
================

Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)

Requirements
------------

None

Role Variables
--------------
| Name              | Default Value       | Description          |
|-------------------|---------------------|----------------------|
| `gcsdk_install_path` | `/usr/local/bin` | Path where SDK is installed |
| `gcsdk_bin_dir` | `[see defaults/main.yml` | Path where SDK binaries are symlinked |
| `gcsdk_link` | `/usr/local/opt` | List of files to symlink to `gcsdk_bin_dir`. |
| `gcsdk_components` | `[gke-cloud-auth-plugin]` | List of components to install. |


Example Playbook
----------------

    - hosts: dev
      roles:
         - samdoran.dev.google_cloud_sdk


License
-------

Apache 2.0
