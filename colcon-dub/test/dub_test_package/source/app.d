import std.stdio;

version (unittest)
{

}
else
{
  void main()
  {
    writeln("Hello, World!");
  }
}

@("success")
unittest
{
  assert(true);
}

@("fail")
unittest
{
  assert(false);
}
