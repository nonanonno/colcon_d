# colcon-dub

An extension for [colcon-core](https://github.com/colcon/colcon-core) to support [DUB](https://dub.pm/index.html) projects.

## Extended functions for DUB
### Handle dub packages using environment variable 

Since DUB doesn't have function to get location of dependent package as environmental variable, this extension use `DUB_PACKAGE_PATH` to know dependent packages location. Then this writes dependent packages to `.dub/packages/local-packages.json`.

### Install any files to any directory

DUB doesn't have any function to copy files to any path, but to use DUB in ROS2, this function is required. So I extend following functions:

- `installFiles` : This directive represents source files(and directories) and destination directory. This may be used to install `package.xml`, `lanuch` and so on.
- `createFiles` : This directive just creates empty files to destination directory. This may be used to create a maker file for ament_index and so on.

Inside these directives, it's possible to use shell variables and following variables are added automatically.

- `$DUB_PACKAGE`: represents dub package name

Example

```json
...
"installFiles": {
    "share/$DUB_PACKAGE": [
        "package.xml",
        "launch"
    ]
},
"createFiles": {
    "share/ament_index/resource_index/packages": [
        "$DUB_PACKAGE"
    ]
}
```


## Status

- [x] Support package identify
- [x] Support build task
- [x] Support test task
- [x] Support handling package dependencies
- [x] Support install any files to any directory
- [ ] Support symlink install


## Notes

- Build task does not install library file to `lib/<package_name>` because dub refers external dub package directly.
- It's better to make symlink instead of copy for executable.
