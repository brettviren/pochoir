#!/usr/bin/env python3
'''
CLI to pochoir

pochoir [global options] <command> [command options] [arguments]

FIXME: most of this verbiage belongs in the manual.

Most commands here can be thought of nodes in a DAG joined by entries
in the pochoir data store.

For consistency the following conventions are followed:

    - both input from the store and named output destined for the
      store are given as command options.

    - input has lower-case short options, output has upper.

    - options may be used for non-store related names

    - arguments are for non-store related information

Every array output to the store should have metadata which describes
what inputs were used to create it.  Commands which need an ancestor
array do not be explicitly require it named on the command line but
instead it is resovled via metadta based on a more immediate input
array.

There is a data type taxonomy and its names are used in a manner
constient between CLI option names and store keys.  These are:

    - domain :: a grid of points in space

    - initial :: a scalar field holding an Initial Value Array

    - boundary :: a scalar field holding a Boundary Value Array

    - potential :: a scalar field such as solved by FDM

    - increment :: a scalar field holding the difference between two
      potentials from subsequent FDM steps aka the "error" in a
      potential solution.

    - velocity :: a vector velocity field

    - gradient :: a vector gradient field

    - points :: points in space

    - ...

Additional metadata may be stored such as:

    - taxon :: name the taxonomy type of the array

    - command :: name the command that produced the array
'''

import sys
import json
import click
import pochoir
# no others than click and pochoir!

@click.group()
@click.option("-s","--store",type=click.Path(),
              envvar="POCHOIR_STORE",
              help="File for primary data storage (input and maybe output)")
@click.option("-o","--outstore",type=click.Path(),
              help="File for output (primary only input)")
@click.pass_context
def cli(ctx, store, outstore):
    '''
    pochoir command line interface
    '''
    if not store:
        store = "."
    ctx.obj = pochoir.main.Main(store, outstore)

@cli.command()
def version():
    '''
    Print the version
    '''
    click.echo(pochoir.__version__)


@cli.command()
@click.option("-m", "--multi", default=None,
              type=click.Path(file_okay=False, dir_okay=True),
              help="Specify a directory to receive multi-file output")
@click.option("-o", "--output", default="/dev/stdout",
              type=click.Path(file_okay=True, dir_okay=False),
              help="Specify output file, default to stdout")
@click.argument("filename")
@click.pass_context
def gencfg(ctx, multi, output, filename):
    '''
    Generate JSON configuration files from master file.
    '''
    import json
    import pochoir.gencfg as gc
    if multi:
        gc.multi(filename, multi, output)
        return
    data = gc.loadf(filename)
    open(output,'wb').write(json.dumps(data).encode())

@cli.command()
@click.option("-s","--shape", type=str, required=True,
              help="The number of grid points in each dimension")
@click.option("-o","--origin", default=None, type=str,
              help="The spatial location of zero index grid point (def=0's)")
@click.option("-S","--spacing", default=None, type=str,
              help="The grid spacing as scalar or vector (def=1's)")
@click.option("-D", "--domain", type=str,
              help="Generated domain name") 
@click.pass_context
def domain(ctx, shape, origin, spacing, domain):
    '''
    Produce a "domain" and store it to the named dataset.

    A domain describes a finite, uniform grid in N-D space in these
    terms:

        - shape :: an N-D integer vector giving the number of grid
          points in each dimension.  Required.

        - origin :: an N-D spatial vector identifying the location of
          the grid point with all indices zero.  These may use spatial
          units.

        - spacing :: a scalar or N-D vector in same distance units as
          used in origin and which gives a common or a per-dimension
          spacing between neighboring grid points.  This may use
          spatial units.

    A vector is given as a comma-separated list of numbers.

    Spatial units are applied by multiplying a unit symbol such as

        - 10*mm

        - 2.4*cm

    If no spatial unit is given, mm is assumed.

    Note: this description corresponds to vtk/paraview uniform
    rectilinear grid, aka an "image".
    '''
    shape = pochoir.arrays.fromstr1(shape, int)
    ndim = shape.size

    if spacing:
        val = pochoir.arrays.fromstr1(spacing)
        if "," in spacing:
            spacing = val
        else:
            spacing = pochoir.arrays.zeros(ndim) + val[0]
    else:
        spacing = pochoir.arrays.ones(ndim)

    if origin:
        origin = pochoir.arrays.fromstr1(origin)
    else:
        origin = pochoir.arrays.zeros(ndim)

    dom = pochoir.domain.Domain(shape, spacing, origin)
    ctx.obj.put_domain(domain, dom)


@cli.command()
@click.option("-d", "--domain", type=str, 
              help="Use named dataset for the domain, (def: indices)")
@click.option("-I","--initial", type=str,
              help="Initial value array to generate")
@click.option("-B","--boundary", type=str,
              help="Boundary array array to generate")
@click.option("-g","--generator", type=str, default=None,
              help="The generator method")
@click.argument("configs", nargs=-1)
@click.pass_context
def gen(ctx, domain, generator, initial, boundary, configs):
    '''
    Generate initial and boundary value arrays from a high-level
    generator.
    '''
    if generator is None:
        print("available geometry generators:")
        for one in pochoir.gen.__dict__:
            if one[0] == "_":
                continue
            print('\t'+one)
        return

    cfg = dict()
    for config in configs:
        cfg.update(json.loads(open(config,'rb').read().decode()))
    cfg = pochoir.util.unitify(cfg)
    meth = getattr(pochoir.gen, generator)

    dom = ctx.obj.get_domain(domain)
    iarr, barr = meth(dom, cfg)
    params = dict(domain=domain, generator=generator,
                  command="gen", config=','.join(configs))
    ctx.obj.put(initial, iarr, taxon="initial", **params)
    ctx.obj.put(boundary, barr, taxon="boundary", **params)

    
@cli.command()
@click.option("-i","--initial", type=str,
              help="Name initial value array")
@click.option("-b","--boundary", type=str,
              help="Name the boundary array")
@click.option("-a","--ambient", type=float, default=0.0,
              help="Ambient potential")
@click.option("-d","--domain", default=None, type=str,
              help="Use domain for the plot")
@click.argument("filenames", nargs=-1)
@click.pass_context
def init(ctx, initial, boundary, ambient, domain, filenames):
    '''
    Initialize a problem with a shape file.

    This produces named initial and boundary value arrays.

    Filename arguments give JSON files which are progressively
    loadeded to update a configuration of shapes and their potentils.

    The full data structure is:

        {
            shapes: [ordered list of shapes],
            values: {shape name to value map},
        }

    Each element of the shapes array holds attributes:

        {
            name: "unique name of shape",
            type: "shape type name",
            ....: parameters depending on shape type
        }

    2D shapes and their args are:

    - rectangle :: "point1" and "point2" giving opposite corners as 2-element lists
    - circle :: "center" as 2 element list and "radius" 

    3D shapes and their args are:

    - box :: "point1" and "point2" giving opposite corners as 3-element lists
    - cylinder :: "center" and "radius" and "hheight" (half height) and axis of symmetry

    All spatial distances are given in the same unit as the domain spacing.
    The domain sets the allowed dimensionality.

    See also the "gen" command for a high-level way to init.
    '''
    dom = ctx.obj.get_domain(domain)

    cfg = dict()
    for fname in filenames:
        cfg.update(json.loads(open(fname,'rb').read().decode()))

    iarr, barr = pochoir.geom.init(dom, cfg, ambient)

    fnames = ",".join(filenames)
    ctx.obj.put(initial, iarr, result="initial",
                geom=fnames, domain=domain)
    ctx.obj.put(boundary, barr, result="boundary",
                geom=fnames, domain=domain)

@cli.command()
@click.option("-i","--initial", type=str,
              help="Input initial value array")
@click.option("-b","--boundary", type=str,
              help="Input the boundary array")
@click.option("-e","--edges", type=str,
              help="Comma separated list of 'fixed' or 'periodic' giving domain edge conditions")
@click.option("--precision", type=float, default=0.0,
              help="Finish when no changes larger than precision")
@click.option("--epoch", type=int, default=1000,
              help="Number of iterations before any check")
@click.option("-n", "--nepochs", type=int, default=1,
              help="Limit number of epochs (def: one epoch)")
@click.option("--engine",
              type=click.Choice(["numpy", "numba", "torch", "cupy", "cumba"]),
              default="numpy",
              help="The FDM engine to use")
@click.option("-P", "--potential", type=str,
              help="Output array holding solution for potential")
@click.option("-I", "--increment", type=str,
              help="Output array holding increment (error) on the solution")
@click.pass_context
def fdm(ctx, initial, boundary,
        edges, precision, epoch, nepochs, engine,
        potential, increment):
    '''
    Apply finite-difference method.

    Solve Laplace equation given initial/boundary value arrays to
    produce a scalar potential array.
    '''
    import pochoir.fdm
    try:
        solve = getattr(pochoir.fdm, f'solve_{engine}')
    except AttributeError as err:
        click.echo(f'no fdm solver engine {engine}')
        click.echo(err)
        sys.exit(-1)

    iarr, imd = ctx.obj.get(initial, True)
    barr, bmd = ctx.obj.get(boundary, True)
    if not "domain" in bmd:
        click.echo(f'failed to get domain for {boundary}')
        click.echo(bmd)
        sys.exit(-1)
    domain = bmd['domain']

    bool_edges = [e.startswith("per") for e in edges.split(",")]
    if len(bool_edges) != iarr.ndim:
        raise ValueError("the number of periodic condition do not match problem dimensions")

    arr, err = solve(iarr, barr, bool_edges,
                     precision, epoch, nepochs)

    params = dict(operation="fdm", domain=domain,
                  initial=initial, boundary=boundary,
                  edges=edges, epoch=epoch, nepochs=nepochs,
                  precision=precision, command="fdm")
    ctx.obj.put(potential, arr, taxon="potential", **params)
    ctx.obj.put(increment, err, taxon="increment", **params)



@cli.command()
@click.option("-t", "--temperature", type=str, default="89*K",
              help="LAr temperature")
@click.option("-p", "--potential", type=str,
              help="Input potential array")
@click.option("-V", "--velocity", type=str,
              help="Output velocity array")
@click.pass_context
def velo(ctx, temperature, potential, velocity):
    '''
    Calculate a velocity field from a potential field
    '''
    temp = pochoir.arrays.fromstr1(temperature)[0]
    pot, md = ctx.obj.get(potential, True)
    domain = md['domain']
    dom = ctx.obj.get_domain(domain)

    efield = pochoir.arrays.gradient(pot, *dom.spacing)
    emag = pochoir.arrays.vmag(efield)
    mu = pochoir.lar.mobility(emag, temp)
    varr = [e*mu for e in efield]
    params = dict(domain=domain, taxon="velocity", command="velo",
                  potential=potential, temperature=temp)
    ctx.obj.put(velocity, varr, **params)



@cli.command()
@click.option("-s", "--scalar", type=str,
              help="Input scalar array")
@click.option("-G", "--gradient", type=str,
              help="Output gradient array")
@click.pass_context
def grad(ctx, scalar, gradient):
    '''
    Calculate the gradient of a scalar field.
    '''
    pot, md = ctx.obj.get(scalar, True)
    domain = md['domain']
    dom = ctx.obj.get_domain(domain)
    field = pochoir.arrays.gradient(pot, *dom.spacing)
    ctx.obj.put(gradient, field, taxon="gradient",
                domain=domain, scalar=scalar, command="grad")


    
@cli.command()
@click.option("-S","--starts", default=None, type=str,
              help="Output starts points array")
@click.argument("points", nargs=-1)
@click.pass_context
def starts(ctx, starts, points):
    '''
    Store "starting" points.
    '''
    npoints = len(points)
    if not npoints:
        raise ValueError("require at least one point")
    points = [pochoir.arrays.fromstr1(p) for p in points]

    # fixme: we say we don't allow numpy in main...
    import numpy
    arr = numpy.asarray(points)
    ctx.obj.put(starts, arr, taxon="points", command="starts")


@cli.command("drift")
@click.option("-P", "--paths", type=str,
              help="Output paths array")
@click.option("--starts", type=str,
              help="Input starting points")
@click.option("--velocity", type=str,
              help="Intput velocity array")
@click.option("--verbose/--no-verbose", default=False,
              help="Verbose print during calculation")
@click.option("--engine", type=click.Choice(["numpy", "torch"]),
              default="numpy",
              help="The IVP engine to use")
@click.argument("steps", nargs=-1)
@click.pass_context
def drift(ctx, paths, starts, velocity, verbose, engine, steps):
    '''
    Calculate drift paths.
    '''
    start_points = ctx.obj.get(starts)
    if start_points is None:
        click.echo(f'no starts: {starts}')
        return -1

    steps = ','.join(steps)
    start, stop, step = pochoir.arrays.fromstr1(steps)
    nsteps = int((stop-start)/step)

    ticks = pochoir.arrays.linspace(start, stop, nsteps,
                                    endpoint=False)

    drifter = getattr(pochoir.drift, f'solve_{engine}')
    velo, md = ctx.obj.get(velocity, True)
    domain = md['domain']
    dom = ctx.obj.get_domain(domain)

    # shape: (nstarts, nticks, ndims)
    thepaths = pochoir.arrays.zeros((len(start_points), len(ticks),
                                     len(dom.shape)))
    for ind, point in enumerate(start_points):
        path = drifter(dom, point, velo, ticks, verbose=verbose)
        thepaths[ind]=path

    params=dict(taxon="paths", command="drift", domain=domain,
                tstart=start, tstop=stop, nsteps=nsteps)
    ctx.obj.put(paths, thepaths, **params)


@cli.command("bc-interp")
@click.option("-x","--xcoord", type=str, default="17.5*mm",
              help="Name distance from the center along Xaxis to setup BC")

@click.option("-p", "--potential2d", type=str,
              help="The input 2D scalar potential array")
@click.option("-i", "--initial3d", type=str,
              help="The input 3D scalar initial values array")
@click.option("-b", "--boundary3d", type=str,
              help="The input 3D scalar boundary value array")

@click.option("-I","--initial", type=str,
              help="The output interpolated 3D initial values array")
@click.option("-B","--boundary", type=str,
              help="The output interpolated 3D boundary array")
@click.pass_context
def bc_interp(ctx, xcoord,                        # option
              potential2d, initial3d, boundary3d, # input
              initial, boundary                   # output
              ):
    '''
    Interpolate 2D solution into 3D boundary condition
    '''
    sol2D, md2d = ctx.obj.get(potential2d, True)
    barr3D, md3d = ctx.obj.get(boundary3d, True)
    arr3D = ctx.obj.get(initial3d)
    domain2d = md2d['domain']
    domain3d = md3d['domain']
    dom2D = ctx.obj.get_domain(domain2d)
    dom3D = ctx.obj.get_domain(domain3d)
    xcoord = pochoir.util.unitify(xcoord)

    from pochoir.bc_interp import interp

    arr, barr= interp(sol2D, arr3D, barr3D, dom2D, dom3D, xcoord)
    params = dict(command="bc-interp",
                  potential2d=potential2d, initial3d=initial3d, boundary3d=boundary3d,
                  domain2d=domain2d, domain3d=domain3d, domain=domain3d,
                  xcoord=xcoord)
    ctx.obj.put(initial, arr, taxon="initial", **params)
    ctx.obj.put(boundary, barr, taxon="boundary", **params)


@cli.command()
@click.option("-i", "--input", type=str, required=True,
              help="The input paths array")
@click.option("-t", "--translation", type=str, required=True,
              help="A spacial vector along which to move the paths")
@click.option("-O", "--output", type=str, required=True,
              help="The output array name")
@click.pass_context
def move_paths(ctx, input, translation, output):
    '''
    Move paths along offset vector.
    '''
    arr, arrmd = ctx.obj.get(input, True)
    try:
        atype = arrmd['taxon']
    except KeyError:
        click.echo(f'array "{input}" has no type')
        click.exit(-1)
    
    if atype != "paths":
        click.echo(f'array "{input}" is not of type "paths"')
        click.exit(-1)

    translation = pochoir.arrays.fromstr1(translation)

    from pochoir.arrays import to_like
    newarr = arr + to_like(translation, arr)
    ctx.obj.put(output, newarr, **arrmd)



@cli.command()
@click.option("-q","--charge", default=1.0,
              help="The amount of drifting charge")
@click.option("-w","--weighting", type=str,
              help="The input scalar weighting potential")
@click.option("-p","--paths", type=str,
              help="The input drift paths array")
@click.option("-O", "--output", type=str,
              help="Output array holding induced current waveforms")
@click.pass_context
def induce(ctx, charge, weighting, paths, output):
    '''
    Calculate induced current.

    The current is that induced by the given charge moving along the
    paths and in the presence of a scalar weighting potential.
    '''
    wpot, wmd = ctx.obj.get(weighting, True)
    try:
        domain = wmd['domain']
    except KeyError:
        click.echo(f'no domain for {weighting}.  metadata:\n{wmd}')
        return -1
    dom = ctx.obj.get_domain(domain)

    the_paths, pmd = ctx.obj.get(paths, True)
    npaths, nsteps, ndim = the_paths.shape
    ticks = pochoir.arrays.linspace(pmd['tstart'], pmd['tstop'],
                                    pmd['nsteps'], endpoint=False)
    rgi = pochoir.arrays.rgi(dom.linspaces, wpot)
    Q = charge * rgi(the_paths)
    assert len(Q.shape) == 2
    assert Q.shape[0] == npaths
    assert Q.shape[1] == nsteps

    dQ = Q[:, 1:] - Q[:, :-1]
    dT = ticks[1:] - ticks[:-1]
    I = dQ/dT

    ctx.obj.put(output, I, command="induce", taxon="current",
                charge = charge,
                domain=domain, paths=paths, weighting=weighting)


    
@cli.command()
@click.option("-w","--weighting", type=str,
              help="Input 3D weighting potential")
@click.option("-p","--paths", type=str,
              help="Input 3D drift paths")
@click.option("-v","--velocity", type=str,
              help="Input velocity array")
@click.option("-C", "--current", type=str,
              help="Output current array")
@click.pass_context
def srdot(ctx, weighting, paths, velocity, current):
    '''
    Apply Ramo theorem dot product.
    '''
    pot, potmd = ctx.obj.get(weighting, True)
    pot_domain = potmd['domain']
    dom_Ew = ctx.obj.get_domain(pot_domain)


    sol_Ew = pochoir.arrays.gradient(pot, dom_Ew.spacing)
    sol_Drift, pathmd = ctx.obj.get(paths, True)
    path_domain = pathmd['domain']
    dom_Drift = ctx.obj.get_domain(path_domain)

    velo = ctx.obj.get(velocity)
    res = pochoir.srdot.dotprod(dom_Ew, dom_Drift, sol_Ew, sol_Drift, velo)
    params = dict(operation="srdot", 
                  weight_domain=pot_domain, path_domain=path_domain,
                  weighting=weighting, paths=paths, velocity=velocity)
    ctx.obj.put(current, res, command="srdot", taxon="response", **params)



@cli.command("plot-image")
@click.option("-a", "--array", type=str, required=True,
              help="Input array to plot")
@click.option("-o", "--output",
              type=click.Path(exists=False, dir_okay=False),
              help="Output graphics file")
@click.option("-s", "--scale", default="linear",
              type=click.Choice(["linear","signedlog"]),
              help="Output graphics file")
@click.option("-u", "--units", type=str, default=None,
              help="The units in which to display magnitude")
@click.pass_context
def plot_image(ctx, array, output, scale, units):
    '''
    Visualize a dataset as 2D image
    '''
    arr, md = ctx.obj.get(array, True)
    domain = md.get("domain")
    if domain:
        dom = ctx.obj.get_domain(domain)
    if units is not None:
        u = pochoir.arrays.fromstr1(units)
        arr = arr/u
    title = f'{array}'
    if units:
        title += f' [{units}]'
    pochoir.plots.image(arr, output, dom, title, scale=scale)

@cli.command("plot-scatter3d")
@click.option("-a", "--array", type=str, required=True,
              help="Input array to plot")
@click.option("-o", "--output",
              type=click.Path(exists=False, dir_okay=False),
              help="Output graphics file")
@click.option("-g", "--gif",
              default="no", type=click.Choice(["yes","no"]),
              help="create gif image ")
@click.pass_context
def plot_scatter3d(ctx, array, output,gif):
    '''
    Visualize a dataset as 3D image pdf + gif
    '''
    arr, md = ctx.obj.get(array, True)
    domain = md.get("domain")
    if domain:
        dom = ctx.obj.get_domain(domain)
    else:
        dom = ctx.obj.get_domain(doma)
    title = f'{array}'
    pochoir.plots.scatt3d(arr, output, dom,gif,title)
    
    
@cli.command("plot-slice3d")
@click.option("-a", "--array", type=str, required=True,
              help="Input array to plot")
@click.option("-o", "--output",
              type=click.Path(exists=False, dir_okay=False),
              help="Output graphics file")
@click.option("-s", "--scale", default="linear",
              type=click.Choice(["linear","signedlog"]),
              help="Output graphics file")
@click.option("-d", "--dim", default="z",
              type=click.Choice(["x","y","z"]),
              help="choose axis to slice")
@click.option("-m", "--magnitude", default="no", type=click.Choice(["yes","no"]),
              help="calc magnitude")
@click.option("-i","--index",type=int, default=1.0,
              help="choose index to slice")
@click.option("-u", "--units", type=str, default=None,
              help="The units in which to display magnitude")
@click.pass_context
def plot_slice3d(ctx, array, output, scale,dim, magnitude, index, units):
    '''
    Visualize a dataset as 2D image
    '''
    parr, md = ctx.obj.get(array, True)
    domain = md.get("domain")
    if magnitude == "yes" :
        import numpy
        arr = numpy.sqrt(parr[0]*parr[0]+parr[1]*parr[1]+parr[2]*parr[2])
    else:
        arr = parr
    if domain:
        dom = ctx.obj.get_domain(domain)
    if units is not None:
        u = pochoir.arrays.fromstr1(units)
        arr = arr/u
    title = f'{array}'
    if units:
        title += f' [{units}]'
    pochoir.plots.slice3d(arr, output, dom,scale,dim,index,title)

@cli.command("plot-mag")
@click.option("-a", "--array", type=str, required=True,
              help="Input array to plot")
@click.option("-o", "--output",
              type=click.Path(exists=False, dir_okay=False),
              help="Output graphics file")
@click.option("-u", "--units", type=str, default=None,
              help="The units in which to display magnitude")
@click.pass_context
def plot_mag(ctx, array, output, units):
    '''
    Plot magnitude of a vector field
    '''
    arr, md = ctx.obj.get(array, True)
    domain = md.get("domain")
    if domain:
        dom = ctx.obj.get_domain(domain)
    mag = pochoir.arrays.vmag(arr)
    if units is not None:
        u = pochoir.arrays.fromstr1(units)
        mag = mag/u
    title = f'{array}'
    if units:
        title += f' [{units}]'
    pochoir.plots.image(mag, output, dom, title)


@cli.command("plot-quiver")
@click.option("-a", "--array", type=str, required=True,
              help="Input array to plot")
@click.option("-o", "--output",
              type=click.Path(exists=False, dir_okay=False),
              help="Output graphics file")
@click.option("--step", default=1,
              help="Step over which to sample the array")
@click.option("--scale", default=None, type=float,
              help="Scale the arrows, larger number makes smaller arrows")
@click.option("--xlim", default=None, type=str,
              help="Limit X plot range")
@click.option("--ylim", default=None, type=str,
              help="Limit Y plot range")
@click.pass_context
def plot_quiver(ctx, array, output, step, scale, xlim, ylim):
    '''
    Visualize a 2D or 3D vector field as a "quiver" plot.
    '''
    arr, md = ctx.obj.get(array, True)
    domain = md.get("domain")
    if domain:
        dom = ctx.obj.get_domain(domain)
    if xlim:
        xlim = pochoir.arrays.fromstr1(xlim)
    if ylim:
        ylim = pochoir.arrays.fromstr1(ylim)

    pochoir.plots.quiver(arr, output, domain=dom, step=step,
                         limits=(xlim, ylim), scale=scale)


@cli.command("plot-drift")
@click.option("-t", "--trajectory", type=int, default=-1,
              help="Number of trajectories to plot (def: plot only traj 0)")
@click.option("-p", "--paths", type=str,
              help="The paths array to plot")
@click.option("-o", "--output",
              type=click.Path(exists=False, dir_okay=False),
              help="Output graphics file")
@click.pass_context
def plot_drift(ctx, trajectory, paths, output):
    '''
    Visualize 2D or 3D paths
    '''
    arr, md = ctx.obj.get(paths, True)
    domain = md.get("domain")
    dom = None
    if domain:
        dom = ctx.obj.get_domain(domain)
    if arr.shape[-1] == 2:
        pochoir.plots.drift2d(arr, output, dom, trajectory)
        return
    if arr.shape[-1] == 3:
        pochoir.plots.drift3d(arr, output, dom, trajectory,gif)
    click.echo(f'unsupported array of shape {arr.shape}')
    return -1

@cli.command("plot-drift3d")
@click.option("-t", "--trajectory", type=int, default=-1,
              help="Number of trajectories to plot (def: plot only traj 0)")
@click.option("-p", "--paths", type=str,
              help="The paths array to plot")
@click.option("-b", "--boundary", type=str,
              help="boundary array")
@click.option("-z", "--zoom", default="no", type=click.Choice(["yes","no"]),
              help="boundary array")
@click.option("-g", "--gif",
              default="no", type=click.Choice(["yes","no"]),
              help="create gif image ")
@click.option("-o", "--output",
              type=click.Path(exists=False, dir_okay=False),
              help="Output graphics file")
@click.pass_context
def plot_drift3d(ctx, trajectory, paths,boundary,zoom,gif, output):
    '''
    '''
    barr, mdb = ctx.obj.get(boundary, True)
    arr, md = ctx.obj.get(paths, True)
    domain = md.get("domain")
    dom = None
    if domain:
        dom = ctx.obj.get_domain(domain)
    title = f'{paths}'
    pochoir.plots.drift3d_b(arr,barr, output, dom, trajectory,zoom,gif,title)


@cli.command("export-vtk-image")
@click.argument("name")
@click.pass_context
def export_vtk(ctx, name):
    '''
    Export a dataset to a vtk file of same name
    '''
    arr = ctx.obj.get(name)
    scalars = {name: arr}
    pochoir.vtkexport.image3d(name, **scalars)


@cli.command()
@click.option("-d", "--domain", type=str, 
              help="Use named dataset for the domain, (def: indices)")
@click.option("-i","--initial", type=str,
              help="Name initial value array")
@click.option("-b","--boundary", type=str,
              help="Name the boundary array")
@click.argument("name")
@click.pass_context
def example(ctx, domain, initial, boundary, name):
    '''
    Generate a boundary and initial array example (try "list")
    '''
    if name == "list":
        for one in dir(pochoir.examples):
            if one.startswith("ex_"):
                print(one[3:])
        return

    meth = getattr(pochoir.examples, "ex_" + name)

    dom = None
    if domain:
        dom = ctx.obj.get_domain(domain)

    iarr, barr = meth(dom)
    ctx.obj.put(initial, iarr)
    ctx.obj.put(boundary, barr)
    

@cli.command()
@click.argument("things", nargs=-1)
@click.pass_context
def ls(ctx, things):
    '''
    List the store store
    '''
    if not things:
        things=["/"]

    for thing in things:
        got = ctx.obj.get(thing, True)
        if isinstance(got, tuple) and len(got) == 3:  # group
            dirs, arrs, mds = got
            print(f'store {ctx.obj.instore_name}: group {thing}:')
            for dirname in dirs:
                print(f'{dirname}/')
            for arrname in arrs:
                if thing == "/":
                    lookfor = arrname
                else:
                    lookfor = thing + "/" + arrname
                arr = ctx.obj.get(lookfor)
                print (f'{lookfor} {arr.dtype} {arr.shape}')
            return

        arr,md = got
        print(f'{thing}:')
        if arr is not None:
            print (f'\t{arr.shape} {arr.dtype}')
        if md is not None:
            print(f'\t{md}')

def main():
    cli(obj=None)


if '__main__' == __name__:
    main()
