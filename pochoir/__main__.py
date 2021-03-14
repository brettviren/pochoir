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
                  initial=intiial, boundary=boundary,
                  edges=edges, epoch=epoch, nepochs=nepochs,
                  precision=precision)
    ctx.obj.put(solution, arr, result="solution", **params)
    ctx.obj.put(error, err, result="error", **params)
    
@cli.command()
@click.argument("dataset")
@click.argument("plotfile")
@click.pass_context
def plot(ctx, dataset, plotfile):
    '''
    Plot a dataset
    '''
    arr = ctx.obj.get(dataset)
    pochoir.plots.image(arr, plotfile)


def main():
    cli(obj=None)


if '__main__' == __name__:
    main()
