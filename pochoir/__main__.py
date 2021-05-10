#!/usr/bin/env python3
'''
CLI to pochoir
'''
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
@click.option("-d","--device",type=click.Choice(["cpu","cuda"]),default='cpu',
              help="Set device on which to calculate")
@click.pass_context
def cli(ctx, store, outstore, device):
    '''
    pochoir command line interface
    '''
    if not store:
        store = "."
    ctx.obj = pochoir.main.Main(store, outstore, device)

@cli.command()
def version():
    '''
    Print the version
    '''
    click.echo(pochoir.__version__)


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
        got = ctx.obj.get(thing)
        if isinstance(got, tuple):  # group
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
        # dataset or md, for now, assume the former
        print (f'{type(got)} {got.shape} {thing}')


@cli.command()
@click.option("-d", "--domain", type=str, 
              help="Use named dataset for the domain, (def: indices)")
@click.option("-i","--initial", type=str,
              help="Name initial value array")
@click.option("-b","--boundary", type=str,
              help="Name the boundary array")
@click.option("-g","--generator", type=str, default=None,
              help="Name the generator module")
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
    params = dict(domain=domain, result="gen", config=','.join(configs))
    ctx.obj.put(initial, iarr, **params)
    ctx.obj.put(boundary, barr, **params)
    

@cli.command()
@click.option("-d", "--domain", type=str, default=None,
              help="Use named dataset for the domain, (def: indices)")
@click.option("-r", "--result", type=str,
              help="Name the storage result")
@click.option("-t", "--temperature", type=str, default="89*K",
              help="Temperature")
@click.argument("potential")
@click.pass_context
def velo(ctx, domain, result, temperature, potential):
    '''
    Calculate a velocity field from a potential field
    '''
    temp = pochoir.arrays.fromstr1(temperature)[0]
    pot = ctx.obj.get(potential)
    dom = ctx.obj.get_domain(domain)

    efield = pochoir.arrays.gradient(pot, dom.spacing)
    emag = pochoir.arrays.vmag(efield)
    mu = pochoir.lar.mobility(emag, temp)
    velocity = [e*mu for e in efield]
    params = dict(domain=domain, result="velo", temperature=temp)
    ctx.obj.put(result, velocity, **params)



@cli.command()
@click.option("-d", "--domain", type=str, default=None,
              help="Use named dataset for the domain, (def: indices)")
@click.argument("scalar")
@click.argument("vector")
@click.pass_context
def grad(ctx, domain, scalar, vector):
    '''
    Calculate the gradient of a scalar field.
    '''
    pot = ctx.obj.get(scalar)
    if domain:
        domain = ctx.obj.get_domain(domain)
        spacing = domain.spacing
    else:
        spacing = None
    field = pochoir.arrays.gradient(pot, spacing=spacing)
    ctx.obj.put(vector, field, scalar=scalar, operation="grad")


@cli.command()
@click.option("-s","--shape", type=str, required=True,
              help="The number of grid points in each dimension")
@click.option("-o","--origin", default=None, type=str,
              help="The spatial location of zero index grid point (def=0's)")
@click.option("-S","--spacing", default=None, type=str,
              help="The grid spacing as scalar or vector (def=1's)")
@click.argument("name")
@click.pass_context
def domain(ctx, shape, origin, spacing, name):
    '''
    Produce a "domain" and store it to the output dataset.

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
    ctx.obj.put_domain(name, dom)

    
@cli.command()
@click.option("-d","--domain", default=None, type=str,
              help="Use domain for the plot")
@click.option("-s","--starts", default=None, type=str,
              help="Name the starts array to store")
@click.argument("points", nargs=-1)
@click.pass_context
def starts(ctx, domain, starts, points):
    '''
    Define drift path start points as N-d comma-separated vectors
    '''
    dom = ctx.obj.get_domain(domain)
    shape = (len(points), len(dom.shape))
    arr = pochoir.arrays.zeros(shape)
    for ind, spoint in enumerate(points):
        pt = pochoir.arrays.fromstr1(spoint)
        arr[ind] = pt

    ctx.obj.put(starts, arr, result="starts", domain=domain)


@cli.command()
@click.option("-r", "--result", type=str,
              help="Name the storage result")
@click.option("-s", "--steps", type=str,
              help="Give start,stop,step")
@click.option("-d","--domain", default=None, type=str,
              help="Use domain for the plot")
@click.option("-e","--engine", type=click.Choice(["scipy","torch"]),
              default="torch",
              help="Name the solver engine")
@click.argument("starts")
@click.argument("velocity")
@click.pass_context
def drift(ctx, result, steps, domain, engine, starts, velocity):
    '''
    Calculate drift paths.
    '''
    start, stop, step = pochoir.arrays.fromstr1(steps)
    nsteps = int((stop-start)/step)

    ticks = pochoir.arrays.linspace(start, stop, nsteps,
                                    endpoint=False)

    drifter = getattr(pochoir.drift, engine)
    dom = ctx.obj.get_domain(domain)
    velo = ctx.obj.get(velocity)
    velo = [v/s for v,s in zip(velo, dom.spacing)]

    start_points = ctx.obj.get(starts)

    paths = pochoir.arrays.zeros((len(start_points), len(ticks), len(dom.shape)))
    for ind, point in enumerate(start_points):
        print (f'path {ind} {point}')
        path = drifter(dom, point, velo, ticks)
        print(f'point: {point}, {path.shape}')
        if engine=="torch":
            paths[ind] = path.cpu().numpy()
        else:
            paths[ind]=path

    params=dict(result="drift", domain=domain,
                engine=engine, steps=steps)
    ctx.obj.put(result, paths, **params)
    

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
@click.option("-s","--solution", type=str,
              help="Name 2D solution value array")
@click.option("-i","--initial", type=str,
              help="Name 3D initial values array")
@click.option("-b","--boundary", type=str,
              help="Name 3D boundary array")
@click.option("-d","--domain2d", type=str,
              help="Name 2D domain")
@click.option("-D","--domain3d", type=str,
              help="Name 3D domain")
@click.option("-x","--xcoord", type=float, default=17.5,
              help="Name distance from the center along Xaxis to setup BC")
@click.argument("init_interpolated")
@click.argument("bc_interpolated")
@click.pass_context
def bc_interp(ctx, solution, initial, boundary,
        domain2d, domain3d, xcoord, init_interpolated,
        bc_interpolated):
    '''
    Interpolate 2D solution into 3D boundary condition
    '''
    sol2D = ctx.obj.get(solution)
    barr3D = ctx.obj.get(boundary)
    arr3D = ctx.obj.get(initial)
    dom2D = ctx.obj.get_domain(domain2d)
    dom3D = ctx.obj.get_domain(domain3d)
    arr, barr= pochoir.bc_interp.interp(sol2D, arr3D, barr3D, dom2D,
                                 dom3D, xcoord)
    params = dict(operation="bc_interp",
                  solution=solution, initial=initial, boundary=boundary,
                          domain2d=domain2d, domain3d=domain3d, xcoord=xcoord)
    ctx.obj.put(init_interpolated, arr, result="init_interpolated", **params)
    ctx.obj.put(bc_interpolated, barr, result="bc_interpolated", **params)


@cli.command()
@click.option("-d","--domaine", type=str,
              help="Name 3D domain for Ew calculation")
@click.option("-D","--domaind", type=str,
              help="Name 3D domain for drift calculation")
@click.option("-s","--solutione", type=str,
              help="Name 3D Ew solution")
@click.option("-S","--solutiond", type=str,
              help="Name 3D drift solution")
@click.option("-v","--velocity", type=str,
              help="Name velocity array")
@click.argument("sr_result")
@click.pass_context
def srdot(ctx,domaine,domaind,solutione,solutiond,velocity,sr_result):
    '''
    Make dot product between drift paths and weighted fields for the Shockley–Ramo theorem
    '''
    dom_Ew = ctx.obj.get_domain(domaine)
    dom_Drift = ctx.obj.get_domain(domaind)
    pot = ctx.obj.get(solutione)
    sol_Ew = pochoir.arrays.gradient(pot, dom_Ew.spacing)
    sol_Drift = ctx.obj.get(solutiond)
    velo = ctx.obj.get(velocity)
    res= pochoir.srdot.dotprod(dom_Ew,dom_Drift,sol_Ew,sol_Drift,velo)
    params = dict(operation="srdot",
                      domaine=domaine,domaind=domaind,solutione=solutione,solutiond=solutiond,velocity=velocity)
    ctx.obj.put(sr_result, res, result="sr_result", **params)


@cli.command()
@click.option("-i","--initial", type=str,
              help="Name initial value array")
@click.option("-b","--boundary", type=str,
              help="Name the boundary array")
@click.option("-e","--edges", type=str,
              help="Comma separated list of 'fixed' or 'periodic' giving domain edge conditions")
@click.option("--precision", type=float, default=0.0,
              help="Finish when no changes larger than precision")
@click.option("--epoch", type=int, default=1000,
              help="Number of iterations before any check")
@click.option("-n", "--nepochs", type=int, default=1,
              help="Limit number of epochs (def: one epoch)")
@click.argument("solution")
@click.argument("error")
@click.pass_context
def fdm(ctx, initial, boundary,
        edges, precision, epoch, nepochs,
        solution, error):
    '''
    Solve a Laplace boundary value problem with finite difference
    method storing the result as named solution.  The error names an
    output array to hold difference in last two iterations.
    '''
    iarr = ctx.obj.get(initial)
    barr = ctx.obj.get(boundary)
    bool_edges = [e.startswith("per") for e in edges.split(",")]
    if len(bool_edges) != iarr.ndim:
        raise ValueError("the number of periodic condition do not match problem dimensions")
    arr, err = pochoir.fdm.solve(iarr, barr, bool_edges,
                                 precision, epoch, nepochs)
    params = dict(operation="fdm", 
                  initial=initial, boundary=boundary,
                  edges=edges, epoch=epoch, nepochs=nepochs,
                  precision=precision)
    ctx.obj.put(solution, arr, result="solution", **params)
    ctx.obj.put(error, err, result="error", **params)

    
@cli.command("plot-image")
@click.option("-d","--domain", default=None, type=str,
              help="Use domain for the plot")
@click.argument("dataset")
@click.argument("plotfile")
@click.pass_context
def plot_image(ctx, domain, dataset, plotfile):
    '''
    Visualize a dataset as 2D image
    '''
    arr = ctx.obj.get(dataset)
    if domain:
        domain = ctx.obj.get_domain(domain)
    pochoir.plots.image(arr, plotfile, domain, dataset)

@cli.command("plot-quiver")
@click.option("-d", "--domain", type=str, default=None,
              help="Use named dataset for the domain, (def: indices)")
@click.option("-s", "--step", type=int, default=1,
              help="Set number of arrows to skip")
@click.argument("dataset")
@click.argument("plotfile")
@click.pass_context
def plot_quiver(ctx, domain, step, dataset, plotfile):
    '''
    Visualize a 2D or 3D vector field as a "quiver" plot.
    '''
    arr = ctx.obj.get(dataset)
    dom = ctx.obj.get_domain(domain)
    pochoir.plots.quiver(arr, plotfile, domain=dom, step=step)


@cli.command("plot-drift")
@click.option("-d", "--domain", type=str, default=None,
              help="Use named dataset for the domain, (def: indices)")
@click.option("-t", "--trajectory", type=int, default=-1,
              help="Numer of trajectories to plot (def: plot only traj 0)")
@click.argument("dataset")
@click.argument("plotfile")
@click.pass_context
def plot_drift(ctx, domain, trajectory, dataset, plotfile):

    arr = ctx.obj.get(dataset)
    dom = ctx.obj.get_domain(domain)
    pochoir.plots.drift(arr, plotfile, dom , trajectory)


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


def main():
    cli(obj=None)


if '__main__' == __name__:
    main()
