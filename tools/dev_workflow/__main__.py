"""One entry point for local checks, Blender operations and delivery."""
import argparse
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

from .records import Run, digest, identity, read, write


def parser():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2])
    p.add_argument('--run-dir',type=Path,help='New task directory under outputs; long logs and receipts stay here')
    commands=p.add_subparsers(dest='command',required=True)
    q=commands.add_parser('query',help='Read only matching historical GUI operations')
    q.add_argument('query'); q.add_argument('--limit',type=int,default=5)
    q=commands.add_parser('plan',help='Propose necessary checks; does not execute them')
    q.add_argument('--kind',choices=['docs','logic','geometry','ui','install'],required=True)
    q.add_argument('--base');q.add_argument('--module',action='append',default=[])
    q=commands.add_parser('check',help='Run only explicitly selected existing test modules')
    q.add_argument('--module',action='append',required=True);q.add_argument('--site',type=Path)
    q.add_argument('--name',default='checks');q.add_argument('--scope',action='append')
    q.add_argument('--input',type=Path,action='append',default=[])
    q.add_argument('--reuse',type=Path);q.add_argument('--retry',action='store_true')
    q=commands.add_parser('build',help='Full extension and node asset rebuild with existing locked wheels')
    q.add_argument('--blender',type=Path,required=True);q.add_argument('--existing-candidate',type=Path)
    q.add_argument('--retry',action='store_true')
    q=commands.add_parser('install',help='Install and verify exact candidate bytes in a fresh Blender process')
    q.add_argument('--candidate',type=Path,required=True);q.add_argument('--blender',type=Path,required=True)
    q.add_argument('--global-profile',action='store_true');q.add_argument('--installed-dir',type=Path)
    q=commands.add_parser('op',help='Execute the same fixed Blender operation through MCP or CLI')
    q.description=('Request JSON: {"action":"identity","args":{}}. Writes also require '
                   '"expected_pid": the current Blender PID. Actions/args: snapshot {}; '
                   'import {source}; annotation.add/edit {object,properties} (QCBlender operator properties); '
                   'trajectory.set {object,frame}; render {filepath,resolution_x?,resolution_y?,samples?}; '
                   'save {filepath}; assert {object,annotation_count?,kinds?,faces_camera?,arc_midpoints?} '
                   'or {expected: snapshot result}; quit {}. CLI owns its fresh process and supplies its PID. '
                   'MCP always requires the caller to verify the current identity before writes.')
    q.add_argument('--request',type=Path,required=True);q.add_argument('--transport',choices=['mcp','cli'],required=True)
    q.add_argument('--blender',type=Path);q.add_argument('--project',type=Path);q.add_argument('--global-profile',action='store_true')
    q.add_argument('--config',type=Path);q.add_argument('--timeout',type=float,default=180)
    q=commands.add_parser('mcp',help='Discover real HTTP MCP tools; credentials never enter receipts')
    q.add_argument('--config',type=Path);q.add_argument('--timeout',type=float,default=30)
    q=commands.add_parser('session',help='Manage one owned Blender process')
    s=q.add_subparsers(dest='session_command',required=True)
    s.add_parser('list')
    start=s.add_parser('start');start.add_argument('--blender',type=Path,required=True)
    start.add_argument('--project',type=Path);start.add_argument('--global-profile',action='store_true')
    start.add_argument('--script',type=Path)
    wait=s.add_parser('wait');wait.add_argument('--pid',type=int,required=True);wait.add_argument('--timeout',type=float,default=60)
    q=commands.add_parser('restore',help='Open the original saved project; optionally compare its saved baseline')
    q.add_argument('--blender',type=Path,required=True);q.add_argument('--project',type=Path,required=True)
    q.add_argument('--baseline',type=Path)
    q=commands.add_parser('finish',help='Preserve ignored files and archive an already merged task worktree')
    q.add_argument('--worktree',type=Path,required=True);q.add_argument('--date',required=True)
    q.add_argument('--apply',action='store_true',help='Perform the reviewed local archive; default only lists retention')
    return p


def native(run, binary, request, project=None, global_profile=False, gui=False):
    from .session import launch_blender
    folder=run.directory/('native-'+str(time.time_ns()))
    folder.mkdir()
    req, report=folder/'request.json',folder/'result.json'
    write(req,request)
    args=[] if gui else ['--background']
    args += [str(Path(project).resolve())] if project else []
    args += ['--python-exit-code','1','--python',str(run.repo/'tools/dev_workflow/blender_entry.py'),
             '--','--request',str(req),'--report',str(report),'--owned-process']
    process=launch_blender(binary,args,profile=None if global_profile else run.directory/'profile',outputdir=folder,wait=not gui)
    if gui:
        deadline=time.monotonic()+30
        while not report.exists() and time.monotonic()<deadline:
            time.sleep(.2)
    result=read(report) if report.exists() else dict(status='Failed',error='Blender did not produce a result; inspect process receipt',process=process)
    if process.get('exit_code',0)!=0:
        result['status']='Failed'
    return result,report,process


def main():
    args=parser().parse_args()
    repo=args.repo.resolve()
    if args.command=='query':
        from .catalog import query
        return query(repo,args.query,args.limit)
    if args.command=='plan':
        from .catalog import plan
        return plan(repo,args.kind,args.base,args.module)
    if args.command=='session' and args.session_command in ('list','wait'):
        from .session import list_blender_processes,wait_exit
        return dict(status='Passed',processes=list_blender_processes()) if args.session_command=='list' else wait_exit(args.pid,args.timeout)
    if not args.run_dir:
        raise ValueError('--run-dir is required for execution and receipts')
    run=Run(repo,args.run_dir)
    if args.command=='check':
        report=run.directory/(args.name+'-tests.json')
        inputs=args.input
        for name in ('dependencies.lock.json','science-sources.lock.json'):
            if (repo/name).exists(): inputs.append(repo/name)
        env=dict(python=sys.version,executable=str(Path(sys.executable).resolve()),
                 executable_sha256=digest(sys.executable),platform=platform.platform(),
                 site=str(args.site.resolve()) if args.site else None,modules=args.module)
        if args.site:
            env['installed_records']={str(p.relative_to(args.site)):digest(p) for p in sorted(args.site.glob('*.dist-info/RECORD'))}
        key=identity(repo,args.scope or ['qcblender','tools','tests'],inputs,env)
        cmd=[sys.executable,'-B',repo/'tools/dev_workflow/check_entry.py','--repo',repo,'--report',report]
        if args.site: cmd+=['--site',args.site.resolve()]
        for module in args.module:cmd+=['--module',module]
        return run.command(args.name,cmd,key,expected_report=report,reuse=args.reuse,retry=args.retry)
    if args.command=='build':
        from .artifacts import prepare_build,compare_candidate
        from .session import list_blender_processes
        from tools.package_identity import extension_filename,source_identity
        source_identity(repo)
        if list_blender_processes(): raise ValueError('Close Blender before the serial full build')
        if args.existing_candidate:prepare_build(repo,args.existing_candidate)
        key=identity(repo,['qcblender','tools/build_extension.py','tools/build_node_assets.py','dependencies.lock.json','science-sources.lock.json'],
                     [args.blender,repo/'outputs/backend-wheel.json'])
        out=run.directory/'dist'
        result=run.command('build',[sys.executable,'-B',repo/'tools/build_extension.py','--blender',args.blender,'--output-dir',out],key,retry=args.retry)
        if result['status']=='Passed':
            candidate=compare_candidate(repo,out/extension_filename(repo))
            run.record('candidate',candidate)
            receipt=read(run.directory/'build.json')
            receipt['outputs']={candidate['path']:candidate['sha256']}
            run.record('build',receipt)
            result['candidate']=candidate['path']
        return result
    if args.command=='mcp':
        from .mcp_client import discover
        started=time.monotonic()
        tools=discover(args.config,args.timeout)
        return run.record('mcp-tools-'+str(time.time_ns()),dict(status='Passed',tools=tools,transport='HTTP MCP',elapsed_seconds=time.monotonic()-started))
    if args.command=='op':
        request=read(args.request)
        name='op-'+request['action'].replace('.','-')+'-'+str(time.time_ns())
        started=time.monotonic()
        if args.transport=='mcp':
            from .mcp_client import run_operation
            result=run_operation(request,repo,args.config,args.timeout)
        else:
            if not args.blender:raise ValueError('CLI operation requires --blender')
            result,_,_=native(run,args.blender,request,args.project,args.global_profile)
        result.update(transport=args.transport,elapsed_seconds=time.monotonic()-started,request_sha256=digest(args.request))
        response=run.record(name,result)
        response['result']=result.get('result') if request['action']=='identity' else {'action':request['action']}
        return response
    if args.command=='install':
        from .artifacts import backup_install
        if args.global_profile:
            if not args.installed_dir:raise ValueError('Global install requires --installed-dir for the existing installation backup')
            backup=backup_install(args.installed_dir,run.directory/('global-before-'+str(time.time_ns())+'.zip'))
            run.record('global-backup',dict(status='Passed',**backup))
            preferences=args.installed_dir.parent.parent.parent/'config/userpref.blend'
            if preferences.is_file():
                import shutil
                target=run.directory/('userpref-before-'+str(time.time_ns())+'.blend')
                shutil.copy2(preferences,target)
        request=dict(action='install',args=dict(filepath=str(args.candidate.resolve()),repo='user_default'))
        result,_,_=native(run,args.blender,request,global_profile=args.global_profile)
        return run.record('global-install' if args.global_profile else 'isolated-install',result)
    if args.command=='session':
        from .session import launch_blender
        cmd=[str(args.project.resolve())] if args.project else []
        if args.script:cmd+=['--python',str(args.script.resolve())]
        result=launch_blender(args.blender,cmd,profile=None if args.global_profile else run.directory/'profile',outputdir=run.directory/('session-'+str(time.time_ns())))
        return dict(status='Passed',**result)
    if args.command=='restore':
        request=dict(action='snapshot',args={})
        if args.baseline:
            baseline=read(args.baseline)
            request=dict(action='assert',args=dict(expected=baseline.get('result',baseline)))
        result,report,process=native(run,args.blender,request,args.project,global_profile=True,gui=True)
        response=run.record('original-restored',dict(**result,process=process))
        response.update(project=str(args.project.resolve()),native_report=str(report))
        return response
    if args.command=='finish':
        from .artifacts import finish
        return finish(repo,args.worktree,run.directory,args.date,args.apply)
    raise ValueError('Unsupported command')


if __name__=='__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    try:
        response=main()
    except Exception as error:
        response={'status':'Failed','error':f'{type(error).__name__}: {error}'}
    print(json.dumps(response,ensure_ascii=False))
    raise SystemExit(response.get('status')!='Passed')
