# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: blob_samples_directory_interface.py
DESCRIPTION:
    This example shows how to perform common filesystem-like operations on a
    container. This includes uploading and downloading files to and from the
    container with an optional prefix, listing files in the container both at
    a single level and recursively, and deleting files in the container either
    individually or recursively.

    To run this sample, provide the name of the storage container to operate on
    as the script argument (e.g. `python3 directory_interface.py my-container`).
    This sample expects that the `AZURE_STORAGE_CONNECTION_STRING` environment
    variable is set. It SHOULD NOT be hardcoded in any code derived from this
    sample.
  USAGE: python blob_samples_directory_interface.py CONTAINER_NAME
    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

import logging
import os

from azure.storage.blob import BlobServiceClient

logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
logger.setLevel("WARNING")


class DirectoryClient:
    def __init__(self, connection_string, container_name):
        service_client = BlobServiceClient.from_connection_string(connection_string)
        self.client = service_client.get_container_client(container_name)

    def upload(self, source, dest):
        """
    Upload a file or directory to a path inside the container
    """
        if os.path.isdir(source):
            self.upload_dir(source, dest)
        else:
            self.upload_file(source, dest)

    def upload_file(self, source, dest):
        """
    Upload a single file to a path inside the container
    """
        print(f"Uploading {source} to {dest}")
        with open(source, "rb") as data:
            self.client.upload_blob(name=dest, data=data, overwrite=True)

    def upload_dir(self, source, dest):
        """
    Upload a directory to a path inside the container
    """
        prefix = "" if dest == "" else dest + "/"
        prefix += os.path.basename(source) + "/"
        for root, dirs, files in os.walk(source):
            for name in files:
                dir_part = os.path.relpath(root, source)
                dir_part = "" if dir_part == "." else dir_part + "/"
                file_path = os.path.join(root, name)
                blob_path = prefix + dir_part + name
                self.upload_file(file_path, blob_path)

    def download(self, source, dest):
        """
    Download a file or directory to a path on the local filesystem
    """
        if not dest:
            raise Exception("A destination must be provided")

        blobs = self.ls_files(source, recursive=True)
        if blobs:
            # if source is a directory, dest must also be a directory
            if not source == "" and not source.endswith("/"):
                source += "/"
            if not dest.endswith("/"):
                dest += "/"
            # append the directory name from source to the destination
            dest += os.path.basename(os.path.normpath(source)) + "/"

            blobs = [source + blob for blob in blobs]
            for blob in blobs:
                blob_dest = dest + os.path.relpath(blob, source)
                self.download_file(blob, blob_dest)
        else:
            self.download_file(source, dest)

    def download_file(self, source, dest):
        """
    Download a single file to a path on the local filesystem
    """
        # dest is a directory if ending with '/' or '.', otherwise it's a file
        if dest.endswith("."):
            dest += "/"
        blob_dest = dest + os.path.basename(source) if dest.endswith("/") else dest

        print(f"Downloading {source} to {blob_dest}")
        os.makedirs(os.path.dirname(blob_dest), exist_ok=True)
        bc = self.client.get_blob_client(blob=source)
        with open(blob_dest, "wb") as file:
            data = bc.download_blob()
            file.write(data.readall())

    def ls_files(self, path, recursive=False):
        """
    List files under a path, optionally recursively
    """
        if not path == "" and not path.endswith("/"):
            path += "/"

        blob_iter = self.client.list_blobs(name_starts_with=path)
        files = []
        for blob in blob_iter:
            relative_path = os.path.relpath(blob.name, path)
            if recursive or not "/" in relative_path:
                files.append(relative_path)
        return files

    def ls_dirs(self, path, recursive=False):
        """
    List directories under a path, optionally recursively
    """
        if not path == "" and not path.endswith("/"):
            path += "/"

        blob_iter = self.client.list_blobs(name_starts_with=path)
        dirs = []
        for blob in blob_iter:
            relative_dir = os.path.dirname(os.path.relpath(blob.name, path))
            if (
                relative_dir
                and (recursive or not "/" in relative_dir)
                and not relative_dir in dirs
            ):
                dirs.append(relative_dir)

        return dirs

    def rm(self, path, recursive=False):
        """
    Remove a single file, or remove a path recursively
    """
        if recursive:
            self.rmdir(path)
        else:
            print(f"Deleting {path}")
            self.client.delete_blob(path)

    def rmdir(self, path):
        """
    Remove a directory and its contents recursively
    """
        blobs = self.ls_files(path, recursive=True)
        if not blobs:
            return

        if not path == "" and not path.endswith("/"):
            path += "/"
        blobs = [path + blob for blob in blobs]
        print(f'Deleting {", ".join(blobs)}')
        self.client.delete_blobs(*blobs)

