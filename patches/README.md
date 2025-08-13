These patches are applied to all submodules in the project to avoid including
foreign repositories and bloating this one.

`oss-quickjs.patch` - Modifies the docker build to use a custom quickjs version
modified by us.

`quickjs-abort.diff` - Patches a quickjs project to add our instrumentations
with a forcefull volatile assembly crash.

`quickjs-nop.diff` - Patches a quickjs project to add our instrumentations
with a forcefull volatile assembly nop, thus leaving the if statements in.

`quickjs-print.diff` - Patches a quickjs project to add our instrumentations
with a print of the instrumenation __FILE__ and __LINE__.
