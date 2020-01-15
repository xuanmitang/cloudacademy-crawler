import setuptools

def _read(filename):
      with open(filename, encoding='UTF-8') as ifs:
            return ifs.read()

def _readlines(filename):
      return [_ for _ in _read(filename).split('\n') if len(_) > 0]

setuptools.setup(
      name="cloudacademy-crawler",
      version="1.0",
      author="xuanmitang",
      author_email="xuanmitang@gmail.com",
      description="A simple cloudacademy course crawling & downloading tool",
      url="https://github.com/aileen0823/cloudacademy-crawler",
      keywords=['cloudacademy-crawler', 'cloudacademy', 'download', 'education'],
      packages=setuptools.find_packages(),
      install_requires=_readlines('requirements.txt'),
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
      ],
      entry_points={
            'console_scripts': ['ca_spider = course_spider:main']
      },
      python_requires='>=3.6',
)
