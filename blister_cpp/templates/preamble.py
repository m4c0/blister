from .. import outputs

_preamble = '''
cstd = -std=c++2a
modules = -fmodules -fprebuilt-module-path={build}/modules -fmodules-cache-path={build}/modules

run_clang = $clang $cflags $cstd $includes $isysroot
run_linker = $linker $ldflags

rule cpp2o
  depfile = $out.d
  command = $run_clang $modules $extra_cflags -MMD -MT $out -MF $out.d -c $in -o $out
  description = Compiling $out (C++)

rule cppm2pcm
  depfile = $out.d
  command = $run_clang $modules $extra_cflags -MMD -MT $out -MF $out.d -c $in -o $out --precompile -xc++-module
  description = Pre-compiling $out (C++ Module)

rule pcm2o
  command = $clang -c $in -o $out
  description = Compiling $out (C++ Module)

rule mm2o
  depfile = $out.d
  command = $run_clang -fmodules $extra_cflags -MMD -MT $out -MF $out.d -c $in -o $out -fobjc-arc
  description = Compiling $out (Obj-C)

rule link
  command = $run_linker $extra_ldflags $in -o $out
  description = Linking $out

rule link-app
  command = $run_linker $extra_ldflags $in -o $out $app_ldflags
  description = Linking Application $out

rule run
  command = $in
  description = Running $in 

rule copy
  command = cp $in $out
  description = Copying File $out

rule image
  command = convert $in PNG32:$out
  description = Copying Image $out

# Metaaaaal

rule metal2o
  command = xcrun -sdk macosx metal -c $in -o $out
  description = Compiling $out (Metal)

rule link-metal
  command = xcrun -sdk macosx metallib $in -o $out
  description = Linking Metal Library $out

'''

def write(f):
    f.write(_preamble.format(build=outputs.get_filename('')))
