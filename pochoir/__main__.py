#!/usr/bin/env python3
'''
CLI to pochoir
'''

import click
import pochoir
# no others than click and pochoir!

@click.group()
@click.option("-s","--store",type=click.Path(),
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
    Generate a boundary and initial array example
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
@click.argument("scalar")
@click.argument("vector")
@click.pass_context
def grad(ctx, scalar, vector):
    '''
    Calculate the gradient of a scalar field.
    '''
    pot = ctx.obj.get(scalar)
    field = pochoir.arrays.gradient(pot)
    ctx.obj.put(vector, field, scalar=scalar, operation="grad")


@cli.command()
@click.option("-o","--output", type=str,
              help="Name output result")
@click.option("-l","--like", type=str, default=None,
              help="Name an existing result to use for dimensions")
@click.argument("axes", nargs=-1)
@click.pass_context
def domain(ctx, output, like, axes):
    '''
    Produce a domain array and store to output dataset.

    Each argument describes a regular grid on one of the axes as three
    numbers: L:H:N

        - L center of the first grid point

        - H center of the last grid point

        - N is the number of bins

    If -l/--like is given then only L:H need be specified
    '''
    if like:
        larr = ctx.obj.get(like)
        shape = larr.shape
    else:
        shape = [int(one[-1]) for one in axes]
        
    lss = list()
    used = list()
    for one,size in zip(axes, shape):
        one = [float(a) for a in one.split(":")]
        this = (one[0], one[1], size)
        lss.append(this)
        used.append(':'.join([str(t) for t in this]))

    dom = pochoir.arrays.domain(lss)
    ctx.obj.put(output, dom, operation="domain", axes=' '.join(used))

    

@cli.command()
@click.option("-i","--initial", type=str,
              help="Name initial value array, elements include boundary values")
@click.option("-b","--boundary", type=str,
              help="Name the boundary array, zero value elemnts subject to solving")
@click.option("-e","--edges", type=str,
              help="Comma separated list of 'fixed' or 'periodic' giving domain edge conditions")
@click.option("--precision", type=float, default=0.0,
              help="Finish when no changes larger than precision")
@click.option("--epoch", type=int, default=1000,
              help="Number of iterations before any check")
@click.option("-n", "--nepochs", type=int, default=1.0,
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
    arr, err = pochoir.fdm.solve(iarr, barr, bool_edges,
                                 precision, epoch, nepochs)
    params = dict(operation="fdm", 
                  initial=initial, boundary=boundary,
                  edges=edges, epoch=epoch, nepochs=nepochs,
                  precision=precision)
    ctx.obj.put(solution, arr, result="solution", **params)
    ctx.obj.put(error, err, result="error", **params)
    
@cli.command("plot-image")
@click.argument("dataset")
@click.argument("plotfile")
@click.pass_context
def plot_image(ctx, dataset, plotfile):
    '''
    Visualize a dataset as 2D image
    '''
    arr = ctx.obj.get(dataset)
    pochoir.plots.image(arr, plotfile)

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
    pochoir.plots.quiver(arr, plotfile, domain=domain)


def main():
    cli(obj=None, auto_envvar_prefix="POCHOIR")


if '__main__' == __name__:
    main()
