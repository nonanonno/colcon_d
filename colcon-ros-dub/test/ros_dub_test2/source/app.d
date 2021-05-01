import std.stdio;
import ros_dub_test1;

version (unittest)
{

}
else
{
  void main()
  {
    writeln(hello());
  }
}

@("success")
unittest
{
  assert(hello() == "ros_dub_test1");
}

@("fail")
unittest
{
  assert(hello() == "ros_dub_test2");
}
