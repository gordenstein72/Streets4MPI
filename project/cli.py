#!/usr/bin/env python2

# Author: Vlad Doster (mvdoster (at) gmail.com)
# Small cli tool to run different versions of streets4 program

import click

from project.streets4mpi import Streets4MPI
from streets4serial import Streets4Serial


@click.group()
@click.option('-n', '--num-residents', default=1000, show_default=True,
              help='This just hot swaps the number_of_residents setting in settings.py')
@click.option('-i', '--iterations', default=10, show_default=True,
              help='Number of iterations for timeit (higher = better average time)')
@click.option('-nt', '--num-threads', default=1, required=False,
              help='This will change number of threads each parallel program uses')
@click.pass_context
def cli(ctx, num_residents, num_threads, iterations):
    ctx.obj['NUM_RESIDENTS'] = num_residents
    ctx.obj['THREADS'] = num_threads
    ctx.obj['ITERATIONS'] = iterations



@cli.command()
@click.pass_context
def run_serial(ctx):
    """Run streets4serial.py"""
    click.echo("Running serial version with %d residents with %d iterations" % (
        ctx.obj['NUM_RESIDENTS'], ctx.obj['ITERATIONS']))
    from timeit import Timer
    t = Timer(lambda: Streets4Serial(num_of_residents=ctx.obj['NUM_RESIDENTS']))
    print("Execution time: " + str(t.timeit(number=ctx.obj['ITERATIONS'])) + " seconds")
    click.echo("Successfully ran serial version with %d residents with %d iterations" % (
        ctx.obj['NUM_RESIDENTS'], ctx.obj['ITERATIONS']))


@cli.command()
def run_mpi(ctx):
    """Run streets4mpi.py"""
    click.echo('Running mpi version with %s nodes' % ctx.obj[''])
    click.echo("Running serial version with %d residents with %d iterations" % (
        ctx.obj['NUM_RESIDENTS'], ctx.obj['ITERATIONS']))
    from timeit import Timer
    t = Timer(lambda: Streets4MPI(num_of_residents=ctx.obj['NUM_RESIDENTS']))
    print("Execution time: " + str(t.timeit(number=ctx.obj['ITERATIONS'])) + " seconds")
    click.echo("Successfully ran serial version with %d residents with %d iterations" % (
        ctx.obj['NUM_RESIDENTS'], ctx.obj['ITERATIONS']))


@cli.command()
@click.option('--num-threads', required=True)
def run_multi_proc(num_threads):
    """Run streets4multiprocessing.py"""
    click.echo("Running multiprocessing version with %s nodes" % num_threads)


if __name__ == '__main__':
    cli(obj={})
