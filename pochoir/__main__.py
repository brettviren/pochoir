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
@click.argument("name")
@click.pass_context
def example(ctx, name):
    '''
    Generate a boundary and initial array example (try "list")
    '''
    if name == "list":
        for one in dir(pochoir.examples):
            if one.startswith("ex_"):
                print(one[3:])
        return

    meth = getattr(pochoir.examples, "ex_" + name)

    iarr, barr = meth()
    ctx.obj.put(f'{name}-initial', iarr)
    ctx.obj.put(f'{name}-boundary', barr)
    

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
                arr = ctx.obj.get(thing + "/" + arrname)
                print (f'{type(arr)} {arr.shape} {arrname}')
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
@click.option("-g","--generator", type=str,
              help="Name the generator module")
@click.argument("configs", nargs=-1)
@click.pass_context
def gen(ctx, domain, generator, initial, boundary, configs):
    '''
    Generate initial and boundary value arrays from a high-level generator.
    '''
    cfg = dict()
    for config in configs:
        cfg.update(json.loads(open(config,'rb').read().decode()))
    meth = getattr(pochoir.gen, generator)

    dom = ctx.obj.get_domain(domain)
    iarr, barr = meth(dom, cfg)
    params = dict(domain=domain, result="gen", configs=','.join(configs))
    ctx.obj.put(initial, iarr, **params)
    ctx.obj.put(boundary, barr, **params)
    

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
@click.option("-s","--shape", default=None, type=str,
              help="The number of grid points in each dimension")
@click.option("-o","--origin", default=None, type=str,
              help="The spatial location of zero index grid point (def=0's)")
@click.option("-s","--spacing", default=None, type=str,
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
          the grid point with all indices zero.

        - spacing :: a scalar or N-D vector in same distance units as
          used in origin and which gives a common or a per-dimension
          spacing between neighboring grid points.

    A vector is given as a comma-separated list of numbers.

    Note: this description corresponds to vtk/paraview uniform
    rectilinear grid, aka an "image".
    '''
    shape = pochoir.arrays.fromstr1(shape, int)
    ndim = shape.size

    if spacing:
        if "," in spacing:
            spacing = pochoir.arrays.fromstr1(spacing)
        else:
            spacing = pochoir.arrays.zeros(ndim) + float(spacing)
    else:
        spacing = pochoir.arrays.ones(ndim)

    if origin:
        origin = pochoir.arrays.fromstr1(origin)
    else:
        origin = pochoir.arrays.zeros(ndim)

    dom = pochoir.domain.Domain(shape, spacing, origin)
    ctx.obj.put_domain(name, dom)

    
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
@click.argument("dataset")
@click.argument("plotfile")
@click.pass_context
def plot_quiver(ctx, domain, dataset, plotfile):
    '''
    Visualize a 2D or 3D vector field as a "quiver" plot.
    '''
    arr = ctx.obj.get(dataset)
    dom = ctx.obj.get_domain(domain)
    pochoir.plots.quiver(arr, plotfile, domain=dom)


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
