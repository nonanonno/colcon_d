# colcon-ros-dub

An extension for [colcon-core](https://github.com/colcon/colcon-core) to support ROS2 DUB projects.

You can use [ros_dub_test1](test/ros_dub_test1) and [ros_dub_test2](test/ros_dub_test2) as example package. These packages explain:

- How to write package.xml and dub.json
    - It's necessary to write `installFiles` and `createFiles` in dub.json. And it's minimum example.
- How to write unittest (not a special method. You can write unittest just like dlang style)
- How to handle dependencies

## Status

- [x] Support package identify
- [x] Support build task
- [x] Support test task
- [x] Support handling package dependencies
