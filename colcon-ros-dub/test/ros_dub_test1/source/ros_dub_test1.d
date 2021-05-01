module ros_dub_test1;

string hello()
{
  return "ros_dub_test1";
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
