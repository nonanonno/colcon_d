colcon-dub
=============

An extension for [colcon-core](https://github.com/colcon/colcon-core) to support [DUB](https://dub.pm/index.html) projects.

### Note

Since DUB doesn't have function to get location of dependent package as environmental variable, this extension use `DUB_PACKAGE_PATH` to know dependent packages location. Then this writes dependent packages to `.dub/packages/local-packages.json`.

### Status

- [x] Support package identify
- [x] Support build task
- [ ] Support test task
- [x] Support handling package dependencies
