from os import getcwd

import platform
import subprocess
import sys

from . import arch, compile_commands, config, ninja, outputs, sources, templates, timing

spec = arch.create_platform_specs()

def _is_osx():
    return platform.system() == 'Darwin'

def scan_and_compile(f, ext):
    cfg = config.cached
    for file in sources.list_recursive(ext):
        vars_1 = cfg.get(file.fold, {}).get('variables', {})
        vars_2 = cfg.get(file.fold, {}).get(file.base, {}).get('variables', {})
        vars = { **vars_1, **vars_2 }
        stmt = ninja.BuildStatement(file.objf, ext + '2o', file.full, deps=file.deps, vars=vars)
        stmt.write(f)

def _list_modules():
    yield from sources.list_recursive('cppm', './sources/common/')
    yield from sources.list('./sources/' + spec.folder, 'cppm')

def scan_and_compile_modules(f):
    modules = ninja.BuildPhonyStatement('modules')
    
    cfg = config.cached
    for file in _list_modules():
        vars_1 = cfg.get(file.fold, {}).get('variables', {})
        vars_2 = cfg.get(file.fold, {}).get(file.base, {}).get('variables', {})
        vars = { **vars_1, **vars_2 }
        stmt = ninja.BuildStatement(file.pcmf, 'cppm2pcm', file.full, deps=file.deps, vars=vars)
        stmt.write(f)
        stmt = ninja.BuildStatement(file.objf, 'pcm2o', file.pcmf, vars=vars)
        stmt.write(f)

        modules.add_dependency(file.pcmf)

    modules.write_default(f)

def _list_modules_for_app(app):
    yield app
    yield from _list_modules()

def scan_and_link_singles(f, folder, ext):
    cfg = config.cached
    for file in sources.list(folder, ext):
        vars = cfg.get(folder, {}).get(file.base, {}).get('variables', {})
        out = "{0}/{1}".format(folder, file.base)
        ins = ' '.join([src.objf for src in _list_modules_for_app(file)])
        stmt = ninja.BuildStatement(out, 'link', ins, file.deps, vars)
        stmt.write_default(f)

def _list_srcs(app, exts):
    for ext in exts:
        yield from sources.list(app.rell, ext)
        yield from sources.list_recursive(ext, './sources/common/')
        yield from sources.list('./sources/' + spec.folder, ext)

def create_infoplist(file):
    out = "{0}/{1}.app/Contents".format(file.fold, file.base)
    outputs.create_dir(out)

    cfg = config.cached
    title = cfg.get(file.fold, {}).get(file.base, {}).get('title', file.base)

    with outputs.create_file(out + '/Info.plist') as f:
        templates.write_infoplist(f, exe=file.base, target='10.14', title=title)

def copy_images(f, app, app_stmt):
    for img in sources.list(app.rell, 'png'):
        out = "{0}/{1}.app/Contents/Resources/{2}.png".format(app.fold, app.base, img.base)

        stmt = ninja.BuildStatement(out, 'image', img.full)
        stmt.write(f)

        app_stmt.add_dependency(out)

def copy_resources(f, app, app_stmt):
    for img in sources.list(app.rell, 'res'):
        out = "{0}/{1}.app/Contents/Resources/{2}.res".format(app.fold, app.base, img.base)

        stmt = ninja.BuildStatement(out, 'copy', img.full)
        stmt.write(f)

        app_stmt.add_dependency(out)

def link_app(f, file, app_stmt):
    cfg = config.cached

    vars = cfg.get(file.fold, {}).get(file.base, {}).get('variables', {})
    out = '{0}/{1}'.format(spec.bundle_folder(file), spec.output_exe(file))
    ins = ' '.join([src.objf for src in _list_srcs(file, [ 'cpp', 'cppm', 'mm' ])])
    stmt = ninja.BuildStatement(out, 'link-app', ins, vars=vars)
    stmt.write(f)

    app_stmt.add_dependency(out)

def link_metal(f, file, app_stmt):
    metal_objs = [src.objf for src in _list_srcs(file, [ 'metal' ])]
    if len(metal_objs) == 0:
        return

    out = "{0}/{1}.app/Contents/Resources/default.metallib".format(file.fold, file.base)
    ins = ' '.join(metal_objs)
    stmt = ninja.BuildStatement(out, 'link-metal', ins)
    stmt.write(f)

    app_stmt.add_dependency(out)

def _gen_includes(f):
    f.write('includes = -I{cwd}/includes/common -I{cwd}/includes/{platform}'.format(
        cwd=getcwd(),
        platform=spec.folder,
    ))
    for folder in spec.includes:
        f.write(' -I' + folder)

    f.write('\n')

def _gen_build_ninja(f):
    cfg = config.cached

    for k, v in cfg.get('variables', {}).items():
        f.write('{0} = {1}\n'.format(k, v))

    f.write(spec.ninja_preamble)
    _gen_includes(f)

    templates.write_preamble(f)

    # TODO: Use SPIR-V or similar to convert between shader variants

    scan_and_compile_modules(f)

    for ext in ['cpp', 'metal', 'mm']:
        scan_and_compile(f, ext)

    scan_and_link_singles(f, 'tools', 'cpp')
    scan_and_link_singles(f, 'unit-tests', 'cpp')

    for file in sources.list_dirs('tests'):
        app_stmt = ninja.BuildPhonyStatement(file.base)
        app_stmt.add_dependency('modules')

        if _is_osx():
            create_infoplist(file)

        link_metal(f, file, app_stmt)

        copy_images(f, file, app_stmt)
        copy_resources(f, file, app_stmt)
        link_app(f, file, app_stmt)

        app_stmt.write_default(f)

    unit_tests_stmt = ninja.BuildPhonyStatement('test')
    for file in sources.list('unit-tests', 'cpp'):
        test = "{0}/{1}".format('unit-tests', file.base)
        out = 'run-{0}'.format(file.base)
        stmt = ninja.BuildStatement(out, 'run', test)
        stmt.write(f)

        unit_tests_stmt.add_dependency(out)

    unit_tests_stmt.write(f)

def run():
    outputs.create_dir()

    with outputs.create_file('build.ninja') as f:
        _gen_build_ninja(f)

    compile_commands.gen()

    if subprocess.call(ninja.run(*sys.argv[1:])) != 0:
        sys.exit(1)

    timing.run()
