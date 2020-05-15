import os
import os.path
import random
import re

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.conf.urls import url
from django.shortcuts import render

import mvs.settings as settings


class Photo:
    def __init__(self, folder, file):
        self.folder = folder
        self.file = file

    def get_link(self):
        # Get a link to the photoalbum page

        # Get index
        index = list(map(lambda p: p.file, self.folder.get_photos()
                         )).index(self.file)
        return self.folder.get_link() + '#' + str(index)

    def get_image_link(self):
        return '/media/fotos/' + self.folder.get_folder() + '/' + self.file

    def get_file_link(self):
        return 'fotos/' + self.folder.get_folder() + '/' + self.file

    def is_video(self):
        return self.file.endswith('.mp4')


class PhotosFolder:
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

    def get_directory(self):
        if self.parent is None:
            return settings.MEDIA_ROOT + '/fotos'
        else:
            return self.parent.get_directory() + '/' + self.name

    def get_breadcrumbs(self):
        if self.parent is None:
            return [self]
        else:
            breadcrumbs = self.parent.get_breadcrumbs()
            breadcrumbs.append(self)
            return breadcrumbs

    def get_name(self):
        return self.name.split('.', 1)[1].strip()

    def get_link(self):
        if self.parent is None:
            return '/fotos'
        else:
            return self.parent.get_link() + '/' + self.get_slug()

    def get_folder(self):
        if self.parent.parent is None:
            return self.name
        else:
            return self.parent.get_folder() + '/' + self.name

    def get_slug(self):
        name = self.get_name()
        name = name.replace('\'', '').lower()
        name = re.sub(r'[^a-z0-9]+', '-', name).strip('-')
        return name

    def get_subfolders(self):
        subfolders = []
        directory = self.get_directory()
        for dirname in sorted(os.listdir(directory)):
            if not dirname.startswith('.') and os.path.isdir(directory + '/' + dirname):
                subfolders.append(PhotosFolder(self, dirname))

        return subfolders

    def has_subfolders(self):
        return len(self.get_subfolders()) > 0

    def get_photos(self):
        return [Photo(self, filename)
                for filename in sorted(os.listdir(self.get_directory()))
                if (filename.endswith('.jpg') or filename.endswith('.mp4')) and not 'autocrop' in filename]

    def get_random_photo(self):
        if self.has_subfolders():
            return random.choice(self.get_subfolders()).get_random_photo()
        else:
            return random.choice(self.get_photos())

    def get_subfolder_for_slug(self, slug):
        for child in self.get_subfolders():
            if child.get_slug() == slug:
                return child

        return None

    @classmethod
    def get_root(cls):
        return PhotosFolder(None, '1. Foto\'s')

    @classmethod
    def get_for_url(cls, url):
        root = PhotosFolder.get_root()
        url_parts = url.split('/')

        folder = root
        for part in url_parts:
            folder = folder.get_subfolder_for_slug(part)
            if folder is None:
                return None

        return folder


def fotos_view(request, url):
    folder = PhotosFolder.get_for_url(url)
    return render(request, 'fotos.html', {'folder': folder})


@apphook_pool.register
class FotosHook(CMSApp):
    name = 'Fotos'

    def get_urls(self, page=None, language=None, **kwargs):
        # replace this with the path to your application's URLs module
        return [
            url(r'^(.+)', fotos_view),
        ]
